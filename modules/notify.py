"""Functions used to send notifications to users and owners."""

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import json
import logging
import re
import smtplib

import requests


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
        raise requests.ConnectionError(
            (
                'Unable to connect to API ({}) and retrieve '
                'user shift codes.'
            ).format(api_url)
        )

def email_welcome(user, emails, app_config):
    """Sends a welcome email to any new user"""

    # Check if user needs email sent (signed up in past 24 hours)
    if user['first_email_sent'] is False:
        LOG.debug('Processing data to send user a welcome email')

        from_name = app_config['email']['from_name']
        from_email = app_config['email']['from_email']
        from_address = formataddr((from_name, from_email))

        to_addresses = []

        for email in emails:
            to_name = user['name']
            to_email = email
            to_address = formataddr((to_name, to_email))

            to_addresses.append(to_address)

        subject = 'Welcome to Your New Online Schedule'

        content = MIMEMultipart('alternative')
        content['From'] = from_address
        content['To'] = ','.join(to_addresses)
        content['Subject'] = subject
        content['List-Unsubscribe'] = '<{}>'.format(
            app_config['email']['unsubscribe_link']
        )

        # Collects text welcome email from template file
        text_loc = app_config['email']['welcome_text']

        with open(text_loc, 'r') as text_file:
            text = text_file.read().replace('\n', '\r\n')

        # try:
        #     with open(text_loc, 'r') as text_file:
        #         text = text_file.read().replace('\n', '\r\n')
        # except Exception:
        #     LOG.warn(
        #         'Unable to read welcome email text template',
        #         exc_info=True
        #     )
        #     return

        # Collects html welcome email from template file
        html_loc = app_config['email']['welcome_html']

        with open(html_loc, 'r') as html_file:
            html = html_file.read()

        # try:
        #     with open(html_loc, 'r') as html_file:
        #         html = html_file.read()
        # except Exception:
        #     LOG.exception(
        #         'Unable to read welcome email html template',
        #         exc_info=True
        #     )
        #     return

        # Assemble an HTML and plain text version
        text_body = MIMEText(text, 'plain')
        html_body = MIMEText(html, 'html')

        content.attach(text_body)
        content.attach(html_body)

        # Attempt to send email
        if app_config['debug']['email_console']:
            LOG.debug(content.as_string())
        else:
            LOG.info('Sending welcome email to %s', user['name'])
            server = smtplib.SMTP(app_config['email']['server'])

            server.ehlo()
            server.starttls()
            server.sendmail(from_address, to_addresses, content.as_string())
            server.quit()

        # Update user profile to mark first_email_sent as true
        update_first_email_sent_flag(user['id'], app_config)

        # try:
        #     if app_config['debug']['email_console']:
        #         LOG.debug(content.as_string())
        #     else:
        #         LOG.info('Sending welcome email to %s', user['name'])
        #         server = smtplib.SMTP(app_config['email']['server'])

        #         server.ehlo()
        #         server.starttls()
        #         server.sendmail(
        #             from_address, to_addresses, content.as_string()
        #         )
        #         server.quit()

        #     # Update user profile to mark first_email_sent as true
        #     user.first_email_sent = True
        #     user.save()

        # except Exception:
        #     LOG.error(
        #         'Unable to send welcome email to {}'.format(user.name),
        #         exc_info=True
        #     )

