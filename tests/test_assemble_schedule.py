"""Unit tests for the manager module."""
# pylint: disable=protected-access

from datetime import datetime, date, time
from decimal import Decimal
from unittest.mock import patch

from modules import assemble_schedule
from modules.custom_exceptions import ScheduleError

from tests.utils import MockRequest404Response, MockRequest200Response


APP_CONFIG = {
    'api_url': 'https://127.0.0.1/api/',
    'api_headers': {'user-agent': 'rdrhc-calendar',},
    'calendar_defaults': {
        'weekday_start': time(1, 0, 0),
        'weekday_duration': Decimal(1.1),
        'weekend_start': time(5, 0, 0),
        'weekend_duration': Decimal(5.5),
        'stat_start': time(9, 0, 0),
        'stat_duration': Decimal(9.9),
    }
}

USER = {
    'id': 1,
}

OLD_SCHEDULE = {
    '2018-01-01': [
        {"shift_code": "C1", "start_date": "2018-01-01"},
    ],
    '2018-02-01': [
        {"shift_code": "C1", "start_date": "2018-02-01"},
    ],
    '2018-03-01': [
        {"shift_code": "C1", "start_date": "2018-03-01"},
        {"shift_code": "vr", "start_date": "2018-03-01"},
    ],
    '2018-04-01': [
        {"shift_code": "C1", "start_date": "2018-04-01"},
        {"shift_code": "D1", "start_date": "2018-04-01"},
    ],
    '2018-05-01': [
        {"shift_code": "C1", "start_date": "2018-05-01"},
        {"shift_code": "C2", "start_date": "2018-04-01"},
    ],
    '2018-06-01': [
        {"shift_code": "C1", "start_date": "2018-06-01"},
    ],
}

EXTRACTED_SCHEDULE = [
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 1, 1),
        'comment': 'SUPER STAT',
    },
    {
        'shift_code': 'C1F',
        'start_date': datetime(2018, 2, 1),
        'comment': '',
    },
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 3, 1),
        'comment': '',
    },
    {
        'shift_code': 'vr',
        'start_date': datetime(2018, 3, 1),
        'comment': '',
    },
    {
        'shift_code': 'D1',
        'start_date': datetime(2018, 4, 1),
        'comment': '',
    },
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 5, 1),
        'comment': '',
    },
    {
        'shift_code': 'C2',
        'start_date': datetime(2018, 5, 1),
        'comment': '',
    },
    {
        'shift_code': 'A1',
        'start_date': datetime(2018, 7, 1),
        'comment': '',
    },
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 8, 1),
        'comment': '',
    },
    {
        'shift_code': 'WR',
        'start_date': datetime(2018, 8, 1),
        'comment': '',
    },
]

NEW_SCHEDULE = [
    {
        'shift_code': 'C1',
        'start_datetime': datetime(2018, 1, 1, 1, 0),
        'end_datetime': datetime(2018, 1, 1, 2, 0),
        'comment': 'SUPER STAT',
        'shift_code_fk': 1,
    },
    {
        'shift_code': 'C1F',
        'start_datetime': datetime(2018, 2, 1, 2, 0),
        'end_datetime': datetime(2018, 2, 1, 3, 0),
        'comment': '',
        'shift_code_fk': 2,
    },
    {
        'shift_code': 'C1',
        'start_datetime': datetime(2018, 3, 1, 3, 0),
        'end_datetime': datetime(2018, 3, 1, 4, 0),
        'comment': '',
        'shift_code_fk': 1,
    },
    {
        'shift_code': 'vr',
        'start_datetime': datetime(2018, 3, 1, 3, 0),
        'end_datetime': datetime(2018, 3, 1, 4, 0),
        'comment': '',
        'shift_code_fk': 2,
    },
    {
        'shift_code': 'D1',
        'start_datetime': datetime(2018, 4, 1, 4, 0),
        'end_datetime': datetime(2018, 4, 1, 5, 0),
        'comment': '',
        'shift_code_fk': None,
    },
    {
        'shift_code': 'C1',
        'start_datetime': datetime(2018, 5, 1, 5, 0),
        'end_datetime': datetime(2018, 5, 1, 6, 0),
        'comment': '',
        'shift_code_fk': 1,
    },
    {
        'shift_code': 'C2',
        'start_datetime': datetime(2018, 5, 1, 5, 0),
        'end_datetime': datetime(2018, 5, 1, 6, 0),
        'comment': '',
        'shift_code_fk': None,
    },
    {
        'shift_code': 'A1',
        'start_datetime': datetime(2018, 7, 1, 7, 0),
        'end_datetime': datetime(2018, 7, 1, 8, 0),
        'comment': '',
        'shift_code_fk': None,
    },
    {
        'shift_code': 'C1',
        'start_datetime': datetime(2018, 8, 1, 8, 0),
        'end_datetime': datetime(2018, 8, 1, 9, 0),
        'comment': '',
        'shift_code_fk': 1,
    },
]

