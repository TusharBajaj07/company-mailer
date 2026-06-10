import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailThreadReply:
    def __init__(self):
        """Initialize Gmail API for sending threaded replies"""
        load_dotenv()
        
        # Gmail API Configuration - Using full access scope
        self.scopes = ['https://mail.google.com/']
        self.sender_email = "training@iitb.ac.in"
        self.sender_name = "Practical Training Cell"
        
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

    def get_original_message_details(self, message_id: str):
        """Retrieve original message details including threadId, Message-ID, subject, and recipient"""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract threadId
            thread_id = message.get('threadId', '')
            
            # Extract headers
            headers = message['payload']['headers']
            message_id_header = None
            subject = None
            to_email = None
            
            for header in headers:
                if header['name'].lower() == 'message-id':
                    message_id_header = header['value']
                elif header['name'].lower() == 'subject':
                    subject = header['value']
                elif header['name'].lower() == 'to':
                    to_email = header['value']
            
            print(f"✅ Original message details retrieved:")
            print(f"   Thread ID: {thread_id}")
            print(f"   Message-ID: {message_id_header}")
            print(f"   Subject: {subject}")
            print(f"   To: {to_email}")
            
            return {
                'thread_id': thread_id,
                'message_id_header': message_id_header,
                'subject': subject,
                'to_email': to_email
            }
            
        except Exception as e:
            print(f"❌ Error retrieving message details: {e}")
            return None

    def send_threaded_reply(self, original_message_id: str, reply_text: str):
        """Send a reply in the same thread as the original message"""
        try:
            # Get original message details
            original_details = self.get_original_message_details(original_message_id)
            
            if not original_details:
                print("❌ Could not retrieve original message details")
                return False
            
            # Extract email address if it contains name (e.g., "Name <email@example.com>")
            to_email = original_details['to_email']
            if '<' in to_email and '>' in to_email:
                to_email = to_email.split('<')[1].split('>')[0]
            
            # Create reply message
            message = MIMEMultipart('related')
            message['From'] = formataddr((self.sender_name, self.sender_email))
            message['To'] = to_email
            
            # Add "Re:" to subject if not already present
            subject = original_details['subject']
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"
            message['Subject'] = subject
            
            # Set threading headers
            message['In-Reply-To'] = original_details['message_id_header']
            message['References'] = original_details['message_id_header']
            
            # Add message body
            msg_alt = MIMEMultipart('alternative')
            message.attach(msg_alt)
            
            html_body = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body>
    <div style="font-size:small; font-family: Arial, sans-serif; line-height: 1.4; color: #333;">
        <p>{reply_text}</p>
    </div>
</body>
</html>'''
            
            msg_alt.attach(MIMEText(html_body, 'html'))
            
            # Encode message
            raw_msg = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Send with threadId to ensure threading
            sent_message = self.gmail_service.users().messages().send(
                userId='me',
                body={
                    'raw': raw_msg,
                    'threadId': original_details['thread_id']
                }
            ).execute()
            
            reply_message_id = sent_message.get('id', '')
            
            print(f"\n✅ Reply sent successfully!")
            print(f"   Reply Message ID: {reply_message_id}")
            print(f"   Thread ID: {original_details['thread_id']}")
            print(f"   To: {to_email}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send reply: {e}")
            return False


def main():
    print("🚀 Gmail Thread Reply Tool")
    print("=" * 60)
    
    # Initialize the reply system
    try:
        reply_system = GmailThreadReply()
        print("✅ Gmail API authenticated with FULL ACCESS scope\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Get message ID from user
    print("Enter the Gmail API Message ID you want to reply to:")
    print("(Example: 19a07cb8e67d7594)")
    message_id = input("\nMessage ID: ").strip()
    
    if not message_id:
        print("❌ No message ID provided")
        return
    
    print(f"\n📧 Retrieving original message details...")
    
    # Send the reply
    success = reply_system.send_threaded_reply(
        original_message_id=message_id,
        reply_text="this is a test mail"
    )
    
    if success:
        print("\n🎉 Reply sent successfully in the same thread!")
    else:
        print("\n❌ Failed to send reply")


if __name__ == "__main__":

    main()