def email_schedule(user, emails, app_config, schedule):
    """Emails user with any schedule changes"""

    if (any([
            schedule.additions, schedule.deletions, schedule.changes,
            schedule.missing, schedule.null
    ])):
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

        # Manage added shifts
        LOG.debug('Updating the "additions" section')

        if schedule.additions:
            # Cycle through additions and insert into templates
            additions_text = []
            additions_html = []

            for addition in schedule.additions:
                additions_text.append(' - {}'.format(addition.msg))
                additions_html.append('<li>{}</li>'.format(addition.msg))

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

        # Manage deleted shifts
        LOG.debug('Updating the "deletions" section')

        if schedule.deletions:
            deletions_text = []
            deletions_html = []

            for deletion in schedule.deletions:
                deletions_text.append(' - {}'.format(deletion.msg))
                deletions_html.append('<li>{}</li>'.format(deletion.msg))

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

        # Manage changed shifts
        LOG.debug('Updating the "changes" section')

        if schedule.changes:
            changes_text = []
            changes_html = []

            for change in schedule.changes:
                changes_text.append(' - {}'.format(change.msg))
                changes_html.append('<li>{}</li>'.format(change.msg))

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

        # Manage missing shifts
        LOG.debug('Updating the "missing" section')

        if schedule.missing:
            # TODO: Update this to use durations

            defaults = app_config['calendar_defaults']

            weekday_start = defaults['weekday_start'].strftime('%H:%M')
            text = text.replace('{{ weekday_start }}', weekday_start)
            html = html.replace('{{ weekday_start }}', weekday_start)

            weekday_end = defaults['weekday_end'].strftime('%H:%M')
            text = text.replace('{{ weekday_end }}', weekday_end)
            html = html.replace('{{ weekday_end }}', weekday_end)

            weekend_start = defaults['weekend_start'].strftime('%H:%M')
            text = text.replace('{{ weekend_start }}', weekend_start)
            html = html.replace('{{ weekend_start }}', weekend_start)

            weekend_end = defaults['weekend_end'].strftime('%H:%M')
            text = text.replace('{{ weekend_end }}', weekend_end)
            html = html.replace('{{ weekend_end }}', weekend_end)

            stat_start = defaults['stat_start'].strftime('%H:%M')
            text = text.replace('{{ stat_start }}', stat_start)
            html = html.replace('{{ stat_start }}', stat_start)

            stat_end = defaults['stat_end'].strftime('%H:%M')
            text = text.replace('{{ stat_end }}', stat_end)
            html = html.replace('{{ stat_end }}', stat_end)

            missing_text = []
            missing_html = []

            for missing in schedule.missing:
                missing_text.append(' - {}'.format(missing.msg))
                missing_html.append('<li>{}</li>'.format(missing.msg))

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

        # Manage excluded shifts
        LOG.debug('Updating the "excluded" section')

        if schedule.null:
            null_text = []
            null_html = []

            for null in schedule.null:
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

        # Add the calendar name
        calendar_name = user['calendar_name']
        text = text.replace('{{ calendar_name }}', calendar_name)
        html = html.replace('{{ calendar_name }}', calendar_name)


        # Setup email settings
        LOG.debug('Setting up the other email settings')

        from_name = app_config['email']['from_name']
        from_email = app_config['email']['from_email']
        from_address = formataddr((from_name, from_email))

        # Create list of all of the user's emails
        to_addresses = []

        for email in emails:
            to_name = user['name']
            to_email = email
            to_address = formataddr((to_name, to_email))

            to_addresses.append(to_address)

        subject = 'RDRHC Schedule Changes'

        content = MIMEMultipart('alternative')
        content['From'] = from_address
        content['To'] = ','.join(to_addresses)
        content['Subject'] = subject
        content['List-Unsubscribe'] = '<{}>'.format(
            app_config['email']['unsubscribe_link']
        )

        # Construct the email body
        text_body = MIMEText(text, 'plain')
        html_body = MIMEText(html, 'html')

        content.attach(text_body)
        content.attach(html_body)

        # Send the email
        if app_config['debug']['email_console']:
            LOG.debug(content.as_string())
        else:
            LOG.info('Sending update email to %s', user.name)

            server = smtplib.SMTP(app_config['email']['server'])
            server.ehlo()
            server.starttls()
            server.sendmail(from_address, to_addresses, content.as_string())
            server.quit()
        # try:
        #     if app_config['debug']['email_console']:
        #         LOG.debug(content.as_string())
        #     else:
        #         LOG.info('Sending update email to %s' % user.name)

        #         server = smtplib.SMTP(app_config['email']['server'])
        #         server.ehlo()
        #         server.starttls()
        #         server.sendmail(
        #             from_address, to_addresses, content.as_string()
        #         )
        #         server.quit()
        # except Exception:
        #     LOG.error(
        #         'Unable to send update email to {}'.format(user.name),
        #         exc_info=True
        #     )

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

    # try:
    #     with open(html_loc, 'r') as htmlFile:
    #         html = htmlFile.read()
    # except Exception:
    #     LOG.warn(
    #         'Unable to read missing codes email html template at {}'.format(
    #             html_loc
    #         ),
    #         exc_info=True
    #     )
    #     html = None

    # Add all the missing shift codes to the email
    LOG.debug('Formatting missing shift codes for email')

    missing_codes_text = []
    missing_codes_html = []

    for code in missing_codes:
        missing_codes_text.append(' - {}'.format(code))
        missing_codes_html.append('<li>{}</li>'.format(code))

    text = text.replace('{{ codes }}', '\r\n'.join(missing_codes_text))
    html = html.replace('{{ codes }}', '\r\n'.join(missing_codes_html))

    # Remove the block markers
    text = text.replace('{% block codes %}', '')
    html = html.replace('{% block codes %}', '')

    # Setup email settings
    LOG.debug('Setting up the other email settings')

    from_name = app_config['email']['from_name']
    from_email = app_config['email']['from_email']
    from_address = formataddr((from_name, from_email))

    to_name = app_config['email']['owner_name']
    to_email = app_config['email']['owner_email']
    to_address = formataddr((to_name, to_email))

    subject = 'RDRHC Calendar Missing Shift Codes'

    content = MIMEMultipart('alternative')
    content['From'] = from_address
    content['To'] = to_address
    content['Subject'] = subject

    # Construct the email body
    text_body = MIMEText(text, 'plain')
    html_body = MIMEText(html, 'html')

    content.attach(text_body)
    content.attach(html_body)

    # Send the email
    if app_config['debug']['email_console']:
        LOG.debug(content.as_string())
    else:
        LOG.info('Sending missing shift code email')

        server = smtplib.SMTP(app_config['email']['server'])
        server.ehlo()
        server.starttls()
        server.sendmail(from_address, to_address, content.as_string())
        server.quit()

    # try:
    #     if app_config['debug']['email_console']:
    #         LOG.debug(content.as_string())
    #     else:
    #         LOG.info('Sending missing shift code email')

    #         server = smtplib.SMTP(app_config['email']['server'])
    #         server.ehlo()
    #         server.starttls()
    #         server.sendmail(from_address, to_address, content.as_string())
    #         server.quit()
    # except Exception:
    #     LOG.error('Unable to send missing shift code email', exc_info=True)

def notify_user(user, app_config, schedule):
    """Determines which emails to send to specified user."""
    # Get the users email(s)
    emails = retrieve_emails(user['id'], app_config)

    # If this is the first schedule, email the welcome details
    email_welcome(user, emails, app_config)

    # Email the user the calendar details
    email_schedule(user, emails, app_config, schedule)
