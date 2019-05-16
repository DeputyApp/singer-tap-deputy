from singer.catalog import Catalog, CatalogEntry, Schema

RESOURCES = [
    'Contact',
    'Employee'
]

RESOURCE_TO_STREAM = {
    'Contact': 'contacts',
    'Employee': 'employees'
}

TYPE_MAP = {
    'Integer': 'integer',
    'Float': 'number',
    'VarChar': 'string',
    'Blob': 'string',
    'Bit': 'boolean'
}

def get_schema(client, resource_name):
    data = client.get('/api/v1/resource/{}/INFO'.format(resource_name))

    properties = {}
    metadata = []
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

    for resource_name in RESOURCES:
        schema_dict, metadata = get_schema(client, resource_name)
        schema = Schema.from_dict(schema_dict)

        stream_name = RESOURCE_TO_STREAM[resource_name]

        catalog.streams.append(CatalogEntry(
            stream=stream_name,
            tap_stream_id=stream_name,
            key_properties=['Id'],
            schema=schema,
            metadata=metadata
        ))

    return catalog
