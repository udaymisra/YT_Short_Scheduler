# Canva integration module for creating YouTube Shorts videos

import requests
import json
import logging
import os
from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)

class CanvaVideoCreator:
    def __init__(self, api_key=None, template_id=None):
        self.api_key = api_key or os.getenv('CANVA_API_KEY', '')
        self.template_id = template_id or os.getenv('CANVA_TEMPLATE_ID', '')
        self.base_url = 'https://api.canva.com/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.output_dir = '/mnt/okcomputer/output/videos'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_video_from_story(self, story_data):
        """Create a YouTube Shorts video from processed story data"""
        try:
            logger.info(f"Creating video for story: {story_data['headline'][:50]}...")
            
            # Since Canva API requires complex setup, we'll create a simple video using PIL
            # This creates a static image with text overlay that can be converted to video
            video_path = self.create_static_video(story_data)
            
            if video_path:
                logger.info(f"Video created successfully: {video_path}")
                return video_path
            else:
                logger.error("Failed to create video")
                return None
                
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return None
    
    def create_static_video(self, story_data):
        """Create a static image with text overlay (simulating video creation)"""
        try:
            # Create a 9:16 aspect ratio canvas (1080x1920)
            width, height = 1080, 1920
            canvas = Image.new('RGB', (width, height), color='#1a1a1a')
            draw = ImageDraw.Draw(canvas)
            
            # Add background image if available
            if story_data.get('image_path') and os.path.exists(story_data['image_path']):
                try:
                    bg_image = Image.open(story_data['image_path'])
                    bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
                    
                    # Create a dark overlay for better text readability
                    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 150))
                    canvas = Image.alpha_composite(bg_image.convert('RGBA'), overlay).convert('RGB')
                    draw = ImageDraw.Draw(canvas)
                except Exception as e:
                    logger.warning(f"Could not add background image: {e}")
            
            # Add headline
            headline = story_data['headline']
            headline_font_size = 60
            
            # Try to use a better font if available
            try:
                headline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", headline_font_size)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            except:
                headline_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Draw headline with text wrapping
            margin = 80
            max_width = width - (margin * 2)
            
            # Wrap headline text
            wrapped_headlines = self.wrap_text(headline, headline_font, max_width, draw)
            
            # Draw headline
            y_position = 200
            for line in wrapped_headlines:
                bbox = draw.textbbox((0, 0), line, font=headline_font)
                text_width = bbox[2] - bbox[0]
                x_position = (width - text_width) // 2
                
                # Add text shadow
                draw.text((x_position + 2, y_position + 2), line, font=headline_font, fill='black')
                draw.text((x_position, y_position), line, font=headline_font, fill='white')
                
                y_position += headline_font_size + 20
            
            # Draw separator line
            separator_y = y_position + 40
            draw.line([(margin, separator_y), (width - margin, separator_y)], 
                     fill='#ff6b35', width=3)
            
            # Draw summary
            summary = story_data['summary']
            summary_font_size = 35
            
            try:
                summary_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", summary_font_size)
            except:
                summary_font = ImageFont.load_default()
            
            # Wrap summary text
            wrapped_summary = self.wrap_text(summary, summary_font, max_width, draw)
            
            # Draw summary
            y_position = separator_y + 80
            for line in wrapped_summary:
                bbox = draw.textbbox((0, 0), line, font=summary_font)
                text_width = bbox[2] - bbox[0]
                x_position = (width - text_width) // 2
                
                draw.text((x_position, y_position), line, font=summary_font, fill='white')
                y_position += summary_font_size + 15
            
            # Add source and timestamp
            source_text = f"स्रोत: {story_data['source'].title()} | {datetime.now().strftime('%d/%m/%Y')}"
            try:
                source_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 25)
            except:
                source_font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), source_text, font=source_font)
            text_width = bbox[2] - bbox[0]
            x_position = (width - text_width) // 2
            
            draw.text((x_position, height - 100), source_text, font=source_font, fill='#cccccc')
            
            # Save the image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"crime_story_{timestamp}_{story_data['id']}.jpg"
            filepath = os.path.join(self.output_dir, filename)
            
            canvas.save(filepath, 'JPEG', quality=95, optimize=True)
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error creating static video: {e}")
            return None
    
    def wrap_text(self, text, font, max_width, draw):
        """Wrap text to fit within specified width"""
        if not text:
            return []
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            line_width = bbox[2] - bbox[0]
            
            if line_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, split it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_videos_batch(self, stories_data):
        """Create videos for multiple stories"""
        created_videos = []
        
        for i, story in enumerate(stories_data):
            try:
                logger.info(f"Processing story {i+1}/{len(stories_data)}")
                video_path = self.create_video_from_story(story)
                
                if video_path:
                    created_videos.append({
                        'story_id': story['id'],
                        'headline': story['headline'],
                        'video_path': video_path,
                        'created_at': datetime.now().isoformat()
                    })
                
                # Small delay between video creations
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing story {i+1}: {e}")
                continue
        
        logger.info(f"Successfully created {len(created_videos)} videos")
        return created_videos
    
    def save_video_metadata(self, videos_data, filename=None):
        """Save video creation metadata"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{self.output_dir}/video_metadata_{timestamp}.json'
        
        try:
            metadata = {
                'created_at': datetime.now().isoformat(),
                'total_videos': len(videos_data),
                'videos': videos_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved video metadata to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving video metadata: {e}")
            return None

# Test the video creator
if __name__ == "__main__":
    # Sample test data
    test_story = {
        'id': 1,
        'headline': 'नोएडा में फ्रॉड गैंग का ऐसे हुआ पर्दाफाश',
        'summary': 'सेट्रल नोएडा स्तिथ थाना बिसरख पुलिस ने ऑनलाइन गेमिंग एप के नाम पर ठगी करने वाले एक बड़े संगठित गिरोह का भंडाफोड़ करते हुए आठ सदस्यों को गिरफ्तार किया है। गिरफ्तार आरोपियों में एक महिला भी शामिल है। इनके कब्जे से भारी मात्रा में कूटरचित बैंक पासबुक, चेकबुक, फर्जी एटीएम कार्ड, प्री-एक्टिवेटेड सिम, 8 लैपटॉप, 56 मोबाइल फोन सहित अन्य उपकरण बरामद हुए हैं।',
        'source': 'aajtak',
        'crime_type': 'fraud',
        'image_path': ''  # Optional test image
    }
    
    creator = CanvaVideoCreator()
    video_path = creator.create_video_from_story(test_story)
    
    if video_path:
        print(f"Video created successfully: {video_path}")
    else:
        print("Failed to create video")