# Configuration settings for the automation system

import os
from dotenv import load_dotenv

load_dotenv()

# News Sources Configuration
NEWS_SOURCES = {
    'aajtak': {
        'url': 'https://www.aajtak.in/topic/crime',
        'selectors': {
            'stories': '.story-item, .news-item, article',
            'headline': 'h2, h3, .headline',
            'image': 'img',
            'summary': '.summary, .excerpt, p'
        },
        'language': 'hindi'
    },
    'amarujala': {
        'url': 'https://www.amarujala.com/crime',
        'selectors': {
            'stories': '.news-card, .story-card, article',
            'headline': 'h2, h3, .title',
            'image': 'img',
            'summary': '.summary, .excerpt, p'
        },
        'language': 'hindi'
    },
    'indiatoday': {
        'url': 'https://www.indiatoday.in/crime',
        'selectors': {
            'stories': '.story-box, .news-item, article',
            'headline': 'h2, h3, .title',
            'image': 'img',
            'summary': '.summary, .excerpt, p'
        },
        'language': 'hindi'
    }
}

# Canva API Configuration
CANVA_CONFIG = {
    'api_key': os.getenv('CANVA_API_KEY', ''),
    'base_url': 'https://api.canva.com/v1',
    'template_id': os.getenv('CANVA_TEMPLATE_ID', ''),
    'video_format': 'mp4',
    'resolution': '1080x1920'  # YouTube Shorts format
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    'daily_time': '06:00',
    'timezone': 'Asia/Kolkata',
    'retry_attempts': 3,
    'retry_delay': 300,  # 5 minutes
    'max_stories': 4
}

# Content Processing Configuration
CONTENT_CONFIG = {
    'summary_length': 200,  # words
    'min_headline_length': 10,
    'max_headline_length': 100,
    'image_quality': 85,
    'output_format': 'mp4'
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': '/mnt/okcomputer/output/logs/automation.log',
    'max_size': '10MB',
    'backup_count': 5
}

# Output Configuration
OUTPUT_CONFIG = {
    'base_dir': '/mnt/okcomputer/output/videos',
    'naming_pattern': 'crime_story_{date}_{index}',
    'metadata_file': 'story_metadata.json'
}

# Error Handling Configuration
ERROR_CONFIG = {
    'max_retries': 3,
    'retry_delay': 60,
    'alert_email': os.getenv('ALERT_EMAIL', ''),
    'timeout': 30
}

# Create output directories
import os
os.makedirs('/mnt/okcomputer/output/videos', exist_ok=True)
os.makedirs('/mnt/okcomputer/output/logs', exist_ok=True)
os.makedirs('/mnt/okcomputer/output/temp', exist_ok=True)