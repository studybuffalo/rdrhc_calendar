"""Extracts and organizes a users schedule details."""
from datetime import datetime, timedelta
import json
import logging

from decimal import Decimal
import requests

from modules.custom_exceptions import ScheduleError
from modules.extract_schedule import generate_raw_schedule
from modules.utils import convert_duration_to_hours_minutes


LOG = logging.getLogger(__name__)


def retrieve_old_schedule(app_config, user_id):
    """Retrieves the user's previous schedule from the database"""

    api_url = f'{app_config["api_url"]}shifts/{user_id}/'

    shifts_response = requests.get(
        api_url,
        headers=app_config['api_headers']
    )

    if shifts_response.status_code >= 400:
        raise ScheduleError(
            f'Unable to connect to API ({api_url}) and retrieve users old shifts.'
        )

    shifts = json.loads(shifts_response.text)

    old_schedule = {}

    for shift in shifts:
        key_match = False
        shift_date = shift['date']

        for key in old_schedule:
            if shift_date == key:
                key_match = True

                # Do not add 'X' shifts
                if shift['text_shift_code'].upper() != 'X':
                    # Append this shift to this key
                    old_schedule[shift_date].append({
                        'shift_code': shift['text_shift_code'],
                        'start_date': shift_date
                    })

        if key_match is False:
            # Do not add 'X' shifts
            if shift['text_shift_code'].upper() != 'X':
                # Append a new key to the groupings
                old_schedule[shift_date] = [{
                    'shift_code': shift['text_shift_code'],
                    'start_date': shift_date
                }]

    return old_schedule


def is_stat(check_date, stat_list):
    """Checks if provided date is a stat in stat_list"""
    for holiday_date in stat_list:
        if check_date == holiday_date:
            return True

    return False


def get_start_time_duration(stat_match, dow, code):
    """Returns proper start time and duration based on date."""
    if stat_match:
        start_time = code['stat_start']
        duration = code['stat_duration']
    elif dow == 0:
        start_time = code['monday_start']
        duration = code['monday_duration']
    elif dow == 1:
        start_time = code['tuesday_start']
        duration = code['tuesday_duration']
    elif dow == 2:
        start_time = code['wednesday_start']
        duration = code['wednesday_duration']
    elif dow == 3:
        start_time = code['thursday_start']
        duration = code['thursday_duration']
    elif dow == 4:
        start_time = code['friday_start']
        duration = code['friday_duration']
    elif dow == 5:
        start_time = code['saturday_start']
        duration = code['saturday_duration']
    elif dow == 6:
        start_time = code['sunday_start']
        duration = code['sunday_duration']
    else:
        start_time = None
        duration = None

    return start_time, duration


def get_start_end_datetimes(start_date, start_time, duration):
    """Calculates and returns the start and end datetimes."""
    hours = int(duration)
    minutes = int((duration * 60) % 60)

    start_datetime = datetime.combine(start_date, start_time)

    end_datetime = start_datetime + timedelta(
        hours=hours,
        minutes=minutes
    )

    return start_datetime, end_datetime


def get_default_start_end_datetimes(start_date, defaults, stat_match, dow):
    """Determines the proper default start & end datetimes touse."""
    if stat_match:
        start_datetime = datetime.combine(
            start_date, defaults['stat_start']
        )

        hours, minutes = convert_duration_to_hours_minutes(
            defaults['stat_duration']
        )
    elif dow >= 5:
        start_datetime = datetime.combine(
            start_date, defaults['weekend_start']
        )

        hours, minutes = convert_duration_to_hours_minutes(
            defaults['weekend_duration']
        )
    else:
        start_datetime = datetime.combine(
            start_date, defaults['weekday_start']
        )

        hours, minutes = convert_duration_to_hours_minutes(
            defaults['weekday_duration']
        )

    end_datetime = start_datetime + timedelta(
        hours=hours, minutes=minutes
    )

    return start_datetime, end_datetime


