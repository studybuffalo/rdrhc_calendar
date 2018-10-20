"""Functions used to send notifications to users and owners."""

from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import json
import logging
import re
import smtplib

import requests

from modules.utils import convert_duration_to_hours_minutes


# Setup logger
LOG = logging.getLogger(__name__)

def retrieve_emails(user_id, app_config):
    """Retrieves the specified user's emails."""
    LOG.debug('Retrieving email(s) for user id = %s', user_id)

    api_url = '{}users/{}/emails/'.format(app_config['api_url'], user_id)

    emails_response = requests.get(
        api_url,
        headers=app_config['api_headers']
    )

    if emails_response.status_code >= 400:
        raise requests.ConnectionError(
            (
                'Unable to connect to API ({}) and retrieve '
                'user shift codes.'
            ).format(api_url)
        )

    emails = []

    for email in json.loads(emails_response.text):
        emails.append(email['email'])

    return emails

def update_first_email_sent_flag(user_id, app_config):
    """Flags specified account as "first email sent"."""
    LOG.debug('Updating "first_email_sent" flag for user id = %s', user_id)

    api_url = '{}users/{}/emails/first-sent/'.format(
        app_config['api_url'], user_id
    )

    response = requests.post(
        api_url,
        headers=app_config['api_headers']
    )

    if response.status_code >= 400:
        print('test')
        raise requests.ConnectionError(
            (
                'Unable to connect to API ({}) and retrieve '
                'user shift codes.'
            ).format(api_url)
        )

def convert_emails_to_addresses(emails, user_name):
    """Formats list of emails for sending."""
    to_addresses = []

    for email in emails:
        to_name = user_name
        to_email = email
        to_address = formataddr((to_name, to_email))

        to_addresses.append(to_address)

    return to_addresses

def send_multipart_email(app_config, to_addresses, subject, body):
    """Constructs a MIMEMultipart email."""
    from_name = app_config['email']['from_name']
    from_email = app_config['email']['from_email']
    from_address = formataddr((from_name, from_email))

    content = MIMEMultipart('alternative')
    content['From'] = from_address
    content['To'] = ','.join(to_addresses)
    content['Subject'] = subject
    content['List-Unsubscribe'] = '<{}>'.format(
        app_config['email']['unsubscribe_link']
    )

    content.attach(body['plain'])
    content.attach(body['html'])

    # Send the email
    if app_config['debug']['email_console']:
        LOG.debug(content.as_string())
    else:
        server = smtplib.SMTP(app_config['email']['server'])

        server.ehlo()
        server.starttls()
        server.sendmail(from_address, to_addresses, content.as_string())
        server.quit()

