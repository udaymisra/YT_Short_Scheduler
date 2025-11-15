# YouTube Shorts Crime Stories Automation System

## System Architecture

### Core Components
1. **News Scraper Engine** - Extracts crime stories from Hindi news sources
2. **Content Processor** - Processes headlines, images, and summaries
3. **Canva Integration** - Creates YouTube Shorts videos
4. **Scheduler** - Daily automation trigger
5. **Monitoring System** - Error handling and logging

### Data Sources
**Primary Hindi News Sources:**
- Aaj Tak (https://www.aajtak.in/topic/crime)
- India Today Hindi (https://www.indiatoday.in/crime)
- Amar Ujala (https://www.amarujala.com/crime)
- BBC Hindi
- NDTV India

### Content Processing Pipeline

#### Stage 1: Story Extraction
```python
# Story structure
{
  "headline": "Hindi crime story headline",
  "image_url": "Related image URL",
  "summary": "200-word Hindi summary",
  "source": "News source",
  "publish_date": "Story date",
  "crime_type": "Murder/Theft/Fraud etc."
}
```

#### Stage 2: Content Validation
- Verify story authenticity
- Check for graphic content
- Ensure Hindi language quality
- Validate image relevance

#### Stage 3: Video Creation
- Canva template integration
- Dynamic content replacement
- Video generation and export

### Technical Implementation

#### Technology Stack
- **Backend**: Python 3.9+
- **Web Scraping**: BeautifulSoup, Selenium
- **HTTP Requests**: requests, aiohttp
- **Image Processing**: PIL/Pillow
- **Scheduling**: APScheduler
- **Database**: SQLite for tracking
- **Canva API**: REST API integration

#### File Structure
```
/mnt/okcomputer/output/
├── main.py                 # Main automation script
├── scraper.py             # News scraping module
├── content_processor.py   # Content processing
├── canva_integration.py   # Video creation
├── scheduler.py          # Daily scheduler
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── logs/                 # Log files
```

### Daily Workflow
1. **6:00 AM IST**: Scheduler triggers automation
2. **6:01-6:05 AM**: Scrape crime stories from sources
3. **6:06-6:10 AM**: Process and validate 4 best stories
4. **6:11-6:20 AM**: Create Canva videos for each story
5. **6:21-6:25 AM**: Export and save videos
6. **6:26 AM**: Send completion notification

### Error Handling
- Retry mechanisms for failed API calls
- Fallback news sources
- Alert system for critical failures
- Automatic cleanup of incomplete processes

### Quality Assurance
- Hindi grammar validation
- Image relevance checking
- Content length optimization
- Sensitivity review

### Monitoring & Logging
- Detailed execution logs
- Success/failure tracking
- Performance metrics
- Error reporting system

## Implementation Phases

### Phase 1: Core Development (Days 1-3)
- [ ] News scraper implementation
- [ ] Content processing pipeline
- [ ] Basic Canva integration

### Phase 2: Testing & Refinement (Days 4-5)
- [ ] Test with sample stories
- [ ] Refine Hindi processing
- [ ] Optimize video templates

### Phase 3: Deployment (Days 6-7)
- [ ] Scheduler setup
- [ ] Monitoring system
- [ ] Production deployment

## Configuration Settings

### News Sources
```python
NEWS_SOURCES = {
    'aajtak': {
        'url': 'https://www.aajtak.in/topic/crime',
        'selector': '.story-item',
        'language': 'hindi'
    },
    'amarujala': {
        'url': 'https://www.amarujala.com/crime',
        'selector': '.news-card',
        'language': 'hindi'
    }
}
```

### Canva Templates
- Template ID for YouTube Shorts format
- Text overlay positions
- Image placement areas
- Branding elements

### Scheduling
```python
SCHEDULE_CONFIG = {
    'daily_time': '06:00',
    'timezone': 'Asia/Kolkata',
    'retry_attempts': 3,
    'retry_delay': 300
}
```

This system will provide complete automation for creating YouTube Shorts videos about real crime stories in Hindi, running efficiently on a daily schedule.