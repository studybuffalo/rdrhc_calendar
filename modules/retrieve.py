from datetime import datetime
import logging
from unipath import Path

# Setup Logging
log = logging.getLogger(__name__)

def get_date():
    """Generates todays date as string (in format yyyy-mm-dd)"""
    today = datetime.today()
    year = today.year
    month = "%02d" % today.month
    day = "%02d" % today.day
    date = "%s-%s-%s" % (year, month, day)
    
    return date

def retrieve_schedules(config):
    schedule_loc = config["schedule_loc"]

    date = get_date()

    # Assemble the details for the assistant schedule
    file_name_a = "{0}_{1}.{2}".format(date, "assistant", config["ext_a"])

    # Assemble the details for the pharmacist schedule
    file_name_p = "{0}_{1}.{2}".format(date, "pharmacist", config["ext_p"])
    
    # Assemble the details for the technician schedule
    file_name_t = "{0}_{1}.{2}".format(date, "technician", config["ext_t"])

    # Return the final details
    return {
        "a": Path(schedule_loc, file_name_a),
        "p": Path(schedule_loc, file_name_p),
        "t": Path(schedule_loc, file_name_t),
    }