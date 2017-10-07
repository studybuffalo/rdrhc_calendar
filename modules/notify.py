from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import re
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
        
        # Opens the update email (text) file
        text_loc = config["email"]["update_text"]
        
        try:
            with open(textLoc, "r") as textFile:
                text = textFile.read().replace("\n", "\r\n")
        except Exception as e:
            log.exception("Unable to read welcome email text template")

        # Opens the update email (html) file
        text_loc = config["email"]["update_text"]
        
        try:
            with open(htmlLoc, "r") as htmlFile:
                html = htmlFile.read()
        except Exception as e:
            log.exception("Unable to read welcome email html template")
        
        # Manage added shifts
        if len(schedule.additions):
            # Cycle through additions and insert into templates
            additions_text = []
            additions_html = []

            for a in schedule.additions:
                additions_text.append(" - {}".format_map(a.msg))
                additions_html.append("<li>{}</li>".format(a.msg))

            text = text.replace("{{ additions }}", "\r\n".join(additions_text))
            html = html.replace("{{ additions }}", "".join(additions_html))

            # Remove the block markers
            text = text.replace("{% block additions %}", "")
            html = html.replace("{% block additions %}", "")
        else:
            # No additions, remove entire section
            regex = r"{% block additions %}.*{% block additions %}"

            text = re.sub(regex, "", text, flags=re.S)
            html = re.sub(regex, "", html, flags=re.S)

        # Manage deleted shifts
        if len(schedule.deletions):
            deletions_text = []
            deletions_html = []

            for d in schedule.deletions:
                deletions_text.append(" - {}".format_map(d.msg))
                deletions_html.append("<li>{}</li>".format(d.msg))
                
            text.replace("{{ deletions }}", "\r\n".join(deletions_text))
            html.replace("{{ deletions }}", "".join(deledtions_html))

            # Remove the block markers
            text = text.replace("{% block deletions %}", "")
            html = html.replace("{% block deletions %}", "")
        else:
            # No deletions, remove entire section
            regex = r"{% block deletions %}.*{% block deletions %}"
            
            text = re.sub(regex, "", text, re.S)
            html = re.sub(regex, "", html, re.S)

        # Manage changed shifts
        if len(schedule.changes):
            changes_text = []
            changes_html = []

            for c in schedule.changes:
                changes_text.append(" - {}".format_map(c.msg))
                changes_html.append("<li>{}</li>".format(c.msg))
                
            text.replace("{{ deletions }}", "\r\n".join(changes_text))
            html.replace("{{ deletions }}", "".join(changes_html))

            # Remove the block markers
            text = text.replace("{% block changes %}", "")
            html = html.replace("{% block changes %}", "")
        else:
            # No changes, remove entire section
            regex = r"{% block changes %}.*{% block changes %}"
            
            text = re.sub(regex, "", text, re.S)
            html = re.sub(regex, "", html, re.S)

        # Manage missing shifts
        if len(schedule.missing):
            defaults = config["calendar_defaults"]

            weekday_start = defaults["weekday_start"].strftime("%H:%M")
            text = text.replace("{{ weekday_start }}", weekday_start)
            html = html.replace(" {{ weekday_start }}", weekday_start)

            weekday_end = defaults["weekday_end"].strftime("%H:%M")
            text = text.replace("{{ weekday_end }}", weekday_end)
            html = html.replace(" {{ weekday_end}}", weekday_end)

            weekend_start = defaults["weekend_start"].strftime("%H:%M")
            text = text.replace("{{ weekend_start }}", weekend_start)
            html = html.replace(" {{ weekend_start }}", weekend_start)

            weekend_end = defaults["weekend_end"].strftime("%H:%M")
            text = text.replace("{{ weekend_end }}", weekend_end)
            html = html.replace(" {{ weekend_end}}", weekend_end)

            stat_start = defaults["stat_start"].strftime("%H:%M")
            text = text.replace("{{ stat_start }}", stat_start)
            html = html.replace(" {{ stat_start }}", stat_start)

            stat_end = defaults["stat_end"].strftime("%H:%M")
            text = text.replace("{{ stat_end }}", stat_end)
            html = html.replace(" {{ stat_end}}", stat_end)

            missing_text = []
            missing_html = []

            for m in schedule.missing:
                missing_text.append(" - {}".format_map(m.msg))
                missing_html.append("<li>{}</li>".format(m.msg))
                
            text.replace("{{ missing }}", "\r\n".join(missing_text))
            html.replace("{{ missing }}", "".join(missing_html))

            # Remove the block markers
            text = text.replace("{% block missing %}", "")
            html = html.replace("{% block missing %}", "")
        else:
            # No missing shifts, remove entire section
            regex = r"{% block missing %}.*{% block missing %}"
            
            text = re.sub(regex, "", text, re.S)
            html = re.sub(regex, "", html, re.S)

        # Manage excluded shifts
        if len(schedule.null):
            null_text = []
            null_html = []

            for n in schedule.null:
                null_text.append(" - {}".format_map(n.msg))
                null_html.append("<li>{}</li>".format(n.msg))
                
            text.replace("{{ excluded }}", "\r\n".join(null_text))
            html.replace("{{ excluded }}", "".join(null_html))

            # Remove the block markers
            text = text.replace("{% block excluded %}", "")
            html = html.replace("{% block excluded %}", "")
        else:
            # No excluded shifts, remove entire section
            regex = r"{% block excluded %}.*{% block excluded %}"
            
            text = re.sub(regex, "", text, re.S)
            html = re.sub(regex, "", html, re.S)

        # Add the calendar name
        calendar_name = user.calendar_name
        text = text.replace("{{ calendar_name }}", calendar_name)
        html = html.replace("{{ calendar_name }}", calendar_name)

        
        # Setup email settings
        fromEmail = config["email"]["from_email"]
        toEmail = user.email
        subject = "RDRHC Schedule Changes"
        
        content = MIMEMultipart('alternative')
        content['From'] = fromEmail
        content['To'] = toEmail
        content['Subject'] = subject
        
        # Construct the email body
        textBody = MIMEText(text, 'plain')
        htmlBody = MIMEText(html, 'html')
        
        content.attach(textBody)
        content.attach(htmlBody)
        
        # Send the email
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
