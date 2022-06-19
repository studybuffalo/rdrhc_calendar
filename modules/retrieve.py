"""Retrieves the paths to the required schedule files."""
import logging
from pathlib import Path


LOG = logging.getLogger(__name__)


def retrieve_schedule_file_paths(config):
    """Creates the path to the schedules from supplied config file."""
    schedule_loc = Path(config['excel']['schedule_loc'])

    # Get the most recent assistant file
    assistant_files = schedule_loc.glob(f'assistant_*.{config["excel"]["ext_a"]}')
    assistant_latest = max(assistant_files, key=lambda x: x.stat().st_ctime)

    # Get the most recent pharmacist file
    pharmacist_files = schedule_loc.glob(f'pharmacist_*.{config["excel"]["ext_p"]}')
    pharmacist_latest = max(pharmacist_files, key=lambda x: x.stat().st_ctime)

    # Get the most recent technician file
    technician_files = schedule_loc.glob(f'technician_*.{config["excel"]["ext_t"]}')
    technician_latest = max(technician_files, key=lambda x: x.stat().st_ctime)

    # Return the final details
    return {
        'a': Path(assistant_latest),
        'p': Path(pharmacist_latest),
        't': Path(technician_latest),
    }
