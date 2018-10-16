"""Downloads, extracts, and uploads schedules for AHS CZ pharmacists.
    Last Update: 2018-Oct-15

    Copyright (c) Notices
        2018  Joshua R. Torrance  <studybuffalo@studybuffalo.com>

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

import logging
import logging.config
import sys

import sentry_sdk
from unipath import Path

from modules.config import assemble_app_configuration_details, LOGGING_DICT
from modules.manager import run_program

# Determine the path to the config file
CONFIG_PATH = Path(sys.argv[1])

# Collect all the application configuration values
APP_CONFIG = assemble_app_configuration_details(CONFIG_PATH)

# Setup Sentry & Logging
logging.config.dictConfig(LOGGING_DICT)
LOG = logging.getLogger(__name__)

sentry_sdk.init(APP_CONFIG['sentry_dsn'])

run_program(APP_CONFIG)
