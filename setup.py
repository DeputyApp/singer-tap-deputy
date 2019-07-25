#!/usr/bin/env python

from setuptools import setup

setup(name='tap-deputy',
      version='0.0.1',
      description='Singer.io tap for extracting data from the Deputy API',
      author='Deputy',
      url='https://www.deputy.com',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_deputy'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.21.0',
          'singer-python==5.8.0'
      ],
      entry_points='''
          [console_scripts]
          tap-deputy=tap_deputy:main
      ''',
      packages=['tap_deputy']
)
