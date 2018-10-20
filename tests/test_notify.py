"""Unit tests for the notify module."""

from email.errors import MessageError
from email.mime.text import MIMEText
from unittest.mock import patch

from requests import ConnectionError as RequestsConnectionError

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

class MockSMTP():
    """A mock SMTP object for testing."""
    # pylint: disable=missing-docstring
    def ehlo(self):
        return True

    def starttls(self):
        return True

    def sendmail(self, from_address, to_addresses, content):
        self.from_address = from_address
        self.to_addresses = to_addresses
        self.content = content

        return True

    def quit(self):
        return True

    def __init__(self, server):
        self.server = server
        self.from_address = ''
        self.to_addresses = ''
        self.content = ''

@patch('requests.get', MockRequest404Response)
def test_retrieve_emails_404_response():
    """Tests handling of 404 response in retrieve_emails."""
    try:
        notify.retrieve_emails(USER['id'], APP_CONFIG)
    except RequestsConnectionError:
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
    except RequestsConnectionError:
        assert True
    else:
        assert False

@patch('requests.post', MockRequest200Response)
def test_update_first_email_flag():
    """Tests 200 response in update_first_email_sent_flag_emails."""
    try:
        notify.update_first_email_sent_flag(USER['id'], APP_CONFIG)
    except RequestsConnectionError:
        assert False
    else:
        assert True

def test_convert_emails_to_ddresses():
    """Tests that emails are properly formatted for smtplib."""
    emails = ['test1@email.com', 'test2@email.com']
    user_name = 'Test User'

    to_addresses = notify.convert_emails_to_addresses(emails, user_name)

    assert len(to_addresses) == 2
    assert to_addresses[0] == 'Test User <test1@email.com>'
    assert to_addresses[1] == 'Test User <test2@email.com>'

def test_send_multipart_email_debug():
    """Tests that email configuration works properly in debug mode."""
    to_addresses = [
        'Test User <test1@email.com>',
        'Test User <test2@email.com>'
    ]
    subject = 'Email Test'
    body = {
        'plain': MIMEText('Test plain text email.', 'plain'),
        'html': MIMEText('<p>Test html email.</p>','html'),
    }

    try:
        notify.send_multipart_email(APP_CONFIG, to_addresses, subject, body)
    except MessageError:
        assert False
    else:
        assert True

@patch('smtplib.SMTP', MockSMTP)
def test_send_multipart_email():
    """Tests that email configuration works properly."""
    custom_config = APP_CONFIG
    custom_config['debug']['email_console'] = False
    to_addresses = [
        'Test User <test1@email.com>',
        'Test User <test2@email.com>'
    ]
    subject = 'Email Test'
    body = {
        'plain': MIMEText('Test plain text email.', 'plain'),
        'html': MIMEText('<p>Test html email.</p>','html'),
    }

    try:
        notify.send_multipart_email(custom_config, to_addresses, subject, body)
    except MessageError:
        assert False
    else:
        assert True
