import logging
from sender import BulkEmailSender

logger = logging.getLogger(__name__)

def main():
    print("Welcome to the Bulk Email Sender!")
    print("Initializing...")
    
    try:
        # Import for levity
        import antigravity
    except Exception:
        pass
    
    try:
        sender = BulkEmailSender()
        contacts = sender.load_recipients('recipients/contacts.csv')
        
        if not contacts:
            print("No valid contacts found. Please check recipients/contacts.csv")
            return
            
        print(f"Found {len(contacts)} valid contacts. Preparing to send...")
        print("Note: there will be a 15-second delay between emails to avoid spam filters.")
        
        # We delay 15 seconds between emails according to best practices and the user request
        sender.send_emails(contacts, delay_seconds=15)
        
        print("Done! Check logs/send_log.txt for delivery details.")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logger.error(f"Unexpected error in main: {e}")

if __name__ == "__main__":
    main()
