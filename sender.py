import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os
import time
import socket
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
from dotenv import load_dotenv
import json
from models import db, EmailAccount, Lead

# Setup logging
# basicConfig is handled by app.py to ensure file routing
logger = logging.getLogger(__name__)

class BulkEmailSender:
    def __init__(self, user, campaign):
        self.user = user
        self.campaign = campaign
            
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # We don't need to load files, we have the campaign object
        self.settings = {
            "subject": self.campaign.subject or "Hello {{first_name}} in {{city}}",
            "plain_text": self.campaign.plain_text or "Hey {{first_name}},\n\nHope things are well in {{city}}.\n\nBest,\n{{sender_name}}"
        }
        
        # Setup Jinja2 environment from string
        self.env = Environment()
        self.template = self.env.from_string(self.campaign.template_html or "<!-- Fallback Template -->")

    def get_accounts(self):
        return EmailAccount.query.filter_by(user_id=self.user.id).all()

    def get_emails_sent_today_by_account(self, account_email):
        """Count how many emails a specific account sent today."""
        # Simplified memory tracking for DB migration: just check how many Leads we updated today
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            count = Lead.query.filter(Lead.campaign_id == self.campaign.id, Lead.sent_at >= today_start).count()
            # Note: We should ideally link Leads to EmailAccounts, but for now we distribute globally across the campaign's accounts
            return count // max(1, len(self.get_accounts()))
        except Exception as e:
            logger.error(f"Could not load sent emails log from DB: {e}")
        return 0

    def get_available_account(self):
        """Find the first account that hasn't hit its daily limit."""
        accounts = self.get_accounts()
        for account in accounts:
            if not account.email or not account.app_password:
                continue
                
            sent_today = self.get_emails_sent_today_by_account(account.email)
            if sent_today < account.daily_limit:
                return {"email": account.email, "app_password": account.app_password, "sender_name": account.sender_name}, sent_today
        return None, 0


    def send_single_email(self, recipient):
        if not recipient:
            return False, None

        # Select an available account right before sending
        active_account, sent_so_far = self.get_available_account()
        if not active_account:
            logger.error("🚫 All connected accounts have reached their daily sending limits. Stopping.")
            return False, None

        smtp_user = active_account['email']
        smtp_pass = active_account['app_password']
        sender_name = active_account.get('sender_name', 'Real Estate Expert')
        sender_email = smtp_user

        email_address = recipient.get('email')
        
        try:
            # 🔍 FIX: Force IPv4 to bypass 'Network is unreachable' on cloud environments
            try:
                # Resolve hostname to IPv4 specifically
                addr_info = socket.getaddrinfo(self.smtp_host, self.smtp_port, socket.AF_INET, socket.SOCK_STREAM)
                target_ip = addr_info[0][4][0]
                logger.info(f"Connecting to SMTP {self.smtp_host} [{target_ip}:{self.smtp_port}]...")
                server = smtplib.SMTP(target_ip, self.smtp_port, timeout=30)
            except Exception as resolve_err:
                logger.warning(f"IPv4 force resolution failed, falling back to DNS: {resolve_err}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)

            server.ehlo()
            server.starttls(server_hostname=self.smtp_host)
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
            server.quit()
            
            return True, sender_email

        except smtplib.SMTPAuthenticationError:
            logger.error(f"SMTP Authentication Error for account {smtp_user}.")
            return False, None
        except Exception as e:
            logger.error(f"SMTP Connection Error: {e}")
            return False, None
