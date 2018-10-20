"""Unit tests for the notify module."""

from unittest.mock import patch

from requests import ConnectionError

from modules import notify

from tests.utils import (
    MockRequest404Response, MockRequest200Response, APP_CONFIG, USER
)


class MockRetrieveEmailsResponse(MockRequest200Response):
    """A mock of a response to the retrieve_old_schedule function."""
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.text = """[
            {"email": "test1@email.com"},
            {"email": "test2@email.com"}
        ]"""

@patch('requests.get', MockRequest404Response)
def test_retrieve_emails_404_response():
    """Tests handling of 404 response in retrieve_emails."""
    try:
        notify.retrieve_emails(USER['id'], APP_CONFIG)
    except ConnectionError:
        assert True
    else:
        assert False

@patch('requests.get', MockRetrieveEmailsResponse)
def test_retrieve_emails():
    """Tests handling of empty schedule in retrieve_emails."""
    emails = notify.retrieve_emails(USER['id'], APP_CONFIG)

    assert len(emails) == 2
    assert emails[0] == 'test1@email.com'
    assert emails[1] == 'test2@email.com'

@patch('requests.post', MockRequest404Response)
def test_update_first_email_flag_404_response():
    """Tests 404 response in update_first_email_sent_flag_emails."""
    try:
        notify.update_first_email_sent_flag(USER['id'], APP_CONFIG)
    except ConnectionError:
        assert True
    else:
        assert False

@patch('requests.post', MockRequest200Response)
def test_update_first_email_flag():
    """Tests 200 response in update_first_email_sent_flag_emails."""
    try:
        notify.update_first_email_sent_flag(USER['id'], APP_CONFIG)
    except ConnectionError:
        assert False
    else:
        assert True
