# Content processing module for handling headlines, images, and summaries

import os
import logging
from PIL import Image
import requests
from io import BytesIO
import re
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ContentProcessor:
    def __init__(self):
        self.processed_stories = []
        self.output_dir = '/mnt/okcomputer/output/videos'
        self.temp_dir = '/mnt/okcomputer/output/temp'
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_stories(self, stories, max_stories=4):
        """Process scraped stories and prepare them for video creation"""
        processed_stories = []
        
        # Sort stories by relevance and quality
        sorted_stories = self.sort_stories_by_quality(stories)
        
        for i, story in enumerate(sorted_stories[:max_stories]):
            try:
                processed_story = self.process_single_story(story, i+1)
                if processed_story:
                    processed_stories.append(processed_story)
                    logger.info(f"Successfully processed story {i+1}: {processed_story['headline'][:50]}...")
                else:
                    logger.warning(f"Failed to process story {i+1}")
            except Exception as e:
                logger.error(f"Error processing story {i+1}: {e}")
                continue
        
        self.processed_stories = processed_stories
        return processed_stories
    
    def sort_stories_by_quality(self, stories):
        """Sort stories by quality score"""
        scored_stories = []
        
        for story in stories:
            score = self.calculate_quality_score(story)
            scored_stories.append((score, story))
        
        # Sort by score (highest first)
        scored_stories.sort(reverse=True, key=lambda x: x[0])
        
        return [story for score, story in scored_stories]
    
    def calculate_quality_score(self, story):
        """Calculate quality score for a story"""
        score = 0
        
        # Headline quality (40%)
        headline = story.get('headline', '')
        if len(headline) > 20 and len(headline) < 100:
            score += 40
        elif len(headline) >= 10:
            score += 20
        
        # Image availability (30%)
        if story.get('image_url'):
            score += 30
        
        # Summary quality (20%)
        summary = story.get('summary', '')
        if len(summary) > 50:
            score += 20
        
        # Crime type specificity (10%)
        if story.get('crime_type') != 'general':
            score += 10
        
        return score
    
    def process_single_story(self, story, index):
        """Process a single story"""
        processed_story = {
            'id': index,
            'original_data': story,
            'headline': '',
            'summary': '',
            'image_path': '',
            'crime_type': story.get('crime_type', 'general'),
            'source': story.get('source', 'unknown'),
            'processed_at': datetime.now().isoformat()
        }
        
        # Process headline
        processed_story['headline'] = self.process_headline(story.get('headline', ''))
        
        # Process summary
        processed_story['summary'] = self.process_summary(
            story.get('summary', ''), 
            story.get('story_url', '')
        )
        
        # Process image
        image_path = self.process_image(story.get('image_url', ''), index)
        if image_path:
            processed_story['image_path'] = image_path
        
        # Validate processed story
        if self.validate_processed_story(processed_story):
            return processed_story
        else:
            return None
    
    def process_headline(self, headline):
        """Process and clean headline"""
        if not headline:
            return ""
        
        # Clean headline
        headline = headline.strip()
        
        # Remove extra spaces
        headline = re.sub(r'\s+', ' ', headline)
        
        # Ensure proper Hindi formatting
        headline = self.clean_hindi_text(headline)
        
        # Truncate if too long (max 80 characters for video)
        if len(headline) > 80:
            headline = headline[:77] + "..."
        
        return headline
    
    def process_summary(self, summary, story_url):
        """Process and generate summary"""
        if not summary and story_url:
            # Try to fetch more content from the story URL
            summary = self.fetch_story_content(story_url)
        
        if not summary:
            summary = ""
        
        # Clean summary
        summary = summary.strip()
        summary = re.sub(r'\s+', ' ', summary)
        
        # Clean Hindi text
        summary = self.clean_hindi_text(summary)
        
        # Generate 200-word summary if content is available
        if len(summary) > 200:
            summary = self.generate_summary(summary, 200)
        elif len(summary) < 50:
            # Add generic crime story context
            summary = self.enhance_summary(summary)
        
        return summary
    
    def fetch_story_content(self, url):
        """Fetch additional content from story URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find article content
                article = soup.find('article') or soup.find('div', class_='content')
                if article:
                    paragraphs = article.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:3]])
                    return content
            
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to fetch story content from {url}: {e}")
            return ""
    
    def generate_summary(self, text, max_words):
        """Generate summary of specified length"""
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        # Simple extraction-based summary
        summary_words = words[:max_words-3]
        return ' '.join(summary_words) + "..."
    
    def enhance_summary(self, summary):
        """Enhance short summaries with context"""
        if not summary:
            summary = "यह एक गंभीर अपराध की घटना है।"
        
        # Add context if summary is too short
        if len(summary.split()) < 30:
            context = " पुलिस जांच में जुटी है और आरोपियों की तलाश जारी है।"
            summary = summary + context
        
        return summary
    
    def process_image(self, image_url, story_index):
        """Download and process image for video"""
        if not image_url:
            return ""
        
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return ""
            
            # Open image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize for YouTube Shorts (9:16 aspect ratio)
            # Target size: 1080x1920
            img = self.resize_for_shorts(img)
            
            # Save processed image
            image_filename = f"story_{story_index}_image.jpg"
            image_path = os.path.join(self.temp_dir, image_filename)
            
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            
            logger.info(f"Processed image saved: {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return ""
    
    def resize_for_shorts(self, img):
        """Resize image for YouTube Shorts format (9:16)"""
        width, height = img.size
        target_width, target_height = 1080, 1920
        
        # Calculate aspect ratios
        img_ratio = width / height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            img = img.crop((left, 0, left + new_width, height))
        else:
            # Image is taller, crop height
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            img = img.crop((0, top, width, top + new_height))
        
        # Resize to target dimensions
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        return img
    
    def clean_hindi_text(self, text):
        """Clean and format Hindi text"""
        # Remove unwanted characters
        text = re.sub(r'[^\u0900-\u097F\u0020-\u007E\s]', '', text)
        
        # Fix common Hindi formatting issues
        text = text.replace(' ,', ',').replace(' .', '.')
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def validate_processed_story(self, story):
        """Validate processed story data"""
        # Check headline
        if not story['headline'] or len(story['headline']) < 10:
            return False
        
        # Check summary
        if not story['summary'] or len(story['summary']) < 50:
            return False
        
        # Check for Hindi content
        hindi_chars = any(ord(char) >= 2304 and ord(char) <= 2431 for char in story['headline'])
        if not hindi_chars:
            return False
        
        return True
    
    def save_processed_stories(self, filename=None):
        """Save processed stories to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{self.temp_dir}/processed_stories_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.processed_stories, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(self.processed_stories)} processed stories to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving processed stories: {e}")
            return None
    
    def get_video_metadata(self):
        """Generate metadata for video creation"""
        metadata = {
            'total_stories': len(self.processed_stories),
            'processing_time': datetime.now().isoformat(),
            'stories': []
        }
        
        for story in self.processed_stories:
            story_meta = {
                'id': story['id'],
                'headline': story['headline'],
                'crime_type': story['crime_type'],
                'source': story['source'],
                'summary_length': len(story['summary']),
                'has_image': bool(story['image_path'])
            }
            metadata['stories'].append(story_meta)
        
        return metadata

