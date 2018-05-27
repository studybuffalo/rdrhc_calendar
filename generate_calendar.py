"""Downloads, extracts, and uploads schedules for AHS CZ pharmacists.
    Last Update: 2017-Oct-01

    Copyright (c) Notices
        2017  Joshua R. Torrance  <studybuffalo@studybuffalo.com>
    
    This program is free software: you can redistribute it and/or 
    modify it under the terms of the GNU General Public License as 
    published by the Free Software Foundation, either version 3 of the 
    License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, 
    see <http://www.gnu.org/licenses/>.
    SHOULD YOU REQUIRE ANY EXCEPTIONS TO THIS LICENSE, PLEASE CONTACT 
    THE COPYRIGHT HOLDERS.
"""

import configparser
from datetime import datetime, timedelta
import django
import logging
import logging.config
from modules import format, notify, retrieve, upload
import os
import sys
from unipath import Path

def collect_config(config):
    """Collects and formats all the require configuration data"""
    weekday_start = datetime.strptime(
        config.get("schedules", "default_weekday_start"),
        "%H:%M"
    )
    
    weekend_start = datetime.strptime(
        config.get("schedules", "default_weekend_start"),
        "%H:%M"
    )

    stat_start = datetime.strptime(
        config.get("schedules", "default_stat_start"),
        "%H:%M"
    )

    weekday_duration = config.getfloat("schedules", "default_weekday_duration")
    weekday_hours = int(weekday_duration)
    weekday_minutes = int((weekday_duration*60) % 60)

    weekend_duration = config.getfloat("schedules", "default_weekend_duration")
    weekend_hours = int(weekend_duration)
    weekend_minutes = int((weekend_duration*60) % 60)

    stat_duration = config.getfloat("schedules", "default_stat_duration")
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
        "timezone": config.get("localization", "timezone"),
        "excel": {
            "schedule_loc": config.get("schedules", "save_location"),
            "ext_a": config.get("schedules", "type_a"),
            "ext_p": config.get("schedules", "type_p"),
            "ext_t": config.get("schedules", "type_t")
        },
        "a_excel": {
            "sheet": config.get("schedules", "sheet_a"),
            "name_row": config.getint("schedules", "name_row_a"),
            "col_start": config.getint("schedules", "name_col_start_a"),
            "col_end": config.getint("schedules", "name_col_end_a") ,
            "row_start": config.getint("schedules", "shift_row_start_a"),
            "row_end": config.getint("schedules", "shift_row_end_a"),
            "date_col": config.getint("schedules", "date_col_a")
        },
        "p_excel": {
            "sheet": config.get("schedules", "sheet_p"),
            "name_row": config.getint("schedules", "name_row_p"),
            "col_start": config.getint("schedules", "name_col_start_p"),
            "col_end": config.getint("schedules", "name_col_end_p") ,
            "row_start": config.getint("schedules", "shift_row_start_p"),
            "row_end": config.getint("schedules", "shift_row_end_p"),
            "date_col": config.getint("schedules", "date_col_p")
        },
        "t_excel": {
            "sheet": config.get("schedules", "sheet_t"),
            "name_row": config.getint("schedules", "name_row_t"),
            "col_start": config.getint("schedules", "name_col_start_t"),
            "col_end": config.getint("schedules", "name_col_end_t") ,
            "row_start": config.getint("schedules", "shift_row_start_t"),
            "row_end": config.getint("schedules", "shift_row_end_t"),
            "date_col": config.getint("schedules", "date_col_t")
        },
        "calendar_defaults": {
            "weekday_start": weekday_start.time(),
            "weekday_end": weekday_end.time(),
            "weekend_start": weekend_start.time(),
            "weekend_end": weekend_end.time(),
            "stat_start": stat_start.time(),
            "stat_end": stat_end.time(),
            "weekday_duration": weekday_duration,
            "weekday_hours": weekday_hours,
            "weekday_minutes": weekday_minutes,
            "weekend_duration": weekday_duration,
            "weekend_hours": weekday_hours,
            "weekend_minutes": weekday_minutes,
            "stat_duration": weekday_duration,
            "stat_hours": weekday_hours,
            "stat_minutes": weekday_minutes,
        },
        "calendar_save_location": config.get("calendar", "save_location"),
        "email": {
            "server": config.get("email", "server"),
            "from_name": config.get("email", "from_name"),
            "from_email": config.get("email", "from_email"),
            "owner_name": config.get("email", "owner_name"),
            "owner_email": config.get("email", "owner_email"),
            "welcome_text": config.get("email", "welcome_text", raw=True),
            "welcome_html": config.get("email", "welcome_html", raw=True),
            "update_text": config.get("email", "update_text", raw=True),
            "update_html": config.get("email", "update_html", raw=True),
            "missing_codes_text": config.get("email", "missing_codes_text", raw=True),
            "missing_codes_html": config.get("email", "missing_codes_html", raw=True),
            "unsubscribe_link": config.get("email", "unsubscribe_link")
        },
        "debug": {
            "email_console": config.getboolean("debug", "email_console")
        }
    }
   
