"""Functions related to application configurations."""
# pylint: disable=too-many-locals

import configparser
from datetime import datetime
from decimal import Decimal
from unipath import Path


def assemble_app_configuration_details(root_path):
    """Collects and formats all the require configuration data"""
    # Assemble Path to config file
    config_path = Path(root_path, 'config', 'rdrhc_calendar.cfg')
    config = configparser.ConfigParser()
    config.read(config_path)

    if not config.sections():
        raise FileNotFoundError('Config file not found or is empty.')

    return {
        'sentry_dsn': config.get('sentry', 'dsn'),
        'api_url': config.get('api', 'url'),
        'api_headers': {
            'user-agent': 'rdrhc-calendar',
            'Authorization': 'Token {}'.format(config.get('api', 'token')),
            'Content-Type': 'application/json',
        },
        'timezone': config.get('localization', 'timezone'),
        'excel': {
            'schedule_loc': config.get('schedules', 'save_location'),
            'ext_a': config.get('schedules', 'type_a'),
            'ext_p': config.get('schedules', 'type_p'),
            'ext_t': config.get('schedules', 'type_t')
        },
        'a_excel': {
            'sheet': config.get('schedules', 'sheet_a').split('|'),
            'name_row': config.getint('schedules', 'name_row_a'),
            'col_start': config.getint('schedules', 'name_col_start_a'),
            'col_end': config.getint('schedules', 'name_col_end_a'),
            'row_start': config.getint('schedules', 'shift_row_start_a'),
            'row_end': config.getint('schedules', 'shift_row_end_a'),
            'date_col': config.getint('schedules', 'date_col_a'),
            'ext': config.get('schedules', 'type_a'),
        },
        'p_excel': {
            'sheet': config.get('schedules', 'sheet_p').split('|'),
            'name_row': config.getint('schedules', 'name_row_p'),
            'col_start': config.getint('schedules', 'name_col_start_p'),
            'col_end': config.getint('schedules', 'name_col_end_p'),
            'row_start': config.getint('schedules', 'shift_row_start_p'),
            'row_end': config.getint('schedules', 'shift_row_end_p'),
            'date_col': config.getint('schedules', 'date_col_p'),
            'ext': config.get('schedules', 'type_p'),
        },
        't_excel': {
            'sheet': config.get('schedules', 'sheet_t').split('|'),
            'name_row': config.getint('schedules', 'name_row_t'),
            'col_start': config.getint('schedules', 'name_col_start_t'),
            'col_end': config.getint('schedules', 'name_col_end_t'),
            'row_start': config.getint('schedules', 'shift_row_start_t'),
            'row_end': config.getint('schedules', 'shift_row_end_t'),
            'date_col': config.getint('schedules', 'date_col_t'),
            'ext': config.get('schedules', 'type_t'),
        },
        'calendar_defaults': {
            'weekday_start': datetime.strptime(
                config.get('schedules', 'default_weekday_start'), '%H:%M'
            ).time(),
            'weekday_duration': Decimal(
                config.getfloat('schedules', 'default_weekday_duration')
            ),
            'weekend_start': datetime.strptime(
                config.get('schedules', 'default_weekend_start'), '%H:%M'
            ).time(),
            'weekend_duration': Decimal(
                config.getfloat('schedules', 'default_weekend_duration')
            ),
            'stat_start': datetime.strptime(
                config.get('schedules', 'default_stat_start'), '%H:%M'
            ).time(),
            'stat_duration': Decimal(
                config.getfloat('schedules', 'default_stat_duration')
            ),
        },
        'calendar_save_location': config.get('calendar', 'save_location'),
        'email': {
            'server': config.get('email', 'server'),
            'from_name': config.get('email', 'from_name'),
            'from_email': config.get('email', 'from_email'),
            'owner_name': config.get('email', 'owner_name'),
            'owner_email': config.get('email', 'owner_email'),
            'welcome_text': config.get('email', 'welcome_text', raw=True),
            'welcome_html': config.get('email', 'welcome_html', raw=True),
            'update_text': config.get('email', 'update_text', raw=True),
            'update_html': config.get('email', 'update_html', raw=True),
            'missing_codes_text': config.get(
                'email', 'missing_codes_text', raw=True
            ),
            'missing_codes_html': config.get(
                'email', 'missing_codes_html', raw=True
            ),
            'unsubscribe_link': config.get('email', 'unsubscribe_link')
        },
        'debug': {
            'email_console': config.getboolean('debug', 'email_console')
        }
    }

LOGGING_DICT = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
