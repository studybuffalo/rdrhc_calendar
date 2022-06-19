"""Retrieves the paths to the required schedule files."""
import logging
from pathlib import Path


LOG = logging.getLogger(__name__)


def _get_most_recent_file(directory, glob_statement):
    """Returns the most recent file from list of files."""
    files = directory.glob(glob_statement)

    try:
        return max(files, key=lambda file: file.stat().st_mtime)
    except ValueError as exception:
        raise FileNotFoundError(f'Unable to find file for glob: "{glob_statement}".') from exception


def retrieve_schedule_file_paths(config):
    """Creates the path to the schedules from supplied config file."""
    schedule_loc = Path(config['excel']['schedule_loc'])

    # Get the most recent assistant file
    assistant_glob = f'assistant_*.{config["excel"]["ext_a"]}'
    assistant_latest = _get_most_recent_file(schedule_loc, assistant_glob)

    # Get the most recent pharmacist file
    pharmacist_glob = f'pharmacist_*.{config["excel"]["ext_p"]}'
    pharmacist_latest = _get_most_recent_file(schedule_loc, pharmacist_glob)

    # Get the most recent technician file
    technician_glob = f'technician_*.{config["excel"]["ext_t"]}'
    technician_latest = _get_most_recent_file(schedule_loc, technician_glob)

    # Return the final details
    return {
        'a': Path(assistant_latest),
        'p': Path(pharmacist_latest),
        't': Path(technician_latest),
    }