class Schedule():
    """Holds all the users shifts and any noted modifications"""
    def _retrieve_shift_codes(self):
        """Takes a specific user and retrieves their shift times."""
        user_id = self.user['sb_user']

        LOG.debug('Collecting shift codes for user id = %s', user_id)

        api_url = f'{self.config["api_url"]}shift-codes/{user_id}/'

        shift_code_response = requests.get(
            api_url,
            headers=self.config['api_headers']
        )

        if shift_code_response.status_code >= 400:
            raise ScheduleError(
                f'Unable to connect to API ({api_url}) and retrieve user shift codes.'
            )

        shift_codes = json.loads(shift_code_response.text)

        for index, code in enumerate(shift_codes):
            date_keys = [
                'monday_start',
                'tuesday_start',
                'wednesday_start',
                'thursday_start',
                'friday_start',
                'saturday_start',
                'sunday_start',
                'stat_start',
            ]
            decimal_keys = [
                'monday_duration',
                'tuesday_duration',
                'wednesday_duration',
                'thursday_duration',
                'friday_duration',
                'saturday_duration',
                'sunday_duration',
                'stat_duration',
            ]

            for key in date_keys:
                if code[key]:
                    shift_codes[index][key] = datetime.strptime(
                        code[key], '%H:%M:%S'
                    ).time()

            for key in decimal_keys:
                if code[key]:
                    shift_codes[index][key] = Decimal(code[key])

        return shift_codes

    def _retrieve_stat_holidays(self):
        """Retrieves any stat holidays occuring between schedule dates."""
        LOG.debug('Retrieving stat holiday information.')

        if self.schedule_new:
            first_day = str(self.schedule_new[0]['start_date'])
            last_day = str(self.schedule_new[-1]['start_date'])

            api_url = f'{self.config["api_url"]}stat-holidays/?date_start={first_day}&date_end={last_day}'

            stat_holidays_response = requests.get(
                api_url,
                headers=self.config['api_headers']
            )

            if stat_holidays_response.status_code >= 400:
                raise ScheduleError(
                    f'Unable to connect to API ({api_url}) and retrieve stat holidays.'
                )

            stat_holidays = []

            for holiday_date in json.loads(stat_holidays_response.text):
                stat_holidays.append(
                    datetime.strptime(holiday_date, '%Y-%m-%d')
                )

            return stat_holidays

        return None

    def _determine_shift_details(self, shift, shift_code_list, stat_holidays):
        is_null = True
        is_missing = True
        db_code_id = None
        dow = shift['start_date'].weekday()
        stat_match = is_stat(shift['start_date'], stat_holidays)

        for code in shift_code_list:
            if shift['shift_code'].upper() == code['code'].upper():
                # Shift code exists for user
                is_missing = False
                db_code_id = code['id']

                # Codes without start times are considered null shifts
                start_time, duration = get_start_time_duration(
                    stat_match, dow, code
                )

                if start_time:
                    is_null = False

                    start_datetime, end_datetime = get_start_end_datetimes(
                        shift['start_date'], start_time, duration
                    )

                break

        if is_missing:
            is_null = False

            # If no shift match, provide default values
            start_datetime, end_datetime = get_default_start_end_datetimes(
                shift['start_date'],
                self.config['calendar_defaults'],
                stat_match,
                dow
            )

            # Record the details for this missing code
            self.notification_details['missing'].append({
                'date': shift['start_date'],
                'email_message': f'{shift["start_date"].strftime("%Y-%m-%d")} - {shift["shift_code"]}',
                'shift_code': shift['shift_code'],
            })

            self.notification_details['missing_upload'].add(
                shift['shift_code']
            )

        # Add any not-null shift
        # Issue logged in GitHub: https://github.com/studybuffalo/rdrhc_calendar/issues/2

        # previously in users schedule
        if is_null is False:
            self.shifts.append({
                'shift_code': shift['shift_code'],
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'comment': shift['comment'],
                'shift_code_fk': db_code_id
            })
        else:
            # Record the details for this null code
            self.notification_details['null'].append({
                'date': shift['start_date'],
                'email_message': f'{shift["start_date"].strftime("%Y-%m-%d")} - {shift["shift_code"]}',
                'shift_code': shift['shift_code'],
            })

    def _group_schedule_by_date(self):
        """Groups schedule shifts by date"""
        groupings = {}

        for shift in self.shifts:
            key_match = False
            shift_date = shift['start_datetime'].strftime('%Y-%m-%d')

            for key in groupings:
                if shift_date == key:
                    key_match = True

                    # https://github.com/studybuffalo/rdrhc_calendar/issues/3
                    # Do not add 'X' shifts
                    if shift['shift_code'].upper() != 'X':
                        # Append this shift to this key
                        groupings[shift_date].append({
                            'shift_code': shift['shift_code'],
                            'start_date': shift_date
                        })

            if key_match is False:
                # Do not add 'X' shifts
                if shift['shift_code'].upper() != 'X':
                    # Append a new key to the groupings
                    groupings[shift_date] = [{
                        'shift_code': shift['shift_code'],
                        'start_date': shift_date
                    }]

        self.schedule_new_by_date = groupings

    def determine_schedule_additions(self):
        """Determines which shifts are additions."""
        for new_date, new_shifts in self.schedule_new_by_date.items():
            if new_date not in self.schedule_old:
                # Get list of all shift codes used
                new_codes = []

                for shift in new_shifts:
                    new_codes.append(shift['shift_code'])

                new_codes_string = '/'.join(new_codes)
                message = f'{new_date} - {new_codes_string}'

                self.notification_details['additions'].append({
                    'date': new_date,
                    'email_message': message,
                    'shift_codes': new_codes,
                })

    def determine_schedule_deletions(self):
        """Determines which shifts are deletions."""
        for old_date, old_shifts in self.schedule_old.items():
            if old_date not in self.schedule_new_by_date:
                old_codes = '/'.join(str(s['shift_code']) for s in old_shifts)
                message = f'{old_date} - {old_codes}'

                self.notification_details['deletions'].append({
                    'date': old_date,
                    'email_message': message
                })

    def determine_schedule_changes(self):
        """Determines which shifts are changes."""
        for old_date, old_shifts in self.schedule_old.items():  # pylint: disable=too-many-nested-blocks
            if old_date in self.schedule_new_by_date:
                # Shift exists for both old and new - check for changes
                shift_match = []

                new_shifts = self.schedule_new_by_date[old_date]

                if len(old_shifts) == len(new_shifts):
                    for old in old_shifts:
                        for new in new_shifts:
                            if old['shift_code'] == new['shift_code']:
                                shift_match.append(True)

                # If the number of Trues equal length of old_shifts,
                # no changes occurred
                if len(shift_match) != len(old_shifts):
                    # Get list of all shift codes used
                    new_codes = []

                    for shift in new_shifts:
                        new_codes.append(shift['shift_code'])

                    new_codes_string = '/'.join(new_codes)

                    old_codes_string = '/'.join(
                        str(s['shift_code']) for s in old_shifts
                    )

                    message = f'{old_date} - {old_codes_string} changed to {new_codes_string}'

                    self.notification_details['changes'].append({
                        'date': old_date,
                        'email_message': message,
                        'shift_codes': new_codes,
                    })

    def clean_missing(self):
        """Remove missing shifts not in additions or changes list.

        The user would have already been notified of these shifts.
        """
        updated_missing = []

        for missing_shift in self.notification_details['missing']:
            is_new = False

            for change in self.notification_details['changes']:
                if missing_shift['shift_code'] in change['shift_codes']:
                    is_new = True
                    break

            for addition in self.notification_details['additions']:
                if missing_shift['shift_code'] in addition['shift_codes']:
                    is_new = True
                    break

            if is_new:
                updated_missing.append(missing_shift)

        self.notification_details['missing'] = updated_missing

    def clean_null(self):
        """Remove null shifts not in additions or changes list.

        The user would have already been notified of these shifts.
        """
        updated_null = []

        for null_shift in self.notification_details['null']:
            is_new = False

            for change in self.notification_details['changes']:
                if null_shift['shift_code'] in change['shift_codes']:
                    is_new = True
                    break

            for addition in self.notification_details['additions']:
                if null_shift['shift_code'] in addition['shift_codes']:
                    is_new = True
                    break

            if is_new:
                updated_null.append(null_shift)

        self.notification_details['null'] = updated_null

    def process_new_schedule(self):
        """Generates a new schedule and identifies important shifts."""

        # Get shift codes/times for user
        shift_code_list = self._retrieve_shift_codes()

        # Get all the stat holidays for the date range of the raw_schedule
        stat_holidays = self._retrieve_stat_holidays()

        # Generate the users shift details
        for shift in self.schedule_new:
            self._determine_shift_details(
                shift, shift_code_list, stat_holidays
            )

        self._group_schedule_by_date()
        self.determine_schedule_additions()
        self.determine_schedule_deletions()
        self.determine_schedule_changes()
        self.clean_missing()
        self.clean_null()

    def __init__(self, schedule_old, schedule_new, user, app_config):
        self.schedule_old = schedule_old
        self.schedule_new = schedule_new
        self.schedule_new_by_date = []
        self.user = user
        self.config = app_config
        self.shifts = []
        self.notification_details = {
            'additions': [],
            'deletions': [],
            'changes': [],
            'missing': [],
            'null': [],
            'missing_upload': set(),
        }


def assemble_schedule(app_config, excel_files, user):
    """Assembles all the schedule details for provided user."""

    old_schedule = retrieve_old_schedule(app_config, user['sb_user'])
    new_schedule_raw = generate_raw_schedule(app_config, excel_files, user)

    new_schedule = Schedule(old_schedule, new_schedule_raw, user, app_config)
    new_schedule.process_new_schedule()

    return new_schedule
