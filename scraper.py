# News scraper module for extracting crime stories from Hindi news sources

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CrimeNewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        
    def setup_selenium(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def close_driver(self):
        """Close the Selenium driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def scrape_aajtak(self):
        """Scrape crime stories from Aaj Tak"""
        stories = []
        url = "https://www.aajtak.in/topic/crime"
        
        try:
            if not self.driver:
                self.setup_selenium()
            
            logger.info(f"Scraping Aaj Tak crime stories from: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(3)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find story elements
            story_elements = soup.find_all('article', limit=10)
            
            for element in story_elements:
                try:
                    story = self.extract_story_data(element, 'aajtak')
                    if story:
                        stories.append(story)
                except Exception as e:
                    logger.warning(f"Error extracting story from Aaj Tak: {e}")
                    continue
            
            logger.info(f"Extracted {len(stories)} stories from Aaj Tak")
            return stories
            
        except Exception as e:
            logger.error(f"Error scraping Aaj Tak: {e}")
            return []
    
    def scrape_amarujala(self):
        """Scrape crime stories from Amar Ujala"""
        stories = []
        url = "https://www.amarujala.com/crime"
        
        try:
            if not self.driver:
                self.setup_selenium()
            
            logger.info(f"Scraping Amar Ujala crime stories from: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "news-card"))
            )
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(3)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find story elements
            story_elements = soup.find_all('div', class_='news-card', limit=10)
            
            for element in story_elements:
                try:
                    story = self.extract_story_data(element, 'amarujala')
                    if story:
                        stories.append(story)
                except Exception as e:
                    logger.warning(f"Error extracting story from Amar Ujala: {e}")
                    continue
            
            logger.info(f"Extracted {len(stories)} stories from Amar Ujala")
            return stories
            
        except Exception as e:
            logger.error(f"Error scraping Amar Ujala: {e}")
            return []
    
    def scrape_indiatoday(self):
        """Scrape crime stories from India Today Hindi"""
        stories = []
        url = "https://www.indiatoday.in/crime"
        
        try:
            if not self.driver:
                self.setup_selenium()
            
            logger.info(f"Scraping India Today crime stories from: {url}")
            self.driver.get(url)
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Scroll to load more content
            self.driver.execute_script("window.scrollTo(0, 2000);")
            time.sleep(3)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find story elements
            story_elements = soup.find_all('div', class_=['story-box', 'story-item'], limit=10)
            
            for element in story_elements:
                try:
                    story = self.extract_story_data(element, 'indiatoday')
                    if story:
                        stories.append(story)
                except Exception as e:
                    logger.warning(f"Error extracting story from India Today: {e}")
                    continue
            
            logger.info(f"Extracted {len(stories)} stories from India Today")
            return stories
            
        except Exception as e:
            logger.error(f"Error scraping India Today: {e}")
            return []
    
    def extract_story_data(self, element, source):
        """Extract story data from HTML element"""
        story = {
            'source': source,
            'scraped_at': datetime.now().isoformat(),
            'headline': '',
            'summary': '',
            'image_url': '',
            'story_url': '',
            'publish_date': '',
            'crime_type': ''
        }
        
        try:
            # Extract headline
            headline_elem = element.find(['h2', 'h3', 'h4'])
            if headline_elem:
                story['headline'] = headline_elem.get_text(strip=True)
            
            # Extract story URL
            link_elem = element.find('a', href=True)
            if link_elem:
                story['story_url'] = urljoin(f"https://www.{source}.in", link_elem['href'])
            
            # Extract summary
            summary_elem = element.find(['p', 'div'], class_=['summary', 'excerpt', 'description'])
            if summary_elem:
                story['summary'] = summary_elem.get_text(strip=True)
            
            # Extract image URL
            img_elem = element.find('img')
            if img_elem and img_elem.get('src'):
                img_url = img_elem['src']
                if img_url.startswith('http'):
                    story['image_url'] = img_url
                else:
                    story['image_url'] = urljoin(f"https://www.{source}.in", img_url)
            
            # Extract publish date if available
            date_elem = element.find(['time', 'span'], class_=['date', 'published'])
            if date_elem:
                story['publish_date'] = date_elem.get_text(strip=True)
            
            # Determine crime type from headline
            story['crime_type'] = self.classify_crime_type(story['headline'])
            
            # Validate story data
            if self.validate_story(story):
                return story
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting story data: {e}")
            return None
    
    def classify_crime_type(self, headline):
        """Classify crime type based on Hindi keywords in headline"""
        headline_lower = headline.lower()
        
        crime_keywords = {
            'murder': ['हत्या', 'मर्डर', 'खून', 'कत्ल', 'मार डाला', 'मौत'],
            'theft': ['चोरी', 'चोर', 'चुराया', 'गायब', 'खोया'],
            'fraud': ['ठगी', 'धोखा', 'फ्रॉड', 'जालसाज', 'बेईमानी'],
            'assault': ['मारपीट', 'हमला', 'झगड़ा', 'लड़ाई'],
            'rape': ['बलात्कार', 'दुष्कर्म', 'छेड़छाड़'],
            'kidnapping': ['अपहरण', 'बंधक', 'गायब'],
            'terrorism': ['आतंकी', 'बम', 'धमाका', 'आतंकवाद'],
            'corruption': ['भ्रष्टाचार', 'रिश्वत', 'घूस']
        }
        
        for crime_type, keywords in crime_keywords.items():
            for keyword in keywords:
                if keyword in headline_lower:
                    return crime_type
        
        return 'general'
    
    def validate_story(self, story):
        """Validate story data"""
        # Check if headline is not empty and has reasonable length
        if not story['headline'] or len(story['headline']) < 10:
            return False
        
        # Check if story is in Hindi (contains Hindi characters)
        hindi_chars = any(ord(char) >= 2304 and ord(char) <= 2431 for char in story['headline'])
        if not hindi_chars:
            return False
        
        # Check if story is crime-related
        if story['crime_type'] == 'general':
            # Additional check for crime-related content
            crime_indicators = ['पुलिस', 'केस', 'गिरफ्तार', 'मुकदमा', 'अदालत', 'जेल']
            if not any(indicator in story['headline'] for indicator in crime_indicators):
                return False
        
        return True
    
    def scrape_all_sources(self):
        """Scrape crime stories from all configured sources"""
        all_stories = []
        
        try:
            # Scrape from Aaj Tak
            aajtak_stories = self.scrape_aajtak()
            all_stories.extend(aajtak_stories)
            
            # Scrape from Amar Ujala
            amarujala_stories = self.scrape_amarujala()
            all_stories.extend(amarujala_stories)
            
            # Scrape from India Today
            indiatoday_stories = self.scrape_indiatoday()
            all_stories.extend(indiatoday_stories)
            
            logger.info(f"Total stories collected: {len(all_stories)}")
            
            # Remove duplicates based on headline similarity
            unique_stories = self.remove_duplicates(all_stories)
            logger.info(f"Unique stories after deduplication: {len(unique_stories)}")
            
            return unique_stories
            
        except Exception as e:
            logger.error(f"Error in scrape_all_sources: {e}")
            return []
        finally:
            self.close_driver()
    
    def remove_duplicates(self, stories):
        """Remove duplicate stories based on headline similarity"""
        unique_stories = []
        seen_headlines = []
        
        for story in stories:
            headline = story['headline']
            is_duplicate = False
            
            for seen_headline in seen_headlines:
                # Simple similarity check (can be improved with more sophisticated methods)
                if self.calculate_similarity(headline, seen_headline) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_stories.append(story)
                seen_headlines.append(headline)
        
        return unique_stories
    
    def calculate_similarity(self, text1, text2):
        """Calculate similarity between two texts"""
        # Simple Jaccard similarity
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        if len(union) == 0:
            return 0
        
        return len(intersection) / len(union)
    
    def save_stories(self, stories, filename=None):
        """Save scraped stories to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'/mnt/okcomputer/output/temp/crime_stories_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(stories, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(stories)} stories to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving stories: {e}")
            return None

# Test the scraper
if __name__ == "__main__":
    scraper = CrimeNewsScraper()
    stories = scraper.scrape_all_sources()
    
    if stories:
        filename = scraper.save_stories(stories)
        print(f"Scraped {len(stories)} stories and saved to {filename}")
        
        # Print first few stories
        for i, story in enumerate(stories[:3]):
            print(f"\nStory {i+1}:")
            print(f"Headline: {story['headline']}")
            print(f"Source: {story['source']}")
            print(f"Crime Type: {story['crime_type']}")
            print(f"Image URL: {story['image_url']}")
    else:
        print("No stories scraped")