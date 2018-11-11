import argparse
import requests
import os
import json
import singer
#import singer.stats
import datetime
import logging

import http.client as http_client

from singer import utils
#from singer import stats
from jsonschema import ValidationError, Draft4Validator, validators, FormatChecker

# TODO: RECORD to SCHEMA Validation prior to write_record()


SESSION = requests.Session()
LOGGER = singer.get_logger()

STATE = {}
CONFIG = {}
RESOURCES = {
    0: "Address",
    1: "Category",
    2: "Comment",
    3: "Company",
    4: "CompanyPeriod",
    5: "Contact",
    6: "CustomAppData",
    7: "CustomField",
    8: "CustomFieldData",
    9: "Employee",
    10: "EmployeeAgreement",
    11: "EmployeeAgreementHistory",
    12: "EmployeeAppraisal",
    13: "EmployeeAvailability",
    14: "EmployeeHistory",
    15: "EmployeePaycycle",
    16: "EmployeePaycycleReturn",
    17: "EmployeeRole",
    18: "EmployeeSalaryOpunitCosting",
    19: "EmployeeWorkplace",
    20: "EmploymentCondition",
    21: "EmploymentContract",
    22: "EmploymentContractLeaveRules",
    23: "Event",
    24: "Geo",
    25: "Journal",
    26: "Leave",
    27: "LeaveAccrual",
    28: "LeavePayLine",
    29: "LeaveRules",
    30: "PublicHoliday",
    31: "Roster",
    32: "RosterOpen",
#    33: "RosterSwap",   # it's ephemeral. Not required!
#    34: "SalesData",    # too big and bloated. Besides we are not owner of the data here
    35: "Schedule",
    36: "StressProfile",
    37: "Timesheet",
    38: "TimesheetPayReturn",
    39: "TrainingModule",
    40: "TrainingRecord"
}


def do_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Config File', required=True)
    parser.add_argument('-s', '--state', help='State File')
    args = parser.parse_args()

    # load config dict and set variables
    with open(args.config) as c:
        config = json.load(c)

        for arg in config:
            CONFIG.update({arg: config[arg]})

        # close the config file
        c.close()

    # load dict if STATE exists
    if args.state:
        with open(args.state, 'r+') as s:
            try:
                state = json.load(s)

                for sta in state:
                    STATE.update({sta: state[sta]})

                # close the state file
                s.close()
            except ValueError:
                LOGGER.critical('Please define state.json file.')
                exit()


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def do_request(url, method, data=None):
    if CONFIG['debugging']:
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
    output =  SESSION.request(url=url, method=method, data=data, headers={'Authorization': 'OAuth ' + CONFIG['deputy_token'], 'dp-meta-option': 'none'})
    if output:
        return output.json()
    return []


def do_get_date(key):
    if key not in STATE:
        STATE[key] = CONFIG['start_date']

    return STATE[key]


def do_map_schema_type(value):
    if value in ['varchar', 'blob', 'string', 'datetime', 'date', 'time']:
        return 'string'
    elif value in ['bit']:
        return 'bool'
    elif value in ['integer']:
        return 'integer'
    elif value in ['float']:
        return 'number'
    else:
        return 'string'


def do_save_state(state):
    # save state to singer
    singer.write_state(STATE)

    # update state.json file with state
    with open('state.json', 'r+') as f:
        json.dump(state, f)


def do_query_records(resource, array, index, initial):
    queries = {}
    more_records = True

    for i in range(0, 10):
        if initial:
            start = i * index
        else:
            start = index + 500
            index = start

        queries.update({
            'batch%d' % i: {
                'url': 'resource/%s/QUERY' % resource, 'method': 'POST', 'data': {
                    'search': {'date_from': {'field': 'Modified', 'type': 'ge', 'data': do_get_date(resource[0].lower() + resource[1:])}},
                    'start': start,
                    'max': 500
                }
            }
        })

    response = do_request(CONFIG['deputy_domain'] + '/api/v1/multi', 'POST', json.dumps(queries))

    for batch in response:
        if len(response[batch]) > 0:
            array += response[batch]
        else:
            more_records = False

    if more_records:
        last_batch = sorted(queries.keys())
        last_batch_index = queries[last_batch[-1]]['data']['start']
        return do_query_records(resource, array, last_batch_index, False)
    else:
        return array


