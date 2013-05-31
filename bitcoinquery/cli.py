import logging
import argparse
import time
import decimal
import json

import pymongo
import bson.json_util

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

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


def _json_decimal(value):
    if type(value) is decimal.Decimal:
        return str(value)
    raise TypeError(
        '{value} is not JSON serializable'.format(
            value=value,
        )
    )


def _bson_upsert(obj):
    son = dict([
        ('$set', obj),
    ])
    son = json.dumps(son, default=_json_decimal)
    son = bson.json_util.loads(son)
    son = dict([
        ('document', son)
    ])
    return son


def collect(database, service):
    start = database.blocks.find_one(
        sort=[('_id', pymongo.DESCENDING)],
        field=['_id'],
    )
    if start is None:
        # Skip genesis block
        start = 1
    else:
        # Always reprocess last block in case we missed transactions
        start = start['_id']
    count = service.getblockcount()
    diff = work = count - start
    log.info('Starting at block {start}'.format(start=start))
    log.info('Processing {diff} blocks'.format(diff=diff))

    current = service.getblockhash(start)
    while current:
        block = service.getblock(current)
        kwargs = _bson_upsert(block)
        mongodb.safe_upsert(
            collection=database.blocks,
            _id=block['height'],
            **kwargs
        )
        txs = block['tx']
        for tx in txs:
            try:
                raw = service.getrawtransaction(tx)
                decoded = service.decoderawtransaction(raw)
                decoded['bitcoinquery'] = dict([
                    ('blockhash', current),
                    ('blockheight', block['height']),
                ])
                kwargs = _bson_upsert(decoded)
                mongodb.safe_upsert(
                    collection=database.transactions,
                    _id=decoded['txid'],
                    **kwargs
                )
            except JSONRPCException, e:
                log.debug(
                    'Failed to get retrieve transaction {tx} in '
                    'block {current}'.format(
                        tx=tx,
                        current=current,
                    )
                )
                error = dict([
                    ('txid', tx),
                    ('error', e.error),
                ])
                database.errors.insert(error)
        current = block.get('nextblockhash')
    # Processing last block does not count as work
    return work


def blockchain_collect():
    (database, service) = parse_args()
    work = collect(database, service)
    wait(work)
    log.info('Ending')
