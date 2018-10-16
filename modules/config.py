"""Functions related to application configurations."""
# pylint: disable=too-many-locals

import configparser
from datetime import datetime, timedelta


def assemble_app_configuration_details(config_path):
    """Collects and formats all the require configuration data"""
    config = configparser.ConfigParser()
    config.read(config_path)

    weekday_start = datetime.strptime(
        config.get('schedules', 'default_weekday_start'),
        '%H:%M'
    )

    weekend_start = datetime.strptime(
        config.get('schedules', 'default_weekend_start'),
        '%H:%M'
    )

    stat_start = datetime.strptime(
        config.get('schedules', 'default_stat_start'),
        '%H:%M'
    )

    weekday_duration = config.getfloat('schedules', 'default_weekday_duration')
    weekday_hours = int(weekday_duration)
    weekday_minutes = int((weekday_duration*60) % 60)

    weekend_duration = config.getfloat('schedules', 'default_weekend_duration')
    weekend_hours = int(weekend_duration)
    weekend_minutes = int((weekend_duration*60) % 60)

    stat_duration = config.getfloat('schedules', 'default_stat_duration')
    stat_hours = int(stat_duration)
    stat_minutes = int((stat_duration*60) % 60)

    weekday_end = weekday_start + timedelta(
        hours=weekday_hours,
        minutes=weekday_minutes
    )

    weekend_end = weekend_start + timedelta(
        hours=weekend_hours,
        minutes=weekend_minutes
    )

    stat_end = stat_start + timedelta(
        hours=stat_hours,
        minutes=stat_minutes
    )

    return {
        'sentry_dsn': config.get('sentry', 'dsn'),
        'api_url': config.get('api', 'url'),
        'api_headers': {
            'user-agent': 'rdrhc-calendar',
            'Authorization': 'Token {}'.format(config.get('api', 'token')),
        },
        'timezone': config.get('localization', 'timezone'),
        'excel': {
            'schedule_loc': config.get('schedules', 'save_location'),
            'ext_a': config.get('schedules', 'type_a'),
            'ext_p': config.get('schedules', 'type_p'),
            'ext_t': config.get('schedules', 'type_t')
        },
        'a_excel': {
            'sheet': config.get('schedules', 'sheet_a'),
            'name_row': config.getint('schedules', 'name_row_a'),
            'col_start': config.getint('schedules', 'name_col_start_a'),
            'col_end': config.getint('schedules', 'name_col_end_a'),
            'row_start': config.getint('schedules', 'shift_row_start_a'),
            'row_end': config.getint('schedules', 'shift_row_end_a'),
            'date_col': config.getint('schedules', 'date_col_a')
        },
        'p_excel': {
            'sheet': config.get('schedules', 'sheet_p'),
            'name_row': config.getint('schedules', 'name_row_p'),
            'col_start': config.getint('schedules', 'name_col_start_p'),
            'col_end': config.getint('schedules', 'name_col_end_p'),
            'row_start': config.getint('schedules', 'shift_row_start_p'),
            'row_end': config.getint('schedules', 'shift_row_end_p'),
            'date_col': config.getint('schedules', 'date_col_p')
        },
        't_excel': {
            'sheet': config.get('schedules', 'sheet_t'),
            'name_row': config.getint('schedules', 'name_row_t'),
            'col_start': config.getint('schedules', 'name_col_start_t'),
            'col_end': config.getint('schedules', 'name_col_end_t'),
            'row_start': config.getint('schedules', 'shift_row_start_t'),
            'row_end': config.getint('schedules', 'shift_row_end_t'),
            'date_col': config.getint('schedules', 'date_col_t')
        },
        'calendar_defaults': {
            'weekday_start': weekday_start.time(),
            'weekday_end': weekday_end.time(),
            'weekend_start': weekend_start.time(),
            'weekend_end': weekend_end.time(),
            'stat_start': stat_start.time(),
            'stat_end': stat_end.time(),
            'weekday_duration': weekday_duration,
            'weekday_hours': weekday_hours,
            'weekday_minutes': weekday_minutes,
            'weekend_duration': weekday_duration,
            'weekend_hours': weekday_hours,
            'weekend_minutes': weekday_minutes,
            'stat_duration': weekday_duration,
            'stat_hours': weekday_hours,
            'stat_minutes': weekday_minutes,
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
