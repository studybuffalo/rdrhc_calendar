"""Retrieves the paths to the required schedule files."""

from datetime import datetime
import logging
import pytz
from unipath import Path


# Setup Logging
LOG = logging.getLogger(__name__)

def get_date(tz_string):
    """Generates todays date as string (in format yyyy-mm-dd)"""
    schedule_tz = pytz.timezone(tz_string)
    today = datetime.utcnow().astimezone(schedule_tz)

    LOG.debug('UTC time is %s', datetime.utcnow())
    LOG.debug('Today is %s', today)

    return today.strftime('%Y-%m-%d')

def retrieve_schedules(config):
    """Creates the path to the schedules from supplied config file."""
    schedule_loc = config['excel']['schedule_loc']

    date = get_date(config['timezone'])

    # Assemble the details for the assistant schedule
    file_name_a = '{0}_{1}.{2}'.format(
        date, 'assistant', config['excel']['ext_a']
    )

    # Assemble the details for the pharmacist schedule
    file_name_p = '{0}_{1}.{2}'.format(
        date, 'pharmacist', config['excel']['ext_p']
    )

    # Assemble the details for the technician schedule
    file_name_t = '{0}_{1}.{2}'.format(
        date, 'technician', config['excel']['ext_t']
    )

    # Return the final details
    return {
        'a': Path(schedule_loc, file_name_a),
        'p': Path(schedule_loc, file_name_p),
        't': Path(schedule_loc, file_name_t),
    }
