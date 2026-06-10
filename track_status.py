import os
import base64
import csv
import pandas as pd
from datetime import datetime
from email.utils import parsedate_to_datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailThreadTracker:
    def __init__(self):
        """Initialize Gmail API for tracking email threads"""
        load_dotenv()
        
        # Gmail API Configuration
        self.scopes = ['https://mail.google.com/']
        self.sender_email = "training@iitb.ac.in"  # Your email address
        
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
                    raise ValueError("credentials.json file not found.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    
    def get_message_body(self, payload):
        """Extract message body from payload"""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        if 'data' in part['body']:
                            return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif 'parts' in part:
                        # Recursive call for nested parts
                        return self.get_message_body(part)
            elif 'body' in payload and 'data' in payload['body']:
                return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            
            return ""
        except Exception as e:
            return ""
    
    
    def parse_message_details(self, message):
        """Parse individual message details from thread"""
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        # Extract headers
        from_email = ""
        to_email = ""
        subject = ""
        date_str = ""
        
        for header in headers:
            name = header['name'].lower()
            if name == 'from':
                from_email = header['value']
            elif name == 'to':
                to_email = header['value']
            elif name == 'subject':
                subject = header['value']
            elif name == 'date':
                date_str = header['value']
        
        # Parse date
        try:
            date_obj = parsedate_to_datetime(date_str)
            formatted_date = date_obj.strftime('%d %b')  # e.g., "14 Oct"
        except:
            formatted_date = date_str[:10] if date_str else "Unknown date"
        
        # Check if message is SENT by you or RECEIVED
        label_ids = message.get('labelIds', [])
        is_sent = 'SENT' in label_ids
        
        # Get snippet/preview
        snippet = message.get('snippet', '')
        
        return {
            'from': from_email,
            'to': to_email,
            'subject': subject,
            'date': formatted_date,
            'date_str': date_str,
            'is_sent': is_sent,
            'snippet': snippet,
            'label_ids': label_ids
        }
    
    
    def create_thread_timeline(self, messages):
        """Create chronological timeline of thread messages"""
        timeline = []
        
        for idx, message in enumerate(messages):
            details = self.parse_message_details(message)
            
            if idx == 0:
                # First message - the original email sent
                description = "Mail sent"
            else:
                # Subsequent messages
                if details['is_sent']:
                    # You sent a reply
                    description = f"Reply sent"
                else:
                    # You received a reply
                    # Extract name from email if possible
                    from_name = details['from'].split('<')[0].strip() if '<' in details['from'] else details['from']
                    if from_name.startswith('"') and from_name.endswith('"'):
                        from_name = from_name[1:-1]
                    
                    # Shorten snippet for description
                    snippet_preview = details['snippet'][:60] + "..." if len(details['snippet']) > 60 else details['snippet']
                    description = f"Reply from {from_name}: {snippet_preview}"
            
            timeline.append(f"{details['date']} - {description}")
        
        return " | ".join(timeline)
    
    
    def get_thread_status(self, message_id):
        """Get thread status and details for a given message ID"""
        try:
            # Get the original message to find its thread ID
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            thread_id = message.get('threadId', '')
            
            # Get the entire thread
            thread = self.gmail_service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()
            
            messages = thread.get('messages', [])
            message_count = len(messages)
            
            # Check if original message is read
            original_labels = message.get('labelIds', [])
            is_read = 'UNREAD' not in original_labels
            
            # Determine status
            if message_count > 1:
                status = "REPLIED"
            elif is_read:
                status = "READ"
            else:
                status = "UNREAD"
            
            # Create chronological timeline comment
            timeline_comment = self.create_thread_timeline(messages)
            
            # Get the latest message details
            latest_message = messages[-1]
            latest_details = self.parse_message_details(latest_message)
            
            return {
                'status': status,
                'thread_id': thread_id,
                'message_count': message_count,
                'reply_count': message_count - 1,
                'is_read': is_read,
                'latest_from': latest_details['from'],
                'latest_date': latest_details['date'],
                'latest_snippet': latest_details['snippet'],
                'comment': timeline_comment
            }
            
        except HttpError as error:
            print(f"❌ HTTP Error for message {message_id}: {error}")
            return {
                'status': 'ERROR',
                'thread_id': '',
                'message_count': 0,
                'reply_count': 0,
                'is_read': False,
                'latest_from': '',
                'latest_date': '',
                'latest_snippet': '',
                'comment': f'Error: {error}'
            }
        except Exception as e:
            print(f"❌ Error for message {message_id}: {e}")
            return {
                'status': 'ERROR',
                'thread_id': '',
                'message_count': 0,
                'reply_count': 0,
                'is_read': False,
                'latest_from': '',
                'latest_date': '',
                'latest_snippet': '',
                'comment': f'Error: {str(e)}'
            }
    
    
    def track_emails_from_csv(self, csv_file, output_file=None):
        """Track email status for all messages in CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            print(f"\n📊 Tracking {len(df)} emails from CSV...")
            print("=" * 100)
            
            # Check if message_id column exists
            if 'message_id' not in df.columns:
                print("❌ Error: 'message_id' column not found in CSV")
                return
            
            # Initialize new columns if they don't exist
            if 'status' not in df.columns:
                df['status'] = ''
            if 'thread_id' not in df.columns:
                df['thread_id'] = ''
            if 'message_count' not in df.columns:
                df['message_count'] = 0
            if 'reply_count' not in df.columns:
                df['reply_count'] = 0
            if 'is_read' not in df.columns:
                df['is_read'] = False
            if 'latest_from' not in df.columns:
                df['latest_from'] = ''
            if 'latest_date' not in df.columns:
                df['latest_date'] = ''
            if 'latest_snippet' not in df.columns:
                df['latest_snippet'] = ''
            if 'comment' not in df.columns:
                df['comment'] = ''
            if 'checked_at' not in df.columns:
                df['checked_at'] = ''
            
            # Track each email
            for idx, row in df.iterrows():
                message_id = row['message_id']
                
                if pd.isna(message_id) or message_id == '':
                    print(f"\n[{idx + 1}/{len(df)}] Skipping row {idx + 1} - No message_id")
                    df.at[idx, 'status'] = 'NO_MESSAGE_ID'
                    df.at[idx, 'comment'] = 'Message ID not found'
                    continue
                
                company_name = row.get('name', 'N/A')
                email = row.get('email', 'N/A')
                
                print(f"\n[{idx + 1}/{len(df)}] Tracking: {company_name} ({email})")
                print(f"   Message ID: {message_id}")
                
                # Get thread status
                thread_info = self.get_thread_status(message_id)
                
                # Update dataframe
                df.at[idx, 'status'] = thread_info['status']
                df.at[idx, 'thread_id'] = thread_info['thread_id']
                df.at[idx, 'message_count'] = thread_info['message_count']
                df.at[idx, 'reply_count'] = thread_info['reply_count']
                df.at[idx, 'is_read'] = thread_info['is_read']
                df.at[idx, 'latest_from'] = thread_info['latest_from']
                df.at[idx, 'latest_date'] = thread_info['latest_date']
                df.at[idx, 'latest_snippet'] = thread_info['latest_snippet']
                df.at[idx, 'comment'] = thread_info['comment']
                df.at[idx, 'checked_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"   ✅ Status: {thread_info['status']}")
                print(f"   Messages in thread: {thread_info['message_count']}")
                print(f"   Timeline: {thread_info['comment'][:150]}...")
            
            # Save updated CSV
            if output_file is None:
                output_file = csv_file.replace('.csv', '_tracked.csv')
            
            df.to_csv(output_file, index=False)
            
            print(f"\n{'=' * 100}")
            print(f"✅ Tracking complete!")
            print(f"📁 Updated CSV saved to: {output_file}")
            
            # Print summary statistics
            print(f"\n📊 Summary:")
            print(f"   Total emails tracked: {len(df)}")
            print(f"   Replied: {len(df[df['status'] == 'REPLIED'])}")
            print(f"   Read (no reply): {len(df[df['status'] == 'READ'])}")
            print(f"   Unread: {len(df[df['status'] == 'UNREAD'])}")
            print(f"   Errors: {len(df[df['status'] == 'ERROR'])}")
            print(f"{'=' * 100}\n")
            
            return df
            
        except FileNotFoundError:
            print(f"❌ CSV file '{csv_file}' not found")
            return None
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    print("=" * 100)
    print("📧 Gmail Thread Tracker - Email Status Monitor with Timeline")
    print("=" * 100)
    
    # Initialize tracker
    try:
        tracker = GmailThreadTracker()
        print("✅ Gmail API authenticated successfully\n")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # CSV file with message IDs
    csv_file = "emails.csv"  # Your CSV file name
    output_file = "emails_tracked.csv"  # Output file name
    
    # Track all emails and update CSV
    tracker.track_emails_from_csv(csv_file, output_file)


if __name__ == "__main__":
    main()
