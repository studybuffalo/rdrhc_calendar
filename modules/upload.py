"""Functions to handle upload to the database."""

import json
import logging

import requests


# Setup logger
LOG = logging.getLogger(__name__)

def delete_user_schedule(user_id, app_config):
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

def upload_user_schedule(user_id, schedule, app_config):
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
        data={'schedule': json.dumps(post_data)},
        headers=app_config['api_headers'],
    )

    if response.status_code >= 400:
        raise requests.ConnectionError(
            (
                'Unable to connect to API ({}) and upload '
                'user schedule: {}'
            ).format(api_url, response.text)
        )

def update_schedule_database(user, schedule, app_config):
    """Uploads user schedule to Django Database"""
    # Delete the current schedule
    delete_user_schedule(user['sb_user'], app_config)

    # Upload the new schedule
    upload_user_schedule(user['sb_user'], schedule, app_config)

def update_missing_codes_database(missing_codes):
    """Uploads any new missing shift codes"""
    LOG.debug("Checking for missing shift codes")

    new_codes = []

    # for role, code_set in missing_codes.items():
    #     for code in code_set:
    #         if code:
                # retrieved_code, missing_code = MissingShiftCode.objects.get_or_create(
                #     code=code,
                #     role=role
                # )

                # # If this is a new code, record it to email owner
                # if missing_code:
                #     LOG.debug("New code to upload: {}".format(code))

                #     new_codes.append("{} - {}".format(role, code))

    return new_codes