USER_SHIFT_CODES = [
    {
        'id': 1, 'code': 'C1', 'sb_user': 1, 'role': 'p',
        'stat_start': time(1, 0, 0), 'stat_duration': Decimal('1.1'),
        'monday_start': time(2, 0, 0), 'monday_duration': Decimal('2.2'),
        'tuesday_start': time(3, 0, 0), 'tuesday_duration': Decimal('3.3'),
        'wednesday_start': time(4, 0, 0), 'wednesday_duration': Decimal('4.4'),
        'thursday_start': time(5, 0, 0), 'thursday_duration': Decimal('5.5'),
        'friday_start': time(6, 0, 0), 'friday_duration': Decimal('6.6'),
        'saturday_start': time(7, 0, 0), 'saturday_duration': Decimal('7.7'),
        'sunday_start': time(8, 0, 0), 'sunday_duration': Decimal('8.8'),
    },
    {
        'id': 2, 'code': 'VR', 'sb_user': 1, 'role': 'p',
        'stat_start': None, 'stat_duration': None,
        'monday_start': None, 'monday_duration': None,
        'tuesday_start': None, 'tuesday_duration':None,
        'wednesday_start': None, 'wednesday_duration': None,
        'thursday_start': None, 'thursday_duration': None,
        'friday_start': None, 'friday_duration': None,
        'saturday_start': None, 'saturday_duration': None,
        'sunday_start': None, 'sunday_duration': None,
    },
    {
        'id': 3, 'code': 'WR', 'sb_user': None, 'role': 'p',
        'stat_start': None, 'stat_duration': None,
        'monday_start': None, 'monday_duration': None,
        'tuesday_start': None, 'tuesday_duration':None,
        'wednesday_start': None, 'wednesday_duration': None,
        'thursday_start': None, 'thursday_duration': None,
        'friday_start': None, 'friday_duration': None,
        'saturday_start': None, 'saturday_duration': None,
        'sunday_start': None, 'sunday_duration': None,
    },
]

STAT_HOLIDAYS = [
    datetime(2018, 1, 1), datetime(2018, 2, 19), datetime(2018, 3, 30),
    datetime(2018, 5, 21), datetime(2018, 7, 1), datetime(2018, 8, 6),
    datetime(2018, 9, 3), datetime(2018, 10, 8), datetime(2018, 11, 11),
    datetime(2018, 12, 25),
]

class MockRetrieveOldScheduleResponse(MockRequest200Response):
    """A mock of a response to the retrieve_old_schedule function."""
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.text = """[
            {"text_shift_code": "C1", "date": "2018-01-01"},
            {"text_shift_code": "C1", "date": "2018-02-01"},
            {"text_shift_code": "X", "date": "2018-02-01"},
            {"text_shift_code": "X", "date": "2018-03-01"},
            {"text_shift_code": "C1", "date": "2018-03-01"},
            {"text_shift_code": "C1", "date": "2018-04-01"},
            {"text_shift_code": "F", "date": "2018-04-01"},
            {"text_shift_code": "C1", "date": "2018-12-01"}
        ]"""

