import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
import re
import pandas as pd
import time
import logging

# Setup logging
# basicConfig is handled by app.py to ensure file routing
logger = logging.getLogger(__name__)

class LeadScraper:
    def __init__(self):
        # Email regex pattern
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Common skip extensions
        self.skip_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.woff', '.pdf']
        
        # Massive list of popular aggregators to skip (forces the scraper to find local businesses only)
        self.directory_domains = [
            'zillow.com', 'realtor.com', 'redfin.com', 'trulia.com', 'homes.com', 'yelp.com', 'yellowpages.com', 
            'facebook.com', 'linkedin.com', 'instagram.com', 'tiktok.com', 'twitter.com', 'x.com', 'youtube.com',
            'manta.com', 'superpages.com', 'bbb.org', 'mapquest.com', 'chamberofcommerce.com', 'expertise.com',
            'angi.com', 'thumbtack.com', 'homeadvisor.com', 'houzz.com', 'porch.com', 'bizapedia.com', 'usnews.com',
            'realestateagent.com', 'housesaround.com', 'fyple.com', 'keenurban.com', 'socialcatfish.com',
            'trovit.com', 'myelisting.com', 'streeteasy.com', 'remax.com', 'century21.com', 'coldwellbanker.com',
            'compass.com', 'exprealty.com', 'kellerwilliams.com', 'kw.com', 'sothebys.com', 'propertyfinder.',
            'loopnet.com', 'crexi.com', 'apartments.com', 'rent.com', 'forrent.com', 'rentcafe.com', 'wikipedia.org',
            'yandex.com', 'mojeek.com', 'search.brave.com', 'google.com', 'bing.com'
        ]

    def is_independent_business(self, url):
        url_lower = url.lower()
        if any(bad_domain in url_lower for bad_domain in self.directory_domains):
            return False
            
        # Skip subdomain aggregators (like something.directory.com)
        if "directory" in url_lower or "list" in url_lower or "top10" in url_lower or "best" in url_lower:
            return False
            
        return True
        
    def find_businesses(self, query, num_results=20):
        """Search DuckDuckGo to get a list of INDEPENDENT business websites for the query, acting like local maps"""
        logger.info(f"Searching for: '{query}'")
        businesses = []
        try:
            # Fetch up to 100 results to give us room to filter out directories and still get our target number
            results = list(DDGS().text(query, max_results=max(100, num_results * 4)))
            for r in results:
                url = r.get('href', '')
                
                if not self.is_independent_business(url):
                    continue
                    
                raw_title = r.get('title', '')
                # Clean up title for business name (remove " | ", " - ", " : ", etc.)
                biz_name = raw_title.split('|')[0].split('-')[0].split('–')[0].split(':')[0].strip()
                if not biz_name:
                    biz_name = "Real Estate Agent"
                    
                businesses.append({
                    'Business Name': biz_name,
                    'Website': url,
                    'Description': r.get('body', '')
                })
                
                if len(businesses) >= num_results:
                    break
                    
            logger.info(f"Found {len(businesses)} truly independent local businesses for this area.")
            return businesses
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def extract_emails_from_url(self, url, max_pages_to_check=3):
        """Visit a website and look for emails on the homepage and contact pages"""
        emails = set()
        visited = set()
        
        # We start with the homepage
        urls_to_visit = [url]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        pages_checked = 0
        
        while urls_to_visit and pages_checked < max_pages_to_check:
            current_url = urls_to_visit.pop(0)
            
            # Skip non-html pages
            if any(current_url.lower().endswith(ext) for ext in self.skip_extensions):
                continue
                
            if current_url in visited:
                continue
                
            visited.add(current_url)
            
            try:
                # Add a tiny 1-second delay so we don't accidentally DDOS small business websites
                time.sleep(1)
                
                response = requests.get(current_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    continue
                    
                # 1. Find emails in the text
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                found_emails = self.email_pattern.findall(text)
                
                for email in found_emails:
                    # Clean up common false positives
                    email_lower = email.lower()
                    if not email_lower.endswith(('png', 'jpg', 'jpeg', 'gif', 'webp', 'sentry.io', 'example.com')):
                        emails.add(email_lower)
                        
                # 2. Find links to 'Contact Us', 'About', 'Team' pages to check those too
                if pages_checked == 0:
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        if any(keyword in href.lower() for keyword in ['contact', 'about', 'team']):
                            # Handle relative URLs
                            if href.startswith('/'):
                                # crude way to get base URL
                                base_url = '/'.join(current_url.split('/')[:3])
                                new_url = base_url + href
                                urls_to_visit.append(new_url)
                            elif href.startswith('http'):
                                # Only stay on the same domain
                                if current_url.split('/')[2] in href:
                                    urls_to_visit.append(href)
                                    
            except Exception as e:
                # Silent fail for individual pages tracking
                pass
                
            pages_checked += 1
            
        # Verify emails using DNS MX checks to ensure deliverability
        from email_validator import validate_email, EmailNotValidError
        valid_emails = []
        invalid_count = 0
        for e in emails:
            try:
                # check_deliverability = True does an active DNS MX check for the domain
                v = validate_email(e, check_deliverability=True)
                valid_emails.append(v.normalized)
            except EmailNotValidError as err:
                logger.info(f"    -> Skipping invalid/bouncing email '{e}': {err}")
                invalid_count += 1
                
        return valid_emails, invalid_count

    def scrape_leads_generator(self, query, num_results=30):
        """Full pipeline: Search -> Extract -> Yield as it finds them"""
        businesses = self.find_businesses(query, num_results)
        
        if not businesses:
            logger.error("No businesses found.")
            return
            
        # Better robust extraction of city guess for the template parsing
        # e.g. "real estate agents in Los Angeles CA" -> "Los Angeles CA"
        query_lower = query.lower()
        city_guess = query
        if " in " in query_lower:
            city_guess = query_lower.split(" in ")[-1].strip().title()
        
        logger.info(f"Parsed city name for email template: {city_guess}")
        logger.info("Starting live extraction and sending...")
        
        for i, biz in enumerate(businesses):
            logger.info(f"[{i+1}/{len(businesses)}] Scanning {biz['Website']}...")
            emails, invalid_count = self.extract_emails_from_url(biz['Website'])
            
            if emails or invalid_count > 0:
                if emails:
                    logger.info(f"    -> Found {len(emails)} emails: {', '.join(emails)}")
                
                yield {
                    'Business Name': biz['Business Name'],
                    'Emails': ','.join(emails) if emails else '',
                    'Website': biz['Website'],
                    'Search location': city_guess,
                    'Skipped Count': invalid_count
                }
            else:
                logger.info("    -> No public emails found.")

    def scrape_and_save(self, query, num_results=20, output_file='recipients/contacts.csv'):
        """Full pipeline: Search -> Extract -> Save to CSV"""
        businesses = self.find_businesses(query, num_results)
        
        if not businesses:
            logger.error("No businesses found.")
            return 0
            
        all_leads = []
        
        # Better robust extraction of city guess for the template parsing
        query_lower = query.lower()
        city_guess = query
        if " in " in query_lower:
            city_guess = query_lower.split(" in ")[-1].strip().title()
        
        logger.info(f"Parsed city name for email template: {city_guess}")
        logger.info("Starting email extraction. This may take a few minutes as we visit the websites...")
        
        for i, biz in enumerate(businesses):
            logger.info(f"[{i+1}/{len(businesses)}] Scanning {biz['Website']}...")
            emails, invalid_count = self.extract_emails_from_url(biz['Website'])
            
            if emails:
                logger.info(f"    -> Found {len(emails)} emails: {', '.join(emails)}")
                all_leads.append({
                    'Business Name': biz['Business Name'],
                    'Emails': ','.join(emails), # Comma separated for our sender.py to explode later
                    'Website': biz['Website'],
                    'Search location': city_guess
                })
            else:
                logger.info("    -> No public emails found.")
                
        if all_leads:
            df = pd.DataFrame(all_leads)
            df.to_csv(output_file, index=False)
            logger.info(f"\n✅ Successfully scraped {len(all_leads)} business properties with valid emails and saved to {output_file}!")
            return len(all_leads)
        else:
            logger.warning("\n❌ Scanned the websites but could not find any valid public email addresses.")
            return 0

if __name__ == "__main__":
    scraper = LeadScraper()
    scraper.scrape_and_save("plumbers in austin texas", num_results=5)
