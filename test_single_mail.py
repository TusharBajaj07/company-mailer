import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- TEST CONFIG ---
TO_EMAIL = "tusharbajaj2085@gmail.com"
COMPANY_NAME = "xyz"
IC_DETAILS = {
    'name': 'Tushar Bajaj',
    'phone': '(+91) 9205811174',
    'linkedin': 'https://www.linkedin.com/in/tushar-bajaj-207b79221/'
}
LOGO_PATH = "logo.png"
# -------------------

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SENDER_EMAIL = "training@iitb.ac.in"
SENDER_NAME = "IIT Bombay, Practical Training Cell"


def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                os.remove('token.json')
                return authenticate_gmail()
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def generate_html_body(company_name, ic_details):
    html_content = f"""
<div dir="ltr">
    <div class="gmail_default" style="font-family:arial,sans-serif;font-size:small;color:#000000">
        <div style="margin:0px;min-width:0px;padding:0px 0px 20px;width:auto;color:rgb(34,34,34)">
            <div>
                <div style="direction:ltr;margin:8px 0px 0px;padding:0px;overflow-x:hidden">
                    <div style="direction:ltr;font-variant-numeric:normal;font-variant-east-asian:normal;font-variant-alternates:normal;font-size-adjust:none;font-kerning:auto;font-feature-settings:normal;font-stretch:normal;line-height:1.5;overflow:auto hidden">
                        <div dir="ltr">
                            <div class="gmail_default" style="color:rgb(0,0,0)">
                                <div style="font-family:Arial,Helvetica,sans-serif">
                                    <font face="arial, sans-serif">
                                        <span style="color:rgb(34,34,34)">Dear Team,<br><br></span>
                                    </font>
                                </div>
                                <div style="font-family:Arial,Helvetica,sans-serif">
                                    <span style="color:rgb(34,34,34)">
                                        <font face="arial, sans-serif">Greetings from the <b>Placement Cell, IIT Bombay</b>!</font>
                                    </span>
                                </div>
                                <div>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)"><br>
                                        I'm <b>{ic_details['name']}</b>, an Internship Coordinator at IIT Bombay. On behalf of the Practical
                                    </font>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)"> Training Cell of IIT Bombay, I cordially invite </font>
                                    <b>{company_name} </b>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)">to
                                        participate in the <b>summer internship</b> recruitment process for the year <b>2025-26</b>.
                                    </font>
                                </div>
                                <div class="gmail_default">
                                    <div class="gmail_default">
                                        <font face="arial, sans-serif" style="color:rgb(34,34,34)"><br>
                                            At IIT Bombay, students take up summer internships to gain first-hand experience in the professional world after the end of the second or third year of their studies. We can vouch for the credibility and genuineness of the students and would also like to add that being among the best students in India, they are not only good academically but also possess an excellent ability to solve problems and apply themselves to practical situations.<br><br>
                                            The duration of the summer internship will be of<b> 8-9 weeks</b>, starting in the <b>second week of May</b> and extending till
                                        </font>
                                        <font face="arial, sans-serif" style="color:rgb(34,34,34)">
                                            <b>mid July</b>.<br>
                                            <br>
                                            I would be grateful if you could inform us of the <b>summer internship opportunities</b> with you this year so that the students of IIT Bombay can hope to be a part of your prestigious organization.
                                        </font>
                                        <div style="font-family:Arial,Helvetica,sans-serif;color:rgb(34,34,34)">
                                            <font face="arial, sans-serif"><br>In case of any queries, feel free to reach out to me at the undersigned number. </font>
                                        </div>
                                        <div style="font-family:Arial,Helvetica,sans-serif;color:rgb(34,34,34)">
                                            <font face="arial, sans-serif"><br>Thanks and Regards,</font>
                                        </div>
                                        <br>
                                        <table style="font-family:arial,helvetica,sans-serif;border-width:medium;border-style:none;border-collapse:collapse">
                                            <tbody>
                                                <tr style="height:0pt">
                                                    <td style="padding:5pt;border-right:1.5pt solid rgb(17,85,204);vertical-align:top">
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.2">
                                                            <span style="font-size:11pt;font-family:Arial;background-color:transparent;vertical-align:baseline">
                                                                <img src="cid:iitb_logo" width="101" height="87" style="border-width: medium; border-style: none;">
                                                            </span>
                                                        </p>
                                                    </td>
                                                    <td style="padding:5pt;border-left:1.5pt solid rgb(17,85,204);vertical-align:top">
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.2">
                                                            <font color="#3d85c6" face="georgia"><span style="font-size:16px"><b>{ic_details['name']}</b></span></font>
                                                        </p>
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.38;color:rgb(34,34,34);font-size:12.8px">
                                                            <span style="font-size:9.5pt;font-family:georgia;color:rgb(102,102,102);vertical-align:baseline">Internship Coordinator</span>
                                                        </p>
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.38;color:rgb(34,34,34);font-size:12.8px">
                                                            <span style="font-size:9.5pt;font-family:georgia;color:rgb(102,102,102);vertical-align:baseline">Institute Placement Team 2025-26</span>
                                                        </p>
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.38;color:rgb(34,34,34);font-size:12.8px">
                                                            <span style="font-size:9.5pt;font-family:georgia;color:rgb(61,133,198);font-weight:700;vertical-align:baseline">Indian Institute of Technology, Bombay</span>
                                                        </p>
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.38;color:rgb(80,0,80)">
                                                            <span style="font-size:9.5pt;font-family:georgia;vertical-align:baseline">
                                                                <font color="#666666">Contact: {ic_details['phone']} | </font>
                                                            </span>
                                                            <span style="color:rgb(17,85,204);background-color:transparent;vertical-align:baseline">
                                                                <a href="{ic_details['linkedin']}" target="_blank"><font face="georgia, serif">LinkedIn</font></a>
                                                            </span>
                                                        </p>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""
    return html_content


def send_email(gmail_service, to_email, subject, html_content, logo_path):
    message = MIMEMultipart('related')
    message['to'] = to_email
    message['from'] = formataddr((SENDER_NAME, SENDER_EMAIL))
    message['subject'] = subject

    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)

    part_html = MIMEText(html_content, 'html')
    msg_alternative.attach(part_html)

    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            img_data = f.read()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', '<iitb_logo>')
        img.add_header('Content-Disposition', 'inline', filename='logo.png')
        message.attach(img)
    else:
        print(f"Warning: Logo not found at {logo_path}")

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return sent['id']


if __name__ == "__main__":
    # Step 1: Delete old token to force fresh auth
    if os.path.exists('token.json'):
        print("Deleting old token.json...")
        os.remove('token.json')

    # Step 2: Authenticate (opens browser for login)
    print("Authenticating with Gmail... (browser will open)")
    creds = authenticate_gmail()
    gmail_service = build('gmail', 'v1', credentials=creds)
    print("Authentication successful! Token saved.")

    # Step 3: Send test email
    subject = f"IIT Bombay | Inviting {COMPANY_NAME} for Internship Recruitment 2025-26"
    html_body = generate_html_body(COMPANY_NAME, IC_DETAILS)

    print(f"\nSending test email to {TO_EMAIL}...")
    msg_id = send_email(gmail_service, TO_EMAIL, subject, html_body, LOGO_PATH)
    print(f"Email sent successfully! Message ID: {msg_id}")
