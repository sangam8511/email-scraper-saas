import logging
import time
import os
import threading
from queue import Queue
from datetime import datetime
from sender import BulkEmailSender
from scraper import LeadScraper

logger = logging.getLogger(__name__)

def email_worker_thread(email_queue, sender, delay_seconds):
    """Background worker that continuously pulls contacts and sends them, handling the 15s delay internally."""
    while True:
        contact = email_queue.get()
        if contact is None:
            # Poison pill to stop thread
            break
            
        print(f"\n[Background Sender] 🚀 Engaging {contact.get('email')} ({contact.get('name_full')})...")
        # send_emails now handles its own delays, but since we are sending 1 by 1 from the queue, 
        # the sender's internal array delay won't trigger. So we sleep in the worker.
        try:
            sender.send_emails([contact], delay_seconds=0) # Delay is 0 inside sender because length is 1
            print(f"[Background Sender] Waiting {delay_seconds} seconds before grabbing the next email from queue to avoid spam filters...")
            time.sleep(delay_seconds)
        except Exception as e:
            logger.error(f"[Background Sender] failed on {contact.get('email')}: {e}")
        finally:
            email_queue.task_done()

def main():
    print("Welcome to the Ultimate Lead Sender!")
    print("===================================")
    print("1. Find new leads & auto-send emails")
    print("2. Send emails to the existing lists")
    print("===================================")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == '1':
        print("\nNote: The scraper is now set to automatically search across all major US cities!")
        niche = input("What kind of business are you targeting? (e.g., 'plumbers' or 'real estate agents'): ").strip()
        
        print("\nChecking Connectivity and Accounts...")
        try:
            sender = BulkEmailSender()
            print(f"Loaded {len(sender.accounts)} sending accounts.")
            
            # Load sent emails to prevent sending duplicates
            sent_emails = set()
            if os.path.exists('logs/sent_emails.txt'):
                with open('logs/sent_emails.txt', 'r') as f:
                    for line in f:
                        if line.strip():
                            sent_emails.add(line.strip().split(',')[0].strip().lower())
            
            # Setup background thread sending queue
            email_queue = Queue()
            # 60 second (1 minute) delay between emails
            worker = threading.Thread(target=email_worker_thread, args=(email_queue, sender, 60), daemon=True)
            worker.start()
            
            print("\nStarting Automated US City Scraper & Sender Engine...")
            scraper = LeadScraper()
            
            # List of top 100 US Cities to iterate through
            us_cities = [
                "New York City NY", "Los Angeles CA", "Chicago IL", "Houston TX", "Phoenix AZ", 
                "Philadelphia PA", "San Antonio TX", "San Diego CA", "Dallas TX", "San Jose CA",
                "Austin TX", "Jacksonville FL", "Fort Worth TX", "Columbus OH", "Charlotte NC",
                "San Francisco CA", "Indianapolis IN", "Seattle WA", "Denver CO", "Washington DC",
                "Boston MA", "El Paso TX", "Nashville TN", "Detroit MI", "Oklahoma City OK",
                "Portland OR", "Las Vegas NV", "Memphis TN", "Louisville KY", "Baltimore MD",
                "Milwaukee WI", "Albuquerque NM", "Tucson AZ", "Fresno CA", "Mesa AZ",
                "Sacramento CA", "Atlanta GA", "Kansas City MO", "Colorado Springs CO", "Omaha NE",
                "Raleigh NC", "Miami FL", "Long Beach CA", "Virginia Beach VA", "Oakland CA",
                "Minneapolis MN", "Tulsa OK", "Tampa FL", "Arlington TX", "New Orleans LA",
                "Wichita KS", "Bakersfield CA", "Cleveland OH", "Aurora CO", "Anaheim CA",
                "Honolulu HI", "Santa Ana CA", "Riverside CA", "Corpus Christi TX", "Lexington KY",
                "Stockton CA", "St. Louis MO", "Saint Paul MN", "Henderson NV", "Pittsburgh PA",
                "Cincinnati OH", "Anchorage AK", "Greensboro NC", "Plano TX", "Newark NJ",
                "Lincoln NE", "Orlando FL", "Irvine CA", "Toledo OH", "Jersey City NJ",
                "Chula Vista CA", "Durham NC", "Fort Wayne IN", "St. Petersburg FL", "Laredo TX",
                "Buffalo NY", "Madison WI", "Lubbock TX", "Chandler AZ", "Scottsdale AZ",
                "Reno NV", "Glendale AZ", "Gilbert AZ", "Winston-Salem NC", "North Las Vegas NV",
                "Norfolk VA", "Chesapeake VA", "Garland TX", "Irving TX", "Hialeah FL",
                "Fremont CA", "Boise ID", "Richmond VA", "Baton Rouge LA", "Spokane WA"
            ]
            
            for city in us_cities:
                query = f"{niche} in {city}"
                print(f"\n=============================================")
                print(f"📍 Now searching: {query}")
                print(f"=============================================")
                
                for lead in scraper.scrape_leads_generator(query, num_results=20):
                    # Split multiple comma-separated emails
                    emails_list = [e.strip() for e in lead['Emails'].split(',')]
                    valid_emails = [e for e in emails_list if e.lower() not in sent_emails]
                    
                    for email_address in valid_emails:
                        contact = {
                            'email': email_address,
                            'name_full': lead['Business Name'],
                            'city': lead['Search location'],
                            'address': ''
                        }
                        
                        # Add to background queue instead of waiting
                        email_queue.put(contact)
                        sent_emails.add(email_address.lower())
                        
                        # Save the lead to the contacts.csv file to keep a record
                        try:
                            csv_file = 'recipients/contacts.csv'
                            file_exists = os.path.isfile(csv_file)
                            with open(csv_file, 'a') as f:
                                # Write headers if file is empty
                                if not file_exists or os.stat(csv_file).st_size == 0:
                                    f.write("Business Name,Emails,Website,Search location\n")
                                
                                # Escape names with commas for safe CSV format
                                safe_name = contact['name_full'].replace('"', '""')
                                safe_location = contact['city'].replace('"', '""')
                                f.write(f'"{safe_name}",{email_address},{lead["Website"]},"{safe_location}"\n')
                        except Exception as e:
                            logger.error(f"Failed to append to contacts.csv: {e}")
                            
            print("\nWaiting for all emails in the queue to finish sending...")
            email_queue.join()
            print("\nDone with real-time web search and outreach sequence.")
        except Exception as e:
            print(f"An error occurred: {e}")
            logger.error(f"Error in hybrid engine: {e}")
            
    elif choice != '2':
        print("Invalid choice. Exiting.")
        return
        
    print("\nInitializing Email Engine...")
    
    try:
        sender = BulkEmailSender()
        print(f"Loaded {len(sender.accounts)} sending accounts.")
        result = sender.load_recipients('recipients/contacts.csv')
        
        if not result or len(result) != 2:
            print("No valid contacts found. Please check recipients/contacts.csv")
            return
            
        contacts, emails_sent_today = result
        
        print(f"Found {len(contacts)} NEW valid contacts. Preparing to send emails...")
        print("Note: there will be a 1-minute delay between emails to avoid spam filters.")
        
        # We delay 60 seconds between emails according to best practices and the user request
        sender.send_emails(contacts, delay_seconds=60)
        
        print("\nDone! Check logs/send_log.txt for delivery details.")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    main()
