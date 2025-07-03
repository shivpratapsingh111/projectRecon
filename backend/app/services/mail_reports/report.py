# External imports
import smtplib, ssl, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Internal imports
from app.interface.database_manager import db_ops
from .report_templates import get_report_template
from app.interface.logger_manager import setup_logger

# Initialization
logger = setup_logger(__name__, log_file_path="service", enable_debug=False)
VULN = None
# Gmail SMTP server details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
# Email credentials
SENDER_EMAIL = "yourmail@gmail.com"  # Replace with your Gmail address
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"  # Replace with your Gmail app password
# Log files
SUCCESS_LOG = "email_success.log"
FAILURE_LOG = "email_failure.log"
# Store domains from success logs
processed_domains = set()


# Logic
# Function to send email
def send_email(
    program_name,
    program_url,
    technology,
    email,
    poc_path,
    target_package,
    target_apk,
    download_url,
    attachment_url,
    report_form,
    acquisitions,
):
    receiver_email = email
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Vulnerability Disclosure Report - {program_name}"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    responses = []

    html_content = get_report_template(VULN, program_name)

    if html_content:
        pass
    else:
        logger.error(f"Report for [{VULN}] is not created yet.")
        return f"Report for [{VULN}] is not created yet."

    part = MIMEText(html_content, "html")
    message.attach(part)
    if poc_path != None:
        try:
            with open(poc_path, "rb") as attachment:
                poc_part = MIMEBase("application", "octet-stream")
                poc_part.set_payload(attachment.read())
                encoders.encode_base64(poc_part)
                poc_part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(poc_path)}",
                )
                message.attach(poc_part)
        except Exception as e:
            logger.exception("Attachment file not found")
            responses.append(f"Error: Attachment file not found: [{e}]")
            responses.append(f"Error: Email not sent")
            return responses
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            # server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
            logger.info(f"[FAKE] - Mail sent [{email}] - [{target_package}]")
            responses.append("Success: Email Sent!")

        result = log_success(
            program_name,
            program_url,
            technology,
            email,
            poc_path,
            target_package,
            target_apk,
            download_url,
            attachment_url,
            report_form,
            acquisitions,
        )
        if result is not None:
            responses.extend(result)

    except Exception as e:
        logger.exception("Email not sent")
        log_failure(email, str(e))
        responses.append(f"Error: Email not sent: {e}")

    return responses


# ---


# Function to log successful emails
def log_success(
    program_name,
    program_url,
    technology,
    email,
    poc_path,
    target_package,
    target_apk,
    download_url,
    attachment_url,
    report_form,
    acquisitions,
):
    responses = []
    if db_ops.query_operations().check_program_exists(program_name=program_name):
        logger.info(f"Program [{program_name}] exists.")
        if db_ops.query_operations().check_mobile_target_exists(target_package):
            logger.info(f"Target [{target_package}] exists.")

            target_id = db_ops.query_operations().get_mobile_target_data(
                target_package=target_package
            )[0][0]
            logger.info(f"Got mobile target data {target_id}")
            db_ops.update_operations().update_mobile_target_vuln(
                target_id, vulnerability_reported={"vulnerability_reported": VULN}
            )
            logger.info(f"Updated mobile target vuln for {target_package}")

        else:
            # Insert Target
            logger.warning(f"Target [{target_package}] doesn't exists.")
            program_uuid = db_ops.query_operations().get_program_details(
                program_name=program_name
            )[0][
                0
            ]  # Get Program ID
            logger.info(f"Got program ID [{program_uuid}]")

            mobile_target_data = {
                "program_uuid": program_uuid,
                "target_package": target_package,
                "target_apk": target_apk,
                "technology": technology,
                "download_url": download_url,
                "vulnerability_reported": [VULN],
            }

            db_ops.insert_operations().insert_mobile_target(mobile_target_data)
            logger.info(f"Created target [{target_package}]")

    else:
        logger.warning(f"Program {program_name} doesn't exists")

        program_data = {
            "program_name": program_name,
            "program_url": program_url,
            "acquisitions": acquisitions,
            "email": email,
            "report_form": report_form,
        }
        # Insert Program
        program_uuid = db_ops.insert_operations().insert_program(program_data)
        logger.info(f"Created progam [{program_uuid}]")

        # Insert Target
        mobile_target_data = {
            "program_uuid": program_uuid,
            "target_package": target_package,
            "target_apk": target_apk,
            "technology": technology,
            "download_url": download_url,
            "vulnerability_reported": [VULN],
        }

        target_id = db_ops.insert_operations().insert_mobile_target(mobile_target_data)
        logger.info(f"Created target [{target_package}] - [{target_id}]")

    with open(SUCCESS_LOG, "a") as f:
        f.write(f"{datetime.now()} - Email sent to: {email}\n")


# ---


# Function to log failed emails
def log_failure(email, error):
    with open(FAILURE_LOG, "a") as f:
        f.write(
            f"{datetime.now()} - Failed to send email to: {email} - Error: {error}\n"
        )


# ---


def process_file(report):
    """Reads the input file, checks the conditions, and processes accordingly."""
    responses = []
    program_name = report["program_name"]
    email = report["email"]
    target_package = report["target_package"]
    target_apk = report["target_apk"]
    download_url = report["download_url"]
    attachment_url = report["attachment_url"]
    program_url = report["program_url"]
    technology = report["technology"]
    report_form = report["report_form"]
    acquisitions = report["acquisitions"]

    if db_ops.query_operations().check_program_exists(program_name=program_name):
        logger.info(f"Program [{program_name}] exists.")
        if db_ops.query_operations().check_mobile_target_exists(target_package):
            logger.info(f"Target [{target_package}] exists.")

            if db_ops.query_operations().check_mobile_target_vuln_exists(
                vulnerability_reported=VULN, target_package=target_package
            ):
                responses.append(f"Info: Already reported!")
                logger.info(f"Already reported [{target_package}]")
                return responses
    try:
        poc_path = report.get("poc_path", None)
        if poc_path == "":
            poc_path = None
        if poc_path:
            logger.info(f"Attachment provided - [{target_package}] - [{poc_path}]")
            responses.append(f"Info: Attachment provided: [{poc_path}]")
        else:
            logger.info(f"No attachment provided - [{target_package}]")
            responses.append(f"Info: Attachment not provided")
    except Exception as e:
        poc_path = None
        logger.exception(f"No attachment provided - [{target_package}]")
        responses.append(f"Error: Attachment not provided: [{e}]")
    logger.info(f"Sending email [{program_name}] - [{email}]")
    if responses.extend(
        send_email(
            program_name,
            program_url,
            technology,
            email,
            poc_path,
            target_package,
            target_apk,
            download_url,
            attachment_url,
            report_form,
            acquisitions,
        )
    ):
        processed_domains.add(program_name)

    return responses


# ---


# Main function
def send_report(report, vuln):
    global processed_domains, VULN

    VULN = vuln

    logger.info(f"===========[VULN] - [{VULN}]===========")
    return process_file(report)
