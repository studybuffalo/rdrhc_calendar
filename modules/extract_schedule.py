"""Functions to extract schedule details from Excel file."""

from datetime import datetime
import logging
import re

import openpyxl
import xlrd

from modules.custom_exceptions import ScheduleError


LOG = logging.getLogger(__name__)

def return_column_index(sheet, user, name_row, col_start, col_end):
    """Determines the Excel column containing the provided user"""
    LOG.debug('Looking for user index in Excel schedule')

    index = None
    role = user['role']

    for i in range(col_start, col_end):
        try:
            if role == 'p':
                cell_name = str(
                    sheet.cell(row=name_row, column=i).value
                ).strip()
            elif role in ('a', 't'):
                cell_name = str(sheet.cell(name_row, i).value).strip()

            if cell_name.upper() == user['schedule_name'].upper():
                index = i
                break
        except IndexError:
            # Expected error if loop exceeds Excel content
            break

    if index:
        return index

    # No index found - raise error
    raise ScheduleError('Unable to find index for {} (role = {})'.format(
        user['name'], role
    ))

def format_shift_details(shift_codes, date, comment, role):
    """Splits up multiple shift codes and assigns details."""
    shifts = []

    if all([
            shift_codes != '',
            re.match(r'\s+$', shift_codes) is None,
            date != ''
    ]):
        # Split each shift code on spaces or slashes
        shift_codes = re.split(r'(?:\s|/)+', shift_codes.strip())

        # Remove any duplicate shift codes
        shift_codes = list(set(shift_codes))

        for code in shift_codes:
            if code != '' and re.match(r'\s+$', code) is None:
                shifts.append({
                    'shift_code': code,
                    'start_date': date,
                    'comment': comment,
                })

                # Add pharmacist 'X' shifts
                if role == 'p' and code[-1:].upper() == 'X':
                    shifts.append({
                        'shift_code': 'X',
                        'start_date': date,
                        'comment': '',
                    })
    return shifts

def extract_raw_schedule(
        book, sheet, user, index, row_start, row_end, date_col
):
    """Returns a list of schedule_shift objects."""

    # Extracts schedule details from spreadsheet
    LOG.info('Extracting schedule details for %s', user['name'])
    role = user['role']

    # Generate comment map if this is an xls file
    if role in ('a', 't'):
        comment_map = sheet.cell_note_map

    # Cycle through each row and extract shift date, code, and comments
    LOG.debug('Cycling through rows of excel schedule')

    shifts = []

    for i in range(row_start, row_end):
        # Extract date
        try:
            if role == 'p':
                date = sheet.cell(row=i, column=date_col).value.date()
            elif role in ('a', 't'):
                date = xlrd.xldate_as_tuple(
                    sheet.cell(i, date_col).value, book.datemode
                )
                date = datetime(*date).date()
        except AttributeError:
            # Expected error when there is no date value
            date = ''
        except IndexError:
            # Expected error when there is no date value
            date = ''
        except TypeError:
            # Expected error when there is no date value
            date = ''

        # Extract shift code
        try:
            if role == 'p':
                shift_codes = sheet.cell(row=i, column=index).value.upper()
            elif role  in ('a', 't'):
                shift_codes = sheet.cell(i, index).value.upper()
        except AttributeError:
            # Expected error when there is no shift code value
            shift_codes = ''
        except IndexError:
            # Expect error when there is no shift code value
            shift_codes = ''

        # Extract cell comments
        comment = ''

        try:
            if role == 'p':
                comment = sheet.cell(row=i, column=index).comment
            elif role in ('a', 't'):
                comment = comment_map[i, index].text

            if comment is None:
                # Replaces 'None' comments as empty string for calendar use
                comment = ''
            else:
                comment = str(comment)
                comment = comment.replace('\n', ' ')
                comment = comment.strip()
        except KeyError:
            # Expected error when there is no comment
            comment = ''

        # Format and add shifts to the master list
        shifts.extend(format_shift_details(shift_codes, date, comment, role))

    # Sort the shifts by date
    # Note: should occur automatically, but just in case
    LOG.debug('Sorting shifts by date')

    sorted_shifts = sorted(shifts, key=lambda s: s['start_date'])

    return sorted_shifts

def generate_raw_schedule(app_config, excel_files, user):
    """Returns a list of shift details for the specified user."""

    # Setup the required Excel details
    role = user['role']
    file_loc = excel_files[role]
    config = app_config['{}_excel'.format(role).lower()]

    # Open the proper Excel worksheet
    LOG.debug('Opening the Excel worksheet')
    excel_sheet = None

    raw_schedule = []

    for sheet_name in config['sheet']:
        if role == 'p':
            try:
                excel_book = openpyxl.load_workbook(file_loc)
                excel_sheet = excel_book[sheet_name]
            except FileNotFoundError:
                raise ScheduleError(
                    'Cannot open .xlsx file for user role = {}: {}'.format(
                        role, file_loc
                    )
                )
        elif role in ('a', 't'):
            try:
                excel_book = xlrd.open_workbook(file_loc)
                excel_sheet = excel_book.sheet_by_name(sheet_name)
            except FileNotFoundError:
                raise ScheduleError(
                    'Cannot open .xls file for user role = {}: {}'.format(
                        role, file_loc
                    )
                )

        # Find column index for this user
        try:
            user_index = return_column_index(
                excel_sheet,
                user,
                config['name_row'],
                config['col_start'],
                config['col_end'],
            )
        except ScheduleError:
            LOG.info(
                'Unable to find user index for %s (role = %s) on worksheet %s',
                user['schedule_name'],
                user['role'],
                sheet_name,
            )
            user_index = None

        if user_index:
            raw_schedule += extract_raw_schedule(
                excel_book, excel_sheet, user, user_index,
                config['row_start'], config['row_end'], config['date_col']
            )

        if not raw_schedule:
            LOG.warning(
                'No shifts found for user %s (role = %s)',
                user['schedule_name'],
                user['role'],
            )

    return raw_schedule
