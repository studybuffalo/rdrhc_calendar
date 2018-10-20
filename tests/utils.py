"""Utility functions for test cases."""

from datetime import datetime, time
from decimal import Decimal


class MockRequest404Response():
    """A mock of requests 404 response."""
    def __init__(self, url, headers, data=None):
        self.url = url
        self.headers = headers
        self.status_code = 404
        self.data = data
        self.text = 'Mock 404 error'

class MockRequest200Response():
    """A mock of request 200 response with custom text."""
    def __init__(self, url, headers, data=None):
        self.url = url
        self.headers = headers
        self.status_code = 200
        self.data = data

APP_CONFIG = {
    'api_url': 'https://127.0.0.1/api/',
    'api_headers': {'user-agent': 'rdrhc-calendar',},
    'calendar_defaults': {
        'weekday_start': time(1, 0, 0),
        'weekday_duration': Decimal('1.1'),
        'weekend_start': time(5, 0, 0),
        'weekend_duration': Decimal('5.5'),
        'stat_start': time(9, 0, 0),
        'stat_duration': Decimal('9.9'),
    },
    'email': {
        'server': 'https://127.0.0.1/',
        'from_name': 'App Owner',
        'from_email': 'app@email.com',
        'unsubscribe_link': 'https://127.0.0.1/unsubscribe/',
        'owner_name': 'App Owner',
        'owner_email': 'owner@email.com',
    },
    'debug': {
        'email_console': True,
    },
}

USER = {
    'id': 1,
    'sb_user': 10,
    'name': 'Test User',
    'calendar_name': 'SecretCalendar',
}

# Mock old and new schedules with additions, changes, deletions,
# missing shift codes, and null shift codes
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

# User-specific shift codes (for mocking API request)
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

# Stat holidays (for mocking API request)
STAT_HOLIDAYS = [
    datetime(2018, 1, 1), datetime(2018, 2, 19), datetime(2018, 3, 30),
    datetime(2018, 5, 21), datetime(2018, 7, 1), datetime(2018, 8, 6),
    datetime(2018, 9, 3), datetime(2018, 10, 8), datetime(2018, 11, 11),
    datetime(2018, 12, 25),
]
