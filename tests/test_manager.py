"""Unit tests for the manager module."""
# pylint: disable=too-few-public-methods
from unittest.mock import patch

import requests

from modules.manager import retrieve_users

from tests.utils import MockRequest404Response


APP_CONFIG = {
    'api_url': 'https://127.0.0.1/api/',
    'api_headers': {'user-agent': 'rdrhc-calendar', }
}


class MockUserGet200Response():
    """Mocks a 200 response on Get User."""
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.status_code = 200
        self.text = """[
            {"id": 1, "name": "Test User 1"},
            {"id": 2, "name": "Test User 2"}
        ]"""


@patch('requests.get', MockRequest404Response)
def test_404_error_on_user_retrieval():
    """Tests for handling of 404 error on user retrieval."""
    try:
        retrieve_users(APP_CONFIG)
    except requests.ConnectionError:
        assert True
    else:
        assert False


@patch('requests.get', MockUserGet200Response)
def test_json_conversion_user_retrieval():
    """Tests for proper JSON conversion of user data."""
    users = retrieve_users(APP_CONFIG)

    assert len(users) == 2
    assert users[0]['name'] == 'Test User 1'
