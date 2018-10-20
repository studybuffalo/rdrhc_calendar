"""Unit tests for the upload module."""

from unittest.mock import patch

from requests import ConnectionError as RequestsConnectionError

from modules import upload

from tests.utils import (
    MockRequest404Response, MockRequest200Response, APP_CONFIG, NEW_SCHEDULE,
    USER
)


class MockUpdateMissingCodes200Response(MockRequest200Response):
    """Mock 200 response for update_missing_codes_database."""
    def __init__(self, url, headers, data):
        super().__init__(url, headers, data)
        self.text = '["A1", "B1", "C1"]'

@patch('requests.delete', MockRequest404Response)
def test_delete_user_schedule_404_response():
    """Tests handling of 404 response for delete_user_schedule."""
    try:
        upload.delete_user_schedule(APP_CONFIG, 1)
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.delete', MockRequest200Response)
def test_delete_user_schedule_200_response():
    """Tests handling of 404 response for delete_user_schedule."""
    try:
        upload.delete_user_schedule(APP_CONFIG, 1)
    except RequestsConnectionError:
        assert False
    else:
        assert True

@patch('requests.post', MockRequest404Response)
def test_upload_user_schedule_404_response():
    """Tests handling of 404 response for upload_user_schedule."""
    try:
        upload.upload_user_schedule(APP_CONFIG, 1, NEW_SCHEDULE)
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.post', MockRequest200Response)
def test_upload_user_schedule_200_response():
    """Tests handling of 404 response for upload_user_schedule."""
    try:
        upload.upload_user_schedule(APP_CONFIG, 1, NEW_SCHEDULE)
    except RequestsConnectionError:
        assert False
    else:
        assert True

@patch('requests.delete', MockRequest404Response)
@patch('requests.post', MockRequest200Response)
def test_update_schedule_database_delete_404_responses():
    """Tests handling of 404 response for update_schedule_database."""
    try:
        upload.update_schedule_database(USER, NEW_SCHEDULE, APP_CONFIG)
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.delete', MockRequest200Response)
@patch('requests.post', MockRequest404Response)
def test_update_schedule_database_upload_404_responses():
    """Tests handling of 404 response for update_schedule_database."""
    try:
        upload.update_schedule_database(USER, NEW_SCHEDULE, APP_CONFIG)
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.delete', MockRequest200Response)
@patch('requests.post', MockRequest200Response)
def test_update_schedule_database_200_responses():
    """Tests handling of 404 response for update_schedule_database."""
    try:
        upload.update_schedule_database(USER, NEW_SCHEDULE, APP_CONFIG)
    except RequestsConnectionError:
        assert False
    else:
        assert True

@patch('requests.post', MockRequest404Response)
def test_update_missing_codes_database_404_response():
    """Tests update_missing_codes_database 404 response handling."""
    missing_codes = {
        'a': set(['A1', 'A2']),
        'p': set(['P1', 'P2']),
        't': set(['T1', 'T2']),
    }
    try:
        upload.update_missing_codes_database(APP_CONFIG, missing_codes)
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.post', MockUpdateMissingCodes200Response)
def test_update_missing_codes_database_200_response():
    """Tests update_missing_codes_database 200 response handling."""
    missing_codes = {
        'a': set(['A1', 'A2']),
        'p': set(['P1', 'P2']),
        't': set(['T1', 'T2']),
    }
    response = upload.update_missing_codes_database(APP_CONFIG, missing_codes)

    assert len(response) == 3
    assert response[0] == 'A1'
    assert response[1] == 'B1'
    assert response[2] == 'C1'

@patch('requests.post', MockUpdateMissingCodes200Response)
def test_update_missing_codes_database_no_codes():
    """Tests update_missing_codes_database 200 response handling."""
    missing_codes = {
        'a': set(),
        'p': set(),
        't': set(),
    }
    response = upload.update_missing_codes_database(APP_CONFIG, missing_codes)

    assert response is None