# Test the content processor
if __name__ == "__main__":
    # Sample test data
    test_stories = [
        {
            'headline': 'नोएडा में फ्रॉड गैंग का ऐसे हुआ पर्दाफाश',
            'summary': 'सेट्रल नोएडा स्तिथ थाना बिसरख पुलिस ने ऑनलाइन गेमिंग एप के नाम पर ठगी करने वाले एक बड़े संगठित गिरोह का भंडाफोड़ करते हुए आठ सदस्यों को गिरफ्तार किया है।',
            'image_url': 'https://example.com/image1.jpg',
            'source': 'aajtak',
            'crime_type': 'fraud'
        },
        {
            'headline': 'दिल्ली ब्लास्ट: आतंकी डॉ. उमर ने बनाया ब्लास्ट का ये प्लान',
            'summary': 'दिल्ली के लाल किला मेट्रो स्टेशन ब्लास्ट में बड़ा खुलासा—हमले के तार फरीदाबाद टेरर मॉड्यूल से जुड़े मिले।',
            'image_url': 'https://example.com/image2.jpg',
            'source': 'aajtak',
            'crime_type': 'terrorism'
        }
    ]
    
    processor = ContentProcessor()
    processed = processor.process_stories(test_stories)
    
    print(f"Processed {len(processed)} stories")
    for story in processed:
        print(f"\nStory {story['id']}:")
        print(f"Headline: {story['headline']}")
        print(f"Summary length: {len(story['summary'])} chars")
        print(f"Image path: {story['image_path']}")
        print(f"Crime type: {story['crime_type']}")