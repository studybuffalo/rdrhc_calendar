import configparser
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import smtplib

# Setup logger
log = logging.getLogger(__name__)

def email_welcome(user, config):
    """Sends a welcome email to any new user"""

    # Check if user needs email sent (signed up in past 24 hours)
    if user.first_email_sent == False:
        fromEmail = config["email"]["from_email"]
        toEmail = user.email
        subject = "Welcome to Your New Online Schedule"

        content = MIMEMultipart('alternative')
        content['From'] = fromEmail
        content['To'] = toEmail
        content['Subject'] = subject

        # Collects text welcome email from template file
        textLoc = config["email"]["welcome_text"]
        
        try:
            with open(textLoc, "r") as textFile:
                text = textFile.read().replace("\n", "\r\n")
        except:
            log.exception("Unable to read welcome email text template")
            return

        # Collects html welcome email from template file
        htmlLoc = config["email"]["welcome_html"]
            
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
            if config["debug"]["email_console"]:
                log.debug(content.as_string())
            else:
                log.info("Sending welcome email to %s" % user.name)
                server = smtplib.SMTP(config["email"]["server"])
                login = config["email"]["user"]
                pw = config["email"]["password"]

                server.ehlo()
                server.starttls()
                server.login(login, pw)
                server.sendmail(fromEmail, toEmail, content.as_string())
                server.quit()
        except:
            log.exception("Unable to send welcome email to %s" % user.name)

def email_schedule(user, config, schedule):
    """Emails user with any schedule changes"""

    if (len(schedule.additions) or len(schedule.deletions) or 
        len(schedule.changes) or len(schedule.missing) or len(schedule.null)):
        
        fromEmail = config["email"]["from_email"]
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
            defaults = config["calendar_defaults"]

            text.append("MISSING SHIFT CODES")
            text.append("------------------------------------")
            text.append(("A default shift time of {} to {} (weekdays), "
                        "{} to {} (weekends), or {} to {} (statutory holidays) "
                        "has been used for these shifts").format(
                            defaults["weekday_start"].strftime("%H:%M"),
                            defaults["weekday_end"].strftime("%H:%M"),
                            defaults["weekend_start"].strftime("%H:%M"),
                            defaults["weekend_end"].strftime("%H:%M"),
                            defaults["stat_start"].strftime("%H:%M"),
                            defaults["stat_end"].strftime("%H:%M"),
                        ))
            
            html.append("<b>MISSING SHIFT CODES</b>")
            html.append(("<br><i>A default shift time of {} to {} (weekdays), "
                         "{} to {} (weekends), or {} to {} (statutory " 
                         "holidays) has been used for these shifts</i>").format(
                            defaults["weekday_start"].strftime("%H:%M"),
                            defaults["weekday_end"].strftime("%H:%M"),
                            defaults["weekend_start"].strftime("%H:%M"),
                            defaults["weekend_end"].strftime("%H:%M"),
                            defaults["stat_start"].strftime("%H:%M"),
                            defaults["stat_end"].strftime("%H:%M"),
                        ))
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
        fileName = user.calendar_name

        # Generate File Location
        fileLoc = fileName

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
            if config["debug"]["email_console"]:
                log.debug(content.as_string())
            else:
                log.info("Sending update email to %s" % user.name)

                login = config["email"]["user"]
                pw = config["email"]["password"]

                server = smtplib.SMTP(config["email"]["server"])
                server.ehlo()
                server.starttls()
                server.login(login, pw)
                server.sendmail(fromEmail, toEmail, content.as_string())
                server.quit()
        except:
            log.exception("Unable to send update email to %s" % user.name)
