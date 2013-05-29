============
bitcoinquery
============

bitcoinquery stores the Bitcoin blockchain in a MongoDB database to
allow querying of block and transaction data

Usage
=====

In order to use bitcoinquery you need a Bitcoind RPC server. The
server must maintain a full index in order to retrieve all
transactions. To do this, run the server with the -txindex option or
set txindex=1 in the server's conf file. If you are already running a
server without a full index you must reindex the server with the
-reindex option.

Installation
============

System dependencies
-------------------

    - Python 2.7
    - MongoDB 2.4.0
    - Bitcoind 0.8.1.0

Python external dependencies
----------------------------

    - python-setuptools
    - python-virtualenv

Setup
-----

To install bitcoinquery run the following commands from the project's
base directory. You can download the source code from github_::

    virtualenv .virtual
    .virtual/bin/python setup.py install
    # At this point, bitcoinquery will already be in easy-install.pth.
    # So, pip will not attempt to download it
    .virtual/bin/pip install bitcoinquery[test]

    # The test requirement installs all the dependencies. But,
    # depending on the service you wish to run you might want to
    # install only the appropriate dependencies as listed in
    # setup.py. For example to run blockchain-collect you only need
    # the mongo and bitcoin requirements which install the pymongo and
    # python-bitcoinrpc dependencies
    .virtual/bin/pip install bitcoinquery[mongo,bitcoin]

Running
=======

It is recommended that you use an init daemon such as upstart_ or
runit_ to run the bitcoinquery services.

Collection service
------------------

To start the service which collects and stores block and transaction
data call the ``blockchain-collect`` cli with the ``CONFIG``
argument::

    .virtual/bin/blockchain-collect collect.conf

where ``collect.conf`` looks like::

    [bitcoind]
    url = http://<username>:<password>@<host>:<port>

    [mongodb]
    host = <host>:<port>
    database = bitcoinquery
    collections = blocks,transactions,errors

Developing
==========

To start developing follow the instructions in the Installation_
section but replace::

    .virtual/bin/python setup.py install

with::

    .virtual/bin/python setup.py develop

If you like to use IPython you can install it with the dev
requirement::

    .virtual/bin/pip install bitcoinquery[dev]

.. _runit: http://smarden.org/runit/
.. _upstart: http://upstart.ubuntu.com/
.. _github: https://github.com/thelinuxkid/bitcoinquery
