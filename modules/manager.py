"""Functions to manage running of all program functions."""

import json
import logging
import logging.config

import requests

from modules import notify, upload
from modules.assemble_schedule import assemble_schedule
from modules.calendar import generate_calendar
from modules.custom_exceptions import ScheduleError
from modules.retrieve import retrieve_schedule_file_paths


LOG = logging.getLogger(__name__)

def retrieve_users(app_config):
    """Retrieves all the calendar users."""
    LOG.info('Retrieving all calendar users')

    response = requests.get(
        '{}users/'.format(app_config['api_url']),
        headers=app_config['api_headers'],
    )

    if response.status_code >= 400:
        raise requests.ConnectionError(
            'Unable to connect to API ({})'.format(app_config['api_url'])
        )

    users = json.loads(response.text)

    return users

def run_program(app_config):
    """Main function to run the program."""

    LOG.info('STARTING RDRHC CALENDAR GENERATOR')

    # Collect the Excel schedule files
    LOG.info('Retrieving the Excel Schedules')
    excel_files = retrieve_schedule_file_paths(app_config)

    # Collect list of all the user names
    users = retrieve_users(app_config)

    # Set to hold any codes not in Django DB
    missing_codes = {
        'a': set(),
        'p': set(),
        't': set()
    }

    # Cycle through each user and process their schedule
    for user in users:
        # Assemble the users schedule
        LOG.info(
            'Assembling schedule for %s (role = %s)',
            user['schedule_name'],
            user['role']
        )

        try:
            schedule = assemble_schedule(app_config, excel_files, user)
        except ScheduleError:
            LOG.exception(
                'Unable to assemble schedule for %s (role = %s)',
                user['schedule_name'],
                user['role']
            )
            schedule = None

        if schedule:
            # Upload the schedule data to the Django server
            upload.update_schedule_database(user, schedule.shifts, app_config)

            # Generate and the iCal file to the Django server
            generate_calendar(
                user, schedule.shifts, app_config['calendar_save_location']
            )

            # Send any required emails to user
            notify.notify_user(user, app_config, schedule)

            # Add the missing codes to the set
            missing_codes[user['role']] = missing_codes[user['role']].union(
                schedule.missing_upload
            )

    # Upload the missing codes to the database
    missing_codes_upload = upload.update_missing_codes_database(missing_codes)

    # Notify owner that there are new codes to upload
    if missing_codes_upload:
        notify.email_missing_codes(missing_codes_upload, app_config)

    LOG.info('CALENDAR GENERATION COMPLETE')
