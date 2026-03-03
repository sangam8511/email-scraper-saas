import os
import queue
import threading
import time
import logging
from flask import Flask, jsonify, request, send_from_directory

from sender import BulkEmailSender
from scraper import LeadScraper
from dotenv import load_dotenv
from models import db, User, EmailAccount, Campaign, Lead

load_dotenv()

# Ensure logs and recipients directory exists
os.makedirs('logs', exist_ok=True)
os.makedirs('recipients', exist_ok=True)

# Set up central file logging for the UI to read
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Reduce requests logging noise
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logging.getLogger("urllib3").setLevel(logging.WARNING)

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    # Attempt to create tables if they don't exist
    try:
        db.create_all()
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")

# Application state
engine_state = {
    "is_running": False,
    "current_niche": "",
    "current_city": "",
    "emails_found": 0,
    "emails_sent": 0,
    "emails_skipped": 0,
    "errors": 0
}

# Thread control
stop_event = threading.Event()
email_queue = queue.Queue()
worker_thread = None
scraper_thread = None

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

def load_sent_emails():
    # Deprecated fallback - now handled inside bg workers via DB
    return set()

def bg_email_worker(delay_seconds):
    """Takes emails from queue and sends them."""
    global engine_state
    
    logger.info("🧵 [Background Email Worker] Starting up...")
    
    with app.app_context():
        try:
            user = get_default_user()
            camp = get_default_campaign(user.id)
            sender = BulkEmailSender(user, camp)
            
            accounts = sender.get_accounts()
            logger.info(f"🧵 [Background Email Worker] Loaded {len(accounts)} sending accounts for campaign {camp.id}")
            
            if not accounts:
                logger.warning("🧵 [Background Email Worker] No sending accounts found in DB! Worker will exit.")
                return

        except Exception as e:
            logger.error(f"🧵 [Background Email Worker] FATAL: Initialization error: {e}")
            return
        
        while not stop_event.is_set() or not email_queue.empty():
            try:
                # We timeout every 2 seconds to check the stop_event
                try:
                    contact_dict = email_queue.get(timeout=2)
                except queue.Empty:
                    if stop_event.is_set():
                        break
                    continue

                if contact_dict is None:
                    break
                    
                logger.info(f"🚀 Engaging {contact_dict.get('email')} ({contact_dict.get('name_full')})...")
                try:
                    success, sender_email = sender.send_single_email(contact_dict)
                    if success:
                        engine_state['emails_sent'] += 1
                        
                        # Update lead in DB
                        try:
                            from datetime import datetime
                            lead = Lead.query.filter_by(campaign_id=camp.id, email=contact_dict['email']).first()
                            if lead:
                                lead.sent_at = datetime.utcnow()
                                db.session.commit()
                        except Exception as db_e:
                            logger.error(f"🧵 [Background Email Worker] DB update error: {db_e}")
                            db.session.rollback()
                            
                        logger.info(f"Waiting {delay_seconds} seconds before next email...")
                        for _ in range(delay_seconds):
                            if stop_event.is_set():
                                break
                            time.sleep(1)
                    else:
                        engine_state['errors'] += 1
                        logger.warning(f"🧵 [Background Email Worker] Failed to send to {contact_dict.get('email')}. Check account limits/auth.")
                except Exception as e:
                    logger.error(f"🧵 [Background Email Worker] Unexpected error on {contact_dict.get('email')}: {e}")
                    engine_state['errors'] += 1
                finally:
                    email_queue.task_done()
            except Exception as outer_e:
                logger.error(f"🧵 [Background Email Worker] Loop error: {outer_e}")
                time.sleep(1)
        
        logger.info("🧵 [Background Email Worker] Shutting down.")

