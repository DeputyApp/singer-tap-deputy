#!/usr/bin/env python3

import sys
import json
import argparse

import singer
from singer.utils import parse_args

from tap_deputy.client import DeputyClient
from tap_deputy.discover import discover
from tap_deputy.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    'start_date',
    'domain',
    'client_id',
    'client_secret',
    'redirect_uri',
    'refresh_token'
]

def do_discover(client):
    LOGGER.info('Testing authentication')
    try:
        # test by making the client fetch a resource info object
        client.get(
            '/api/v1/resource/Contact/INFO',
            endpoint='resource_info')
    except Exception as err:
        raise Exception('Error testing Deputy authentication') from err

    LOGGER.info('Starting discover')
    catalog = discover(client)
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info('Finished discover')

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = parse_args(REQUIRED_CONFIG_KEYS)
    if parsed_args.dev:
        LOGGER.warning("Executing Tap in Dev mode",)

    with DeputyClient(parsed_args.config, parsed_args.config_path, parsed_args.dev) as client:
        if parsed_args.discover:
            do_discover(client)
        else:
            sync(client,
                 parsed_args.catalog,
                 parsed_args.state,
                 parsed_args.config['start_date'])