def do_resource_sync():
    # get all resources for syncing
    resources = do_get_resources()

    for resource in resources:
        #with singer.stats.Timer(source=resource[0].lower() + resource[1:]) as stats:
        if 1:
            array = []
            data = do_query_records(resource, array, 500, True)

            # only write records/state is there are records to sync
            if len(data) > 0:

                schema = utils.load_json(get_abs_path('schemas/{}.json'.format(resource[0].lower() + resource[1:])))

                singer.write_schema(resource[0].lower() + resource[1:], schema, ["Id"])
                #stats.record_count = len(data)

                # for each record
                for row in data:
                    # for each item in each record
                    for item in row:
                        # if item is dict, update dict to str
                        if isinstance(row[item], dict):
                            row[item] = str(row[item])

                    singer.write_record(resource[0].lower() + resource[1:], row)
                    utils.update_state(STATE, resource[0].lower() + resource[1:], row['Modified'])

                # update state after each resource
                do_save_state(STATE)
            else:
                LOGGER.info('%s schema is up to date, sync not required.', resource)
                utils.update_state(STATE, resource[0].lower() + resource[1:], CONFIG['start_date'])
                do_save_state(STATE)


def do_build_schema(resource):
    #with singer.stats.Timer(source=resource[0].lower() + resource[1:]):
    if 1:
        data = do_request(CONFIG['deputy_domain'] + '/api/v1/resource/%s/INFO' % resource, 'GET')
        fields = data['fields']
        joins = data['joins']
        count = data['count']

        # build the template schema
        schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "description": "https://www.deputy.com/api-doc/Resources/" + resource,
            "definitions": {
                resource[0].lower() + resource[1:]: {
                    "type": "object",
                    "properties": {}
                }
            },
            "type": "object",
            "properties": {}
        }

        # add all properties of the RESOURCE to the schema object
        for field in fields:
            objAttributes = schema['definitions'][resource[0].lower() + resource[1:]]['properties']

            if fields[field].lower() == 'datetime':
                objAttributes[field[0].lower() + field[1:]] = {"type": do_map_schema_type(fields[field].lower()),
                                                               "format": "date-time"}
            else:
                objAttributes[field[0].lower() + field[1:]] = {"type": do_map_schema_type(fields[field].lower())}

        # add the resource joins and reference the object
        for join in joins:
            objJoins = schema['properties']
            objJoins[join[0].lower() + join[1:]] = {"$ref": "#/definitions/" + joins[join][0].lower() + joins[join][1:]}

        file = 'schemas/' + resource[0].lower() + resource[1:] + '.json'

        # if file doesnt exist, create one and dump the schema
        if not os.path.exists(file):
            with open(file, 'w') as f:
                LOGGER.info('Creating %s Schema', resource[0].lower() + resource[1:])
                json.dump(schema, f)
        else:
            with open(file, 'r+') as f:
                # if schema exists and isn't correct, update it
                if not json.load(f) == schema:
                    LOGGER.info('Updating %s Schema', resource[0].lower() + resource[1:])
                    json.dump(schema, open(file, 'w'))

        # close file when finished
        f.close()


def do_get_resources():
    resources = []

    # get customer resources from config.json file
    if CONFIG['resources']:
        if 'ALL' in CONFIG['resources']:
            # build list of all resource schemas
            for resource in RESOURCES:
                if resource != 'ALL':
                    resources.append(RESOURCES[resource])
        else:
            for resource in CONFIG['resources']:
                resources.append(resource)

        return resources
    LOGGER.error('No resources defined in config.json')
    exit()


def do_schema_setup():
    # get all resources for syncing
    resources = do_get_resources()

    LOGGER.info('Syncing Streams: %s', [stream for stream in resources])

    for resource in resources:
        do_build_schema(resource)

    LOGGER.info("Schema Setup Completed")


def main():
    do_setup()
    do_schema_setup()
    do_resource_sync()


if __name__ == '__main__':
    main()
