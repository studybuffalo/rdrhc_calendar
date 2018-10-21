"""Unit tests for extract schedule module."""
from datetime import date

from modules import extract_schedule


def test_format_shift_details_one_code():
    """Tests format_shift_details returns 1 shift with details."""
    shifts = extract_schedule.format_shift_details(
        'A1', date(2018, 1, 1), '', 'p'
    )

    assert len(shifts) == 1
    assert shifts[0]['shift_code'] == 'A1'
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == ''

def test_format_shift_details_code_with_slash():
    """Tests format_shift_details returns two shifts with details."""
    shifts = extract_schedule.format_shift_details(
        'A1/A2', date(2018, 1, 1), 'TEST', 'p'
    )

    assert len(shifts) == 2
    assert shifts[0]['shift_code'] in ('A1', 'A2')
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == 'TEST'
    assert shifts[1]['shift_code'] in ('A1', 'A2')
    assert shifts[1]['start_date'] == date(2018, 1, 1)
    assert shifts[1]['comment'] == 'TEST'
    assert shifts[0]['shift_code'] != shifts[1]['shift_code']

def test_format_shift_details_code_with_space():
    """Tests format_shift_details returns two shifts with details."""
    shifts = extract_schedule.format_shift_details(
        'A1 A2', date(2018, 1, 1), '', 'p'
    )

    assert len(shifts) == 2
    assert shifts[0]['shift_code'] in ('A1', 'A2')
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == ''
    assert shifts[1]['shift_code'] in ('A1', 'A2')
    assert shifts[1]['start_date'] == date(2018, 1, 1)
    assert shifts[1]['comment'] == ''
    assert shifts[0]['shift_code'] != shifts[1]['shift_code']

def test_format_shift_details_code_with_trailing_spaces():
    """Tests format_shift_details returns two shifts with details."""
    shifts = extract_schedule.format_shift_details(
        'A1  ', date(2018, 1, 1), '', 'p'
    )

    assert len(shifts) == 1
    assert shifts[0]['shift_code'] == 'A1'
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == ''

def test_format_shift_details_code_with_leading_spaces():
    """Tests format_shift_details returns two shifts with details."""
    shifts = extract_schedule.format_shift_details(
        '  A1', date(2018, 1, 1), '', 'p'
    )

    assert len(shifts) == 1
    assert shifts[0]['shift_code'] == 'A1'
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == ''

def test_format_shift_details_x_shift():
    """Tests format_shift_details returns X shift."""
    shifts = extract_schedule.format_shift_details(
        'A1X', date(2018, 1, 1), 'TEST', 'p'
    )

    assert len(shifts) == 2
    assert shifts[0]['shift_code'] == 'A1X'
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == 'TEST'
    assert shifts[1]['shift_code'] == 'X'
    assert shifts[1]['start_date'] == date(2018, 1, 1)
    assert shifts[1]['comment'] == ''

def test_format_shift_details_x_shift_non_pharmacist():
    """Tests format_shift_details ignores X shift."""
    shifts = extract_schedule.format_shift_details(
        'A1X', date(2018, 1, 1), 'TEST', 't'
    )

    assert len(shifts) == 1
    assert shifts[0]['shift_code'] == 'A1X'
    assert shifts[0]['start_date'] == date(2018, 1, 1)
    assert shifts[0]['comment'] == 'TEST'
