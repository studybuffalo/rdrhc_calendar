"""Functions to handle upload to the database."""
import json
import logging

import requests

from modules.custom_exceptions import UploadError


LOG = logging.getLogger(__name__)


def delete_user_schedule(app_config, user_id):
    """Removes the provided users schedule from the database."""
    LOG.debug("Removing old shifts for user id = %s", user_id)

    api_url = f'{app_config["api_url"]}shifts/{user_id}/delete/'

    response = requests.delete(api_url, headers=app_config['api_headers'])

    if response.status_code >= 400:
        raise requests.ConnectionError(
            f'Unable to connect to API ({api_url}) and delete user shift codes.'
        )


def upload_user_schedule(app_config, user_id, schedule):
    """Uploads the provided users schedule to the database."""
    LOG.debug("Uploading the new shifts for user")

    api_url = f'{app_config["api_url"]}shifts/{user_id}/upload/'

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
        data=json.dumps({'schedule': post_data}),
        headers=app_config['api_headers'],
    )

    if response.status_code >= 400:
        raise UploadError(
            f'Unable to connect to API ({api_url}) and upload user schedule: {response.text}'
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

    api_url = f'{app_config["api_url"]}shift-codes/missing/upload/'

    post_data = []

    for role, codes in missing_codes.items():
        for code in codes:
            post_data.append({'code': code, 'role': role})

    if post_data:
        response = requests.post(
            api_url,
            data=json.dumps({'codes': post_data}),
            headers=app_config['api_headers'],
        )

        if response.status_code >= 400:
            raise UploadError(
                f'Unable to connect to API ({api_url}) and upload missing codes: {response}'
            )

        new_codes = json.loads(response.text)

        return new_codes

    return None
