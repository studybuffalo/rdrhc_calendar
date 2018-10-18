"""Extracts and organizes a users schedule details."""

from datetime import datetime, timedelta
import json
import logging

from decimal import Decimal
import requests

from modules.custom_exceptions import ScheduleError
from modules.extract_schedule import generate_raw_schedule


LOG = logging.getLogger(__name__)

class FormattedShift():
    """Holds expanded details on a user's specified shift"""

    def __init__(self, code, start_datetime, end_datetime, comment, django):
        self.shift_code = code
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.comment = comment
        self.django_shift = django

    def __str__(self):
        return "{} ({} to {})".format(
            self.shift_code, self.start_datetime, self.end_datetime
        )

class Schedule():
    """Holds all the users shifts and any noted modifications"""

    def __init__(
            self, shifts, additions, deletions, changes, missing, null,
            missing_upload
    ):
        self.shifts = shifts
        self.additions = additions
        self.deletions = deletions
        self.changes = changes
        self.missing = missing
        self.null = null
        self.missing_upload = missing_upload

class EmailShift():
    """Holds details on shift modifications for emailing to the user"""
    date = 0
    msg = ""

    def __init__(self, date, msg):
        self.date = date
        self.msg = msg

def retrieve_shift_codes(app_config, user_id):
    """Takes a specific user and retrieves their shift times."""
    LOG.debug('Collecting shift codes for user id = %s', user_id)

    api_url = '{}shift-codes/{}/'.format(app_config['api_url'], user_id)

    shift_code_response = requests.get(
        api_url,
        headers=app_config['api_headers']
    )

    if shift_code_response.status_code >= 400:
        raise ScheduleError(
            (
                'Unable to connect to API ({}) and retrieve '
                'user shift codes.'
            ).format(api_url)
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
            shift_codes[index][key] = datetime.strptime(
                code[key], '%H:%M:%S'
            ).time()

        for key in decimal_keys:
            shift_codes[index][key] = Decimal(code[key])

    return shift_codes

def retrieve_stat_holidays(app_config, schedule):
    """Retrieves any stat holidays occuring between schedule dates."""
    LOG.debug('Retrieving stat holiday information.')

    try:
        first_day = str(schedule[0]['start_date'])
        last_day = str(schedule[-1]['start_date'])
    except IndexError:
        # Known error when a user has no shifts
        first_day = datetime(2001, 1, 1)
        last_day = datetime(2025, 12, 31)

    api_url = '{}stat-holidays/?date_start={}&date_end={}'.format(
        app_config['api_url'], first_day, last_day
    )

    stat_holidays_response = requests.get(
        api_url,
        headers=app_config['api_headers']
    )

    if stat_holidays_response.status_code >= 400:
        raise ScheduleError(
            (
                'Unable to connect to API ({}) and retrieve '
                'stat holidays.'
            ).format(api_url)
        )

    stat_holidays = []

    for holiday_date in json.loads(stat_holidays_response.text):
        stat_holidays.append(
            datetime.strptime(holiday_date, '%Y-%m-%d')
        )

    return stat_holidays

def retrieve_old_schedule(app_config, user_id):
    """Retrieves the user's previous schedule from the database"""

    api_url = '{}shifts/{}/'.format(
        app_config['api_url'], user_id
    )

    shifts_response = requests.get(
        api_url,
        headers=app_config['api_headers']
    )

    if shifts_response.status_code >= 400:
        raise ScheduleError(
            (
                'Unable to connect to API ({}) and retrieve '
                'users old shifts.'
            ).format(api_url)
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

def generate_formatted_schedule(user, app_config, raw_schedule, old_schedule):
    """Takes the raw schedule and returns the required formatted objects"""

    def is_stat(stat_holidays, date):
        """Determines if the date is a stat holiday or not"""

        for holiday in stat_holidays:
            if date == holiday:
                return True

        return False

    def group_schedule_by_date(schedule):
        """Groups schedule shifts by date"""
        groupings = {}

        for shift in schedule:
            key_match = False
            shift_date = shift.start_datetime.date()

            for key in groupings:
                if shift_date == key:
                    key_match = True

                    # Do not add 'X' shifts
                    if shift['shift_code'] != 'X':
                        # Append this shift to this key
                        groupings[shift_date].append({
                            'shift_code': shift['shift_code'],
                            'start_date': shift_date
                        })

            if key_match is False:
                # Do not add 'X' shifts
                if shift['shift_code'] != 'X':
                    # Append a new key to the groupings
                    groupings[shift_date] = [{
                        'shift_code': shift['shift_code'],
                        'start_date': shift_date
                    }]

        return groupings

    # Get shift codes/times for user
    shift_code_list = retrieve_shift_codes(app_config, user['sb_user'])

    # Get all the stat holidays for the date range of the raw_schedule
    stat_holidays = retrieve_stat_holidays(app_config, raw_schedule)

    # Assign start and end date/times to user's shifts
    schedule = []
    null_shifts = []
    missing_shifts = []
    missing_codes_for_upload = set()

    for shift in raw_schedule:
        # Search for a shift match
        shift_match = False

        # Record the day of the week
        dow = shift['start_date'].weekday()

        # Check if this is a stat holiday
        stat_match = is_stat(stat_holidays, shift['start_date'])

        for code in shift_code_list:
            # If matched, find the proper day to base shift details on

            if shift['shift_code'] == code['code']:
                shift_match = True

                # Apply proper start time and duration
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

                if start_time:
                    # Shift has time, process as normal

                    # Convert the decimal hours duration to h, m, and s
                    hours = int(duration)
                    minutes = int((duration*60) % 60)

                    start_datetime = datetime.combine(
                        shift['start_date'], start_time
                    )

                    end_datetime = start_datetime + timedelta(
                        hours=hours,
                        minutes=minutes
                    )

                    schedule.append(FormattedShift(
                        shift['shift_code'], start_datetime, end_datetime,
                        shift['comment'], code
                    ))
                else:
                    # Shift has no times - don't add to schedule and mark
                    # it in the null shift list
                    msg = '{} - {}'.format(
                        shift.start_date.strftime('%Y-%m-%d'),
                        shift['shift_code']
                    )

                    null_shifts.append(
                        EmailShift(shift['start_date'], msg)
                    )

                # End loop
                break

        # If no shift match, provide default values
        if shift_match is False:
            # Add missing shift to the Missing shift list
            msg = '{} - {}'.format(
                shift['start_date'].strftime('%Y-%m-%d'), shift['shift_code']
            )

            missing_shifts.append(
                EmailShift(shift['start_date'], msg)
            )

            # Add the missing code to the missing code set
            missing_codes_for_upload.add(shift['shift_code'])

            # Set default times
            defaults = app_config['calendar_defaults']

            if stat_match:
                start_datetime = datetime.combine(
                    shift['start_date'], defaults['stat_start']
                )

                end_datetime = start_datetime + timedelta(
                    hours=defaults['stat_hours'],
                    minutes=defaults['stat_minutes']
                )
            elif dow >= 5:
                start_datetime = datetime.combine(
                    shift['start_date'], defaults['weekend_start']
                )

                end_datetime = start_datetime + timedelta(
                    hours=defaults['weekend_hours'],
                    minutes=defaults['weekend_minutes']
                )
            else:
                start_datetime = datetime.combine(
                    shift['start_date'], defaults['weekday_start']
                )

                end_datetime = start_datetime + timedelta(
                    hours=defaults['weekday_hours'],
                    minutes=defaults['weekday_minutes']
                )

            schedule.append(FormattedShift(
                shift['shift_code'], start_datetime, end_datetime,
                shift['comment'], None
            ))


    # Determine the shift additions, deletions, and changes
    # Generate a new schedule listing organized by date
    new_by_date = group_schedule_by_date(schedule)

    # Check if there are any deletions or changes
    deletions = []
    changes = []

    for old_date, old_shifts in old_schedule.items():
        shift_match = []

        if old_date in new_by_date:
            new_shifts = new_by_date[old_date]

            if len(old_shifts) == len(new_shifts):
                for old in old_shifts:
                    for new in new_shifts:
                        if old['shift_code'] == new.shift_code:
                            shift_match.append(True)

            # If the number of Trues equal length of old_shifts,
            # no changes occurred
            if len(shift_match) != len(old_shifts):
                old_codes = '/'.join(str(s['shift_code']) for s in old_shifts)
                new_codes = '/'.join(str(s.shift_code) for s in new_shifts)
                msg = '{} - {} changed to {}'.format(
                    old_date, old_codes, new_codes
                )

                changes.append(EmailShift(old_date, msg))
        else:
            # Shift was deleted
            old_codes = '/'.join(str(s['shift_code']) for s in old_shifts)
            msg = '{} - {}'.format(old_date, old_codes)

            deletions.append(EmailShift(old_date, msg))

    # Checks if there are any new additions
    additions = []

    for new_date, new_shifts in new_by_date.items():
        shift_match = []

        if new_date not in old_schedule:
            new_codes = '/'.join(str(s['shift_code']) for s in new_shifts)
            msg = '{} - {}'.format(new_date.strftime('%Y-%m-%d'), new_codes)

            additions.append(EmailShift(new_date, msg))

    # Removes missing shifts not in the additions or changes lists
    # (user will have already been notified on these shifts)
    missing = []

    for missing_shift in missing_shifts:
        for change in changes:
            if missing_shift.date == change.date:
                missing.append(missing_shift)

        for addition in additions:
            if missing_shift.date == addition.date:
                missing.append(missing_shift)

    null = []

    # Removes null shifts not in the additions or changes lists
    # (user will have already been notified on these shifts)
    for null_shift in null_shifts:
        for change in changes:
            if null_shift.date == change.date:
                null.append(null_shift)

        for addition in additions:
            if null_shift.date == addition.date:
                null.append(null_shift)

    # Return all the required items to generate the calendar and emails
    return Schedule(
        schedule, additions, deletions, changes, missing, null,
        missing_codes_for_upload
    )

def assemble_schedule(app_config, excel_files, user):
    """Assembles all the schedule details for provided user."""

    old_schedule = retrieve_old_schedule(app_config, user['id'])

    new_schedule_raw = generate_raw_schedule(app_config, excel_files, user)

    new_schedule_formatted = generate_formatted_schedule(
        user, app_config, new_schedule_raw, old_schedule
    )

    return new_schedule_formatted
