import logging
import argparse
import time

import pymongo

from bitcoinrpc.authproxy import AuthServiceProxy

from bitcoinquery.util.config import config_parser
from bitcoinquery.util import mongodb

log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Start the blockchain data collection service',
    )
    parser.add_argument(
        'config',
        help=('path to the file with information on how to '
              'connect to other services'
              ),
        metavar='CONFIG',
        type=str,
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help='output DEBUG logging statements (default: %(default)s)',
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s.%(msecs)03d %(name)s: %(levelname)s: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    config = config_parser(args.config)
    database = mongodb.database(config)
    url = config.get('bitcoind', 'url')
    service = AuthServiceProxy(url)
    return (database, service)


def wait(diff):
    seconds = 60
    if not diff:
        log.info(
            'Sleeping {seconds} seconds'.format(seconds=seconds)
        )
        time.sleep(seconds)


def collect(database, service):
    block = database.blockchain.find_one(
        sort=[('_id', pymongo.ASCENDING)],
        field=['_id'],
    )
    if block is None:
        block = 0
    else:
        block = block['_id']
    count = service.getblockcount()
    diff = count - block
    log.info('Starting at block {block}'.format(block=block))
    log.info('Processing {diff} blocks'.format(diff=diff))

    return wait(diff)


def blockchain_collect():
    (database, service) = parse_args()
    collect(database, service)
