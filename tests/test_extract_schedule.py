"""Unit tests for extract schedule module."""
from datetime import date
from unittest.mock import patch

from modules import extract_schedule


def mock_openpyxl_load_workbook(file_loc): # pylint: disable=unused-argument
    """Mock of the openpyxl load_workbook function."""
    return {
        'test1': None,
        'test2': None,
    }

def mock_xlrd_open_workbook(file_loc): # pylint: disable=unused-argument
    """Mock of the xlrd open_workbook function."""
    class MockOpenWorkbook():
        """Mock of the open_workbook function object."""
        def __init__(self, file_loc):
            self.file_loc = file_loc

        def sheet_by_name(sheet_name): # pylint: disable=unused-argument, no-self-argument
            """Mocking the sheet_by_name method."""
            return None

    return MockOpenWorkbook

def mock_return_column_index(sheet, user, cfg): # pylint: disable=unused-argument
    """Mock of the return_column_index function."""
    return 1

def mock_extract_raw_schedule(book, sheet, user, index, cfg): # pylint: disable=unused-argument
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

@patch(
    'modules.extract_schedule.openpyxl.load_workbook',
    mock_openpyxl_load_workbook
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
    'modules.extract_schedule.xlrd.open_workbook',
    mock_xlrd_open_workbook
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
    'modules.extract_schedule.openpyxl.load_workbook',
    mock_openpyxl_load_workbook
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
    'modules.extract_schedule.xlrd.open_workbook',
    mock_xlrd_open_workbook
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

    assert len(schedule) == 2
