import os
import base64
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
import time

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailAutoMailer:
    def __init__(self):
        """Initialize Gmail API for automated email sending"""
        load_dotenv()
        
        # Gmail API Configuration - Using full access scope
        self.scopes = ['https://mail.google.com/']
        self.sender_email = "training@iitb.ac.in"
        self.sender_name = "Tushar Bajaj"
        
        # Initialize Gmail API service
        self.gmail_service = self.authenticate_gmail()
    
    
    def authenticate_gmail(self):
        """Authenticate with Gmail API using OAuth2"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise ValueError("credentials.json file not found. Please download it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    
    def read_companies_from_csv(self, csv_file):
        """Read company names and emails from CSV file"""
        companies = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, skipinitialspace=True)
                
                for row in reader:
                    company_name = row['name'].strip()
                    email_addresses = [email.strip() for email in row['email'].split(',')]
                    
                    companies.append({
                        'name': company_name,
                        'emails': email_addresses
                    })
            
            print(f"✅ Successfully loaded {len(companies)} companies from CSV")
            return companies
            
        except FileNotFoundError:
            print(f"❌ CSV file '{csv_file}' not found")
            return []
        except Exception as e:
            print(f"❌ Error reading CSV: {e}")
            return []
    
    
    def create_email_html(self, company_name):
        """Create HTML email body with company name"""
        html_body = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <div dir="ltr">
        <div class="gmail_default" style="font-family:arial,sans-serif;font-size:small;color:#000000">
            <div class="gmail_default">
                <div class="gmail_default">
                    <div class="gmail_default">
                        Dear Team,<br><br>
                        Warm greetings from the Placement Office, Indian Institute of Technology Bombay.<br><br>
                        On behalf of the Placement Office of IIT Bombay, I, Tushar Bajaj, an Internship Coordinator (2025-2026), hereby invite <b>{company_name}</b> for campus recruitment 2025-2026.
                    </div>
                    <div class="gmail_default">
                        <br>
                        IIT Bombay has been ranked 28th in Engineering and Technology in the Quacquarelli Symonds (QS) World University Rankings for 2025, making it India's leading technical institute with an acceptance rate of less than 2%. This year with 2250+ graduates across 17 different departments, 6 research centers, 1 Design Centre, 3 Interdisciplinary Programs and 11 programs, namely BTech, 4-year BS/BDes, Dual Degree (BTech + MTech), MTech, MSc, MS By Research, MA by Research, Masters in Public Policy, MDes, and PhD is organizing its campus recruitment to connect its students with prestigious organization like yours where students can utilize their potential to contribute towards accelerated growth and success of organization.<br><br>
                        
                        <b>Our Campus Placement Timeline:</b><br><br>
                        Company Registration Begins: August 2025<br>
                        Job Announcement Form (JAF) Opening: September 2025<br>
                        Assessments Begin: September-end 2025<br>
                        Interviews: Starting from 1st December 2025<br>
                        Joining Date: June to August 2026<br><br>
                        
                        I would also like to invite you to recruit students from our campus for <b>summer/winter internships</b> at your organization. Doing so would further strengthen our association with your organization. Please let me know if there are any internship opportunities at your organization.<br><br>
                        
                        Requesting you to provide the contact details (phone number and email ID), of a point of contact if interested in recruitment for further communication regarding the placement process. We would appreciate your presence in the upcoming recruitment session.<br><br>
                        
                        Thanks and Regards,
                    </div>
                </div>
                <div><br></div>
            </div>
            <div style="color:rgb(34,34,34);font-family:Arial,Helvetica,sans-serif">
                <div dir="ltr">
                    <div dir="ltr">
                        <table style="color:rgb(0,0,0);font-family:arial,helvetica,sans-serif;border-width:medium;border-style:none;border-collapse:collapse">
                            <tbody>
                                <tr style="height:0pt">
                                    <td style="padding:5pt; border-right:1.5pt solid rgb(17,85,204); vertical-align:top;">
                                        <p dir="ltr" style="margin-top:0pt; margin-bottom:0pt; line-height:1.2;">
                                            <span style="font-size:11pt; font-family:Arial; background-color:transparent; vertical-align:baseline;">
                                                <img src="cid:iitb_logo" 
                                                    width="101" 
                                                    height="87" 
                                                    style="border-width: medium; border-style: none;" 
                                                    alt="IIT Bombay Logo">
                                            </span>
                                        </p>
                                    </td>
                                    <td style="padding:5pt;border-left:1.5pt solid rgb(17,85,204);vertical-align:top">
                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.2">
                                            <font color="#3d85c6" face="georgia"><span style="font-size:16px"><b>Tushar Bajaj</b></span></font>
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
                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.38;font-size:12.8px;color:rgb(80,0,80)">
                                            <span style="font-size:9.5pt;font-family:georgia;vertical-align:baseline">
                                                <font color="#666666">Contact: (+91) 92058111174 | <a href="https://www.linkedin.com/in/tushar-bajaj-207b79221" target="_blank">LinkedIn</a></font>
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
</body>
</html>'''
        
        return html_body
    
    
    def send_email_with_bcc(self, company_name, email_addresses):
        """Send email with all recipients in BCC and embedded logo"""
        try:
            # Create MIME message
            message = MIMEMultipart('related')
            message['From'] = formataddr((self.sender_name, self.sender_email))
            # Do NOT set the 'To' field - leave it empty for BCC-only emails
            message['Bcc'] = ', '.join(email_addresses)
            message['Subject'] = 'IIT Bombay | Invitation to Campus Recruitment 2025-2026'
            
            # Create HTML body
            msg_alt = MIMEMultipart('alternative')
            message.attach(msg_alt)
            
            html_body = self.create_email_html(company_name)
            msg_alt.attach(MIMEText(html_body, 'html'))
            
            # Attach the IIT Bombay logo as an embedded image
            try:
                with open('logo.png', 'rb') as fp:
                    msgImage = MIMEImage(fp.read())
                    # Define the image's Content-ID as referenced in HTML
                    msgImage.add_header('Content-ID', '<iitb_logo>')
                    msgImage.add_header('Content-Disposition', 'inline', filename='logo.png')
                    message.attach(msgImage)
            except FileNotFoundError:
                print(f"⚠️  Warning: logo.png not found. Email will be sent without logo.")
            except Exception as img_error:
                print(f"⚠️  Warning: Could not attach logo: {img_error}")
            
            # Encode message
            raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send email
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_msg}
            ).execute()
            
            message_id = sent_message.get('id', '')
            
            print(f"✅ Email sent to {company_name}")
            print(f"   Message ID: {message_id}")
            print(f"   BCC Recipients: {', '.join(email_addresses)}")
            
            return True
            
        except HttpError as error:
            print(f"❌ HTTP Error for {company_name}: {error}")
            return False
        except Exception as e:
            print(f"❌ Failed to send email to {company_name}: {e}")
            return False
    
    
    def send_bulk_emails(self, csv_file, delay_seconds=2):
        """Send emails to all companies in CSV file with delay between sends"""
        companies = self.read_companies_from_csv(csv_file)
        
        if not companies:
            print("❌ No companies to process")
            return
        
        print(f"\n🚀 Starting bulk email campaign...")
        print(f"   Total companies: {len(companies)}")
        print(f"   Delay between emails: {delay_seconds} seconds\n")
        
        success_count = 0
        failed_count = 0
        
        for idx, company in enumerate(companies, 1):
            print(f"\n[{idx}/{len(companies)}] Processing: {company['name']}")
            
            success = self.send_email_with_bcc(
                company_name=company['name'],
                email_addresses=company['emails']
            )
            
            if success:
                success_count += 1
            else:
                failed_count += 1
            
            # Add delay between sends to avoid rate limiting (except for last email)
            if idx < len(companies):
                print(f"   Waiting {delay_seconds} seconds before next send...")
                time.sleep(delay_seconds)
        
        print(f"\n{'='*60}")
        print(f"📊 Campaign Summary:")
        print(f"   Total: {len(companies)}")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"{'='*60}")


def main():
    print("=" * 60)
    print("🚀 IIT Bombay Automated Email Campaign System")
    print("=" * 60)
    
    # Initialize the mailer
    try:
        mailer = GmailAutoMailer()
        print("✅ Gmail API authenticated successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # CSV file path
    csv_file = "companies.csv"
    
    # Send bulk emails with 2-second delay between sends
    mailer.send_bulk_emails(csv_file, delay_seconds=2)


if __name__ == "__main__":
    main()
