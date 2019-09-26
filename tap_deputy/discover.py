from singer.catalog import Catalog, CatalogEntry, Schema

RESOURCES = {
    'Address': 'addresses',
    'Category': 'categories',
    'Comment': 'comments',
    'Company': 'companies',
    'CompanyPeriod': 'company_periods',
    'Contact': 'contacts',
    'Country': 'countries',
    'CustomAppData': 'custom_app_data',
    'CustomField': 'custom_fields',
    'CustomFieldData': 'custom_field_data',
    'Employee': 'employees',
    'EmployeeAgreement': 'employee_agreements',
    'EmployeeAgreementHistory': 'employee_agreement_history',
    'EmployeeAppraisal': 'employee_appraisal',
    'EmployeeAvailability': 'employee_availability',
    'EmployeeHistory': 'employee_history',
    'EmployeePaycycle': 'employee_paycycles',
    'EmployeePaycycleReturn': 'employee_paycycle_returns',
    'EmployeeRole': 'employee_roles',
    'EmployeeSalaryOpunitCosting': 'employee_salary_opunit_costing',
    'EmployeeWorkplace': 'employee_workplaces',
    'EmploymentCondition': 'employment_conditions',
    'EmploymentContract': 'employee_contracts',
    'EmploymentContractLeaveRules': 'employee_contract_leave_rules',
    'Event': 'events',
    'Geo': 'geo',
    'Journal': 'journal',
    'Kiosk': 'kiosks',
    'Leave': 'leaves',
    'LeaveAccrual': 'leave_accruals',
    'LeavePayLine': 'leave_pay_lines',
    'LeaveRules': 'leave_rules',
    'Memo': 'memos',
    'OperationalUnit': 'operational_units',
    'PayPeriod': 'pay_periods',
    'PayRules': 'pay_rules',
    'PublicHoliday': 'public_holidays',
    'Roster': 'rosters',
    'RosterOpen': 'roster_opens',
    'RosterSwap': 'roster_swaps',
    'SalesData': 'sales_data',
    'Schedule': 'schedules',
    'SmsLog': 'sms_logs',
    'State': 'states',
    'StressProfile': 'stress_profiles',
    'SystemUsageBalance': 'system_usage_balances',
    'SystemUsageTracking': 'system_usage_tracking',
    'Task': 'tasks',
    'TaskGroup': 'task_groups',
    'TaskGroupSetup': 'task_group_setups',
    'TaskOpunitConfig': 'task_opunit_configs',
    'TaskSetup': 'task_setups',
    'Team': 'teams',
    'Timesheet': 'timesheets',
    'TimesheetPayReturn': 'timesheet_pay_returns',
    'TrainingModule': 'training_modules',
    'TrainingRecord': 'training_records',
    'Webhook': 'webhooks'
}

TYPE_MAP = {
    'Integer': 'integer',
    'Float': 'number',
    'VarChar': 'string',
    'Blob': 'string',
    'Bit': 'boolean',
    'Time': 'string'
}

def get_schema(client, resource_name):
    data = client.get(
        '/api/v1/resource/{}/INFO'.format(resource_name),
        endpoint='resource_info')

    properties = {}
    metadata = [
        {
            'breadcrumb': [],
            'metadata': {
                'tap-deputy.resource': resource_name
            }
        }
    ]

    for field_name, field_type in data['fields'].items():
        if field_type in ['Date', 'DateTime']:
            json_schema = {
                'type': ['null', 'string'],
                'format': 'date-time'
            }
        else:
            json_schema = {
                'type': ['null', TYPE_MAP[field_type]]
            }

        properties[field_name] = json_schema

        metadata.append({
            'breadcrumb': ['properties', field_name],
            'metadata': {
                'inclusion': 'automatic' if field_name == 'Id' else 'available'
            }
        })

    schema = {
        'type': 'object',
        'additionalProperties': False,
        'properties': properties
    }

    return schema, metadata

def discover(client):
    catalog = Catalog([])

    for resource_name in RESOURCES.keys():
        schema_dict, metadata = get_schema(client, resource_name)
        schema = Schema.from_dict(schema_dict)

        stream_name = RESOURCES[resource_name]

        catalog.streams.append(CatalogEntry(
            stream=stream_name,
            tap_stream_id=stream_name,
            key_properties=['Id'],
            schema=schema,
            metadata=metadata
        ))

    return catalog
