import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BossAzScraper:
    def __init__(self, delay=2):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay
        self.base_url = 'https://boss.az'
        self.resume_data = []
    
    def get_page(self, url):
        """Fetch a page with error handling and delay"""
        try:
            time.sleep(self.delay)
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_resume_links(self, soup):
        """Extract resume links from listing page"""
        links = []
        resume_items = soup.find_all('div', class_='results-i')
        
        for item in resume_items:
            link_elem = item.find('a', class_='results-i-link')
            if link_elem and 'href' in link_elem.attrs:
                href = link_elem['href']
                full_url = urljoin(self.base_url, href)
                links.append(full_url)
        
        return links
    
    def get_next_page_url(self, soup):
        """Extract next page URL from pagination"""
        pagination = soup.find('nav', class_='pagination')
        if pagination:
            next_link = pagination.find('span', class_='next')
            if next_link:
                a_tag = next_link.find('a', attrs={'rel': 'next'})
                if a_tag and 'href' in a_tag.attrs:
                    return urljoin(self.base_url, a_tag['href'])
        return None
    
    def scrape_listing_pages(self, start_url, max_pages=None):
        """Scrape all listing pages and collect resume URLs"""
        current_url = start_url
        page_count = 0
        all_resume_links = []
        
        while current_url and (max_pages is None or page_count < max_pages):
            logging.info(f"Scraping listing page {page_count + 1}: {current_url}")
            
            response = self.get_page(current_url)
            if not response:
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract resume links from current page
            resume_links = self.extract_resume_links(soup)
            all_resume_links.extend(resume_links)
            logging.info(f"Found {len(resume_links)} resumes on page {page_count + 1}")
            
            # Get next page URL
            current_url = self.get_next_page_url(soup)
            page_count += 1
        
        logging.info(f"Total resume links collected: {len(all_resume_links)}")
        return all_resume_links
    
    def parse_resume_detail(self, soup, url):
        """Parse individual resume detail page"""
        data = {'url': url}
        
        # Basic info
        title_elem = soup.find('h1', class_='post-title')
        data['title'] = title_elem.text.strip() if title_elem else None
        
        salary_elem = soup.find('span', class_='post-salary salary')
        data['salary'] = salary_elem.text.strip() if salary_elem else None
        
        seeker_elem = soup.find('div', class_='post-seeker')
        data['seeker_name'] = seeker_elem.text.strip() if seeker_elem else None
        
        # Contact information
        phone_elem = soup.find('a', class_='phone')
        if phone_elem and 'href' in phone_elem.attrs:
            data['phone'] = phone_elem['href'].replace('tel:', '').strip()
        else:
            data['phone'] = None
        
        email_elem = soup.find('a', href=lambda x: x and x.startswith('mailto:'))
        if email_elem:
            data['email'] = email_elem['href'].replace('mailto:', '').strip()
        else:
            data['email'] = None
        
        # Extract parameters
        params = {}
        param_items = soup.find_all('li', class_='params-i')
        for item in param_items:
            label_elem = item.find(class_='params-i-label')
            value_elem = item.find(class_='params-i-val')
            
            if label_elem and value_elem:
                label = label_elem.text.strip()
                value = value_elem.text.strip()
                params[label] = value
        
        # Map common parameters
        data['city'] = params.get('Şəhər')
        data['age'] = params.get('Yaş')
        data['gender'] = params.get('Cins')
        data['approval_date'] = params.get('Elanın tarixi')
        data['expiry_date'] = params.get('Bitmə tarixi')
        data['full_name'] = params.get('Ad')
        
        # Extract detailed information
        data['skills'] = self.extract_detailed_info(soup, 'skills')
        data['education'] = self.extract_detailed_info(soup, 'education')
        data['education_info'] = self.extract_detailed_info(soup, 'education_info')
        data['experience'] = self.extract_detailed_info(soup, 'experience')
        data['experience_info'] = self.extract_detailed_info(soup, 'experience_info')
        data['personal_info'] = self.extract_detailed_info(soup, 'personal')
        
        # Extract listing number and view count
        header_secondary = soup.find('div', class_='post-header-secondary')
        if header_secondary:
            text = header_secondary.get_text()
            
            listing_match = re.search(r'Elan #(\d+)', text)
            data['listing_number'] = listing_match.group(1) if listing_match else None
            
            view_match = re.search(r'Baxışların sayı:\s*(\d+)', text)
            data['view_count'] = view_match.group(1) if view_match else None
        else:
            data['listing_number'] = None
            data['view_count'] = None
        
        return data
    
    def extract_detailed_info(self, soup, field_class):
        """Extract detailed information from specific field"""
        element = soup.find('dd', class_=f'{field_class} params-i-val')
        if element:
            # Get all text, preserving structure
            paragraphs = element.find_all('p')
            if paragraphs:
                text_parts = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if text:
                        text_parts.append(text)
                return '\n'.join(text_parts)
            else:
                return element.get_text().strip()
        return None
    
    def scrape_resume_details(self, resume_urls):
        """Scrape details for all resume URLs"""
        for i, url in enumerate(resume_urls, 1):
            logging.info(f"Scraping resume {i}/{len(resume_urls)}: {url}")
            
            response = self.get_page(url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            resume_data = self.parse_resume_detail(soup, url)
            self.resume_data.append(resume_data)
    
    def save_to_csv(self, filename='resume_data.csv'):
        """Save scraped data to CSV file"""
        if not self.resume_data:
            logging.warning("No data to save")
            return
        
        # Get all unique keys from all resume data
        all_keys = set()
        for resume in self.resume_data:
            all_keys.update(resume.keys())
        
        fieldnames = list(all_keys)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.resume_data)
        
        logging.info(f"Data saved to {filename}")
    
    def run_scraper(self, start_url, max_pages=None, output_file='resume_data.csv'):
        """Main method to run the complete scraping process"""
        logging.info("Starting Boss.az resume scraper")
        
        # Step 1: Scrape listing pages
        resume_links = self.scrape_listing_pages(start_url, max_pages)
        
        if not resume_links:
            logging.error("No resume links found")
            return
        
        # Step 2: Scrape individual resume details
        self.scrape_resume_details(resume_links)
        
        # Step 3: Save to CSV
        self.save_to_csv(output_file)
        
        logging.info(f"Scraping completed. Total resumes scraped: {len(self.resume_data)}")


def main():
    # Configuration
    START_URL = "https://boss.az/resumes?action=index&controller=resumes&only_path=true&page=1&type=resumes"
    MAX_PAGES = None  # Set to None to scrape all pages
    OUTPUT_FILE = "boss_az_resumes.csv"
    DELAY = 2  # Delay between requests in seconds
    
    # Create scraper instance
    scraper = BossAzScraper(delay=DELAY)
    
    # Run the scraper
    scraper.run_scraper(START_URL, max_pages=MAX_PAGES, output_file=OUTPUT_FILE)


if __name__ == "__main__":
    main()