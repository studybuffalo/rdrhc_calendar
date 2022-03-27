"""Unit tests for the calendar module."""
from datetime import datetime

from modules import calendar


def test_generate_full_day_dt_start_end():
    """Tests that proper values are generated for full day event."""
    shift = {
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
    }

    event = calendar.generate_full_day_dt_start_end(shift)

    assert event['dt_start'] == 'DTSTART;VALUE=DATE:20180101'
    assert event['dt_end'] == 'DTEND;VALUE=DATE:20180102'
    assert event['start_date'] == '20180101'
    assert event['start_time'] == '000000'


def test_generate_dt_start_end():
    """Tests that proper values are generated for a calendar event."""
    shift = {
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2018, 1, 1, 17, 0, 0),
    }

    event = calendar.generate_dt_start_end(shift)

    assert event['dt_start'] == 'DTSTART;TZID=America/Edmonton:20180101T090000'
    assert event['dt_end'] == 'DTEND;TZID=America/Edmonton:20180101T170000'
    assert event['start_date'] == '20180101'
    assert event['start_time'] == '090000'


def test_generate_alarm_0_minutes():
    """Tests that alarm event is created with 0 minute reminder."""
    lines = calendar.generate_alarm(0, 'A1')

    assert lines[1] == 'TRIGGER:-PT0M'
    assert lines[3] == 'DESCRIPTION:A1 shift starting now'


def test_generate_alarm_1_minute():
    """Tests that alarm event is created with 1 minute reminder."""
    lines = calendar.generate_alarm(1, 'A1')

    assert lines[1] == 'TRIGGER:-PT1M'
    assert lines[3] == 'DESCRIPTION:A1 shift starting in 1 minute'


def test_generate_alarm_multiple_minutes():
    """Tests that alarm event is created with > 1 minute reminder."""
    lines = calendar.generate_alarm(2, 'A1')

    assert lines[1] == 'TRIGGER:-PT2M'
    assert lines[3] == 'DESCRIPTION:A1 shift starting in 2 minutes'


def test_generate_calendar_event():
    """Tests proper event generation for calendar event."""
    shift = {
        'shift_code': 'A1',
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2018, 1, 1, 17, 0, 0),
        'comment': '',
    }
    user = {
        'full_day': False,
        'reminder': None,
    }
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    index = 0

    lines = calendar.generate_calendar_event(shift, user, dt_stamp, index)

    assert lines[0] == 'BEGIN:VEVENT'
    assert lines[1] == 'DTSTART;TZID=America/Edmonton:20180101T090000'
    assert lines[2] == 'DTEND;TZID=America/Edmonton:20180101T170000'
    assert lines[3] == f'DTSTAMP:{dt_stamp}'
    assert lines[4] == 'UID:20180101T090000@studybuffalo.com-0'
    assert lines[6] == 'DESCRIPTION:'
    assert lines[-1] == 'END:VEVENT'


def test_generate_calendar_event_with_comment():
    """Tests proper event generation for calendar event."""
    shift = {
        'shift_code': 'A1',
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2018, 1, 1, 17, 0, 0),
        'comment': 'TEST',
    }
    user = {
        'full_day': False,
        'reminder': None,
    }
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    index = 0

    lines = calendar.generate_calendar_event(shift, user, dt_stamp, index)

    assert lines[6] == 'DESCRIPTION:TEST'


def test_generate_full_day_calendar_event():
    """Tests proper event generation for full day calendar event."""
    shift = {
        'shift_code': 'A1',
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2018, 1, 1, 17, 0, 0),
        'comment': '',
    }
    user = {
        'full_day': True,
        'reminder': None,
    }
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    index = 0

    lines = calendar.generate_calendar_event(shift, user, dt_stamp, index)

    assert lines[1] == 'DTSTART;VALUE=DATE:20180101'
    assert lines[2] == 'DTEND;VALUE=DATE:20180102'


def test_generate_calendar_event_with_reminder():
    """Tests proper event generation for event with reminder."""
    shift = {
        'shift_code': 'A1',
        'start_datetime': datetime(2018, 1, 1, 9, 0, 0),
        'end_datetime': datetime(2018, 1, 1, 17, 0, 0),
        'comment': '',
    }
    user = {
        'full_day': False,
        'reminder': 0,
    }
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    index = 0

    lines = calendar.generate_calendar_event(shift, user, dt_stamp, index)

    assert lines[14] == 'TRIGGER:-PT0M'
    assert lines[16] == 'DESCRIPTION:A1 shift starting now'


def test_fold_calendar_lines_10_characters():
    """Tests handling of line under 75 characters."""
    lines = [
        'a' * 10,
    ]
    folded_lines = calendar.fold_calendar_lines(lines)

    assert len(folded_lines) == 1
    assert folded_lines[0] == f'{"a" * 10}\n'


def test_fold_calendar_lines_80_characters():
    """Tests handling of line between 75 and 150 characters."""
    lines = [
        'a' * 80,
    ]
    folded_lines = calendar.fold_calendar_lines(lines)

    assert len(folded_lines) == 2
    assert folded_lines[0] == f'{"a" * 75}\n'
    assert folded_lines[1] == f' {"a" * 5}\n'


def test_fold_calendar_lines_160_characters():
    """Tests handling of line between over 150 characters."""
    lines = [
        'a' * 160,
    ]
    folded_lines = calendar.fold_calendar_lines(lines)

    assert len(folded_lines) == 3
    assert folded_lines[0] == f'{"a" * 75}\n'
    assert folded_lines[1] == f' {"a" * 74}\n'
    assert folded_lines[2] == f' {"a" * 11}\n'
