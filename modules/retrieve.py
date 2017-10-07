from datetime import datetime
import logging
from unipath import Path

def get_date():
    """Generates todays date as string (in format yyyy-mm-dd)"""
    today = datetime.today()
    year = today.year
    month = "%02d" % today.month
    day = "%02d" % today.day
    date = "%s-%s-%s" % (year, month, day)
    
    return date

def retrieve_schedules(config):
    # Setup Logging
    log = logging.getLogger(__name__)

    schedule_loc = config.get("schedules", "save_location")

    date = get_date()

    # Assemble the details for the assistant schedule
    ext_a = config.get("schedules", "type_a")
    file_name_a = "{0}_{1}.{2}".format(date, "assistant", ext_a)

    # Assemble the details for the pharmacist schedule
    ext_p = config.get("schedules", "type_p")
    file_name_p = "{0}_{1}.{2}".format(date, "pharmacist", ext_p)
    
    # Assemble the details for the technician schedule
    ext_t = config.get("schedules", "type_t")
    file_name_t = "{0}_{1}.{2}".format(date, "technician", ext_t)

    # Return the final details
    return {
        "a": Path(schedule_loc, file_name_a),
        "p": Path(schedule_loc, file_name_p),
        "t": Path(schedule_loc, file_name_t),
    }