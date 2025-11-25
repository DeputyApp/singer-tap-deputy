import pytest
from unittest.mock import Mock

from tap_deputy.discover import discover, RESOURCES


@pytest.mark.parametrize(
    "deputy_type, expected_jsonschema_type",
    [
        ("Integer", ["null", "integer"]),
        ("Float", ["null", "number"]),
        ("VarChar", ["null", "string"]),
        ("Blob", ["null", "string"]),
        ("Bit", ["null", "boolean"]),
        ("Time", ["null", "string"]),
        ("Json", ["null", "string"]),
    ],
)
def test_discover_simple_type_mappings(deputy_type, expected_jsonschema_type):
    """
    Verify that Deputy API field types are correctly mapped to simple
    JSON schema types in the generated catalog.
    """
    client = Mock()
    resource_name = "Employee"
    stream_name = RESOURCES[resource_name]

    client.get.return_value = {
        "fields": {"Id": "Integer", "SomeTestField": deputy_type}
    }

    catalog = discover(client)
    employees_stream = next((s for s in catalog.streams if s.tap_stream_id == stream_name), None)

    assert employees_stream is not None
    schema_properties = employees_stream.schema.to_dict()["properties"]

    assert "SomeTestField" in schema_properties
    assert schema_properties["SomeTestField"]["type"] == expected_jsonschema_type


@pytest.mark.parametrize("deputy_type", ["Date", "DateTime"])
def test_discover_datetime_type_mapping(deputy_type):
    """
    Verify that Deputy API 'Date' and 'DateTime' field types are correctly
    mapped to a 'string' with 'date-time' format in the catalog schema.
    """
    client = Mock()
    resource_name = "Employee"
    stream_name = RESOURCES[resource_name]

    client.get.return_value = {
        "fields": {"Id": "Integer", "SomeDateField": deputy_type}
    }

    catalog = discover(client)
    employees_stream = next((s for s in catalog.streams if s.tap_stream_id == stream_name), None)

    assert employees_stream is not None
    schema_properties = employees_stream.schema.to_dict()["properties"]

    assert "SomeDateField" in schema_properties
    field_schema = schema_properties["SomeDateField"]
    assert field_schema["type"] == ["null", "string"]
    assert field_schema["format"] == "date-time"
