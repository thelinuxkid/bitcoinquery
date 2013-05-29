import mock

from bitcoinquery import cli


@mock.patch('bitcoinquery.cli._bson_upsert')
@mock.patch('bitcoinquery.util.mongodb.safe_upsert')
def test_collect_simple(fake_upsert, fake_bson):
    fake_db = mock.Mock()
    one = dict([
        ('_id', 2),
    ])
    fake_db.blocks.find_one.return_value = one

    fake_sv = mock.Mock()
    fake_sv.getblockcount.return_value = 2
    fake_sv.getblockhash.return_value = 'foo hash'
    block = dict([
        ('tx', ['foo tx']),
        ('nextblockhash', None),
        ('height', 2),
    ])
    fake_sv.getblock.return_value = block
    fake_sv.getrawtransaction.return_value = 'foo raw'
    decoded = dict([
        ('txid', 'foo txid'),
    ])
    fake_sv.decoderawtransaction.return_value = decoded

    block_bson = dict([('block', 'bson')])
    transaction_bson = dict([('transaction', 'bson')])
    fake_bson.side_effect = [block_bson, transaction_bson]

    cli.collect(fake_db, fake_sv)

    query = mock.call.blocks.find_one(
        sort=[('_id', -1)],
        field=['_id'],
    )
    db_calls = [query]
    assert fake_db.mock_calls == db_calls

    count = mock.call.getblockcount()
    hash_ = mock.call.getblockhash(2)
    block = mock.call.getblock('foo hash')
    raw = mock.call.getrawtransaction('foo tx')
    decode = mock.call.decoderawtransaction('foo raw')
    sv_calls = [count, hash_, block, raw, decode]
    assert fake_sv.mock_calls == sv_calls

    block_upsert = mock.call(
        collection=fake_db.blocks,
        _id=2,
        block='bson',
    )
    transaction_upsert = mock.call(
        collection=fake_db.transactions,
        _id='foo txid',
        transaction='bson',
    )
    upsert_calls = [block_upsert, transaction_upsert]
    assert fake_upsert.mock_calls == upsert_calls
