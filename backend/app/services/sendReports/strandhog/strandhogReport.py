"""
This file takes input URLs and emails for the same domain, and reports them a clickjacking vulnerability.
If mails are more than one, it seperates them into another file, so you can decide which one to mail.

Example Input:

https://lego.com/.well-known/security.txt, whitehat@lego.com
https://yoast.com/.well-known/security.txt, security@yoast.com
https://httpwg.org/.well-known/security.txt, httpbis-chairs@ietf.org, ietf-http-wg@w3.org, ietf-http-wg-request@w3.org
https://rferl.org/.well-known/security.txt, vulnerability_disclosure@usagm.gov
https://unimelb.edu.au/.well-known/security.txt, it-security@unimelb.edu.au
https://telenor.no/.well-known/security.txt, tsoc@tsoc.telenor.net
https://fu-berlin.de/.well-known/security.txt, abuse@fu-berlin.de
https://smartsheet.com/.well-known/security.txt, security@smartsheet.com
https://meltwater.com/.well-known/security.txt, security@meltwater.com
https://ethereum.org/.well-known/security.txt, security@ethereum.org
 
"""
import json
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from urllib.parse import urlparse
import logging
# from app.services.sendReports.db.db_manager import *

from app.db.db_manager import DatabaseManager
from app.db.db_operations import DatabaseOperations

# from app.testDB.db_manager import DatabaseManager
# from app.testDB.db_operations import DatabaseOperations

db_config = {
    'dbname': 'test_monitor',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost'
}
db_manager = DatabaseManager(db_config)
db_ops = DatabaseOperations(db_manager)


# Gmail SMTP server details
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# Email credentials
SENDER_EMAIL = "riley.quinn.mail@gmail.com"  # Replace with your Gmail address
SENDER_PASSWORD = "mvto dzkn bsoi hgmv"      # Replace with your Gmail app password

# Log files
SUCCESS_LOG = "email_success.log"
FAILURE_LOG = "email_failure.log"

# Store domains from success logs
processed_domains = set()

logging.basicConfig(
    level=logging.INFO,  # Set logging level to DEBUG
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('endpoint_monitor.log', mode='a'),  # Append mode for the log file
        logging.StreamHandler()  # Print logs to the terminal
    ]
)

# Create a logger for the class
logger = logging.getLogger()  # Use the class name for better context
logger.setLevel(logging.INFO)  # Ensure the logger level is set to DEBUG


