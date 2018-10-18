"""Unit tests for the manager module."""
# pylint: disable=protected-access

from datetime import datetime, time
from decimal import Decimal
from unittest.mock import patch

from modules import assemble_schedule
from modules.custom_exceptions import ScheduleError

from tests.utils import MockRequest404Response, MockRequest200Response


APP_CONFIG = {
    'api_url': 'https://127.0.0.1/api/',
    'api_headers': {'user-agent': 'rdrhc-calendar',},
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
    ],
    '2018-04-01': [
        {"shift_code": "C1", "start_date": "2018-04-01"},
        {"shift_code": "F", "start_date": "2018-04-01"},
    ],
    '2018-05-01': [
        {"shift_code": "C1", "start_date": "2018-12-01"},
    ]
}

EXTRACTED_SCHEDULE = [
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 1, 1),
        'comment': 'SUPER STAT',
    },
    {
        'shift_code': 'C1',
        'start_date': datetime(2018, 12, 1),
        'comment': '',
    },
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
        OLD_SCHEDULE, EXTRACTED_SCHEDULE, USER, APP_CONFIG
    )
    stat_holidays = schedule._retrieve_stat_holidays()

    assert len(stat_holidays) == 10
