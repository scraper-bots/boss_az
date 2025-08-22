import scrapy
import re
from urllib.parse import urljoin


class ResumeSpider(scrapy.Spider):
    name = "resume_spider"
    allowed_domains = ["boss.az"]
    start_urls = [
        "https://boss.az/resumes?action=index&controller=resumes&only_path=true&page=1&type=resumes"
    ]
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
    }

    def parse(self, response):
        """Parse listing pages and extract resume links"""
        
        # Extract all resume links from current page
        resume_links = response.css('.results-i-link::attr(href)').getall()
        
        for link in resume_links:
            full_url = urljoin('https://boss.az', link)
            yield response.follow(full_url, self.parse_resume_detail, 
                                meta={'resume_url': full_url})
        
        # Follow pagination
        next_page = response.css('nav.pagination span.next a[rel="next"]::attr(href)').extract_first()
        if next_page:
            next_page_url = urljoin('https://boss.az', next_page)
            yield response.follow(next_page_url, self.parse)

    def parse_resume_detail(self, response):
        """Parse individual resume detail pages"""
        
        # Extract basic listing info from the page
        title = response.css('h1.post-title::text').get()
        if title:
            title = title.strip()
        
        salary = response.css('span.post-salary.salary::text').get()
        if salary:
            salary = salary.strip()
        
        seeker_name = response.css('.post-seeker::text').get()
        if seeker_name:
            seeker_name = seeker_name.strip()
        
        # Extract contact information
        phone = response.css('a.phone::attr(href)').get()
        if phone:
            phone = phone.replace('tel:', '').strip()
        
        email = response.css('a[href^="mailto:"]::attr(href)').get()
        if email:
            email = email.replace('mailto:', '').strip()
        
        # Extract parameters from the detail page
        params = {}
        param_items = response.css('ul.params li.params-i')
        
        for item in param_items:
            label = item.css('.params-i-label::text').get()
            value = item.css('.params-i-val::text').get()
            
            if label and value:
                label = label.strip()
                value = value.strip()
                params[label] = value
        
        # Extract skills, education, experience info
        skills = self.extract_detailed_info(response, 'skills')
        education = self.extract_detailed_info(response, 'education')
        education_info = self.extract_detailed_info(response, 'education_info')
        experience = self.extract_detailed_info(response, 'experience')
        experience_info = self.extract_detailed_info(response, 'experience_info')
        personal_info = self.extract_detailed_info(response, 'personal')
        
        # Extract listing number from the page
        listing_number = None
        listing_text = response.css('.post-header-secondary::text').getall()
        for text in listing_text:
            if 'Elan #' in text:
                listing_number = re.search(r'Elan #(\d+)', text)
                if listing_number:
                    listing_number = listing_number.group(1)
                break
        
        # Extract view count
        view_count = None
        for text in listing_text:
            if 'Baxışların sayı:' in text:
                view_count = re.search(r'Baxışların sayı:\s*(\d+)', text)
                if view_count:
                    view_count = view_count.group(1)
                break
        
        yield {
            'url': response.meta.get('resume_url'),
            'title': title,
            'seeker_name': seeker_name,
            'salary': salary,
            'phone': phone,
            'email': email,
            'listing_number': listing_number,
            'view_count': view_count,
            'city': params.get('Şəhər'),
            'age': params.get('Yaş'),
            'gender': params.get('Cins'),
            'approval_date': params.get('Elanın tarixi'),
            'expiry_date': params.get('Bitmə tarixi'),
            'full_name': params.get('Ad'),
            'skills': skills,
            'education': education,
            'education_info': education_info,
            'experience': experience,
            'experience_info': experience_info,
            'personal_info': personal_info,
        }

    def extract_detailed_info(self, response, field_class):
        """Extract detailed information from dd tags"""
        info_element = response.css(f'dd.{field_class}.params-i-val')
        if info_element:
            # Try to get text content, preserving line breaks
            paragraphs = info_element.css('p::text').getall()
            if paragraphs:
                return '\n'.join([p.strip() for p in paragraphs if p.strip()])
            else:
                text = info_element.css('::text').get()
                return text.strip() if text else None
        return None