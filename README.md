# YouTube Shorts Crime Stories Automation System

## Overview

This is a comprehensive automation system that extracts real crime stories in Hindi from various news sources and creates YouTube Shorts videos using Canva-style templates. The system runs on a daily schedule to generate 4 high-quality crime story videos automatically.

## Features

- **Automated News Scraping**: Extracts crime stories from Aaj Tak, Amar Ujala, India Today, and other Hindi news sources
- **Content Processing**: Automatically processes headlines, extracts images, and generates 200-word summaries
- **Video Creation**: Creates YouTube Shorts videos in 9:16 format with professional templates
- **Daily Scheduling**: Runs automatically every day at 6:00 AM IST
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Monitoring**: Detailed logging and statistics tracking

## System Architecture

### Components

1. **News Scraper** (`scraper.py`): Extracts crime stories from multiple Hindi news sources
2. **Content Processor** (`content_processor.py`): Processes and validates story content
3. **Video Creator** (`canva_integration.py`): Creates YouTube Shorts videos
4. **Scheduler** (`scheduler.py`): Manages daily automation
5. **Main Controller** (`main.py`): Orchestrates the complete workflow

### Technology Stack

- **Backend**: Python 3.9+
- **Web Scraping**: BeautifulSoup, Selenium
- **Image Processing**: PIL/Pillow
- **Scheduling**: APScheduler
- **HTTP Requests**: requests library
- **Logging**: Python logging module

## Installation

### Prerequisites

- Python 3.9 or higher
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (automatically managed)
- 2GB+ free disk space
- Internet connection

### Setup Steps

1. **Clone or Download the Project**
   ```bash
   cd /mnt/okcomputer/output
   ```

2. **Install Dependencies**
   ```bash
   pip install beautifulsoup4 requests Pillow selenium apscheduler python-dotenv lxml
   ```

3. **Create Required Directories**
   ```bash
   mkdir -p /mnt/okcomputer/output/videos
   mkdir -p /mnt/okcomputer/output/logs
   mkdir -p /mnt/okcomputer/output/temp
   ```

4. **Set Up Environment Variables** (Optional)
   Create a `.env` file for configuration:
   ```env
   CANVA_API_KEY=your_canva_api_key
   CANVA_TEMPLATE_ID=your_template_id
   ALERT_EMAIL=your_email@example.com
   ```

## Usage

### Quick Start

1. **Test the System**
   ```bash
   python main.py --test-scraper
   ```

2. **Run Automation Once**
   ```bash
   python main.py --run
   ```

3. **Start Daily Scheduler**
   ```bash
   python main.py --schedule
   ```

### Command Line Options

```bash
# Run complete automation workflow
python main.py --run

# Start daily scheduler
python main.py --schedule

# Test scraper only
python main.py --test-scraper

# Test video creation
python main.py --test-video

# Show current status
python main.py --status
```

### Manual Testing

1. **Test Scraper**
   ```python
   from scraper import CrimeNewsScraper
   scraper = CrimeNewsScraper()
   stories = scraper.scrape_all_sources()
   print(f"Found {len(stories)} stories")
   ```

2. **Test Content Processor**
   ```python
   from content_processor import ContentProcessor
   processor = ContentProcessor()
   processed = processor.process_stories(stories)
   ```

3. **Test Video Creator**
   ```python
   from canva_integration import CanvaVideoCreator
   creator = CanvaVideoCreator()
   video_path = creator.create_video_from_story(processed_story)
   ```

## Configuration

### News Sources

The system scrapes from these Hindi news sources:
- Aaj Tak (aajtak.in)
- Amar Ujala (amarujala.com)
- India Today Hindi (indiatoday.in)

You can add more sources by modifying the `NEWS_SOURCES` configuration in `config.py`.

### Scheduling

Default schedule: Daily at 6:00 AM IST
Modify in `config.py`:
```python
SCHEDULE_CONFIG = {
    'daily_time': '06:00',  # Change as needed
    'timezone': 'Asia/Kolkata'
}
```

### Video Settings

- **Format**: JPEG images (simulating video)
- **Resolution**: 1080x1920 (9:16 aspect ratio)
- **Quality**: 95% JPEG quality
- **Template**: Professional crime news template

## Output Structure

```
/mnt/okcomputer/output/
├── videos/                    # Generated YouTube Shorts
│   ├── crime_story_20251115_060000_1.jpg
│   ├── crime_story_20251115_060000_2.jpg
│   └── ...
├── logs/                      # Log files
│   └── automation.log
├── temp/                      # Temporary files
│   ├── crime_stories_20251115_060000.json
│   └── processed_stories_20251115_060000.json
├── workflow_results_20251115_060000.json
└── videos_metadata_20251115_060000.json
```

## Monitoring and Maintenance

### Logs

- **Main Log**: `/mnt/okcomputer/output/logs/automation.log`
- **Log Level**: INFO (can be changed to DEBUG for detailed logging)

### Statistics

The system maintains statistics in `/mnt/okcomputer/output/automation_statistics.json`:
- Total stories scraped
- Total videos created
- Success rates
- Run history

### Health Checks

The scheduler performs hourly health checks and logs system status.

## Troubleshooting

### Common Issues

1. **No Stories Found**
   - Check internet connection
   - Verify news source websites are accessible
   - Check logs for specific errors

2. **Video Creation Fails**
   - Ensure sufficient disk space
   - Check image processing dependencies
   - Verify output directory permissions

3. **Selenium Errors**
   - Install Chrome/Chromium browser
   - Check ChromeDriver compatibility
   - Run with `--headless` flag for server environments

4. **Permission Errors**
   - Ensure write permissions for output directories
   - Run with appropriate user privileges

### Debug Mode

Enable detailed logging by setting log level to DEBUG:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Performance Optimization

### Scraping Optimization
- Uses Selenium for JavaScript-heavy sites
- Implements intelligent waiting for content loading
- Handles dynamic content with scrolling

### Content Processing
- Filters stories by quality score
- Removes duplicate stories
- Validates Hindi content

### Video Creation
- Optimizes image sizes for YouTube Shorts
- Uses efficient text wrapping
- Implements caching for repeated elements

## Security Considerations

- No sensitive data storage
- Uses environment variables for API keys
- Implements rate limiting for requests
- Sanitizes all external content

## Future Enhancements

- [ ] Real Canva API integration
- [ ] Actual video generation (MP4)
- [ ] Multiple language support
- [ ] Advanced story classification
- [ ] Social media integration
- [ ] Web dashboard for monitoring
- [ ] Email notifications
- [ ] Cloud deployment options

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Test individual components
4. Check system requirements

## License

This project is created for educational and automation purposes. Please respect the terms of service of the news sources being scraped.

---

**Note**: This system is designed to work with publicly available news content. Ensure compliance with the terms of service of the news sources and YouTube's content policies.