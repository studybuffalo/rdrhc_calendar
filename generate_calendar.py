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
import logging
import logging.config
from modules import format, notify, retrieve, upload
import sys
from unipath import Path


# FUNCTIONS

# Set root for this program to allow absolute paths
root = Path(sys.argv[1])

# Connect to the config file
config = configparser.ConfigParser()
config.read(Path(root.parent, "config", "rdrhc_calendar.cfg"))

# Setup Logging
log_config = Path(root.parent, "config", "rdrhc_calendar_logging.cfg")
logging.config.fileConfig(log_config)
log = logging.getLogger(__name__)

log.info("STARTING RDRHC CALENDAR GENERATOR")

# Collect the Excel schedule files
excel_files = retrieve.retrieve_schedules(config)

# Collect a list of all the user names
users = None

# Cycle through each user and process their schedule
for user in users:
    # Assemble the users schedule
    schedule = format.assemble_schedule(config, excel_files, user)

    if schedule:
        # Upload the schedule/missing shift data to the Django server
        upload.update_db(user, schedule)

        # Generate and the iCal file to the Django server
        format.generate_calendar(user, schedule)

        # If this is the first schedule, email the welcome details
        notify.email_welcome(user, schedule)

        # Email the user the calendar details
        notify.email_schedule(user, schedule)

log.info("CALENDAR GENERATION COMPLETE")