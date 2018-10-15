"""Functions to handle upload to the database."""

import logging

# Setup logger
LOG = logging.getLogger(__name__)

def update_schedule_database(user, schedule):
    """Uploads user schedule to Django Database"""

    # Remove the user's old schedule
    log.debug("Removing old shifts for user")

    try:
        Shift.objects.filter(sb_user=user.sb_user).delete()
    except Exception:
        log.error(
            "Unable to remove old schedule for {}".format(user.name),
            exc_info=True
        )

    # Upload the new schedule
    log.debug("Uploading the new shifts for user")

    for s in schedule:
        upload = Shift(
            sb_user=user.sb_user,
            date=s.start_datetime.date(),
            shift_code=s.django_shift,
            text_shift_code=s.shift_code
        )

        try:
            upload.save()
        except Exception:
            log.error(
                "Unable to save shift ({}) to schedule for {}".format(
                    s.shift_code, user.name
                ),
                exc_info=True
            )

def update_missing_codes_database(missing_codes):
    """Uploads any new missing shift codes"""
    LOG.debug("Checking for missing shift codes")

    new_codes = []

    for role, code_set in missing_codes.items():
        for code in code_set:
            if code:
                retrieved_code, missing_code = MissingShiftCode.objects.get_or_create(
                    code=code,
                    role=role
                )

                # If this is a new code, record it to email owner
                if missing_code:
                    log.debug("New code to upload: {}".format(code))

                    new_codes.append("{} - {}".format(role, code))

    return new_codes
