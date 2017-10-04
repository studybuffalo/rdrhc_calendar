def email_welcome(user):
    """Sends a welcome email to any new user"""

    # Get dates of the user's sign up
    end = datetime.now()
    start = end - timedelta(days=1)
    
    # Check if user needs email sent (signed up in past 24 hours)
    try:
        if user.start > start and user.start < end:
            sendEmail = True
        else:
            sendEmail = False
    except:
        sendEmail = False

        log.exception("Unable to check %s's start date" % user.name)

    # Send email if user started in past 24 hours
    if sendEmail:
        server = priCon.get("email", "server")
        login = priCon.get("email", "user")
        pw = priCon.get("email", "password")
        fromEmail = login
        toEmail = user.email
        subject = "Welcome to Your New Online Schedule"

        content = MIMEMultipart('alternative')
        content['From'] = fromEmail
        content['To'] = toEmail
        content['Subject'] = subject

        # Collects text welcome email from template file
        textLoc = pubCon.get("email", "welcome_text", raw=True)
        
        try:
            with open(textLoc, "r") as textFile:
                text = textFile.read().replace("\n", "\r\n")
        except:
            log.exception("Unable to read welcome email text template")
            return

        # Collects html welcome email from template file
        htmlLoc = pubCon.get("email", "welcome_html", raw=True)
            
        try:
            with open(htmlLoc, "r") as htmlFile:
                html = htmlFile.read()
        except:
            log.exception("Unable to read welcome email html template")
            return

        # Assemble an HTML and plain text version
        textBody = MIMEText(text, 'plain')
        htmlBody = MIMEText(html, 'html')
        
        content.attach(textBody)
        content.attach(htmlBody)
        
        # Attempt to send email
        try:
            log.info("Sending welcome email to %s" % user.name)

            server = smtplib.SMTP(server)
            server.ehlo()
            server.starttls()
            server.login(login, pw)
            server.sendmail(fromEmail, toEmail, content.as_string())
            server.quit()
        except:
            log.exception("Unable to send welcome email to %s" % user.name)

def email_schedule(schedule, user):
    """Emails user with any schedule changes"""

    if (len(schedule.additions) or len(schedule.deletions) or 
        len(schedule.changes) or len(schedule.missing) or len(schedule.null)):
        
        login = priCon.get('email', 'user')
        pw = priCon.get('email', 'password')
        fromEmail = login
        toEmail = user.email
        subject = "RDRHC Schedule Changes"
        
        content = MIMEMultipart('alternative')
        content['From'] = fromEmail
        content['To'] = toEmail
        content['Subject'] = subject
        
        text = []
        html = []
        
        # Initial HTML Setup
        html.append("<html>")
        html.append("<head></head>")
        html.append("<body>")
        
        # Email opening
        text.append("Hello %s,\r\n" % user.name)
        text.append("Please see the following details regarding your work "
                    "schedule at the Red Deer Regional Hospital Centre:\r\n")
        
        html.append("<p>Hello %s,</p>" % user.name)
        html.append("<p>Please see the following details regarding your "
                    "work schedule at the Red Deer Regional Hospital "
                    "Centre:</p>")
        
        # Cycle through changes and create html & text email messages
        if len(schedule.additions):
            text.append("ADDITIONS")
            text.append("------------------------------------")
            
            html.append("<b>ADDITIONS</b>")
            html.append("<ul>")
            
            for a in schedule.additions:
                text.append(a.msg)
                
                html.append("<li>%s</li>" % a.msg)
                
            text.append("")
            
            html.append("</ul>")
            
        if len(schedule.deletions):
            text.append("DELETIONS")
            text.append("------------------------------------")
            
            html.append("<b>DELETIONS</b>")
            html.append("<ul>")
            
            for d in schedule.deletions:
                text.append(d.msg)
                
                html.append("<li>%s</li>" % d.msg)
                
            text.append("")

            html.append("</ul>")
            
        if len(schedule.changes):
            text.append("CHANGES")
            text.append("------------------------------------")
            
            html.append("<b>CHANGES</b>")
            html.append("<ul>")
            
            for c in schedule.changes:
                text.append(c.msg)
                
                html.append("<li>%s</li>" % c.msg)
                
            text.append("")
            
            html.append("</ul>")
            
        if len(schedule.missing):
            text.append("MISSING SHIFT CODES")
            text.append("------------------------------------")
            text.append("A default shift time of 07:00 to 22:00 (weekdays) "
                        "or 07:00 to 19:30 (weekends and stats) has been "
                        "used for these shifts")
            
            html.append("<b>MISSING SHIFT CODES</b>")
            html.append("<br><i>A default shift time of 07:00 to 22:00 "
                        "(weekdays) or 07:00 to 19:30 (weekends and stats) "
                        "has been used for these shifts</i>")
            html.append("<ul>")
            
            for m in schedule.missing:
                text.append(m.msg)
                
                html.append("<li>%s</li>" % m.msg)
                
            text.append("")
            
            html.append("</ul>")
            
        if len(schedule.null):
            text.append("EXCLUDED CODES")
            text.append("------------------------------------")
            text.append("These codes are for you to review to ensure no "
			            "work shifts have been missed; these codes have " 
			            "interpretted either as holidays/vacations/sick " 
			            "time/etc. or as being unrelated to start and end " 
			            "times")
            
            html.append("<b>EXCLUDED CODES</b>")
            html.append("<br><i>These codes are for you to review to "
                        "ensure no work shifts have been missed; these "
                        "codes have interpretted either as holidays/"
                        "vacations/sick time/etc. or as being unrelated to "
                        "start and end times</i>")
            html.append("<ul>")
            
            for n in schedule.null:
                text.append(n.msg)
                
                html.append("<li>%s</li>" % n.msg)
                
            text.append("")
            
            html.append("</ul>")
            
        # Add email footer
        # Generate File Name
        fileName = user.codeName

        # Generate File Location
        if user.public is True:
            fileLoc = fileName
        elif user.public is False:
            fileLoc = "private/%s" % fileName


        text.append("The address for your schedule is: "
                    "http://www.studybuffalo.com/calendar/%s.ics" % fileLoc)
        text.append("")
        
        html.append("<hr>")
        html.append("<p>The address for your schedule is: "
                    "http://www.studybuffalo.com/calendar/%s.ics </p>" 
                    % fileLoc)
        
        # Add tutorials
        text.append("For help using the calendar file, please see the "
                    "tutorials located at: "
                    "http://www.studybuffalo.com/calendar/")
        text.append("")
        
        html.append("<p>For help using the calendar file, please see the "
                    "tutorials located at: "
                    "http://www.studybuffalo.com/calendar/ </p>")
        
        # Add final notice
        text.append("If you wish to have any modifications made to your "
                    "shift codes (including exlcuded or missing shift "
                    "codes), please contact the owner of this program")
        
        html.append("<p>If you wish to have any modifications made to your "
                    "shift codes (including exlcuded or missing shift "
                    "codes), please contact the owner of this program</p>")
        
		# HTML finishing
        html.append("</body>")
        html.append("</html>")

        # Assemble final html and txt email content
        text = "\r\n".join(text)
        html = "".join(html)
        
        textBody = MIMEText(text, 'plain')
        htmlBody = MIMEText(html, 'html')
        
        content.attach(textBody)
        content.attach(htmlBody)
        
        try:
            log.info("Sending update email to %s" % user.name)
            
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(login, pw)
            server.sendmail(fromEmail, toEmail, content.as_string())
            server.quit()
        except:
            log.exception("Unable to send update email to %s" % user.name)
