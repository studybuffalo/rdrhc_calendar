"""Functions to generate .ics calendar from user schedule."""

from datetime import datetime, timedelta
import logging

from unipath import Path


LOG = logging.getLogger(__name__)

def generate_calendar(user, schedule, cal_loc):
    """Generates an .ics file from the extracted user schedule"""
    # TODO: Better handle general uncaught exceptions
    # TODO: Combine shifts that have same start and end datetimes

    LOG.info('Generating .ics calendar for %s', user['name'])

    # Generate initial calendar information
    lines = []

    lines.append('BEGIN:VCALENDAR')
    lines.append('PRODID:-//StudyBuffalo.com//RDRHC Calendar//EN')
    lines.append('VERSION:2.0')
    lines.append('CALSCALE:GREGORIAN')
    lines.append('X-WR-CALNAME:Work Schedule')
    lines.append('X-WR-TIMEZONE:America/Edmonton')
    lines.append('BEGIN:VTIMEZONE')
    lines.append('TZID:America/Edmonton')
    lines.append('X-LIC-LOCATION:America/Edmonton')
    lines.append('BEGIN:DAYLIGHT')
    lines.append('TZOFFSETFROM:-0700')
    lines.append('TZOFFSETTO:-0600')
    lines.append('TZNAME:MDT')
    lines.append('DTSTART:19700308T020000')
    lines.append('RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU')
    lines.append('END:DAYLIGHT')
    lines.append('BEGIN:STANDARD')
    lines.append('TZOFFSETFROM:-0600')
    lines.append('TZOFFSETTO:-0700')
    lines.append('TZNAME:MST')
    lines.append('DTSTART:19701101T020000')
    lines.append('RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU')
    lines.append('END:STANDARD')
    lines.append('END:VTIMEZONE')

    # Cycle through schedule and generate schedule events
    dt_stamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    i = 0

    LOG.debug('Cycling through shifts for %s', user['name'])

    for shift in schedule:
        start_date = shift['start_datetime'].strftime('%Y%m%d')
        comment = shift['comment']

        # try:
        #     start_date = shift.start_datetime.strftime('%Y%m%d')
        #     comment = shift.comment
        # except Exception:
        #     LOG.error(
        #         'Unable to extract shift data to generate calendar',
        #         exc_info=True
        #     )
        #     start_date = '20010101'
        #     comment = ''

        lines.append('BEGIN:VEVENT')

        if user['full_day'] is False:
            start_time = str(
                shift['start_datetime'].time()
            ).replace(':', '').zfill(6)
            end_date = shift['end_datetime'].strftime('%Y%m%d')
            end_time = str(shift['end_datetime'].time()).replace(':', '').zfill(6)

            # try:
            #     start_time = str(
            #           shift.start_datetime.time()
            #     ).replace(':', '').zfill(6)
            #     end_date = shift.end_datetime.strftime('%Y%m%d')
            #     end_time = str(
            #         shift.end_datetime.time()
            #     ).replace(':', '').zfill(6)
            # except Exception:
            #     LOG.error(
            #         'Unable to generate shift times for calendar',
            #         exc_info=True
            #     )
            #     start_time = '000000'
            #     end_date = '20010102'
            #     end_time = '000000'

            lines.append('DTSTART;TZID=America/Edmonton:{}T{}'.format(
                start_date, start_time
            ))
            lines.append('DTEND;TZID=America/Edmonton:{}T{}'.format(
                end_date, end_time
            ))
        elif user.full_day:
            start_time = '000000'

            end_date = shift['start_datetime'].date() + timedelta(days=1)
            end_date = end_date.strftime('%Y%m%d')

            # try:
            #     end_date = shift.start_datetime.date() + timedelta(days=1)
            #     end_date = end_date.strftime('%Y%m%d')
            # except Exception:
            #     LOG.error(
            #         'Unable to generate full day shift for schedule',
            #         exc_info=True
            #     )
            #     end_date = '20010102'
            #     end_time = '000000'

            lines.append('DTSTART;VALUE=DATE:{}'.format(start_date))
            lines.append('DTEND;VALUE=DATE:{}'.format(end_date))

        lines.append('DTSTAMP:{}'.format(dt_stamp))
        lines.append('UID:{}T{}@studybuffalo.com-{}'.format(
            start_date, start_time, i
        ))
        lines.append('CREATED:{}'.format(dt_stamp))
        lines.append('DESCRIPTION:{}'.format(comment))
        lines.append('LAST-MODIFIED:{}'.format(dt_stamp))
        lines.append('LOCATION:Red Deer Regional Hospital Centre')
        lines.append('SEQUENCE:0')
        lines.append('STATUS:CONFIRMED')
        lines.append('SUMMARY:{} Shift'.format(shift['shift_code']))
        lines.append('TRANSP:TRANSPARENT')

        if user['reminder'] is not None:
            # Set the description text
            if user.reminder == 0:
                alarm_description = (
                    'DESCRIPTION:{} shift starting now'
                ).format(shift['shift_code'])
            elif user.reminder == 1:
                alarm_description = (
                    'DESCRIPTION:{} shift starting in {} minute'
                ).format(shift['shift_code'], user['reminder'])
            else:
                alarm_description = (
                    'DESCRIPTION:{} shift starting in {} minutes'
                ).format(shift['shift_code'], user['reminder'])

            lines.append('BEGIN:VALARM')
            lines.append('TRIGGER:-PT{}M'.format(user['reminder']))
            lines.append('ACTION:DISPLAY')
            lines.append(alarm_description)
            lines.append('END:VALARM')

            # try:
            #     # Set the description text
            #     if user.reminder == 0:
            #         alarm_description = (
            #             'DESCRIPTION:{} shift starting now'
            #         ).format(shift.shift_code)
            #     elif user.reminder == 1:
            #         alarm_description = (
            #             'DESCRIPTION:{} shift starting in {} minute'
            #         ).format(shift.shift_code, user.reminder)
            #     else:
            #         alarm_description = (
            #             'DESCRIPTION:{} shift starting in {} minutes'
            #         ).format(shift.shift_code, user.reminder)

            #     lines.append('BEGIN:VALARM')
            #     lines.append('TRIGGER:-PT{}M'.format(user.reminder))
            #     lines.append('ACTION:DISPLAY')
            #     lines.append(alarm_description)
            #     lines.append('END:VALARM')
            # except Exception:
            #     LOG.error('Unable to set reminder for shift', exc_info=True)

            #     lines.append('BEGIN:VALARM')
            #     lines.append('TRIGGER:-PT30M')
            #     lines.append('ACTION:DISPLAY')
            #     lines.append('DESCRIPTION:Shift starts in 30 minutes')
            #     lines.append('END:VALARM')
        lines.append('END:VEVENT')

        i = i + 1

    # End calendar file
    lines.append('END:VCALENDAR')

    # Fold any lines > 75 characters long
    LOG.debug('Folding lines greater than 75 characters long')

    folded = []

    for line in lines:
        if len(line) > 75:

            # Create line with first 75 characters
            new_line = line[0:75]
            folded.append(new_line + '\n')

            # Go through remainder and fold them
            line = line[75:]
            length = len(line)

            while length > 75:
                # Add folded line
                new_line = line[0:75]
                folded.append(' ' + new_line + '\n')

                # Generate new line and length
                line = line[75:]
                length = len(line)

            # Add remainder
            folded.append(' ' + line + '\n')
        else:
            folded.append(line + '\n')

    # Cycle through schedule list and generate .ics file
    calendar_name = user['calendar_name']
    cal_title = '{}.ics'.format(calendar_name)
    file_loc = Path(cal_loc, cal_title)

    LOG.debug('Saving calendar to %s', file_loc)

    with open(file_loc, 'w') as ics:
        for line in folded:
            ics.write(line)
