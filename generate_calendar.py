"""Downloads, extracts, and uploads schedules for AHS CZ pharmacists.
    Last Update: 2017-Oct-01

    Copyright (c) Notices
        2017  Joshua R. Torrance  <studybuffalo@studybuffalo.com>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not,
    see <http://www.gnu.org/licenses/>.
    SHOULD YOU REQUIRE ANY EXCEPTIONS TO THIS LICENSE, PLEASE CONTACT
    THE COPYRIGHT HOLDERS.
"""

import json
import logging
import logging.config
import sys

import requests
import sentry_sdk
from unipath import Path

from modules import notify, upload
from modules.assemble_schedule import assemble_schedule
from modules.calendar import generate_calendar
from modules.config import assemble_app_configuration_details, LOGGING_DICT
from modules.custom_exceptions import ScheduleError
from modules.retrieve import retrieve_schedule_file_paths


# Set root for this program to allow absolute paths
ROOT = Path(sys.argv[1])

# Collect all the application configuration values
APP_CONFIG = assemble_app_configuration_details(ROOT)

# Setup Sentry & Logging
logging.config.dictConfig(LOGGING_DICT)
LOG = logging.getLogger(__name__)

sentry_sdk.init(APP_CONFIG['sentry_dsn'])


LOG.info('STARTING RDRHC CALENDAR GENERATOR')

# Collect the Excel schedule files
LOG.info('Retrieving the Excel Schedules')
EXCEL_FILES = retrieve_schedule_file_paths(APP_CONFIG)

# Collect a list of all the user names
LOG.info('Retrieving all calendar users')
USER_RESPONSE = requests.get(
    '{}users/'.format(APP_CONFIG['api_url']),
    headers=APP_CONFIG['api_headers'],
)

if USER_RESPONSE.status_code >= 400:
    raise requests.ConnectionError(
        'Unable to connect to API ({})'.format(APP_CONFIG['api_url'])
    )

USERS = json.loads(USER_RESPONSE.text)

# Set to hold any codes not in Django DB
MISSING_CODES = {
    'a': set(),
    'p': set(),
    't': set()
}

# Cycle through each user and process their schedule
for user in USERS:
    # Assemble the users schedule
    LOG.info(
        'Assembling schedule for %s (role = %s)',
        user['schedule_name'],
        user['role']
    )

    try:
        schedule = assemble_schedule(APP_CONFIG, EXCEL_FILES, user)
    except ScheduleError:
        LOG.exception(
            'Unable to assemble schedule for %s (role = %s)',
            user['schedule_name'],
            user['role']
        )
        schedule = None

    if schedule:
        # Upload the schedule data to the Django server
        upload.update_schedule_database(user, schedule.shifts, APP_CONFIG)

        # Generate and the iCal file to the Django server
        generate_calendar(
            user, schedule.shifts, APP_CONFIG['calendar_save_location']
        )

        # Send any required emails to user
        notify.notify_user(user, APP_CONFIG, schedule)

        # Add the missing codes to the set
        MISSING_CODES[user['role']] = MISSING_CODES[user['role']].union(
            schedule.missing_upload
        )

# # Upload the missing codes to the database
MISSING_CODES_UPLOAD = upload.update_missing_codes_database(MISSING_CODES)

# # Notify owner that there are new codes to upload
if MISSING_CODES_UPLOAD:
    notify.email_missing_codes(MISSING_CODES_UPLOAD, APP_CONFIG)

LOG.info('CALENDAR GENERATION COMPLETE')
