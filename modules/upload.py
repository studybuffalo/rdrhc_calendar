import logging

# Setup logger
log = logging.getLogger(__name__)

def update_db(user, schedule, Shift):
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

def update_missing_codes(codes, role, MissingShiftCode):
    """Uploads any new missing shift codes"""
    for code in codes:
        missing_code = MisshingShiftCode(
            code = code
            role = role
        )

        try:
            missing_code.save()
        Except