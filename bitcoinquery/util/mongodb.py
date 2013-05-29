import pymongo

from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import InvalidName

DEFAULT_DB_HOST = 'localhost:27017'


class ProxyDatabase(Database):
    """
    A Mongo database which only allows collections specified at object
    creation
    """

    def __init__(self, connection, name, collections, *args, **kwargs):
        self._collections = collections
        Database.__init__(self, connection, name, *args, **kwargs)

    def __getattr__(self, name):
        """Get a collection of this database by name.

        Raises InvalidName if an invalid collection name is used or
        if the collection name is not in the collections list.

        :Parameters:
          - `name`: the name of the collection to get
        """
        if name not in self._collections:
            raise InvalidName(
                'Collection {name} is not in collections list'.format(
                    name=name,
                )
            )
        return Collection(self, name)


def _connection(config):
    conn = dict(config.items('mongodb'))
    if 'host' not in conn:
        conn['host'] = DEFAULT_DB_HOST

    colls = conn['collections'].split(',')
    colls = [coll.strip() for coll in colls]
    conn['collections'] = colls
    return conn


def database(
    config,
    read_preference=None,
):
    conn = _connection(config)
    host = conn['host']
    replica_set = conn.get('replica-set')
    db = conn['database']
    colls = conn['collections']

    if replica_set:
        conn = pymongo.ReplicaSetConnection(
            host,
            replicaSet=replica_set,
        )
        # ReadPreference.PRIMARY is the default
        if read_preference is not None:
            conn.read_preference = read_preference
    else:
        conn = pymongo.Connection(host)

    db = ProxyDatabase(conn, db, colls)
    return db


def create_indices(
    collection,
    indices,
):
    for index in indices:
        collection.ensure_index(index.items())


def safe_upsert(
    collection,
    _id,
    **kwargs
):
    if kwargs:
        collection.update(
            spec=dict([
                ('_id', _id),
            ]),
            upsert=True,
            safe=True,
            **kwargs
        )
