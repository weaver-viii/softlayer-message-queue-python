#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='softlayer_messaging',
    version='0.2',
    author='Kevin McDonald',
    author_email='kmcdonald@softlayer.com',
    install_requires=['requests'],
    tests_require=['nose', 'mock'],
    packages=find_packages(exclude=['tests', 'ez_setup', 'examples']),
    test_suite='nose.collector',
    package_data={
        'softlayer_messaging': ['resources/config.json'],
    }
)
