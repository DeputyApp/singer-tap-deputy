#!/usr/bin/env python3

import sys
import json
import argparse

import singer
from singer import metadata

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
        pass
        ## TODO: find test endpoint
    except:
        raise Exception('Error testing Deputy authentication')

    LOGGER.info('Starting discover')
    catalog = discover(client)
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info('Finished discover')

##### TEMP

import argparse

from singer.catalog import Catalog

def check_config(config, required_keys):
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise Exception("Config is missing required keys: {}".format(missing_keys))

def load_json(path):
    with open(path) as fil:
        return json.load(fil)

def parse_args(required_config_keys):
    '''Parse standard command-line args.
    Parses the command-line arguments mentioned in the SPEC and the
    BEST_PRACTICES documents:
    -c,--config     Config file
    -s,--state      State file
    -d,--discover   Run in discover mode
    -p,--properties Properties file: DEPRECATED, please use --catalog instead
    --catalog       Catalog file
    Returns the parsed args object from argparse. For each argument that
    point to JSON files (config, state, properties), we will automatically
    load and parse the JSON file.
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--config',
        help='Config file',
        required=True)

    parser.add_argument(
        '-s', '--state',
        help='State file')

    parser.add_argument(
        '-p', '--properties',
        help='Property selections: DEPRECATED, Please use --catalog instead')

    parser.add_argument(
        '--catalog',
        help='Catalog file')

    parser.add_argument(
        '-d', '--discover',
        action='store_true',
        help='Do schema discovery')

    args = parser.parse_args()
    if args.config:
        setattr(args, 'config_path', args.config)
        args.config = load_json(args.config)
    if args.state:
        setattr(args, 'state_path', args.state)
        args.state = load_json(args.state)
    else:
        args.state = {}
    if args.properties:
        setattr(args, 'properties_path', args.properties)
        args.properties = load_json(args.properties)
    if args.catalog:
        setattr(args, 'catalog_path', args.catalog)
        args.catalog = Catalog.load(args.catalog)

    check_config(args.config, required_config_keys)

    return args

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = parse_args(REQUIRED_CONFIG_KEYS)

    with DeputyClient(parsed_args.config, parsed_args.config_path) as client:
        if parsed_args.discover:
            do_discover(client)
        else:
            if parsed_args.catalog:
                catalog = parsed_args.catalog
            else:
                catalog = discover(client)

            sync(client,
                 catalog,
                 parsed_args.state,
                 parsed_args.config['start_date'])
