"""Unit tests for the notify module."""

from copy import deepcopy
from email.errors import MessageError
from email.mime.text import MIMEText
from unittest.mock import patch

from requests import ConnectionError as RequestsConnectionError
from unipath import Path

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
        'html': MIMEText('<p>Test html email.</p>', 'html'),
    }

    # Will need to update exceptions if any occur in production
    try:
        notify.send_multipart_email(APP_CONFIG, to_addresses, subject, body)
    except MessageError:
        assert False
    else:
        assert True

@patch('smtplib.SMTP', MockSMTP)
def test_send_multipart_email():
    """Tests that email configuration works properly."""
    custom_config = deepcopy(APP_CONFIG)
    custom_config['debug']['email_console'] = False
    to_addresses = [
        'Test User <test1@email.com>',
        'Test User <test2@email.com>'
    ]
    subject = 'Email Test'
    body = {
        'plain': MIMEText('Test plain text email.', 'plain'),
        'html': MIMEText('<p>Test html email.</p>', 'html'),
    }

    # Will need to update exceptions if any occur in production
    try:
        notify.send_multipart_email(custom_config, to_addresses, subject, body)
    except MessageError:
        assert False
    else:
        assert True

@patch('requests.post', MockRequest200Response)
def test_email_welcome():
    """Tests that the welcome email sends properly."""
    emails = ['test1@email.com', 'test2@email.com']

    template_text = Path('tests/files/welcome.txt')
    template_html = Path('tests/files/welcome.html')

    custom_config = deepcopy(APP_CONFIG)
    custom_config['email']['welcome_text'] = template_text.absolute()
    custom_config['email']['welcome_html'] = template_html.absolute()

    # Will need to update exceptions if any occur in production
    try:
        notify.email_welcome(USER, emails, custom_config)
    except OSError:
        assert False
    else:
        assert True

def test_update_additions_section_with_codes():
    """Tests that additions section is replaced with provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    additions = [
        {'email_message': '2018-01-01 - A1'},
        {'email_message': '2018-01-02 - A2'},
    ]

    text, html = notify.update_additions_section(text, html, additions)

    assert 'ADDITIONS' in text
    assert 'ADDITIONS' in html
    assert ' - 2018-01-01 - A1' in text
    assert '<li>2018-01-01 - A1</li>' in html
    assert ' - 2018-01-02 - A2' in text
    assert '<li>2018-01-02 - A2</li>' in html

def test_update_additions_section_without_codes():
    """Tests that additions section is removed without provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    text, html = notify.update_additions_section(text, html, [])

    assert 'ADDITIONS' not in text
    assert 'ADDITIONS' not in html

def test_update_deletions_section_with_codes():
    """Tests that deletions section is replaced with provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    deletions = [
        {'email_message': '2018-01-01 - A1'},
        {'email_message': '2018-01-02 - A2'},
    ]

    text, html = notify.update_deletions_section(text, html, deletions)

    assert 'DELETIONS' in text
    assert 'DELETIONS' in html
    assert ' - 2018-01-01 - A1' in text
    assert '<li>2018-01-01 - A1</li>' in html
    assert ' - 2018-01-02 - A2' in text
    assert '<li>2018-01-02 - A2</li>' in html

def test_update_deletions_section_without_codes():
    """Tests that deletions section is removed without provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    text, html = notify.update_deletions_section(text, html, [])

    assert 'DELETIONS' not in text
    assert 'DELETIONS' not in html

def test_update_changes_section_with_codes():
    """Tests that changes section is replaced with provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    changes = [
        {'email_message': '2018-01-01 - A1 to B1'},
        {'email_message': '2018-01-02 - A2 to B2'},
    ]

    text, html = notify.update_changes_section(text, html, changes)

    assert 'CHANGES' in text
    assert 'CHANGES' in html
    assert ' - 2018-01-01 - A1 to B1' in text
    assert '<li>2018-01-01 - A1 to B1</li>' in html
    assert ' - 2018-01-02 - A2 to B2' in text
    assert '<li>2018-01-02 - A2 to B2</li>' in html

def test_update_changes_section_without_codes():
    """Tests that changes section is removed without provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    text, html = notify.update_changes_section(text, html, [])

    assert 'CHANGES' not in text
    assert 'CHANGES' not in html

