import pytest
from unittest.mock import Mock

from singer.transform import SchemaMismatch

from tap_deputy.sync import process_records


@pytest.fixture
def stream_fixture(request):
    """A dynamic fixture to create a mock stream with a given schema."""
    stream = Mock()
    stream.tap_stream_id = request.param["stream_name"]
    stream.key_properties = ["Id"]
    stream.schema.to_dict.return_value = request.param["schema"]
    return stream


@pytest.mark.parametrize(
    "stream_fixture, date_field",
    [
        # Employees Stream
        ({"stream_name": "employees", "schema": {
             "type": "object", "properties": {
                 "Id": {"type": "integer"},
                 "Modified": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "DateOfBirth": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "StartDate": {
                     "type": ["string", "null"], "format": "date-time"
                 },
             }}}, "DateOfBirth"
         ),
        ({"stream_name": "employees", "schema": {
             "type": "object", "properties": {
                 "Id": {"type": "integer"},
                 "Modified": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "DateOfBirth": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "StartDate": {
                     "type": ["string", "null"], "format": "date-time"
                 },
             }}}, "StartDate"
         ),

        # Rosters Stream
        ({"stream_name": "rosters", "schema": {
             "type": "object", "properties": {
                 "Id": {"type": "integer"},
                 "Modified": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "Date": {"type": ["string", "null"], "format": "date-time"},
             }}}, "Date"
         ),

        # Timesheets Stream
        ({"stream_name": "timesheets", "schema": {
             "type": "object", "properties": {
                 "Id": {"type": "integer"},
                 "Modified": {
                     "type": ["string", "null"], "format": "date-time"
                 },
                 "Date": {"type": ["string", "null"], "format": "date-time"},
                 "AccrualStateChangedAt": {
                     "type": ["string", "null"], "format": "date-time"
                 },
             }}}, "AccrualStateChangedAt"
         ),
    ],
    indirect=["stream_fixture"]
)
def test_process_records_handles_empty_date_strings(
    stream_fixture,
    capsys,
    date_field
):
    """
    Verify that process_records correctly handles an empty string for any
    date-time field by converting it to null and processing successfully.
    """
    records = [{
        "Id": 1,
        "Modified": "2025-11-20T15:03:32.000000Z",
        date_field: ""  # This invalid format should be converted to null
    }]
    mdata = {}
    max_modified = "2025-01-01T00:00:00.000000Z"

    try:
        # This should run without raising an exception
        process_records(stream_fixture, mdata, max_modified, records)
    except SchemaMismatch:
        pytest.fail("process_records raised SchemaMismatch unexpectedly for "
                    f"field '{date_field}' with an empty string value.")

    # Verify that a record was written to stdout
    captured = capsys.readouterr()
    assert '"type": "RECORD"' in captured.out
    assert f'"{date_field}":null' in captured.out.replace(" ", "")
