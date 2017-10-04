

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

def update_db(schedule, cursor):
    """Uploads user schedule to MySQL database"""

    # Delete all items for this user
    query = "DELETE FROM calendar_schedules WHERE user = %s AND role = %s"
    args = (user.name, user.role)

    try:
        cursor.execute(query, args)
    except:
        log.exception("Unable to remove old schedule from database for %s" 
                      % user.name)
    
    # Cycle through and create an array of mysql data
    mysqlData = []
    
    for day in schedule.shifts:
        mysqlData.append((day.startDate, day.shift, user.name, user.role))
    
    # Upload the new schedule
    query = ("INSERT INTO calendar_schedules (date, shift, user, role) "
             "VALUES (%s, %s, %s, %s)")

    try:
        cursor.executemany(query, mysqlData)
    except:
        log.exception("Unable to upload new schedule to database for %s" 
                      % user.name)