class MockRetrieveShiftCodeResponse(MockRequest200Response):
    """A mock of a response to the retireve_shift_codes function."""
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.text = """[
            {
                "monday_start": "07:00:00", "monday_duration": 8.25,
                "tuesday_start": "07:00:00", "tuesday_duration": 8.25,
                "wednesday_start": "07:00:00", "wednesday_duration": 8.25,
                "thursday_start": "07:00:00", "thursday_duration": 8.25,
                "friday_start": "07:00:00", "friday_duration": 8.25,
                "saturday_start": "07:00:00", "saturday_duration": 8.25,
                "sunday_start": "07:00:00", "sunday_duration": 8.25,
                "stat_start": "07:00:00", "stat_duration": 8.25
            }
        ]"""

class MockRetrieveStatHolidaysResponse(MockRequest200Response):
    """A mock of a response to the retrieve_stat_holidays function."""
    def __init__(self, url, headers):
        super().__init__(url, headers)
        self.text = """[
            "2018-01-01", "2018-02-19", "2018-03-30", "2018-05-21",
            "2018-07-01", "2018-08-06", "2018-09-03", "2018-10-08",
            "2018-11-11", "2018-12-25"
        ]"""

@patch('requests.get', MockRequest404Response)
def test_retrieve_old_schedule_404_response():
    """Tests handling of 404 response in retrieve_old_schedule."""
    try:
        assemble_schedule.retrieve_old_schedule(APP_CONFIG, 1)
    except ScheduleError:
        assert True
    else:
        assert False

@patch('requests.get', MockRetrieveOldScheduleResponse)
def test_retrieve_old_schedule_group_by_date():
    """Tests handling of empty schedule in retrieve_stat_holidays."""
    schedule = assemble_schedule.retrieve_old_schedule(APP_CONFIG, 1)

    assert len(schedule) == 5
    assert len(schedule['2018-01-01']) == 1
    assert len(schedule['2018-04-01']) == 2

@patch('requests.get', MockRetrieveOldScheduleResponse)
def test_retrieve_old_schedule_x_shift_handling():
    """Tests handling of empty schedule in retrieve_stat_holidays."""
    schedule = assemble_schedule.retrieve_old_schedule(APP_CONFIG, 1)

    # Ensure no X shifts were added
    x_removed = True

    for _, shift_date in schedule.items():
        for shift in shift_date:
            if shift['shift_code'].upper() == 'X':
                x_removed = True

    assert x_removed

def test_is_stat_is_true_on_stat():
    """Tests that is_stat returns True on stat holiday."""
    assert assemble_schedule.is_stat(datetime(2018, 1, 1), STAT_HOLIDAYS)

def test_is_stat_is_false_on_non_stat():
    """Tests that is_stat returns False on non-stat date."""
    stat_result = assemble_schedule.is_stat(
        datetime(2018, 1, 2), STAT_HOLIDAYS
    )

    assert stat_result is False

def test_get_start_time_duration_stat():
    """Checks get_start_time_duration returns proper stat values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        True, 1, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['stat_start']
    assert duration == USER_SHIFT_CODES[0]['stat_duration']

def test_get_start_time_duration_monday():
    """Checks get_start_time_duration returns proper Monday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 0, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['monday_start']
    assert duration == USER_SHIFT_CODES[0]['monday_duration']

def test_get_start_time_duration_tuesday():
    """Checks get_start_time_duration returns proper Tuesday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 1, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['tuesday_start']
    assert duration == USER_SHIFT_CODES[0]['tuesday_duration']

def test_get_start_time_duration_wednesday():
    """Checks get_start_time_duration returns proper Wednesday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 2, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['wednesday_start']
    assert duration == USER_SHIFT_CODES[0]['wednesday_duration']

def test_get_start_time_duration_thursday():
    """Checks get_start_time_duration returns proper Thursday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 3, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['thursday_start']
    assert duration == USER_SHIFT_CODES[0]['thursday_duration']

def test_get_start_time_duration_friday():
    """Checks get_start_time_duration returns proper Friday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 4, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['friday_start']
    assert duration == USER_SHIFT_CODES[0]['friday_duration']

