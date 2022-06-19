"""Unit tests for extract schedule module."""
# pylint: disable=too-few-public-methods, no-self-use, protected-access
import os
from datetime import date
from unittest.mock import patch

from unipath import Path
import openpyxl
import xlrd

from modules import extract_schedule
from modules.custom_exceptions import ScheduleError


def mock_open_worksheet(config, file_loc, sheet_name, role):
    """Mock of the _open_worksheet function."""
    book = {'config': config, 'file_loc': file_loc, 'role': role, 'sheet_name': sheet_name, 'test': 'book'}
    sheet = {'config': config, 'file_loc': file_loc, 'role': role, 'sheet_name': sheet_name, 'test': 'sheet'}

    return book, sheet


def mock_return_column_index(sheet, user, cfg):  # pylint: disable=unused-argument
    """Mock of the return_column_index function."""
    return 1


def mock_extract_raw_schedule(book, sheet, user, index, cfg):  # pylint: disable=unused-argument
    """Mock of the extract_raw_schedule function."""
    return [1]


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


def test__open_worksheet__xlsx__correct_worksheet():
    """Tests xlsx extraction when correct worksheet provided."""
    config = {'ext': 'xlsx'}
    current_dir = Path(os.path.abspath(__file__)).parent
    file_loc = Path(current_dir, 'files/example_xlsx 1.xlsx')

    excel_book, excel_sheet = extract_schedule._open_worksheet(config, file_loc, 'Current Schedule', 'a')

    # Confirm proper types returned
    assert isinstance(excel_book, openpyxl.workbook.workbook.Workbook)
    assert isinstance(excel_sheet, openpyxl.worksheet.worksheet.Worksheet)

    # Confirm names of returned content
    assert excel_sheet.title == 'Current Schedule'


def test__open_worksheet__xlsx__incorrect_worksheet():
    """Tests xlsx extraction when incorrect worksheet is provided."""
    config = {'ext': 'xlsx'}
    current_dir = Path(os.path.abspath(__file__)).parent
    file_loc = Path(current_dir, 'files/example_xlsx.xlsx')

    try:
        extract_schedule._open_worksheet(config, file_loc, 'ERROR', 'a')
    except ScheduleError as error:
        assert 'Cannot open .xlsx file for user role = a: ' in str(error)
    else:
        assert False


def test__open_worksheet__xls__correct_worksheet():
    """Tests xls extraction when correct worksheet is provided."""
    config = {'ext': 'xls'}
    current_dir = Path(os.path.abspath(__file__)).parent
    file_loc = Path(current_dir, 'files/example_xls.xls')

    excel_book, excel_sheet = extract_schedule._open_worksheet(config, file_loc, 'Current Schedule', 'a')

    # Confirm proper types returned
    assert isinstance(excel_book, xlrd.book.Book)
    assert isinstance(excel_sheet, xlrd.sheet.Sheet)

    # Confirm names of returned content
    assert excel_sheet.name == 'Current Schedule'


def test__open_worksheet__xls__no_worksheet():
    """Tests xls extraction when incorrect worksheet is provided."""
    config = {'ext': 'xls'}
    current_dir = Path(os.path.abspath(__file__)).parent
    file_loc = Path(current_dir, 'files/example_xls.xls')

    try:
        extract_schedule._open_worksheet(config, file_loc, 'ERROR', 'a')
    except ScheduleError as error:
        assert 'Cannot open .xls file for user role = a: ' in str(error)
    else:
        assert False


@patch(
    'modules.extract_schedule._open_worksheet',
    mock_open_worksheet
)
@patch(
    'modules.extract_schedule.return_column_index',
    mock_return_column_index
)
@patch(
    'modules.extract_schedule.extract_raw_schedule',
    mock_extract_raw_schedule
)
def test_generate_raw_schedule_pharmacist_single():
    """Tests function returns list for pharmacist with single worksheet."""
    app_config = {
        'p_excel': {
            'sheet': ['test1'],
            'name_row': 0,
            'col_start': 1,
            'col_end': 100,
            'row_start': 1,
            'row_end': 100,
            'date_col': 0,
            'ext': 'xlsx',
        }
    }
    excel_files = {
        'p': '/fake/path'
    }
    user = {
        'role': 'p',
    }

    schedule = extract_schedule.generate_raw_schedule(
        app_config, excel_files, user
    )

    assert len(schedule) == 1


@patch(
    'modules.extract_schedule._open_worksheet',
    mock_open_worksheet
)
@patch(
    'modules.extract_schedule.return_column_index',
    mock_return_column_index
)
@patch(
    'modules.extract_schedule.extract_raw_schedule',
    mock_extract_raw_schedule
)
def test_generate_raw_schedule_technician_single():
    """Tests function returns list for technician with single worksheet."""
    app_config = {
        't_excel': {
            'sheet': ['test1'],
            'name_row': 0,
            'col_start': 1,
            'col_end': 100,
            'row_start': 1,
            'row_end': 100,
            'date_col': 0,
            'ext': 'xls',
        }
    }
    excel_files = {
        't': '/fake/path'
    }
    user = {
        'role': 't',
    }

    schedule = extract_schedule.generate_raw_schedule(
        app_config, excel_files, user
    )

    assert len(schedule) == 1


@patch(
    'modules.extract_schedule._open_worksheet',
    mock_open_worksheet
)
@patch(
    'modules.extract_schedule.return_column_index',
    mock_return_column_index
)
@patch(
    'modules.extract_schedule.extract_raw_schedule',
    mock_extract_raw_schedule
)
def test_generate_raw_schedule_pharmacist_multiple():
    """Tests function returns list for pharmacist with multiple worksheets."""
    app_config = {
        'p_excel': {
            'sheet': ['test1', 'test2'],
            'name_row': 0,
            'col_start': 1,
            'col_end': 100,
            'row_start': 1,
            'row_end': 100,
            'date_col': 0,
            'ext': 'xlsx',
        }
    }
    excel_files = {
        'p': '/fake/path'
    }
    user = {
        'role': 'p',
    }

    schedule = extract_schedule.generate_raw_schedule(
        app_config, excel_files, user
    )

    assert len(schedule) == 2


@patch(
    'modules.extract_schedule._open_worksheet',
    mock_open_worksheet
)
@patch(
    'modules.extract_schedule.return_column_index',
    mock_return_column_index
)
@patch(
    'modules.extract_schedule.extract_raw_schedule',
    mock_extract_raw_schedule
)
def test_generate_raw_schedule_technician_multiple():
    """Tests function returns list for technician with multiple worksheets."""
    app_config = {
        't_excel': {
            'sheet': ['test1', 'test2'],
            'name_row': 0,
            'col_start': 1,
            'col_end': 100,
            'row_start': 1,
            'row_end': 100,
            'date_col': 0,
            'ext': 'xls',
        }
    }
    excel_files = {
        't': '/fake/path'
    }
    user = {
        'role': 't',
        'schedule_name': 'test',
    }

    schedule = extract_schedule.generate_raw_schedule(
        app_config, excel_files, user
    )

    print(schedule)
    assert len(schedule) == 2