# Function to send email
def send_email(program_name, program_url, technology, email, poc_path, target_package, target_apk, download_url, attachment_url, report_form, acquisitions):
    receiver_email = email
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Vulnerability Disclosure Report - {program_name}"
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Vulnerability Report</title>
    <style>
        body {{
            font-family: Georgia, serif;
            background-color: #f8f9fa;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
            margin: 0;

        }}
        .container {{
            margin: 0 auto;
            max-width: 800px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: left;
            overflow-y: auto;
        }}
        h1 {{
            font-size: 28px;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        h2 {{
            font-size: 22px;
            color: #34495e;
            border-bottom: 2px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }}
        h3 {{
            font-size: 18px;
            color: #2c3e50;
            margin-top: 20px;
        }}
        p {{
            font-size: 16px;
            color: #555;
            report-height: 1.6;
            margin-bottom: 10px;
        }}
        .code-block {{
            background: #f4f4f4;
            padding: 10px;
            border-left: 4px solid #2c3e50;
            font-family: "Courier New", monospace;
            font-size: 14px;
            overflow-x: auto;
            white-space: pre-wrap;
            margin-bottom: 15px;
        }}
        .footer {{
            text-align: center;
            font-size: 14px;
            color: #7f8c8d;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Security Vulnerability Report</h1>
        <h2>StrandHogg Bug in {program_name} Android App</h2>
        
        <h3>Description</h3>
        <p>The StrandHogg vulnerability allows a malicious application to pose as the legitimate {program_name} app and perform various unauthorized actions on behalf of the user. It exploits a flaw in Android's multitasking system, enabling attackers to hijack user sessions and gain access to sensitive information.</p>
        
        <h3>Proof of Concept (PoC)</h3>
        <h4>PoC video is attached for better understanding</h4>
        <p>
            1. Install a malicious app on the same device as the {program_name} app.<br>
            2. Launch the malicious app, then open {program_name}. Clicking back triggers the vulnerability.<br>
            3. The malicious app appears as the {program_name} app on the device screen.<br>
            4. Interacting with the fake app allows attackers to steal credentials and data.<br>
        </p>
        
        <h3>Building PoC APK</h3>
        <p>Follow these steps to build the PoC APK:</p>
        <div class="code-block">
&lt;manifest<br>
    android:compileSdkVersion="33"<br>
    package="dev.lucasnlm.strandhogg"<br>
    xmlns:android="http://schemas.android.com/apk/res/android"&gt;<br>
    &lt;application<br>
        android:theme="@style/AppTheme"<br>
        android:label="@string/app_name"<br>
        android:debuggable="true"&gt;<br>
        &lt;activity<br>
            android:name="ch.nexusinformatik.strandhogg.InoffensiveActivity"<br>
            android:launchMode="singleInstance"&gt;<br>
        &lt;/activity&gt;<br>
        &lt;activity<br>
            android:name="ch.nexusinformatik.strandhogg.FakeLoginActivity"<br>
            android:exported="true"<br>
            android:taskAffinity="com.example.android"&gt;<br>
        &lt;/activity&gt;<br>
    &lt;/application&gt;<br>
&lt;/manifest&gt;
        </div>
        
        <h3>Verifying the Exploit</h3>
        <p>
            1. Open the target app and send it to the background.<br>
            2. Launch the exploit app.<br>
            3. Resume the target app. If the exploit activity appears instead, the attack is successful.<br>
        </p>
        
        <h3>Impact</h3>
        <p>
            - <strong>Credential Theft:</strong> Attackers can steal user login credentials.<br>
            - <strong>Data Exposure:</strong> Personal and sensitive data can be compromised.<br>
            - <strong>Financial Loss:</strong> Fraudulent transactions may be initiated.<br>
            - <strong>Unauthorized Actions:</strong> Attackers can manipulate app functionalities.<br>
        </p>
        
        <h3>Remediation</h3>
        <p>To mitigate this vulnerability, consider implementing the following:</p>
        <div class="code-block">Set launchMode to singleInstance</div>
        <div class="code-block">Override onBackPressed()</div>
        <div class="code-block">Set taskAffinity=""</div>
        
        <h3>Conclusion</h3>
        <p>Addressing the StrandHogg vulnerability is critical to ensuring user security. Implementing the recommended mitigations will help prevent attackers from exploiting this issue.</p>
        
        <p class="footer">Best Regards,<br>Riley Quinn</p>
    </div>
</body>
</html>

    """
    responses = []

    part = MIMEText(html_content, "html")
    message.attach(part)
    if poc_path != None:
        try:
            with open(poc_path, "rb") as attachment:
                poc_part = MIMEBase("application", "octet-stream")
                poc_part.set_payload(attachment.read())
                encoders.encode_base64(poc_part)
                poc_part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(poc_path)}")
                message.attach(poc_part)
        except Exception as e:
            print(f"[FILE NOT FOUND] Attachment file not found - [{e}]")
            responses.append(f"Error: Attachment file not found: [{e}]")
            responses.append(f"Error: Email not sent")
            return responses
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            # server.login(SENDER_EMAIL, SENDER_PASSWORD)
            # server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
            print(f"[FAKE] - Mail sent [{email}] - [{target_package}]")
            responses.append("Success: Email Sent!")

        result = log_success(program_name, program_url, technology, email, poc_path, target_package, target_apk, download_url, attachment_url, report_form, acquisitions)
        if result is not None:
            responses.extend(result)
        
    except Exception as e:
        logging.exception("An error occurred")
        log_failure(email, str(e))
        print(f"Email not sent: [{e}]")
        responses.append(f"Error: Email not sent: {e}")
        
    return responses
# Function to log successful emails
def log_success(program_name, program_url, technology, email, poc_path, target_package, target_apk, download_url, attachment_url, report_form, acquisitions):
    responses = []
    if db_ops.query_operations().check_program_exists(program_name=program_name):
        logger.info(f"Program [{program_name}] exists.")
        if db_ops.query_operations().check_mobile_target_exists(target_package):
            logger.info(f"Target [{target_package}] exists.")

            target_id = db_ops.query_operations().get_mobile_target_data(target_package=target_package)[0][0]
            logger.info(f"Got mobile target data {target_id}")
            db_ops.update_operations().update_mobile_target_vuln(target_id, vulnerability_reported={'vulnerability_reported': 'Strandhog'})
            logger.info(f"Updated mobile target vuln for {target_package}")

        else:
        # Insert Target
            logger.info(f"Target [{target_package}] doesn't exists.")
            program_id = db_ops.query_operations().get_program_details(program_name=program_name)[0][0] # Get Program ID
            logger.info(f"Got program ID [{program_id}]")

            mobile_target_data = {
                'program_id': program_id,
                'target_package': target_package,
                'target_apk': target_apk,
                'technology': technology,
                'download_url': download_url,
                'vulnerability_reported': ['Strandhog']
            }
            
            db_ops.insert_operations().insert_mobile_target(mobile_target_data)
            logger.info(f"Created target [{target_package}]")

    else:
        logger.info(f"Program {program_name} doesn't exists")
        
        program_data = {
            'program_name': program_name,
            'program_url': program_url,
            'acquisitions': acquisitions,
            'email': email,
            'report_form': report_form
        }
        # Insert Program
        program_id = db_ops.insert_operations().insert_program(program_data)
        logger.info(f"Created progam [{program_id}]")

        
        # Insert Target
                    
        mobile_target_data = {
            'program_id': program_id,
            'target_package': target_package,
            'target_apk': target_apk,
            'technology': technology,
            'download_url': download_url,
            'vulnerability_reported': ['Strandhog']
        }
        
        target_id = db_ops.insert_operations().insert_mobile_target(mobile_target_data)
        logger.info(f"Created target [{target_package}] - [{target_id}]")
        
    with open(SUCCESS_LOG, "a") as f:
        f.write(f"{datetime.now()} - Email sent to: {email}\n")

# Function to log failed emails
def log_failure(email, error):
    with open(FAILURE_LOG, "a") as f:
        f.write(f"{datetime.now()} - Failed to send email to: {email} - Error: {error}\n")


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
        
    if db_ops.query_operations().check_mobile_target_vuln_exists(vulnerability_reported="Strandhog", target_package=target_package):
        print(f"[ALREADY REPORTED] [Strandhog] - [{target_package}]")
        responses.append(f"Info: Already reported!")
        return responses
    try:
        poc_path = report.get("poc_path", None)
        if poc_path == "":
            poc_path = None
        if poc_path:
            print(f"[INFO] Attachment provided - [{target_package}] - [{poc_path}]")
            responses.append(f"Info: Attachment provided: [{poc_path}]")
        else:
            print(f"[INFO] No attachment provided - [{target_package}]")
            responses.append(f"Info: Attachment not provided")
    except Exception as e:
        poc_path = None
        print(f"[INFO] No attachment provided - [{target_package}]")
        responses.append(f"Error: Attachment not provided: [{e}]")
    print(f"[INFO] Sending email [{program_name}] - [{email}]")
    if responses.extend(send_email(program_name, program_url, technology, email, poc_path, target_package, target_apk, download_url, attachment_url, report_form, acquisitions)):
        processed_domains.add(program_name)
                
    return responses
# Main function
def strandhog_send_mail(report):
    global processed_domains
    
    # parser = argparse.ArgumentParser(description="Send emails to domain security contacts.")
    # parser.add_argument("-f", "--file", required=True, help="File containing list of URLs/domains")
    # args = parser.parse_args()
    # if process_file(reports):
        # return f"Mail sent successfully to {reports[0]["email"]}"
    # else: 
        # return "Something went wrong"
    return process_file(report)