def test_update_missing_section_with_codes():
    """Tests that missing section is replaced with provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    missings = [
        {'email_message': '2018-01-01 - A1'},
        {'email_message': '2018-01-02 - A2'},
    ]

    text, html = notify.update_missing_section(
        text, html, missings, APP_CONFIG
    )

    assert 'MISSING SHIFT CODES' in text
    assert 'MISSING SHIFT CODES' in html
    assert '01:00 to 02:06 (weekdays)' in text
    assert '01:00 to 02:06 (weekdays)' in html
    assert '05:00 to 10:30 (weekends)' in text
    assert '05:00 to 10:30 (weekends)' in html
    assert '09:00 to 18:54 (statutory holidays)' in text
    assert '09:00 to 18:54 (statutory holidays)' in html
    assert ' - 2018-01-01 - A1' in text
    assert '<li>2018-01-01 - A1</li>' in html
    assert ' - 2018-01-02 - A2' in text
    assert '<li>2018-01-02 - A2</li>' in html

def test_update_missing_section_without_codes():
    """Tests that missing section is removed without provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    text, html = notify.update_missing_section(text, html, [], APP_CONFIG)

    assert 'MISSING SHIFT CODES' not in text
    assert 'MISSING SHIFT CODES' not in html

def test_update_null_section_with_codes():
    """Tests that null section is replaced with provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    nulls = [
        {'email_message': '2018-01-01 - A1 to B1'},
        {'email_message': '2018-01-02 - A2 to B2'},
    ]

    text, html = notify.update_null_section(text, html, nulls)

    assert 'EXCLUDED CODES' in text
    assert 'EXCLUDED CODES' in html
    assert ' - 2018-01-01 - A1 to B1' in text
    assert '<li>2018-01-01 - A1 to B1</li>' in html
    assert ' - 2018-01-02 - A2 to B2' in text
    assert '<li>2018-01-02 - A2 to B2</li>' in html

def test_update_null_section_without_codes():
    """Tests that null section is removed without provided codes."""
    with open(Path('tests/files/update.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/update.html'), 'r') as html_file:
        html = html_file.read()

    text, html = notify.update_null_section(text, html, [])

    assert 'EXCLUDED CODES' not in text
    assert 'EXCLUDED CODES' not in html

def test_email_schedule():
    """Tests that the schedule update email sends properly."""
    emails = ['test1@email.com', 'test2@email.com']

    template_text = Path('tests/files/update.txt')
    template_html = Path('tests/files/update.html')

    custom_config = deepcopy(APP_CONFIG)
    custom_config['email']['update_text'] = template_text.absolute()
    custom_config['email']['update_html'] = template_html.absolute()

    notification_details = {
        'additions': [],
        'deletions': [],
        'changes': [],
        'missing': [],
        'null': [],
    }

    # Will need to update exceptions if any occur in production
    try:
        notify.email_schedule(
            USER, emails, custom_config, notification_details
        )
    except OSError:
        assert False
    else:
        assert True

def test_update_codes_section_with_codes():
    """Tests that codes section is replaced with provided codes."""
    with open(Path('tests/files/missing_codes.txt'), 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    with open(Path('tests/files/missing_codes.html'), 'r') as html_file:
        html = html_file.read()

    codes = ['A1', 'A2']

    text, html = notify.update_codes_section(text, html, codes)

    assert ' - A1' in text
    assert '<li>A1</li>' in html
    assert ' - A2' in text
    assert '<li>A2</li>' in html

def test_email_missing_codes():
    """Tests that the missing codes email sends properly."""
    template_text = Path('tests/files/missing_codes.txt')
    template_html = Path('tests/files/missing_codes.html')

    custom_config = deepcopy(APP_CONFIG)
    custom_config['email']['missing_codes_text'] = template_text.absolute()
    custom_config['email']['missing_codes_html'] = template_html.absolute()

    missing_codes = ['A1', 'A2']

    # Will need to update exceptions if any occur in production
    try:
        notify.email_missing_codes(
            missing_codes, custom_config
        )
    except MessageError:
        assert False
    else:
        assert True
