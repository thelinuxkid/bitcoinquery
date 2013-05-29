#!/usr/bin/python
from setuptools import setup, find_packages
import os

EXTRAS_REQUIRES = dict(
    mongo=[
        'pymongo>=2.3',
    ],
    bitcoin=[
        'python-bitcoinrpc>=0.1',
    ],
    test=[
        'nose>=1.3.0',
        'mock>=0.8.0',
        ],
    dev=[
        'ipython>=0.13',
        ],
    )

# Pypi package documentation
root = os.path.dirname(__file__)
path = os.path.join(root, 'README.rst')
with open(path) as fp:
    long_description = fp.read()

# Tests always depend on all other requirements, except dev
for k,v in EXTRAS_REQUIRES.iteritems():
    if k == 'test' or k == 'dev':
        continue
    EXTRAS_REQUIRES['test'] += v

setup(
    name='bitcoinquery',
    version='0.0.2',
    description='Bitcoinquery -- Query blockchain data',
    long_description=long_description,
    author='Andres Buritica',
    author_email='andres@thelinuxkid.com',
    maintainer='Andres Buritica',
    maintainer_email='andres@thelinuxkid.com',
    url='https://github.com/thelinuxkid/bitcoinquery',
    license='MIT',
    packages = find_packages(),
    test_suite='nose.collector',
    install_requires=[
        'setuptools',
        ],
    entry_points={
        'console_scripts': [
            'blockchain-collect = bitcoinquery.cli:blockchain_collect[mongo,bitcoin]',
            ],
        },
    extras_require=EXTRAS_REQUIRES,
    dependency_links=[
        'http://github.com/jgarzik/python-bitcoinrpc/tarball/master#egg=python-bitcoinrpc-0.1',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7'
    ],
)
