import logging

# Setup logger
log = logging.getLogger(__name__)

def update_db(user, schedule, Shift):
    """Uploads user schedule to Django Database"""

    # Remove the user's old schedule
    try:
        Shift.objects.filter(user__exact=user.id).delete()
    except Exception as e:
        log.warn(
            "Unable to remove old schedule for {}".format(user.name)
        )

    # Upload the new schedule
    for s in schedule:
        upload = Shift(
            user=user,
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
                )
            )