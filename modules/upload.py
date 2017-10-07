import logging

# Setup logger
log = logging.getLogger(__name__)

def upload_calendar(user):
    """Uploads .ics calendar to server"""
    address = priCon.get("ftp", "address")
    username = priCon.get("ftp", "user")
    password = priCon.get("ftp", "password")
    
    ftp = ftplib.FTP(address, username, password)

    # Open the calendar file
    fileName = user.codeName
    schedTitle = "%s - %s.ics" % (today, fileName)
    fileLoc = root.child("calendars", schedTitle).absolute()
    calFile = open(fileLoc, 'rb')

    # Generate website name and STOR message
    onlineName = "%s.ics" % user.codeName

    storMsg = "STOR %s" % onlineName

    # Chooses location based on public or private access
    if user.public is True:
        ftpLoc = pubCon.get("ftp", "public_location")
    elif user.public is False:
        ftpLoc = pubCon.get("ftp", "private_location")
    
    # Set FTP directory
    try:
        ftp.cwd(ftpLoc)
    except:
        log.exception("Unable to change FTP directory to %s" % ftpLoc)
    
    # Upload the .ics calendar to the server
    try:
        log.info("Uploading .ics calendar to server for %s" % user.name)

        ftp.storlines(storMsg, calFile)
    
        calFile.close()
        ftp.quit()
    except:
        log.exception("Unable to upload .ics calendar to server for %s" 
                      % user.name)

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
    