def test_get_start_time_duration_saturday():
    """Checks get_start_time_duration returns proper Satuday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 5, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['saturday_start']
    assert duration == USER_SHIFT_CODES[0]['saturday_duration']

def test_get_start_time_duration_sunday():
    """Checks get_start_time_duration returns proper Sunday values."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, 6, USER_SHIFT_CODES[0]
    )

    assert start_time == USER_SHIFT_CODES[0]['sunday_start']
    assert duration == USER_SHIFT_CODES[0]['sunday_duration']

def test_get_start_time_duration_blank():
    """Checks get_start_time_duration returns proper blank."""
    start_time, duration = assemble_schedule.get_start_time_duration(
        False, None, USER_SHIFT_CODES[0]
    )

    assert start_time is None
    assert duration is None

def test_get_start_end_datetimes():
    """Checks that get_start_end_datetimes returns proper values."""
    start, end = assemble_schedule.get_start_end_datetimes(
        datetime(2018, 1, 1), time(7, 0, 0), Decimal(8.25)
    )

    assert start == datetime(2018, 1, 1, 7, 0, 0)
    assert end == datetime(2018, 1, 1, 15, 15, 0)

def test_get_default_start_end_datetimes_stat():
    """Checks get_default_start_end_datetimes returns stat default."""
    start, end = assemble_schedule.get_default_start_end_datetimes(
        datetime(2018, 1, 1), APP_CONFIG['calendar_defaults'], True, 0
    )

    assert start == datetime(2018, 1, 1, 9, 0)
    assert end == datetime(2018, 1, 1, 18, 54)

def test_get_default_start_end_datetimes_weekday():
    """Checks get_default_start_end_datetimes returns weekday default."""
    start, end = assemble_schedule.get_default_start_end_datetimes(
        datetime(2018, 1, 1), APP_CONFIG['calendar_defaults'], False, 0
    )

    assert start == datetime(2018, 1, 1, 1, 0)
    assert end == datetime(2018, 1, 1, 2, 6)

def test_get_default_start_end_datetimes_weekend():
    """Checks get_default_start_end_datetimes returns weekend default."""
    start, end = assemble_schedule.get_default_start_end_datetimes(
        datetime(2018, 1, 1), APP_CONFIG['calendar_defaults'], False, 5
    )

    assert start == datetime(2018, 1, 1, 5, 0)
    assert end == datetime(2018, 1, 1, 10, 30)

@patch('requests.get', MockRequest404Response)
def test_retrieve_shift_codes_404_response():
    """Tests handling of 404 response in retrieve_shift_codes."""
    try:
        schedule = assemble_schedule.Schedule(
            OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
        )
        schedule._retrieve_shift_codes()
    except ScheduleError:
        assert True
    else:
        assert False

@patch('requests.get', MockRetrieveShiftCodeResponse)
def test_retrieve_shift_codes_time_conversions():
    """Tests that time conversions work properly."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    shift_codes = schedule._retrieve_shift_codes()

    assert isinstance(shift_codes[0]['monday_start'], time)

@patch('requests.get', MockRetrieveShiftCodeResponse)
def test_retrieve_shift_codes_decimal_conversions():
    """Tests that decimal conversions work properly."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    shift_codes = schedule._retrieve_shift_codes()

    assert isinstance(shift_codes[0]['monday_duration'], Decimal)

@patch('requests.get', MockRequest404Response)
def test_retrieve_stat_holidays_404_response():
    """Tests handling of 404 response in retrieve_stat_holidays."""
    try:
        schedule = assemble_schedule.Schedule(
            OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
        )
        schedule._retrieve_stat_holidays()
    except ScheduleError:
        assert True
    else:
        assert False

@patch('requests.get', MockRetrieveStatHolidaysResponse)
def test_retrieve_stat_holidays_date_conversion():
    """Tests handling of empty schedule in retrieve_stat_holidays."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    stat_holidays = schedule._retrieve_stat_holidays()

    assert isinstance(stat_holidays[0], datetime)

@patch('requests.get', MockRetrieveStatHolidaysResponse)
def test_retrieve_stat_holidays_with_no_shifts():
    """Tests handling of empty schedule in retrieve_stat_holidays."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, [], USER, APP_CONFIG
    )
    stat_holidays = schedule._retrieve_stat_holidays()

    assert len(stat_holidays) == 10

