"""Tests for the retrieve module."""
# pylint: disable=protected-access
import os
from pathlib import Path
from unittest.mock import patch

from modules import retrieve


def test__get_most_recent_file__one_file():
    """Tests expected handling when one file available."""
    # Get reference to test file directory
    current_dir = Path(__file__).parent.absolute()
    directory = Path(current_dir, 'files')

    # Setup glob statement
    glob_statement = 'example_*.xls'

    file = retrieve._get_most_recent_file(directory, glob_statement)

    assert 'example_xls.xls' in str(file)


def test__get_most_recent_file__multiple_files():
    """Tests expected handling when multiple files available."""
    # Get reference to test file directory
    current_dir = Path(__file__).parent.absolute()
    directory = Path(current_dir, 'files')

    # Get reference to test files
    file_1 = directory / 'example_xlsx 1.xlsx'
    file_2 = directory / 'example_xlsx 2.xlsx'
    file_3 = directory / 'example_xlsx 3.xlsx'

    # Manipulate modified times
    os.utime(file_1, (10, 100))
    os.utime(file_2, (20, 200))
    os.utime(file_3, (15, 150))

    # Setup glob statement
    glob_statement = 'example_xlsx*.xlsx'

    file = retrieve._get_most_recent_file(directory, glob_statement)

    assert 'example_xlsx 2.xlsx' in str(file)


def test__get_most_recent_file__no_files():
    """Tests expected handling when no files available."""
    # Get reference to test file directory
    current_dir = Path(__file__).parent.absolute()
    directory = Path(current_dir, 'files')

    # Setup glob statement
    glob_statement = 'incorrect_example*.xlsx'

    try:
        retrieve._get_most_recent_file(directory, glob_statement)
    except FileNotFoundError as error:
        assert 'Unable to find file for glob: "incorrect_example*.xlsx".' in str(error)
    else:
        assert False


@patch('modules.retrieve._get_most_recent_file', lambda x, y: f'{x}_{y}')
def test__retrieve_schedule_file_paths():
    """Tests for exected processing and results in function."""
    config = {
        'excel': {
            'schedule_loc': 'A',
            'ext_a': 'B',
            'ext_p': 'C',
            'ext_t': 'D',
        }
    }

    details = retrieve.retrieve_schedule_file_paths(config)

    assert isinstance(details, dict)
    assert 'a' in details
    assert 'A_assistant_*.B' in str(details['a'])
    assert 'p' in details
    assert 'A_pharmacist_*.C' in str(details['p'])
    assert 't' in details
    assert 'A_technician_*.D' in str(details['t'])
