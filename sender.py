import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import time
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
from dotenv import load_dotenv
import json

# Setup logging
# basicConfig is handled by app.py to ensure file routing
logger = logging.getLogger(__name__)

class BulkEmailSender:
    def __init__(self):
        load_dotenv()
        
        # Load multiple accounts if available
        self.accounts = []
        if os.path.exists('accounts.json'):
            try:
                import json
                with open('accounts.json', 'r') as f:
                    self.accounts = json.load(f)
            except Exception as e:
                logger.error(f"Error loading accounts.json: {e}")
                
        # Fallback to .env if accounts.json is missing or invalid
        if not self.accounts:
            self.accounts = [{
                'email': os.getenv('SMTP_USER'),
                'app_password': os.getenv('SMTP_PASS'),
                'sender_name': os.getenv('SENDER_NAME', 'Default Sender'),
                'daily_limit': 150
            }]
            
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('email_template.html')
        
        # Load settings
        self.settings = {
            "subject": "Hello {{first_name}} in {{city}}",
            "plain_text": "Hey {{first_name}},\n\nHope things are well in {{city}}.\n\nBest,\n{{sender_name}}"
        }
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                logger.error(f"Error loading settings.json: {e}")

    def get_emails_sent_today_by_account(self, account_email):
        """Count how many emails a specific account sent today."""
        count = 0
        today_str = datetime.now().strftime('%Y-%m-%d')
        try:
            if os.path.exists('logs/sent_emails.txt'):
                with open('logs/sent_emails.txt', 'r') as f:
                    for line in f:
                        parts = line.strip().split(',')
                        # Format: recipient@email.com, 2023-10-01, sender@gmail.com
                        if len(parts) >= 3:
                            if parts[1].strip() == today_str and parts[2].strip().lower() == account_email.lower():
                                count += 1
                        # Backwards compatibility check
                        elif len(parts) == 2 and parts[1].strip() == today_str:
                            # We don't know who sent it, assume it was the main account
                            if account_email.lower() == self.accounts[0].get('email', '').strip().lower():
                                count += 1
        except Exception as e:
            logger.error(f"Could not load sent emails log: {e}")
        return count

    def get_available_account(self):
        """Find the first account that hasn't hit its daily limit."""
        for account in self.accounts:
            sender_email = account.get('email', '').strip()
            daily_limit = int(account.get('daily_limit', 150))
            
            if not sender_email or not account.get('app_password'):
                continue
                
            sent_today = self.get_emails_sent_today_by_account(sender_email)
            if sent_today < daily_limit:
                return account, sent_today
        return None, 0

    def load_recipients(self, csv_path='recipients/contacts.csv'):
        try:
            df = pd.read_csv(csv_path)
            
            # 1) If the new Google Maps columns exist, rename them to our internal standard
            rename_mapping = {}
            if 'Emails' in df.columns: rename_mapping['Emails'] = 'email'
            elif 'Email' in df.columns: rename_mapping['Email'] = 'email'
            
            if 'Name' in df.columns: rename_mapping['Name'] = 'name_full'
            if 'Business Name' in df.columns: rename_mapping['Business Name'] = 'name_full'
            if 'Search location' in df.columns: rename_mapping['Search location'] = 'city'
            if 'Address' in df.columns: rename_mapping['Address'] = 'address'
            if rename_mapping: df = df.rename(columns=rename_mapping)
                
            # Basic validation
            if 'email' not in df.columns:
                logger.error(f"No 'email' column found in {csv_path}. Columns: {df.columns.tolist()}")
                return [], 0
                
            df = df.dropna(subset=['email'])
            
            # Since the 'email' column can contain multiple emails separated by commas, let's explode them
            # Convert commas to lists, then explode the lists so each email gets its own row
            df['email'] = df['email'].astype(str).str.split(',')
            df = df.explode('email')
            df['email'] = df['email'].str.strip()
            
            # Basic email regex validation
            valid_emails = df[df['email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False, regex=True)]
            
            # Fill NaN values for other columns with empty strings
            valid_emails = valid_emails.fillna('')
            
            # 2) Filter against already sent emails and count today's volume
            sent_emails = set()
            emails_sent_today = 0
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            try:
                if os.path.exists('logs/sent_emails.txt'):
                    with open('logs/sent_emails.txt', 'r') as f:
                        for line in f:
                            if not line.strip(): continue
                            
                            # Format: email@example.com (or email@example.com,2023-10-01)
                            parts = line.strip().split(',')
                            saved_email = parts[0].strip().lower()
                            sent_emails.add(saved_email)
                            
                            if len(parts) > 1 and parts[1].strip() == today_str:
                                emails_sent_today += 1
            except Exception as e:
                logger.error(f"Could not load sent emails log: {e}")

            # Keep only emails we haven't sent to
            valid_emails = valid_emails[~valid_emails['email'].str.lower().isin(sent_emails)]
            
            # Remove entirely duplicate rows within the current batch to be safe
            valid_emails = valid_emails.drop_duplicates(subset=['email'])

            logger.info(f"Loaded {len(valid_emails)} NEW valid recipients from {csv_path} (Skipped previous/invalid ones).")
            return valid_emails.to_dict('records'), emails_sent_today
        except Exception as e:
            logger.error(f"Error loading recipients from {csv_path}: {e}")
            return [], 0

    def send_emails(self, recipients, delay_seconds=15):
        if not recipients:
            logger.warning("No recipients to send to.")
            return

        for i, recipient in enumerate(recipients):
            # Select an available account right before sending
            active_account, sent_so_far = self.get_available_account()
            if not active_account:
                logger.error("🚫 All connected accounts have reached their daily sending limits. Stopping.")
                return

            smtp_user = active_account['email']
            smtp_pass = active_account['app_password']
            sender_name = active_account.get('sender_name', 'Real Estate Expert')
            sender_email = smtp_user

            email_address = recipient.get('email')
            
            try:
                # Disconnect and Reconnect per-email ensures we can safely rotate accounts dynamically
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_pass)

                # 2) Parse the full name to just get the first name
                raw_name = str(recipient.get('first_name', recipient.get('name_full', ''))).strip()
                email_target = email_address.lower()
                
                first_name = "there" # Default fallback
                
                # Check if raw_name looks like a person's name (less than 3 words usually)
                if raw_name and raw_name.lower() != 'nan':
                    words = raw_name.split()
                    if len(words) <= 3 and "llc" not in raw_name.lower() and "inc" not in raw_name.lower():
                        first_name = words[0].capitalize()
                
                # If we still have fallback but the email format is name@..., let's guess the name
                if first_name == "there" and "@" in email_target:
                    local_part = email_target.split("@")[0]
                    # Common non-person emails
                    if local_part in ["info", "contact", "support", "sales", "hello", "admin", "office"]:
                        first_name = "team"
                    else:
                        # try to get name from something like john.doe or john
                        potential_name = local_part.split(".")[0].split("_")[0]
                        if len(potential_name) > 2 and not any(char.isdigit() for char in potential_name):
                            first_name = potential_name.capitalize()
                
                # Default "city" parsing improvement
                raw_city = str(recipient.get('city', ''))
                if raw_city.lower() == 'nan' or not raw_city.strip():
                    addr = str(recipient.get('address', ''))
                    if addr.lower() != 'nan' and ',' in addr:
                        parts = [p.strip() for p in addr.split(',')]
                        if len(parts) >= 2:
                            raw_city = parts[-2]
                            if len(parts) == 2:
                                raw_city = parts[0]

                city = raw_city if raw_city and raw_city.lower() != 'nan' else 'your area'
                
                similar_city = str(recipient.get('similar_city', city))
                if similar_city.lower() == 'nan' or not similar_city.strip(): similar_city = city

                # Create message
                msg = MIMEMultipart('alternative')
                
                # Context for Jinja2 rendering
                try:
                    # If niche isn't passed directly into the recipient level, we try loading it from engine state or default
                    # For now, let's inject a generic placeholder if missing, or use a global we can pass in later
                    niche = str(recipient.get('niche', 'local businesses'))
                except:
                    niche = "local businesses"
                    
                context = {
                    "first_name": first_name,
                    "city": city,
                    "similar_city": similar_city,
                    "unsubscribe_link": "https://example.com/unsubscribe?email=" + email_address,
                    "sender_name": sender_name,
                    "niche": niche
                }
                
                # Render dynamic subject
                try:
                    subject_template = Template(self.settings.get("subject", "Message for {{first_name}}"))
                    rendered_subject = subject_template.render(**context)
                except Exception as e:
                    logger.error(f"Error rendering subject: {e}")
                    rendered_subject = f"Hello {first_name}"
                
                msg['Subject'] = rendered_subject
                msg['From'] = f"{sender_name} <{sender_email}>"
                msg['To'] = email_address

                try:
                    # Render HTML template
                    html_content = self.template.render(**context)

                    # Render Plain Text fallback
                    try:
                        text_template = Template(self.settings.get("plain_text", "Hello.\nUnsubscribe: {{unsubscribe_link}}"))
                        text_content = text_template.render(**context)
                    except Exception as e:
                        logger.error(f"Error rendering plain text: {e}")
                        text_content = f"Hello {first_name}.\n\nUnsubscribe: {context['unsubscribe_link']}"

                    part1 = MIMEText(text_content, 'plain')
                    part2 = MIMEText(html_content, 'html')

                    msg.attach(part1)
                    msg.attach(part2)

                    server.send_message(msg)
                    logger.info(f"SUCCESS: Sent to {email_address} [via {sender_email}]")
                    
                    # Record it in the sent list with today's date and the sender account
                    try:
                        today_str = datetime.now().strftime('%Y-%m-%d')
                        with open('logs/sent_emails.txt', 'a') as f:
                            f.write(f"{email_address},{today_str},{sender_email}\n")
                    except Exception as e:
                        logger.error(f"Failed to write to sent_emails.txt: {e}")
                        
                except Exception as e:
                    logger.error(f"FAILED: Could not send to {email_address}. Error: {e}")

                server.quit()
                
                # Rate limiting (don't delay after the last email)
                if i < len(recipients) - 1:
                    logger.info(f"Waiting {delay_seconds} seconds before sending the next email to avoid spam filters...")
                    time.sleep(delay_seconds)

            except smtplib.SMTPAuthenticationError:
                logger.error(f"SMTP Authentication Error for account {smtp_user}. Check your username and password or App Password settings.")
                # We do not sleep here, so it will instantly fail and try the next recipient (or account if we make it smarter later).
            except Exception as e:
                logger.error(f"SMTP Connection Error: {e}")

if __name__ == "__main__":
    sender = BulkEmailSender()
    contacts = sender.load_recipients()
    sender.send_emails(contacts, delay_seconds=15)
