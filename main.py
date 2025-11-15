#!/usr/bin/env python3
"""
Main automation script for YouTube Shorts Crime Stories
This script orchestrates the entire workflow from scraping to video creation
"""

import os
import sys
import logging
import argparse
from datetime import datetime
import json
import time

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import CrimeNewsScraper
from content_processor import ContentProcessor
from canva_integration import CanvaVideoCreator
from scheduler import AutomationScheduler
from config import OUTPUT_CONFIG, LOGGING_CONFIG

def setup_logging():
    """Setup logging configuration"""
    log_dir = os.path.dirname(LOGGING_CONFIG['file'])
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format'],
        handlers=[
            logging.FileHandler(LOGGING_CONFIG['file']),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def run_full_workflow(logger):
    """Run the complete automation workflow"""
    logger.info("Starting full automation workflow")
    
    workflow_start = datetime.now()
    results = {
        'workflow_id': workflow_start.strftime('%Y%m%d_%H%M%S'),
        'start_time': workflow_start.isoformat(),
        'steps': {},
        'success': False
    }
    
    try:
        # Step 1: Initialize components
        logger.info("Step 1: Initializing components...")
        scraper = CrimeNewsScraper()
        processor = ContentProcessor()
        video_creator = CanvaVideoCreator()
        
        results['steps']['initialization'] = {
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        
        # Step 2: Scrape crime stories
        logger.info("Step 2: Scraping crime stories from news sources...")
        stories = scraper.scrape_all_sources()
        
        results['steps']['scraping'] = {
            'status': 'success',
            'stories_found': len(stories),
            'timestamp': datetime.now().isoformat()
        }
        
        if len(stories) == 0:
            raise Exception("No crime stories found from any source")
        
        logger.info(f"Found {len(stories)} crime stories")
        
        # Step 3: Process stories
        logger.info("Step 3: Processing and selecting best stories...")
        processed_stories = processor.process_stories(stories, max_stories=4)
        
        results['steps']['processing'] = {
            'status': 'success',
            'stories_processed': len(processed_stories),
            'timestamp': datetime.now().isoformat()
        }
        
        if len(processed_stories) == 0:
            raise Exception("No stories could be processed successfully")
        
        logger.info(f"Successfully processed {len(processed_stories)} stories")
        
        # Step 4: Create videos
        logger.info("Step 4: Creating YouTube Shorts videos...")
        created_videos = video_creator.create_videos_batch(processed_stories)
        
        results['steps']['video_creation'] = {
            'status': 'success',
            'videos_created': len(created_videos),
            'timestamp': datetime.now().isoformat()
        }
        
        if len(created_videos) == 0:
            raise Exception("No videos could be created")
        
        logger.info(f"Successfully created {len(created_videos)} videos")
        
        # Step 5: Generate final report
        logger.info("Step 5: Generating final report...")
        workflow_end = datetime.now()
        duration = (workflow_end - workflow_start).total_seconds()
        
        results['end_time'] = workflow_end.isoformat()
        results['duration_seconds'] = duration
        results['success'] = True
        results['summary'] = {
            'stories_scraped': len(stories),
            'stories_processed': len(processed_stories),
            'videos_created': len(created_videos),
            'success_rate': (len(created_videos) / len(processed_stories)) * 100 if processed_stories else 0
        }
        
        # Save results
        save_workflow_results(results, created_videos)
        
        logger.info(f"Workflow completed successfully in {duration:.2f} seconds")
        logger.info(f"Created {len(created_videos)} YouTube Shorts videos")
        
        return True, results
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        results['error'] = str(e)
        results['end_time'] = datetime.now().isoformat()
        
        save_workflow_results(results)
        return False, results

def save_workflow_results(results, videos_data=None):
    """Save workflow results and metadata"""
    try:
        # Save main results
        results_file = f"/mnt/okcomputer/output/workflow_results_{results['workflow_id']}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # Save videos metadata if available
        if videos_data:
            videos_file = f"/mnt/okcomputer/output/videos_metadata_{results['workflow_id']}.json"
            with open(videos_file, 'w', encoding='utf-8') as f:
                json.dump(videos_data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to {results_file}")
        
    except Exception as e:
        print(f"Error saving results: {e}")

def print_summary(results):
    """Print workflow summary"""
    print("\n" + "="*60)
    print("AUTOMATION WORKFLOW SUMMARY")
    print("="*60)
    
    if results.get('success'):
        print(f"✅ Status: SUCCESS")
        print(f"📅 Workflow ID: {results['workflow_id']}")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        print(f"📰 Stories Scraped: {results['summary']['stories_scraped']}")
        print(f"🔧 Stories Processed: {results['summary']['stories_processed']}")
        print(f"🎬 Videos Created: {results['summary']['videos_created']}")
        print(f"📊 Success Rate: {results['summary']['success_rate']:.1f}%")
        
        print("\n📁 Output Files:")
        results_file = f"/mnt/okcomputer/output/workflow_results_{results['workflow_id']}.json"
        videos_file = f"/mnt/okcomputer/output/videos_metadata_{results['workflow_id']}.json"
        
        if os.path.exists(results_file):
            print(f"   • Results: {results_file}")
        if os.path.exists(videos_file):
            print(f"   • Videos: {videos_file}")
    else:
        print(f"❌ Status: FAILED")
        print(f"📅 Workflow ID: {results['workflow_id']}")
        print(f"❌ Error: {results.get('error', 'Unknown error')}")
    
    print("="*60)

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description='YouTube Shorts Crime Stories Automation System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --run           # Run automation once
  python main.py --schedule      # Start daily scheduler
  python main.py --test-scraper  # Test scraper only
  python main.py --test-video    # Test video creation
        """
    )
    
    parser.add_argument('--run', action='store_true', 
                       help='Run complete automation workflow once')
    
    parser.add_argument('--schedule', action='store_true',
                       help='Start daily scheduler')
    
    parser.add_argument('--test-scraper', action='store_true',
                       help='Test news scraper only')
    
    parser.add_argument('--test-video', action='store_true',
                       help='Test video creation with sample data')
    
    parser.add_argument('--output-dir', default='/mnt/okcomputer/output',
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.run:
        # Run complete workflow
        logger.info("Starting complete automation workflow...")
        success, results = run_full_workflow(logger)
        print_summary(results)
        
        if success:
            print("\n🎉 Automation completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Automation failed!")
            sys.exit(1)
    
    elif args.schedule:
        # Start scheduler
        logger.info("Starting daily scheduler...")
        scheduler = AutomationScheduler()
        scheduler.start()
    
    elif args.test_scraper:
        # Test scraper only
        logger.info("Testing news scraper...")
        scraper = CrimeNewsScraper()
        stories = scraper.scrape_all_sources()
        
        print(f"\n📊 Scraper Test Results:")
        print(f"   Stories found: {len(stories)}")
        
        if stories:
            print(f"\n📰 Sample Stories:")
            for i, story in enumerate(stories[:3]):
                print(f"   {i+1}. {story['headline'][:60]}...")
                print(f"      Source: {story['source']}")
                print(f"      Type: {story['crime_type']}")
                print(f"      URL: {story.get('story_url', 'N/A')}")
                print()
        
        scraper.close_driver()
        
        if stories:
            print("✅ Scraper test passed!")
            sys.exit(0)
        else:
            print("❌ Scraper test failed!")
            sys.exit(1)
    
    elif args.test_video:
        # Test video creation
        logger.info("Testing video creation...")
        
        # Sample test data
        test_story = {
            'id': 1,
            'headline': 'नोएडा में फ्रॉड गैंग का ऐसे हुआ पर्दाफाश',
            'summary': 'सेट्रल नोएडा स्तिथ थाना बिसरख पुलिस ने ऑनलाइन गेमिंग एप के नाम पर ठगी करने वाले एक बड़े संगठित गिरोह का भंडाफोड़ किया। आठ सदस्यों को गिरफ्तार किया गया है जिनमें एक महिला भी शामिल है। पुलिस ने भारी मात्रा में कूटरचित दस्तावेज और उपकरण बरामद किए हैं।',
            'source': 'aajtak',
            'crime_type': 'fraud',
            'image_path': ''
        }
        
        creator = CanvaVideoCreator()
        video_path = creator.create_video_from_story(test_story)
        
        if video_path:
            print(f"\n🎬 Video Test Results:")
            print(f"   ✅ Video created successfully!")
            print(f"   📁 Path: {video_path}")
            print(f"   📊 Size: {os.path.getsize(video_path) / 1024:.1f} KB")
            sys.exit(0)
        else:
            print(f"\n🎬 Video Test Results:")
            print(f"   ❌ Video creation failed!")
            sys.exit(1)
    
    else:
        # Show help
        parser.print_help()
        print("\n🎯 Quick Start:")
        print("   python main.py --run       # Run automation once")
        print("   python main.py --schedule  # Start daily scheduler")
        print("   python main.py --test      # Test all components")

if __name__ == "__main__":
    main()