import os
import time
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import formataddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIGURATION ---
SPREADSHEET_ID = '1EaMSsBBDcNGjDc3R8_axEVGxk1GpgSiSRCxhAjVAUNY'  # <--- PASTE YOUR SHEET ID HERE
SHEET_NAME = 'Sheet1'  # Name of the tab
# ---------------------

class GSheetOutreach:
    def __init__(self):
        # We need both Gmail (send) and Sheets (read/write) scopes
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        self.sender_email = "training@iitb.ac.in" 
        self.sender_name = "IIT Bombay, Practical Training Cell"
        
        # Authenticate (Handles both Gmail and Sheets)
        self.creds = self.authenticate_google()
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)
        self.sheet_service = build('sheets', 'v4', credentials=self.creds)
        
        # Load IC Data (Local CSV remains best for static contacts, or you can hardcode)
        self.ic_dict = self.load_local_ic_contacts("contacts.csv")

    def authenticate_google(self):
        creds = None
        # Use existing token if available
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.scopes)
        
        # If no valid token, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    # If refresh fails (e.g. scopes changed), force re-login
                    os.remove('token.json')
                    return self.authenticate_google()
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save the new token
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def load_local_ic_contacts(self, csv_file):
        """Helper to load IC contacts from local file"""
        import pandas as pd
        try:
            df = pd.read_csv(csv_file)
            ic_map = {}
            for _, row in df.iterrows():
                ic_map[row['name_IC']] = {
                    'name': row['name_IC'],
                    'phone': row['ph_no'],
                    'linkedin': row['linkedin_link']
                }
            print(f"✅ Loaded {len(ic_map)} IC contacts locally.")
            return ic_map
        except Exception as e:
            print(f"⚠️ Could not load contacts.csv: {e}")
            return {}

    def get_ic_details(self, ic_name):
        if ic_name in self.ic_dict:
            return self.ic_dict[ic_name]
        else:
            print(f"⚠️ IC '{ic_name}' not found. Using default (Tushar Bajaj).")
            return {
                'name': 'Tushar Bajaj',
                'phone': '(+91) 9205811174',
                'linkedin': 'https://www.linkedin.com/in/tushar-bajaj-207b79221/'
            }

    def generate_html_body(self, recipient_name, company_name, ic_details):
        first_name = recipient_name.split()[0] if recipient_name else "There"
        
        # (Keeping your HTML template identical)
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
                                        <font face="arial, sans-serif">Greetings from the <b>Placement Cell, IIT Bombay</b>!</font>
                                    </span>
                                </div>
                                <div>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)"><br>
                                        I'm <b>{ic_details['name']}</b>,<span class="gmail_default" style="color:rgb(0,0,0)"> </span>an Internship Coordinator at IIT Bombay. On behalf of the Practical
                                    </font>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)"> Training Cell of IIT Bombay, I cordially invite </font>
                                    <b>{company_name} </b>
                                    <font face="arial, sans-serif" style="color:rgb(34,34,34)">to 
                                        <span class="gmail_default" style="color:rgb(0,0,0)">participate in</span> the <b>summer internship</b> recruitment process for the year <b>2025-26</b>.
                                    </font>
                                </div>
                                <div class="gmail_default">
                                    <div class="gmail_default">
                                        <font face="arial, sans-serif" style="color:rgb(34,34,34)"><br>
                                            At IIT Bombay, students take up summer internships to gain first-hand experience <span class="gmail_default" style="color:rgb(0,0,0)">in</span> the professional world after the end of the second or third year of their studies. We can vouch for the credibility and genuineness of the students and would also like to add that being among the best students in India, they are not only good academically but also possess an excellent ability to solve problems and apply themselves to practical situations.<br><br>
                                            The duration of the summer internship <span class="gmail_default" style="color:rgb(0,0,0)">will be of<b> 8</b></span><b><span class="gmail_default">-9</span> weeks</b>,<span class="gmail_default" style="color:rgb(0,0,0)"></span> starting <span class="gmail_default" style="color:rgb(0,0,0)">in</span> the <b>second week of May</b> and extending till 
                                        </font>
                                        <font face="arial, sans-serif" style="color:rgb(34,34,34)">
                                            <b><font color="#000000">mid </font>July</b>
                                            <span class="gmail_default"><font color="#000000">.<br></font></span>
                                            <font color="#000000"><br></font>
                                            I would be grateful if you could inform us of the <b>summer internship opportunities</b> with you this year so that the students of IIT Bombay can hope to be a part of your prestigious organization.
                                        </font>
                                        <div style="font-family:Arial,Helvetica,sans-serif;color:rgb(34,34,34)">
                                            <font face="arial, sans-serif"><br>In case of any queries, feel free to reach out to me at the undersigned number. </font>
                                        </div>
                                        <div style="font-family:Arial,Helvetica,sans-serif;color:rgb(34,34,34)">
                                            <font face="arial, sans-serif"><font color="#000000"><br></font>Thanks and Regards,</font>
                                        </div>
                                        <br>
                                        <table style="font-family:arial,helvetica,sans-serif;border-width:medium;border-style:none;border-collapse:collapse">
                                            <tbody>
                                                <tr style="height:0pt">
                                                    <td style="padding:5pt;border-right:1.5pt solid rgb(17,85,204);vertical-align:top">
                                                        <p dir="ltr" style="margin-top:0pt;margin-bottom:0pt;line-height:1.2">
                                                            <span style="font-size:11pt;font-family:Arial;background-color:transparent;vertical-align:baseline">
                                                                <img src="cid:iitb_logo" width="101" height="87" class="gmail-CToWUd" style="border-width: medium; border-style: none;">
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
                                                                <font color="#666666">Contact: {ic_details['phone']} | </font>
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

    def send_email(self, to_email, subject, html_content, logo_path="logo.png"):
        try:
            message = MIMEMultipart('related')
            message['to'] = to_email
            message['from'] = formataddr((self.sender_name, self.sender_email))
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

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            sent_message = self.gmail_service.users().messages().send(userId='me', body={'raw': raw}).execute()
            return sent_message['id']
        except Exception as e:
            print(f"❌ Failed to send to {to_email}: {e}")
            return None

    def read_sheet_data(self):
        """Reads all data from the Google Sheet"""
        range_name = f"{SHEET_NAME}!A:G" # Assuming columns A to G
        result = self.sheet_service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
        rows = result.get('values', [])
        return rows

    def update_message_id(self, row_index, message_id):
        """Updates Column G (Message ID) for a specific row"""
        # Column G is the 7th column, so index 6 (0-based) but Sheet ranges are 1-based letters.
        # G is the 7th letter.
        # Row index in Sheets is 1-based. Python list is 0-based.
        # If we read the header as row 0, then data starts at row 1.
        
        range_name = f"{SHEET_NAME}!G{row_index + 1}"  # +1 because Sheets is 1-indexed
        body = {'values': [[message_id]]}
        
        self.sheet_service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=range_name,
            valueInputOption="RAW", body=body).execute()
        print(f"📝 Updated Sheet Row {row_index + 1} with ID.")

    def run_campaign(self):
        print("🌍 Connecting to Google Sheets...")
        rows = self.read_sheet_data()
        
        if not rows:
            print("⚠️ No data found in Sheet.")
            return

        headers = rows[0]
        # Map headers to indices
        try:
            idx_name = headers.index("Name")
            idx_email = headers.index("Emails")
            idx_company = headers.index("Company Name")
            idx_ic = headers.index("IC")
            idx_msg_id = headers.index("message ID")
        except ValueError as e:
            print(f"❌ Error: Missing column header in Sheet. Found: {headers}")
            print(f"Required: Name, Emails, Company Name, IC, message ID")
            return

        print(f"✅ Sheet loaded. Processing {len(rows)-1} entries...")

        # Loop through data rows (skip header)
        for i, row in enumerate(rows[1:], start=1):
            # Pad row if empty cells at end
            while len(row) <= idx_msg_id:
                row.append("")

            msg_id_val = row[idx_msg_id]
            
            # Check if already sent
            if msg_id_val and len(msg_id_val.strip()) > 5:
                continue

            name = row[idx_name]
            email = row[idx_email]
            company = row[idx_company]
            ic_name = row[idx_ic]

            ic_details = self.get_ic_details(ic_name)
            subject = f"IIT Bombay | Inviting {company} for Internship Recruitment 2025-26"
            html_body = self.generate_html_body(name, company, ic_details)

            print(f"📤 Sending to {company} ({email})...")
            
            new_msg_id = self.send_email(email, subject, html_body)
            
            if new_msg_id:
                print(f"✅ Sent! Updating Sheet...")
                # Update the specific cell in Google Sheets
                self.update_message_id(i, new_msg_id)
                time.sleep(2) # Avoid rate limits

        print("\n🎉 Google Sheet Campaign Complete!")

if __name__ == "__main__":
    # IMPORTANT: Delete your old token.json before running this!
    # Because we added a new Scope (Sheets).
    if os.path.exists('token.json'):
        print("🔄 Deleting old token.json to refresh permissions...")
        os.remove('token.json')
        
    campaign = GSheetOutreach()
    campaign.run_campaign()