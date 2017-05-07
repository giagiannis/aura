#!/usr/bin/python

from setuptools import setup

setup(
        name='aura',
        version='1.0',
        author='Giannis Giannakopoulos',
        author_email='ggian@cslab.ece.ntua.gr',
        description='A deployment tool for Openstack with error-recovery enhancements',
        license='Apache License 2.0',
        url='https://github.com/giagiannis/aura',
        packages=['aura', 'tests'],
        scripts=['bin/aura', 'bin/aura-server'],
        setup_requires=['pytest-runner'],
        tests_require=['pytest']
        )