def test_group_schedule_by_date():
    """Tests that the extracted schedule is properly grouped by date."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    schedule.shifts = NEW_SCHEDULE
    schedule._group_schedule_by_date()

    assert len(schedule.schedule_new_by_date) == 7
    assert len(schedule.schedule_new_by_date['2018-01-01']) == 1
    assert len(schedule.schedule_new_by_date['2018-05-01']) == 2
    assert schedule.schedule_new_by_date['2018-05-01'][1]['shift_code'] == 'C2'

def test_group_schedule_by_date_x_handling():
    """Tests that the extracted schedule ignores "X" shifts."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    updated_new_schedule = NEW_SCHEDULE
    updated_new_schedule.append({
        'shift_code': 'X',
        'start_datetime': datetime(2018, 1, 1, 1, 0),
        'end_datetime': datetime(2018, 1, 1, 2, 0),
        'comment': '',
        'shift_code_fk': None,
    })
    schedule.shifts = updated_new_schedule

    schedule._group_schedule_by_date()

    assert len(schedule.schedule_new_by_date) == 7
    assert len(schedule.schedule_new_by_date['2018-01-01']) == 1

def test_determine_shift_details_defined_shift():
    """Tests assigning details to a defined shift."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    shift = {
        'shift_code': 'C1',
        'start_date': date(2018, 1, 2),
        'comment': '',
    }

    schedule._determine_shift_details(shift, USER_SHIFT_CODES, STAT_HOLIDAYS)

    assert len(schedule.shifts) == 1
    assert schedule.shifts[0]['shift_code'] == 'C1'
    assert schedule.shifts[0]['start_datetime'] == datetime(2018, 1, 2, 3, 0)
    assert schedule.shifts[0]['end_datetime'] == datetime(2018, 1, 2, 6, 18)
    assert schedule.shifts[0]['comment'] == ''
    assert schedule.shifts[0]['shift_code_fk'] == 1

def test_determine_shift_details_with_comment():
    """Tests that comments are added to a shift."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    shift = {
        'shift_code': 'C1',
        'start_date': date(2018, 1, 2),
        'comment': 'TEST',
    }

    schedule._determine_shift_details(shift, USER_SHIFT_CODES, STAT_HOLIDAYS)

    assert len(schedule.shifts) == 1
    assert schedule.shifts[0]['comment'] == 'TEST'

def test_determine_shift_details_null_shift():
    """Tests handling of null shift."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    shift = {
        'shift_code': 'vr',
        'start_date': date(2018, 1, 2),
        'comment': '',
    }

    schedule._determine_shift_details(shift, USER_SHIFT_CODES, STAT_HOLIDAYS)
    null_details = schedule.notification_details['null']

    assert not schedule.shifts
    assert len(null_details) == 1
    assert null_details[0]['date'] == date(2018, 1, 2)
    assert null_details[0]['email_message'] == '2018-01-02 - vr'

def test_determine_shift_details_missing_shift():
    """Tests handling of missing shift."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    shift = {
        'shift_code': 'E1',
        'start_date': date(2018, 1, 2),
        'comment': '',
    }

    schedule._determine_shift_details(shift, USER_SHIFT_CODES, STAT_HOLIDAYS)
    missing = schedule.notification_details['missing']
    missing_upload = schedule.notification_details['missing_upload']

    assert len(schedule.shifts) == 1
    assert len(missing) == 1
    assert len(missing_upload) == 1

    assert schedule.shifts[0]['shift_code'] == 'E1'
    assert schedule.shifts[0]['start_datetime'] == datetime(2018, 1, 2, 1, 0)
    assert schedule.shifts[0]['end_datetime'] == datetime(2018, 1, 2, 2, 6)
    assert schedule.shifts[0]['shift_code_fk'] is None

    assert missing[0]['date'] == date(2018, 1, 2)
    assert missing[0]['email_message'] == '2018-01-02 - E1'
    assert 'E1' in missing_upload