def bg_scraper_worker(niche):
    """Iterates through cities and scrapes."""
    global engine_state
    
    with app.app_context():
        try:
            user = get_default_user()
            camp = get_default_campaign(user.id)
            
            # Fetch sent emails from DB for this campaign so we don't scrape and queue them again
            sent_leads = Lead.query.filter(Lead.campaign_id == camp.id, Lead.sent_at != None).all()
            sent_emails = set([l.email.lower() for l in sent_leads])
            
            scraper = LeadScraper()
            
            for city in us_cities:
                if stop_event.is_set():
                    break
                    
                engine_state['current_city'] = city
                query = f"{niche} in {city}"
                logger.info(f"=============================================")
                logger.info(f"📍 Now searching: {query}")
                logger.info(f"=============================================")
                
                for lead_data in scraper.scrape_leads_generator(query, num_results=20):
                    if stop_event.is_set():
                        break
                        
                    if 'Skipped Count' in lead_data and lead_data['Skipped Count'] > 0:
                        engine_state['emails_skipped'] += lead_data['Skipped Count']
                        
                    if not lead_data.get('Emails'):
                        continue
                        
                    emails_list = [e.strip() for e in lead_data['Emails'].split(',')]
                    valid_emails = [e for e in emails_list if e.lower() not in sent_emails]
                    
                    for email_address in valid_emails:
                        # Add to Database ONLY if it doesn't already exist
                        existing_lead = Lead.query.filter_by(campaign_id=camp.id, email=email_address).first()
                        if not existing_lead:
                            new_lead = Lead(
                                campaign_id=camp.id,
                                name_full=lead_data.get('Business Name', ''),
                                email=email_address,
                                website=lead_data.get('Website', ''),
                                city=lead_data.get('Search location', '')
                            )
                            db.session.add(new_lead)
                            try:
                                db.session.commit()
                            except:
                                db.session.rollback()
                        
                        contact_dict = {
                            'email': email_address,
                            'name_full': lead_data.get('Business Name', ''),
                            'city': lead_data.get('Search location', ''),
                            'address': lead_data.get('Address', ''),
                            'niche': niche
                        }
                        
                        email_queue.put(contact_dict)
                        sent_emails.add(email_address.lower())
                        engine_state['emails_found'] += 1
                        
            logger.info("Finished searching all cities. Waiting for email queue to complete...")
            while not email_queue.empty() and not stop_event.is_set():
                time.sleep(1)
                
            engine_state['is_running'] = False
            logger.info("Campaign completed naturally.")
        except Exception as e:
            logger.error(f"Error in bg_scraper_worker: {e}")
            engine_state['is_running'] = False

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        **engine_state,
        "queue_size": email_queue.qsize()
    })

@app.route('/api/start', methods=['POST'])
def start_campaign():
    global engine_state, worker_thread, scraper_thread, stop_event
    
    if engine_state['is_running']:
        return jsonify({"error": "Engine is already running"}), 400
        
    data = request.json
    niche = data.get('niche', 'plumbers')
    
    engine_state['is_running'] = True
    engine_state['current_niche'] = niche
    engine_state['emails_found'] = 0
    engine_state['emails_sent'] = 0
    engine_state['emails_skipped'] = 0
    engine_state['errors'] = 0
    
    stop_event.clear()
    
    # Start the email worker thread (60 second delay logic inside)
    # Clear queue first just in case
    while not email_queue.empty():
        try:
            email_queue.get_nowait()
            email_queue.task_done()
        except:
            pass
        
    worker_thread = threading.Thread(target=bg_email_worker, args=(60,), daemon=True)
    worker_thread.start()
    
    scraper_thread = threading.Thread(target=bg_scraper_worker, args=(niche,), daemon=True)
    scraper_thread.start()
    
    return jsonify({"success": True, "message": "Campaign started!"})

@app.route('/api/stop', methods=['POST'])
def stop_campaign():
    global engine_state, stop_event
    if not engine_state['is_running']:
        return jsonify({"error": "Engine is not running"}), 400
        
    stop_event.set()
    engine_state['is_running'] = False
    logger.info("STOP SIGNAL RECEIVED! Ending campaign gracefully...")
    return jsonify({"success": True, "message": "Stopping campaign (will finish current email if sending)..."})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        if not os.path.exists('logs/app.log'):
            return jsonify({"logs": []})
            
        with open('logs/app.log', 'r') as f:
            lines = f.readlines()
            # Return last 100 lines
            return jsonify({"logs": [line.strip() for line in lines[-100:] if line.strip()]})
    except Exception as e:
        return jsonify({"logs": [f"Error reading logs: {e}"]})

# --- NEW SAAS ENDPOINTS (MIGRATED TO NEON POSTGRES) ---
def get_default_user():
    user = User.query.first()
    if not user:
        user = User(email="admin@saas.com", password_hash="test")
        db.session.add(user)
        db.session.commit()
    return user