def email_welcome(user, emails, app_config):
    """Sends a welcome email to any new user."""
    LOG.debug('Processing data to send user a welcome email')

    # Collects text welcome email from template file
    text_loc = app_config['email']['welcome_text']

    with open(text_loc, 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    # Collects html welcome email from template file
    html_loc = app_config['email']['welcome_html']

    with open(html_loc, 'r') as html_file:
        html = html_file.read()

    # Send the email
    to_addresses = convert_emails_to_addresses(emails, user['name'])
    subject = 'Welcome to Your New Online Schedule'
    body = {
        'plain': MIMEText(text, 'plain'),
        'html': MIMEText(html, 'html'),
    }
    send_multipart_email(app_config, to_addresses, subject, body)

    update_first_email_sent_flag(user['id'], app_config)

def update_additions_section(text, html, additions):
    """Updates the email templates' addition section."""
    # Manage added shifts
    LOG.debug('Updating the "additions" section')

    if additions:
        # Cycle through additions and insert into templates
        additions_text = []
        additions_html = []

        for addition in additions:
            additions_text.append(
                ' - {}'.format(addition['email_message'])
            )
            additions_html.append(
                '<li>{}</li>'.format(addition['email_message'])
            )

        text = text.replace('{{ additions }}', '\r\n'.join(additions_text))
        html = html.replace('{{ additions }}', '\r\n'.join(additions_html))

        # Remove the block markers
        text = text.replace('{% block additions %}', '')
        html = html.replace('{% block additions %}', '')
    else:
        # No additions, remove entire section
        regex = r'{% block additions %}.*{% block additions %}'

        text = re.sub(regex, '', text, flags=re.S)
        html = re.sub(regex, '', html, flags=re.S)

    return text, html

def update_deletions_section(text, html, deletions):
    """Updates the email templates' deletion section."""
    LOG.debug('Updating the "deletions" section')

    if deletions:
        deletions_text = []
        deletions_html = []

        for deletion in deletions:
            deletions_text.append(
                ' - {}'.format(deletion['email_message'])
            )
            deletions_html.append(
                '<li>{}</li>'.format(deletion['email_message'])
            )

        text = text.replace('{{ deletions }}', '\r\n'.join(deletions_text))
        html = html.replace('{{ deletions }}', '\r\n'.join(deletions_html))

        # Remove the block markers
        text = text.replace('{% block deletions %}', '')
        html = html.replace('{% block deletions %}', '')
    else:
        # No deletions, remove entire section
        regex = r'{% block deletions %}.*{% block deletions %}'

        text = re.sub(regex, '', text, flags=re.S)
        html = re.sub(regex, '', html, flags=re.S)

    return text, html

def update_changes_section(text, html, changes):
    """Updates the email templates' changes section."""
    LOG.debug('Updating the "changes" section')

    if changes:
        changes_text = []
        changes_html = []

        for change in changes:
            changes_text.append(
                ' - {}'.format(change['email_message'])
            )
            changes_html.append(
                '<li>{}</li>'.format(change['email_message'])
            )

        text = text.replace('{{ changes }}', '\r\n'.join(changes_text))
        html = html.replace('{{ changes }}', '\r\n'.join(changes_html))

        # Remove the block markers
        text = text.replace('{% block changes %}', '')
        html = html.replace('{% block changes %}', '')
    else:
        # No changes, remove entire section
        regex = r'{% block changes %}.*{% block changes %}'

        text = re.sub(regex, '', text, flags=re.S)
        html = re.sub(regex, '', html, flags=re.S)

    return text, html

def determine_end_time(start_time, duration):
    """Calculates an endtime based on start time and duration."""
    start_datetime = datetime(2000, 1, 1, start_time.hour, start_time.minute)
    hours, minutes = convert_duration_to_hours_minutes(duration)

    end_time = start_datetime + timedelta(
        hours=hours, minutes=minutes
    )

    return end_time.strftime('%H:%M')

def update_missing_section(text, html, missings, app_config):
    """Updates the email templates' missing section."""
    LOG.debug('Updating the "missing" section')

    if missings:
        defaults = app_config['calendar_defaults']

        weekday_start = defaults['weekday_start'].strftime('%H:%M')
        text = text.replace('{{ weekday_start }}', weekday_start)
        html = html.replace('{{ weekday_start }}', weekday_start)

        weekday_end = determine_end_time(
            defaults['weekday_start'], defaults['weekday_duration']
        )
        text = text.replace('{{ weekday_end }}', weekday_end)
        html = html.replace('{{ weekday_end }}', weekday_end)

        weekend_start = defaults['weekend_start'].strftime('%H:%M')
        text = text.replace('{{ weekend_start }}', weekend_start)
        html = html.replace('{{ weekend_start }}', weekend_start)

        weekend_end = determine_end_time(
            defaults['weekend_start'], defaults['weekend_duration']
        )
        text = text.replace('{{ weekend_end }}', weekend_end)
        html = html.replace('{{ weekend_end }}', weekend_end)

        stat_start = defaults['stat_start'].strftime('%H:%M')
        text = text.replace('{{ stat_start }}', stat_start)
        html = html.replace('{{ stat_start }}', stat_start)

        stat_end = determine_end_time(
            defaults['stat_start'], defaults['stat_duration']
        )
        text = text.replace('{{ stat_end }}', stat_end)
        html = html.replace('{{ stat_end }}', stat_end)

        missing_text = []
        missing_html = []

        for missing in missings:
            missing_text.append(
                ' - {}'.format(missing['email_message'])
            )
            missing_html.append(
                '<li>{}</li>'.format(missing['email_message'])
            )

        text = text.replace('{{ missing }}', '\r\n'.join(missing_text))
        html = html.replace('{{ missing }}', '\r\n'.join(missing_html))

        # Remove the block markers
        text = text.replace('{% block missing %}', '')
        html = html.replace('{% block missing %}', '')
    else:
        # No missing shifts, remove entire section
        regex = r'{% block missing %}.*{% block missing %}'

        text = re.sub(regex, '', text, flags=re.S)
        html = re.sub(regex, '', html, flags=re.S)

    return text, html

def update_null_section(text, html, nulls):
    """Updates the email templates' excluded (null) section."""
    LOG.debug('Updating the "excluded" section')

    if nulls:
        null_text = []
        null_html = []

        for null in nulls:
            null_text.append(' - {}'.format(null.msg))
            null_html.append('<li>{}</li>'.format(null.msg))

        text = text.replace('{{ excluded }}', '\r\n'.join(null_text))
        html = html.replace('{{ excluded }}', '\r\n'.join(null_html))

        # Remove the block markers
        text = text.replace('{% block excluded %}', '')
        html = html.replace('{% block excluded %}', '')
    else:
        # No excluded shifts, remove entire section
        regex = r'{% block excluded %}.*{% block excluded %}'

        text = re.sub(regex, '', text, flags=re.S)
        html = re.sub(regex, '', html, flags=re.S)

    return text, html

def email_schedule(user, emails, app_config, notification_details):
    """Emails user with any schedule changes"""
    LOG.debug('User qualifies for an update email to be sent')

    # Opens the update email (text) file
    LOG.debug('Opening the email templates')

    text_loc = app_config['email']['update_text']

    with open(text_loc, 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    # Opens the update email (html) file
    html_loc = app_config['email']['update_html']

    with open(html_loc, 'r') as html_file:
        html = html_file.read()

    # Set the user name
    text = text.replace('{{ user_name }}', user['name'])
    html = html.replace('{{ user_name }}', user['name'])

    # Update all the different notification sections
    text, html = update_additions_section(
        text, html, notification_details['additions']
    )
    text, html = update_deletions_section(
        text, html, notification_details['deletions']
    )
    text, html = update_changes_section(
        text, html, notification_details['changes']
    )
    text, html = update_missing_section(
        text, html, notification_details['missing'], app_config
    )
    text, html = update_null_section(
        text, html, notification_details['null']
    )

    # Add the calendar name
    calendar_name = user['calendar_name']
    text = text.replace('{{ calendar_name }}', calendar_name)
    html = html.replace('{{ calendar_name }}', calendar_name)

    # Send the email
    LOG.info('Sending update email to %s', user['name'])
    to_addresses = convert_emails_to_addresses(emails, user['name'])
    subject = 'RDRHC Schedule Changes'
    body = {
        'plain': MIMEText(text, 'plain'),
        'html': MIMEText(html, 'html'),
    }
    send_multipart_email(app_config, to_addresses, subject, body)

def update_codes_section(text, html, codes):
    """Replaces the codes section with all the missing shift codes."""
    LOG.debug('Formatting missing shift codes for email')

    missing_codes_text = []
    missing_codes_html = []

    for code in codes:
        missing_codes_text.append(' - {}'.format(code))
        missing_codes_html.append('<li>{}</li>'.format(code))

    text = text.replace('{{ codes }}', '\r\n'.join(missing_codes_text))
    html = html.replace('{{ codes }}', '\r\n'.join(missing_codes_html))

    # Remove the block markers
    text = text.replace('{% block codes %}', '')
    html = html.replace('{% block codes %}', '')

    return text, html

def email_missing_codes(missing_codes, app_config):
    """Emails owner with any new missing shift codes"""

    LOG.debug('New missing shift codes uploaded to database - notifying owner')

    # Opens the notification (text) template
    LOG.debug('Opening the email templates')

    text_loc = app_config['email']['missing_codes_text']

    with open(text_loc, 'r') as text_file:
        text = text_file.read().replace('\n', '\r\n')

    # Opens the notification (text) template
    html_loc = app_config['email']['missing_codes_html']

    with open(html_loc, 'r') as html_file:
        html = html_file.read()

    text, html = update_codes_section(text, html, missing_codes)

    # Send the email
    to_addresses = convert_emails_to_addresses(
        [app_config['email']['owner_email']],
        app_config['email']['owner_name']
    )
    subject = 'RDRHC Calendar Missing Shift Codes'
    body = {
        'plain': MIMEText(text, 'plain'),
        'html': MIMEText(html, 'html'),
    }
    send_multipart_email(app_config, to_addresses, subject, body)

def notify_user(user, app_config, schedule):
    """Determines which emails to send to specified user."""
    # Get the users email(s)
    emails = retrieve_emails(user['id'], app_config)

    # If this is the first schedule, email the welcome details
    if user['first_email_sent'] is False:
        email_welcome(user, emails, app_config)

    # Email the user the calendar details
    email_notifications = [
        schedule.notification_details['additions'],
        schedule.notification_details['deletions'],
        schedule.notification_details['changes'],
        schedule.notification_details['missing'],
        schedule.notification_details['null'],
    ]

    if any(email_notifications):
        email_schedule(user, emails, app_config, schedule.notification_details)