def test_determine_schedule_additions():
    """Tests identification of shift additions."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    schedule.shifts = NEW_SCHEDULE
    schedule._group_schedule_by_date()
    schedule.determine_schedule_additions()

    additions = schedule.notification_details['additions']
    assert len(additions) == 2
    assert additions[0]['date'] == '2018-07-01'
    assert additions[0]['email_message'] == '2018-07-01 - A1'
    assert additions[1]['date'] == '2018-08-01'
    assert additions[1]['email_message'] == '2018-08-01 - C1'

# TODO: Add test for an X shift addition

def test_determine_schedule_deletions():
    """Tests identification of shift deletions."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    schedule.shifts = NEW_SCHEDULE
    schedule._group_schedule_by_date()
    schedule.determine_schedule_deletions()

    deletions = schedule.notification_details['deletions']
    assert len(deletions) == 1
    assert deletions[0]['date'] == '2018-06-01'
    assert deletions[0]['email_message'] == '2018-06-01 - C1'

# TODO: Add test for an X shift deletion

def test_determine_schedule_changes():
    """Tests identification of shift changes."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    schedule.shifts = NEW_SCHEDULE
    schedule._group_schedule_by_date()
    schedule.determine_schedule_changes()

    changes = schedule.notification_details['changes']

    assert len(changes) == 2
    assert changes[0]['date'] == '2018-02-01'
    assert changes[0]['email_message'] == '2018-02-01 - C1 changed to C1F'
    assert changes[1]['date'] == '2018-04-01'
    assert changes[1]['email_message'] == '2018-04-01 - C1/D1 changed to D1'

# TODO: Add test for X shift change (addition and deletion)

def test_clean_missing_removes_shifts_properly():
    """Tests that old missing shifts are removed from list."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    # Mimic initial shift detail generation
    for shift in schedule.schedule_new:
        schedule._determine_shift_details(
            shift, USER_SHIFT_CODES, STAT_HOLIDAYS
        )

    # Initial test of original number of missing entries
    assert len(schedule.notification_details['missing']) == 4
    assert schedule.notification_details['missing'][0]['shift_code'] == 'C1F'
    assert schedule.notification_details['missing'][1]['shift_code'] == 'D1'
    assert schedule.notification_details['missing'][2]['shift_code'] == 'C2'
    assert schedule.notification_details['missing'][3]['shift_code'] == 'A1'

    schedule._group_schedule_by_date()
    schedule.determine_schedule_additions()
    schedule.determine_schedule_changes()
    schedule.clean_missing()

    missing = schedule.notification_details['missing']

    assert len(missing) == 3
    assert missing[0]['shift_code'] == 'C1F'
    assert missing[1]['shift_code'] == 'D1'
    assert missing[2]['shift_code'] == 'A1'

def test_clean_null_removing_shifts_properly():
    """Tests that old null shifts are removed from list."""
    schedule = assemble_schedule.Schedule(
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )

    # Mimic initial shift detail generation
    for shift in schedule.schedule_new:
        schedule._determine_shift_details(
            shift, USER_SHIFT_CODES, STAT_HOLIDAYS
        )

    # Initial test of original number of null entries
    assert len(schedule.notification_details['null']) == 2
    assert schedule.notification_details['null'][0]['shift_code'] == 'vr'
    assert schedule.notification_details['null'][1]['shift_code'] == 'WR'

    schedule._group_schedule_by_date()
    schedule.determine_schedule_additions()
    schedule.determine_schedule_changes()

    # Manually add the WR shift to changes/additions (this normally wouldn't
    # happen as all null shifts are removed during initial processing).
    schedule.notification_details['changes'][1]['shift_codes'].append('WR')
    schedule.notification_details['additions'][1]['shift_codes'].append('WR')

    schedule.clean_null()

    null = schedule.notification_details['null']

    assert len(null) == 1
    assert null[0]['shift_code'] == 'WR'
