import logging

# Setup logger
log = logging.getLogger(__name__)

def update_db(user, schedule, Shift):
    """Uploads user schedule to Django Database"""

    # Remove the user's old schedule
    log.debug("Removing old shifts for user")

    try:
        Shift.objects.filter(sb_user=user.sb_user).delete()
    except Exception as e:
        log.warn(
            "Unable to remove old schedule for {}".format(user.name),
            exc_info=e
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
        except Exception as e:
            log.warn(
                "Unable to save shift ({}) to schedule for {}".format(
                    s.shift_code, user.name
                ),
                exc_info=e
            )