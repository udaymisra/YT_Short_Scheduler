# Scheduler module for daily automation

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import os
import sys
from datetime import datetime
import json

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import CrimeNewsScraper
from content_processor import ContentProcessor
from canva_integration import CanvaVideoCreator
from config import SCHEDULE_CONFIG, OUTPUT_CONFIG

logger = logging.getLogger(__name__)

class AutomationScheduler:
    def __init__(self):
        self.scheduler = BlockingScheduler()
        self.scraper = CrimeNewsScraper()
        self.processor = ContentProcessor()
        self.video_creator = CanvaVideoCreator()
        
        # Setup logging
        self.setup_logging()
        
        # Track execution statistics
        self.stats = {
            'last_run': None,
            'total_stories_scraped': 0,
            'total_videos_created': 0,
            'last_success_rate': 0,
            'runs': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = '/mnt/okcomputer/output/logs'
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def run_automation(self):
        """Main automation workflow"""
        run_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        logger.info(f"Starting automation run: {run_id}")
        
        run_stats = {
            'run_id': run_id,
            'start_time': datetime.now().isoformat(),
            'stories_scraped': 0,
            'stories_processed': 0,
            'videos_created': 0,
            'errors': [],
            'status': 'started'
        }
        
        try:
            # Step 1: Scrape crime stories
            logger.info("Step 1: Scraping crime stories...")
            stories = self.scraper.scrape_all_sources()
            run_stats['stories_scraped'] = len(stories)
            
            if len(stories) == 0:
                raise Exception("No stories scraped from any source")
            
            # Step 2: Process stories
            logger.info("Step 2: Processing stories...")
            processed_stories = self.processor.process_stories(stories, max_stories=4)
            run_stats['stories_processed'] = len(processed_stories)
            
            if len(processed_stories) == 0:
                raise Exception("No stories could be processed")
            
            # Step 3: Create videos
            logger.info("Step 3: Creating videos...")
            created_videos = self.video_creator.create_videos_batch(processed_stories)
            run_stats['videos_created'] = len(created_videos)
            
            # Step 4: Save metadata
            logger.info("Step 4: Saving metadata...")
            self.save_run_metadata(run_stats, created_videos)
            
            # Update overall statistics
            self.update_statistics(run_stats)
            
            run_stats['status'] = 'completed'
            run_stats['end_time'] = datetime.now().isoformat()
            
            logger.info(f"Automation completed successfully. Created {len(created_videos)} videos")
            
            return True
            
        except Exception as e:
            error_msg = f"Automation failed: {str(e)}"
            logger.error(error_msg)
            
            run_stats['status'] = 'failed'
            run_stats['errors'].append(error_msg)
            run_stats['end_time'] = datetime.now().isoformat()
            
            self.stats['runs'].append(run_stats)
            return False
        
        finally:
            # Save run statistics
            self.save_statistics()
    
    def save_run_metadata(self, run_stats, videos_data):
        """Save metadata for the current run"""
        try:
            metadata = {
                'run_id': run_stats['run_id'],
                'timestamp': datetime.now().isoformat(),
                'statistics': run_stats,
                'videos': videos_data,
                'summary': {
                    'total_stories': run_stats['stories_scraped'],
                    'processed_stories': run_stats['stories_processed'],
                    'created_videos': run_stats['videos_created'],
                    'success_rate': (run_stats['videos_created'] / 4) * 100 if run_stats['stories_processed'] > 0 else 0
                }
            }
            
            filename = f"/mnt/okcomputer/output/run_metadata_{run_stats['run_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved run metadata: {filename}")
            
        except Exception as e:
            logger.error(f"Error saving run metadata: {e}")
    
    def update_statistics(self, run_stats):
        """Update overall statistics"""
        self.stats['last_run'] = datetime.now().isoformat()
        self.stats['total_stories_scraped'] += run_stats['stories_scraped']
        self.stats['total_videos_created'] += run_stats['videos_created']
        
        if run_stats['stories_processed'] > 0:
            self.stats['last_success_rate'] = (run_stats['videos_created'] / run_stats['stories_processed']) * 100
        
        self.stats['runs'].append(run_stats)
        
        # Keep only last 30 runs in memory
        if len(self.stats['runs']) > 30:
            self.stats['runs'] = self.stats['runs'][-30:]
    
    def save_statistics(self):
        """Save statistics to file"""
        try:
            filename = "/mnt/okcomputer/output/automation_statistics.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
            
            logger.info("Saved automation statistics")
            
        except Exception as e:
            logger.error(f"Error saving statistics: {e}")
    
    def load_statistics(self):
        """Load existing statistics"""
        try:
            filename = "/mnt/okcomputer/output/automation_statistics.json"
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
                logger.info("Loaded existing statistics")
        except Exception as e:
            logger.warning(f"Could not load statistics: {e}")
    
    def setup_scheduler(self):
        """Setup the daily scheduler"""
        # Load existing statistics
        self.load_statistics()
        
        # Schedule daily automation
        daily_time = SCHEDULE_CONFIG['daily_time']  # "06:00"
        hour, minute = map(int, daily_time.split(':'))
        
        # Schedule for daily execution
        self.scheduler.add_job(
            self.run_automation,
            trigger=CronTrigger(
                hour=hour,
                minute=minute,
                timezone=SCHEDULE_CONFIG['timezone']
            ),
            id='daily_crime_stories',
            name='Daily Crime Stories Automation',
            replace_existing=True
        )
        
        logger.info(f"Scheduled daily automation at {daily_time} IST")
        
        # Add health check job every hour
        self.scheduler.add_job(
            self.health_check,
            trigger=CronTrigger(minute=0),  # Every hour
            id='health_check',
            name='Health Check',
            replace_existing=True
        )
    
    def health_check(self):
        """Perform health check"""
        logger.info("Health check: System is running")
        
        # Check if next run is scheduled
        jobs = self.scheduler.get_jobs()
        for job in jobs:
            if job.id == 'daily_crime_stories':
                next_run = job.next_run_time
                logger.info(f"Next automation run: {next_run}")
    
    def start(self):
        """Start the scheduler"""
        try:
            self.setup_scheduler()
            logger.info("Starting automation scheduler...")
            logger.info("Press Ctrl+C to stop")
            
            # Start the scheduler
            self.scheduler.start()
            
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def run_once(self):
        """Run automation once immediately"""
        logger.info("Running automation once...")
        return self.run_automation()
    
    def get_status(self):
        """Get current status"""
        jobs = self.scheduler.get_jobs()
        status = {
            'scheduler_running': self.scheduler.running,
            'jobs': [],
            'statistics': self.stats
        }
        
        for job in jobs:
            status['jobs'].append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None
            })
        
        return status

# Command line interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Crime Stories Automation Scheduler')
    parser.add_argument('--start', action='store_true', help='Start the scheduler')
    parser.add_argument('--run-once', action='store_true', help='Run automation once')
    parser.add_argument('--status', action='store_true', help='Show current status')
    
    args = parser.parse_args()
    
    scheduler = AutomationScheduler()
    
    if args.start:
        scheduler.start()
    elif args.run_once:
        success = scheduler.run_once()
        if success:
            print("Automation completed successfully")
        else:
            print("Automation failed")
    elif args.status:
        status = scheduler.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print("Use --start to start scheduler, --run-once for single run, or --status for current status")