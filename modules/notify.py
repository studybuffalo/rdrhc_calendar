from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import logging
import re
import smtplib

# Setup logger
log = logging.getLogger(__name__)

def email_welcome(user, config):
    """Sends a welcome email to any new user"""

    # Check if user needs email sent (signed up in past 24 hours)
    if user.first_email_sent == False:
        log.debug("Processing data to send user a welcome email")

        from_name = config["email"]["from_name"]
        from_email = config["email"]["from_email"]
        from_address = formataddr((from_name, from_email))

        to_name = user.name
        to_email = user.email
        to_address = formataddr((to_name, to_email))

        subject = "Welcome to Your New Online Schedule"

        content = MIMEMultipart('alternative')
        content['From'] = from_address
        content['To'] = to_address
        content['Subject'] = subject
        content["List-Unsubscribe"] = "<{}>".format(
            config["email"]["unsubscribe_link"]
        )

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

                server.ehlo()
                server.starttls()
                server.sendmail(from_address, to_address, content.as_string())
                server.quit()

            # Update user profile to mark first_email_sent as true
            user.first_email_sent = True
            user.save()

        except:
            log.exception("Unable to send welcome email to %s" % user.name)

def email_schedule(user, config, schedule):
    """Emails user with any schedule changes"""

    if (len(schedule.additions) or len(schedule.deletions) or 
        len(schedule.changes) or len(schedule.missing) or len(schedule.null)):
        log.debug("User qualifies for an update email to be sent")

        # Opens the update email (text) file
        log.debug("Opening the email templates")

        text_loc = config["email"]["update_text"]
        
        try:
            with open(text_loc, "r") as textFile:
                text = textFile.read().replace("\n", "\r\n")
        except Exception as e:
            log.exception(
                "Unable to read welcome email text template at {}".format(
                    text_loc
                )
            )
            text = None

        # Opens the update email (html) file
        html_loc = config["email"]["update_html"]
        
        try:
            with open(html_loc, "r") as htmlFile:
                html = htmlFile.read()
        except Exception as e:
            log.exception(
                "Unable to read welcome email html template at {}".format(
                    html_loc
                )
            )
            html = None
        
        # Set the user name
        text = text.replace("{{ user_name }}", user.name)
        html = html.replace("{{ user_name }}", user.name)

        # Manage added shifts
        log.debug("Updating the 'additions' section")

        if len(schedule.additions):
            # Cycle through additions and insert into templates
            additions_text = []
            additions_html = []

            for a in schedule.additions:
                additions_text.append(" - {}".format(a.msg))
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
        log.debug("Updating the 'deletions' section")

        if len(schedule.deletions):
            deletions_text = []
            deletions_html = []

            for d in schedule.deletions:
                deletions_text.append(" - {}".format(d.msg))
                deletions_html.append("<li>{}</li>".format(d.msg))
                
            text = text.replace("{{ deletions }}", "\r\n".join(deletions_text))
            html = html.replace("{{ deletions }}", "".join(deletions_html))

            # Remove the block markers
            text = text.replace("{% block deletions %}", "")
            html = html.replace("{% block deletions %}", "")
        else:
            # No deletions, remove entire section
            regex = r"{% block deletions %}.*{% block deletions %}"

            text = re.sub(regex, "", text, flags=re.S)
            html = re.sub(regex, "", html, flags=re.S)

        # Manage changed shifts
        log.debug("Updating the 'changes' section")

        if len(schedule.changes):
            changes_text = []
            changes_html = []

            for c in schedule.changes:
                changes_text.append(" - {}".format(c.msg))
                changes_html.append("<li>{}</li>".format(c.msg))
                
            text = text.replace("{{ changes }}", "\r\n".join(changes_text))
            html = html.replace("{{ changes }}", "".join(changes_html))

            # Remove the block markers
            text = text.replace("{% block changes %}", "")
            html = html.replace("{% block changes %}", "")
        else:
            # No changes, remove entire section
            regex = r"{% block changes %}.*{% block changes %}"
            
            text = re.sub(regex, "", text, flags=re.S)
            html = re.sub(regex, "", html, flags=re.S)

        # Manage missing shifts
        log.debug("Updating the 'missing' section")

        if len(schedule.missing):
            defaults = config["calendar_defaults"]

            weekday_start = defaults["weekday_start"].strftime("%H:%M")
            text = text.replace("{{ weekday_start }}", weekday_start)
            html = html.replace("{{ weekday_start }}", weekday_start)

            weekday_end = defaults["weekday_end"].strftime("%H:%M")
            text = text.replace("{{ weekday_end }}", weekday_end)
            html = html.replace("{{ weekday_end }}", weekday_end)

            weekend_start = defaults["weekend_start"].strftime("%H:%M")
            text = text.replace("{{ weekend_start }}", weekend_start)
            html = html.replace("{{ weekend_start }}", weekend_start)

            weekend_end = defaults["weekend_end"].strftime("%H:%M")
            text = text.replace("{{ weekend_end }}", weekend_end)
            html = html.replace("{{ weekend_end }}", weekend_end)

            stat_start = defaults["stat_start"].strftime("%H:%M")
            text = text.replace("{{ stat_start }}", stat_start)
            html = html.replace("{{ stat_start }}", stat_start)

            stat_end = defaults["stat_end"].strftime("%H:%M")
            text = text.replace("{{ stat_end }}", stat_end)
            html = html.replace("{{ stat_end }}", stat_end)

            missing_text = []
            missing_html = []

            for m in schedule.missing:
                missing_text.append(" - {}".format(m.msg))
                missing_html.append("<li>{}</li>".format(m.msg))
                
            text = text.replace("{{ missing }}", "\r\n".join(missing_text))
            html = html.replace("{{ missing }}", "".join(missing_html))

            # Remove the block markers
            text = text.replace("{% block missing %}", "")
            html = html.replace("{% block missing %}", "")
        else:
            # No missing shifts, remove entire section
            regex = r"{% block missing %}.*{% block missing %}"
            
            text = re.sub(regex, "", text, flags=re.S)
            html = re.sub(regex, "", html, flags=re.S)

        # Manage excluded shifts
        log.debug("Updating the 'excluded' section")

        if len(schedule.null):
            null_text = []
            null_html = []

            for n in schedule.null:
                null_text.append(" - {}".format(n.msg))
                null_html.append("<li>{}</li>".format(n.msg))
                
            text = text.replace("{{ excluded }}", "\r\n".join(null_text))
            html = html.replace("{{ excluded }}", "".join(null_html))

            # Remove the block markers
            text = text.replace("{% block excluded %}", "")
            html = html.replace("{% block excluded %}", "")
        else:
            # No excluded shifts, remove entire section
            regex = r"{% block excluded %}.*{% block excluded %}"
            
            text = re.sub(regex, "", text, flags=re.S)
            html = re.sub(regex, "", html, flags=re.S)

        # Add the calendar name
        calendar_name = user.calendar_name
        text = text.replace("{{ calendar_name }}", calendar_name)
        html = html.replace("{{ calendar_name }}", calendar_name)

        
        # Setup email settings
        log.debug("Setting up the other email settings")

        from_name = config["email"]["from_name"]
        from_email = config["email"]["from_email"]
        from_address = formataddr((from_name, from_email))

        to_name = user.name
        to_email = user.email
        to_address = formataddr((to_name, to_email))

        subject = "RDRHC Schedule Changes"
        
        content = MIMEMultipart('alternative')
        content['From'] = from_address
        content['To'] = to_address
        content['Subject'] = subject
        content["List-Unsubscribe"] = "<{}>".format(
            config["email"]["unsubscribe_link"]
        )

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

                server = smtplib.SMTP(config["email"]["server"])
                server.ehlo()
                server.starttls()
                server.sendmail(from_address, to_address, content.as_string())
                server.quit()
        except:
            log.exception("Unable to send update email to %s" % user.name)
