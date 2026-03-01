import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import time
import logging
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/send_log.txt"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BulkEmailSender:
    def __init__(self):
        load_dotenv()
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_pass = os.getenv('SMTP_PASS')
        self.sender_name = os.getenv('SENDER_NAME', 'Default Sender')
        self.sender_email = os.getenv('SENDER_EMAIL', self.smtp_user)
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader('templates'))
        self.template = self.env.get_template('email_template.html')

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
                return []
                
            df = df.dropna(subset=['email'])
            
            # Since the 'email' column can contain multiple emails separated by commas, let's explode them
            # Convert commas to lists, then explode the lists so each email gets its own row
            df['email'] = df['email'].astype(str).str.split(',')
            df = df.explode('email')
            df['email'] = df['email'].str.strip()
            
            # 2) Filter against already sent emails
            sent_emails = set()
            try:
                if os.path.exists('logs/sent_emails.txt'):
                    with open('logs/sent_emails.txt', 'r') as f:
                        sent_emails = set(line.strip().lower() for line in f if line.strip())
            except Exception as e:
                logger.error(f"Could not load sent emails log: {e}")

            # Keep only emails we haven't sent to
            valid_emails = valid_emails[~valid_emails['email'].str.lower().isin(sent_emails)]
            
            # Remove entirely duplicate rows within the current batch to be safe
            valid_emails = valid_emails.drop_duplicates(subset=['email'])

            logger.info(f"Loaded {len(valid_emails)} NEW valid recipients from {csv_path} (Skipped previous/invalid ones).")
            return valid_emails.to_dict('records')
        except Exception as e:
            logger.error(f"Error loading recipients: {e}")
            return []

    def send_emails(self, recipients, delay_seconds=15):
        if not recipients:
            logger.warning("No recipients to send to.")
            return
            
        if not self.smtp_host or not self.smtp_user or not self.smtp_pass:
            logger.error("SMTP credentials are not fully configured in .env file.")
            return

        try:
            logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port}...")
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_pass)
            logger.info("Successfully connected and authenticated.")

            for i, recipient in enumerate(recipients):
                # 2) Parse the full name to just get the first name (e.g. "KALEO Real Estate Company" -> "KALEO")
                raw_name = str(recipient.get('first_name', recipient.get('name_full', 'there')))
                first_name = raw_name.split()[0] if raw_name.strip() and raw_name.lower() != 'nan' else 'there'
                
                email_address = recipient.get('email')
                
                # Default "city" parsing improvement
                raw_city = str(recipient.get('city', ''))
                if raw_city.lower() == 'nan' or not raw_city.strip():
                    addr = str(recipient.get('address', ''))
                    if addr.lower() != 'nan' and ',' in addr:
                        parts = [p.strip() for p in addr.split(',')]
                        # Address usually like: "1898 320 Rd, Beloit, KS 67420"
                        if len(parts) >= 2:
                            # The city is usually the part before the State/Zip part
                            # So in [1898 320 Rd, Beloit, KS 67420], parts[-2] is 'Beloit'
                            raw_city = parts[-2]
                            
                            # Just in case they provide "City, Country"
                            if len(parts) == 2:
                                raw_city = parts[0]

                city = raw_city if raw_city and raw_city.lower() != 'nan' else 'your area'
                
                # Since we don't have "similar_city" in the map extract, just use their city
                similar_city = str(recipient.get('similar_city', city))
                if similar_city.lower() == 'nan' or not similar_city.strip(): similar_city = city

                # Create message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = f"Helped a {city} realtor get more leads — here's how"
                msg['From'] = f"{self.sender_name} <{self.sender_email}>"
                msg['To'] = email_address
                
                # Setup Unsubscribe Link
                unsubscribe_link = "https://example.com/unsubscribe?email=" + email_address

                try:
                    # Render HTML template
                    html_content = self.template.render(
                        first_name=first_name,
                        city=city,
                        similar_city=similar_city,
                        unsubscribe_link=unsubscribe_link,
                        sender_name=self.sender_name
                    )

                    # Plain text fallback
                    text_content = f"""Hey {first_name},

I recently redesigned a real estate agent's website in {similar_city} — they went from getting 2-3 contact form submissions a month to 15+.

The changes were simple: faster load time, lead form on the homepage, mobile optimization, and a clear call-to-action.

I specialize in exactly this for US real estate agents.

I'd love to show you what your website could look like — free homepage mockup, no payment until you approve it.

Can I send it over?

{self.sender_name}

---
Unsubscribe: {unsubscribe_link}"""

                    part1 = MIMEText(text_content, 'plain')
                    part2 = MIMEText(html_content, 'html')

                    msg.attach(part1)
                    msg.attach(part2)

                    server.send_message(msg)
                    logger.info(f"SUCCESS: Sent to {email_address}")
                    
                    # Record it in the sent list so we never send to it again
                    try:
                        with open('logs/sent_emails.txt', 'a') as f:
                            f.write(email_address + '\n')
                    except Exception as e:
                        logger.error(f"Failed to write to sent_emails.txt: {e}")
                        
                except Exception as e:
                    logger.error(f"FAILED: Could not send to {email_address}. Error: {e}")

                # Rate limiting (don't delay after the last email)
                if i < len(recipients) - 1:
                    logger.info(f"Waiting {delay_seconds} seconds before sending the next email to avoid spam filters...")
                    time.sleep(delay_seconds)

            server.quit()
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication Error. Check your username and password.")
        except Exception as e:
            logger.error(f"SMTP Connection Error: {e}")

if __name__ == "__main__":
    sender = BulkEmailSender()
    contacts = sender.load_recipients()
    sender.send_emails(contacts, delay_seconds=15)
