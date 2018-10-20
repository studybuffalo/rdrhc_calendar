"""Functions to generate .ics calendar from user schedule."""

from datetime import datetime, timedelta
import logging

from unipath import Path


LOG = logging.getLogger(__name__)

def generate_full_day_dt_start_end(shift):
    """Generates start/end datetime strings for full day event."""
    start_date = shift['start_datetime'].strftime('%Y%m%d')
    start_time = '000000'
    end_date = shift['start_datetime'].date() + timedelta(days=1)
    end_date = end_date.strftime('%Y%m%d')

    dt_start = 'DTSTART;VALUE=DATE:{}'.format(start_date)
    dt_end = 'DTEND;VALUE=DATE:{}'.format(end_date)

    return {
        'dt_start': dt_start,
        'dt_end': dt_end,
        'start_date': start_date,
        'start_time':start_time,
    }

def generate_dt_start_end(shift):
    """Generates start/end datetime strings for shift."""
    start_date = shift['start_datetime'].strftime('%Y%m%d')
    start_time = str(shift['start_datetime'].time()).replace(':', '').zfill(6)
    end_date = shift['end_datetime'].strftime('%Y%m%d')
    end_time = str(shift['end_datetime'].time()).replace(':', '').zfill(6)

    dt_start = 'DTSTART;TZID=America/Edmonton:{}T{}'.format(
        start_date, start_time
    )
    dt_end = 'DTEND;TZID=America/Edmonton:{}T{}'.format(
        end_date, end_time
    )

    return {
        'dt_start': dt_start,
        'dt_end': dt_end,
        'start_date': start_date,
        'start_time':start_time,
    }

def generate_alarm(reminder_time, shift_code):
    """Generates VALARM text for calendar reminder."""
    lines = []

    if reminder_time == 0:
        alarm_description = (
            'DESCRIPTION:{} shift starting now'
        ).format(shift_code)
    elif reminder_time == 1:
        alarm_description = (
            'DESCRIPTION:{} shift starting in {} minute'
        ).format(shift_code, reminder_time)
    else:
        alarm_description = (
            'DESCRIPTION:{} shift starting in {} minutes'
        ).format(shift_code, reminder_time)

    lines.append('BEGIN:VALARM')
    lines.append('TRIGGER:-PT{}M'.format(reminder_time))
    lines.append('ACTION:DISPLAY')
    lines.append(alarm_description)
    lines.append('END:VALARM')

    return lines

def generate_calendar_event(shift, user, dt_stamp, i):
    """Generates a .ics calendar event from a shift.

    Arguments:
        shift (dict): A dictionary of one shift's details.
        user (dict): A dictionary of user details.
        dt_stamp (str): A string timestamp of the .ics creation date.
        i (int): an incrementing count to generate a unique ID.
    """
    lines = []

    lines.append('BEGIN:VEVENT')

    # Generate the event datetime starts and ends
    if user['full_day']:
        event_details = generate_full_day_dt_start_end(shift)
        lines.append(event_details['dt_start'])
        lines.append(event_details['dt_end'])
    else:
        event_details = generate_dt_start_end(shift)
        lines.append(event_details['dt_start'])
        lines.append(event_details['dt_end'])

    lines.append('DTSTAMP:{}'.format(dt_stamp))
    lines.append('UID:{}T{}@studybuffalo.com-{}'.format(
        event_details['start_date'], event_details['start_time'], i
    ))
    lines.append('CREATED:{}'.format(dt_stamp))
    lines.append('DESCRIPTION:{}'.format(shift['comment']))
    lines.append('LAST-MODIFIED:{}'.format(dt_stamp))
    lines.append('LOCATION:Red Deer Regional Hospital Centre')
    lines.append('SEQUENCE:0')
    lines.append('STATUS:CONFIRMED')
    lines.append('SUMMARY:{} Shift'.format(shift['shift_code']))
    lines.append('TRANSP:TRANSPARENT')

    if user['reminder'] >= 0:
        lines.extend(generate_alarm(user['reminder'], shift['shift_code']))

    lines.append('END:VEVENT')

    return lines

def fold_calendar_lines(lines):
    """Folds all lines so that max length is 75."""
    LOG.debug('Folding lines greater than 75 characters long')

    folded_lines = []

    for line in lines:
        if len(line) > 75:

            # Create line with first 75 characters
            new_line = line[0:75]
            folded_lines.append(new_line + '\n')

            # Go through remainder and fold them
            line = line[75:]
            length = len(line)

            while length > 75:
                # Add folded line
                new_line = line[0:75]
                folded_lines.append(' ' + new_line + '\n')

                # Generate new line and length
                line = line[75:]
                length = len(line)

            # Add remainder
            folded_lines.append(' ' + line + '\n')
        else:
            folded_lines.append(line + '\n')

    return folded_lines

def save_calendar(lines, calendar_name, calendar_location):
    """Saves the provided lines as an .ics calendar file."""
    calendar_title = '{}.ics'.format(calendar_name)
    file_path = Path(calendar_location, calendar_title)

    LOG.debug('Saving calendar to %s', file_path)

    with open(file_path, 'w') as ics:
        for line in lines:
            ics.write(line)

def generate_calendar(user, schedule, calendar_location):
    """Generates an .ics file from the extracted user schedule"""
    # TODO: Combine shifts that have same start and end datetimes
    LOG.info('Generating .ics calendar for %s', user['name'])

    # Generate initial calendar information
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    lines = [
        'BEGIN:VCALENDAR',
        'PRODID:-//StudyBuffalo.com//RDRHC Calendar//EN',
        'VERSION:2.0',
        'CALSCALE:GREGORIAN',
        'X-WR-CALNAME:Work Schedule',
        'X-WR-TIMEZONE:America/Edmonton',
        'BEGIN:VTIMEZONE',
        'TZID:America/Edmonton',
        'X-LIC-LOCATION:America/Edmonton',
        'BEGIN:DAYLIGHT',
        'TZOFFSETFROM:-0700',
        'TZOFFSETTO:-0600',
        'TZNAME:MDT',
        'DTSTART:19700308T020000',
        'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU',
        'END:DAYLIGHT',
        'BEGIN:STANDARD',
        'TZOFFSETFROM:-0600',
        'TZOFFSETTO:-0700',
        'TZNAME:MST',
        'DTSTART:19701101T020000',
        'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU',
        'END:STANDARD',
        'END:VTIMEZONE',
    ]

    for index, shift in enumerate(schedule):
        lines.extend(generate_calendar_event(shift, user, dt_stamp, index))

    # End calendar file
    lines.append('END:VCALENDAR')

    # Fold lines to meet .ics standard (max length of 75 characters)
    folded_lines = fold_calendar_lines(lines)

    # Save the calendar file
    save_calendar(folded_lines, user['calendar_name'], calendar_location)