def get_default_campaign(user_id):
    camp = Campaign.query.filter_by(user_id=user_id).first()
    if not camp:
        camp = Campaign(
            user_id=user_id, 
            subject="Helped a {{city}} {{niche}} get more leads — here's how", 
            plain_text="Hey {{first_name}},\n\nI recently redesigned a {{niche}} website in {{similar_city}}...",
            template_html="<!-- Template not found -->"
        )
        db.session.add(camp)
        db.session.commit()
    return camp

@app.route('/api/accounts', methods=['GET'])
def get_accounts():
    try:
        user = get_default_user()
        accounts = EmailAccount.query.filter_by(user_id=user.id).all()
        return jsonify([{"email": a.email, "app_password": a.app_password, "daily_limit": a.daily_limit, "sender_name": a.sender_name} for a in accounts])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/accounts', methods=['POST'])
def save_accounts():
    try:
        user = get_default_user()
        accounts_data = request.json
        if not isinstance(accounts_data, list):
            return jsonify({"error": "Expected a list of accounts"}), 400
            
        # Clear old and add new (sync logic)
        EmailAccount.query.filter_by(user_id=user.id).delete()
        
        for acc in accounts_data:
            if acc.get('email') and acc.get('app_password'):
                new_acc = EmailAccount(
                    user_id=user.id,
                    email=acc.get('email'),
                    app_password=acc.get('app_password'),
                    daily_limit=int(acc.get('daily_limit', 150)),
                    sender_name=acc.get('sender_name', '')
                )
                db.session.add(new_acc)
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    try:
        user = get_default_user()
        camp = get_default_campaign(user.id)
        return jsonify({
            "subject": camp.subject,
            "plain_text": camp.plain_text,
            "niche": camp.niche
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    try:
        user = get_default_user()
        camp = get_default_campaign(user.id)
        settings = request.json
        
        camp.subject = settings.get('subject', camp.subject)
        camp.plain_text = settings.get('plain_text', camp.plain_text)
        camp.niche = settings.get('niche', camp.niche)
        # Assuming OpenAI key might be stored here originally, skipped for DB for now unless needed
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/template', methods=['GET'])
def get_template():
    try:
        user = get_default_user()
        camp = get_default_campaign(user.id)
        return jsonify({"content": camp.template_html})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/api/template', methods=['POST'])
def save_template():
    try:
        user = get_default_user()
        camp = get_default_campaign(user.id)
        data = request.json
        
        camp.template_html = data.get('content', '')
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        user = get_default_user()
        camp = get_default_campaign(user.id)
        
        # Get all leads for this campaign that have been sent
        sent_leads = Lead.query.filter(Lead.campaign_id == camp.id, Lead.sent_at != None).order_by(Lead.sent_at.desc()).limit(100).all()
        
        history = []
        for lead in sent_leads:
            history.append({
                "email": lead.email,
                "date": lead.sent_at.strftime('%Y-%m-%d %H:%M:%S'),
                "sender": "Backend Engine" # We can add relations to EmailAccount later if needed
            })
            
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-template', methods=['POST'])
def generate_template():
    try:
        data = request.json
        prompt = data.get('prompt')
        api_key = data.get('api_key')
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        if not api_key:
            return jsonify({"error": "Google Gemini API Key is required"}), 400

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        system_msg = """
        You are an elite B2B cold email copywriter. You must write a highly converting, personalized cold email template.
        The template MUST use Jinja variables for merge tags, e.g., {{first_name}}, {{city}}, {{niche}}, {{sender_name}}.
        
        IMPORTANT: You MUST respond ONLY with a raw JSON object and nothing else. Do not use markdown backticks.
        Your JSON must have exactly two keys:
        {
            "subject": "Compelling subject line here",
            "html_body": "The HTML email body here using <p>, <br>. Make it look natural."
        }
        """

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_msg)
        response = model.generate_content(f"User Request: Write a cold email template based on this instruction: {prompt}")
        
        import json
        
        # Clean the output because LLMs might still inject ```json markers
        content = response.text
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)

        return jsonify({
            "success": True,
            "subject": result.get("subject", ""),
            "html_body": result.get("html_body", ""),
            "plain_text": result.get("html_body", "").replace("<p>", "").replace("</p>", "\n").replace("<br>", "\n").replace("<strong>", "").replace("</strong>", "")
        })

    except Exception as e:
        logger.error(f"Gemini Generation Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

