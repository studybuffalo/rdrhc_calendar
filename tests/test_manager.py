"""Unit tests for the manager module."""
# pylint: disable=missing-docstring

from unittest.mock import patch

import requests

from modules.manager import retrieve_users


APP_CONFIG = {
    'api_url': 'https://127.0.0.1/api/',
    'api_headers': {'user-agent': 'rdrhc-calendar',}
}

class MockUserGet404Response():
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.status_code = 404

@patch('requests.get', MockUserGet404Response)
def test_404_error_on_user_retrieval():
    try:
        retrieve_users(APP_CONFIG)
    except requests.ConnectionError:
        assert True
    else:
        assert False

class MockUserGet200Response():
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers,
        self.status_code = 200
        self.text = """[
            {"id": 1, "name": "Test User 1"},
            {"id": 2, "name": "Test User 2"}
        ]"""

@patch('requests.get', MockUserGet200Response)
def test_json_conversion_user_retrieval():
    users = retrieve_users(APP_CONFIG)

    assert len(users) == 2
    assert users[0]['name'] == 'Test User 1'
