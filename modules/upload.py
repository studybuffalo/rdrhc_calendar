"""Functions to handle upload to the database."""

import json
import logging

import requests

from modules.custom_exceptions import UploadError

# Setup logger
LOG = logging.getLogger(__name__)

def delete_user_schedule(app_config, user_id):
    """Removes the provided users schedule from the database."""
    LOG.debug("Removing old shifts for user id = %s", user_id)

    api_url = '{}shifts/{}/delete/'.format(app_config['api_url'], user_id)

    response = requests.delete(api_url, headers=app_config['api_headers'])

    if response.status_code >= 400:
        raise requests.ConnectionError(
            (
                'Unable to connect to API ({}) and delete '
                'user shift codes.'
            ).format(api_url)
        )

def upload_user_schedule(app_config, user_id, schedule):
    """Uploads the provided users schedule to the database."""
    LOG.debug("Uploading the new shifts for user")

    api_url = '{}shifts/{}/upload/'.format(app_config['api_url'], user_id)

    post_data = []

    for shift in schedule:
        post_data.append({
            'sb_user': user_id,
            'date': shift['start_datetime'].strftime('%Y-%m-%d'),
            'shift_code': (
                shift['shift_code_fk'] if shift['shift_code_fk'] else ''
            ),
            'text_shift_code': shift['shift_code'],
        })

    response = requests.post(
        api_url,
        data={'schedule': post_data},
        headers=app_config['api_headers'],
    )

    if response.status_code >= 400:
        raise UploadError(
            (
                'Unable to connect to API ({}) and upload '
                'user schedule: {}'
            ).format(api_url, response.text)
        )

def update_schedule_database(user, schedule, app_config):
    """Uploads user schedule to Django Database"""
    # Delete the current schedule
    delete_user_schedule(app_config, user['sb_user'])

    # Upload the new schedule
    upload_user_schedule(app_config, user['sb_user'], schedule)

def update_missing_codes_database(app_config, missing_codes):
    """Uploads any new missing shift codes"""
    LOG.debug("Checking for missing shift codes")

    api_url = '{}shift-codes/missing/upload/'.format(app_config['api_url'])

    post_data = []

    for role, codes in missing_codes.items():
        for code in codes:
            post_data.append({'code': code, 'role': role})

    if post_data:
        response = requests.post(
            api_url,
            data={'codes': post_data},
            headers=app_config['api_headers'],
        )

        if response.status_code >= 400:
            raise UploadError(
                (
                    'Unable to connect to API ({}) and upload '
                    'missing codes: {}'
                ).format(api_url, response.text)
            )

        new_codes = json.loads(response.text)

        return new_codes

    return None