def collect_emails(calendar, EmailAccounts):
    """Retrieves a specified calendar user's email"""
    emails = EmailAccounts.objects.filter(user=calendar.sb_user)

    email_list = []

    for e in emails:
        email_list.append(e.email)
    
    return(email_list)

# Set root for this program to allow absolute paths
root = Path(sys.argv[1])

# Connect to the config file
config = configparser.ConfigParser()
config.read(Path(root.parent, "config", "rdrhc_calendar.cfg"))

# Setup Logging
log_config = Path(root.parent, "config", "rdrhc_calendar_logging.cfg")
logging.config.fileConfig(log_config)
log = logging.getLogger(__name__)

# Setup connection to the Django server
djangoApp = config.get("django", "location")

sys.path.append(djangoApp)
sys.path.append("/home/django/studybuffalo/study_buffalo")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")
django.setup()

# pylint: disable=import-error
from rdrhc_calendar.models import CalendarUser, ShiftCode, StatHoliday, Shift, MissingShiftCode
from allauth.account.models import EmailAddress

log.info("STARTING RDRHC CALENDAR GENERATOR")

# Collect all the application configuration values
app_config = collect_config(config)

# Collect the Excel schedule files
log.info("Retrieving the Excel Schedules")
excel_files = retrieve.retrieve_schedules(app_config)

# Collect a list of all the user names
log.info("Retrieving all calendar users")
users = CalendarUser.objects.all()

# Set to hold any codes not in Django DB
missing_codes = {
    "a": set(),
    "p": set(),
    "t": set()
}

# Cycle through each user and process their schedule
for user in users:
    # Assemble the users schedule
    log.info("Assembling schedule for {0}".format(user.name))

    schedule = format.assemble_schedule(app_config, excel_files, user, ShiftCode, StatHoliday, Shift)

    if schedule:
        # Upload the schedule data to the Django server
        upload.update_db(user, schedule.shifts, Shift)

        # Generate and the iCal file to the Django server
        format.generate_calendar(
            user, schedule.shifts, app_config["calendar_save_location"]
        )

        # Get the user's email(s)
        emails = collect_emails(user, EmailAddress)

        # If this is the first schedule, email the welcome details
        notify.email_welcome(user, emails, app_config)

        # Email the user the calendar details
        notify.email_schedule(user, emails, app_config, schedule)
        
        # Add the missing codes to the set
        missing_codes[user.role] = missing_codes[user.role].union(
            schedule.missing_upload
        )

# Upload the missing codes to the database
missing_upload = upload.update_missing_codes(missing_codes, MissingShiftCode)

# Notify owner that there are new codes to upload
if missing_upload:
    notify.email_missing_codes(missing_upload, app_config)

log.info("CALENDAR GENERATION COMPLETE")


