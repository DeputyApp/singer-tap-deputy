from asyncio import wait_for
import unittest
import os
import json
import requests
from tap_deputy.client import DeputyClient, Server401TokenExpiredError
from unittest import mock
from singer.utils import now, strptime_to_utc
from datetime import timedelta


test_config = {
    "client_id": "client_id",
    "client_secret": "client_secret",
    "domiain": "domain",
    "start_date": "2021-09-20T00:00:00Z",
    "redirect_uri": "redirect_uri",
    "refresh_token": "old_refresh_token",
    "access_token": "old_access_token"
}
test_config_path = "/tmp/test_config.json"

class Mockresponse:
    """ Mock response object class."""

    def __init__(self, status_code, raise_error, text=""):
        self.status_code = status_code
        self.raise_error = raise_error
        self.text = text

    def raise_for_status(self):
        if not self.raise_error:
            return self.status_code

        raise requests.HTTPError("Sample message")

    def json(self):
        """ Response JSON method."""
        return self.text

def get_mock_http_response(status_code):
    """Return http mock response."""
    response = requests.Response()
    response.status_code = status_code
    return response

def get_response(status_code, raise_error=True):
    """ Returns required mock response. """
    return Mockresponse(status_code, raise_error=raise_error)


def write_new_config_file():
    with open(test_config_path, 'w') as config:
        # Reset tokens while writing the test config
        test_config["refresh_token"] = "old_refresh_token"
        test_config["access_token"] = "old_access_token"
        config.write(json.dumps(test_config))


class TestDevMode(unittest.TestCase):
    def tearDown(self):
        if os.path.isfile(test_config_path):
            os.remove(test_config_path)

    @mock.patch('json.dump')
    @mock.patch('tap_deputy.client.DeputyClient.post')
    def test_dev_mode_not_enabled_no_expiry(self, mocked_post_request, mocked_json_dump):
        write_new_config_file()
        deputy = DeputyClient(config=test_config,
                              config_path=test_config_path,
                              dev_mode=False)
        mocked_post_request.return_value = {"refresh_token": "new_refresh_token",
                                            "access_token": "new_access_token",
                                            "expires_in": 86400}
        deputy.refresh()
        self.assertEqual(deputy.refresh_token, "new_refresh_token")
        self.assertEqual(deputy.access_token, "new_access_token")

    @mock.patch('json.dump')
    @mock.patch('tap_deputy.client.DeputyClient.post')
    def test_dev_mode_not_enabled_expired_token(self, mocked_post_request, mocked_json_dump):
        write_new_config_file()
        deputy = DeputyClient(config=test_config,
                              config_path=test_config_path,
                              dev_mode=False)
        mocked_post_request.return_value = {"refresh_token": "new_refresh_token",
                                            "access_token": "new_access_token",
                                            "expires_in": 86400}
        deputy.expires_at = now() - timedelta(seconds=10)
        deputy.refresh()

        self.assertEqual(deputy.refresh_token, "new_refresh_token")
        self.assertEqual(deputy.access_token, "new_access_token")

    @mock.patch('requests.Session.request')
    @mock.patch('tap_deputy.client.DeputyClient.refresh')
    def test_dev_mode_not_enabled_valid_token(self, mocked_refresh, mock_session_request):
        """Verify that in dev mode token validation succeeds with token is not expired"""
        mock_session_request.side_effect = [get_response(200, raise_error = False)]
        write_new_config_file()
        deputy = DeputyClient(config=test_config,
                              config_path=test_config_path,
                              dev_mode=False)
        deputy.expires_at = now() + timedelta(days=1)
        deputy.get(path='/api/v1/resource/dummy_resource', endpoint='resource_info')

        self.assertEqual(deputy.refresh_token, "old_refresh_token")
        self.assertEqual(deputy.access_token, "old_access_token")
        self.assertEquals(mocked_refresh.call_count, 0)

    @mock.patch('tap_deputy.client.DeputyClient.post')
    def test_dev_mode_enabled_valid_token(self, mocked_post_request):
        """Verify that in dev mode token validation succeeds with token is not expired"""
        write_new_config_file()
        deputy = DeputyClient(config=test_config,
                              config_path=test_config_path,
                              dev_mode=True)
        deputy.expires_at = now() + timedelta(days=1)
        deputy.refresh()
        self.assertEqual(deputy.refresh_token, "old_refresh_token")
        self.assertEqual(deputy.access_token, "old_access_token")

    @mock.patch('time.sleep')
    @mock.patch('requests.Session.request')
    def test_dev_mode_disabled_token_expired(self, mocked_post_request, mock_sleep):
        retry_count = 5
        mocked_post_request.side_effect = [get_response(401, raise_error = True)] * retry_count
        deputy = DeputyClient(config=test_config,
                              config_path=test_config_path,
                              dev_mode=False)

        with self.assertRaises(Server401TokenExpiredError) as e:
            deputy.request("POST",
                           "/oauth/access_token",
                           auth_call=True)

        # Verify the call count for each error
        self.assertEquals(mocked_post_request.call_count, retry_count)