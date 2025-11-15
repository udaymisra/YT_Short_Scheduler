#!/usr/bin/env python3
"""
Test script for the YouTube Shorts Crime Stories Automation System
This script tests all major components of the system
"""

import os
import sys
import logging
import json
from datetime import datetime

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from scraper import CrimeNewsScraper
        print("✅ scraper.py - OK")
    except ImportError as e:
        print(f"❌ scraper.py - FAILED: {e}")
        return False
    
    try:
        from content_processor import ContentProcessor
        print("✅ content_processor.py - OK")
    except ImportError as e:
        print(f"❌ content_processor.py - FAILED: {e}")
        return False
    
    try:
        from canva_integration import CanvaVideoCreator
        print("✅ canva_integration.py - OK")
    except ImportError as e:
        print(f"❌ canva_integration.py - FAILED: {e}")
        return False
    
    try:
        from scheduler import AutomationScheduler
        print("✅ scheduler.py - OK")
    except ImportError as e:
        print(f"❌ scheduler.py - FAILED: {e}")
        return False
    
    try:
        from main import run_full_workflow
        print("✅ main.py - OK")
    except ImportError as e:
        print(f"❌ main.py - FAILED: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist or can be created"""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        '/mnt/okcomputer/output/videos',
        '/mnt/okcomputer/output/logs',
        '/mnt/okcomputer/output/temp'
    ]
    
    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            if os.path.exists(dir_path):
                print(f"✅ {dir_path} - OK")
            else:
                print(f"❌ {dir_path} - FAILED: Cannot create directory")
                return False
        except Exception as e:
            print(f"❌ {dir_path} - FAILED: {e}")
            return False
    
    return True

def test_scraper():
    """Test the news scraper with a simple test"""
    print("\n🧪 Testing news scraper...")
    
    try:
        from scraper import CrimeNewsScraper
        scraper = CrimeNewsScraper()
        
        # Test basic functionality without actually scraping
        print("✅ Scraper initialization - OK")
        
        # Test story validation
        test_story = {
            'headline': 'नोएडा में फ्रॉड गैंग का पर्दाफाश',
            'summary': 'पुलिस ने बड़े गिरोह का भंडाफोड़ किया',
            'image_url': 'https://example.com/image.jpg',
            'source': 'test',
            'crime_type': 'fraud'
        }
        
        is_valid = scraper.validate_story(test_story)
        if is_valid:
            print("✅ Story validation - OK")
        else:
            print("❌ Story validation - FAILED")
            return False
        
        # Test crime classification
        crime_type = scraper.classify_crime_type('नोएडा में हत्या का मामला')
        if crime_type == 'murder':
            print("✅ Crime classification - OK")
        else:
            print(f"❌ Crime classification - FAILED: Got {crime_type}")
            return False
        
        scraper.close_driver()
        return True
        
    except Exception as e:
        print(f"❌ Scraper test - FAILED: {e}")
        return False

def test_content_processor():
    """Test the content processor"""
    print("\n🧪 Testing content processor...")
    
    try:
        from content_processor import ContentProcessor
        processor = ContentProcessor()
        
        # Test headline processing
        test_headline = "  नोएडा में   फ्रॉड गैंग का   पर्दाफाश  "
        processed = processor.process_headline(test_headline)
        
        if processed and "नोएडा में फ्रॉड गैंग का पर्दाफाश" in processed:
            print("✅ Headline processing - OK")
        else:
            print(f"❌ Headline processing - FAILED: {processed}")
            return False
        
        # Test summary processing
        test_summary = "यह एक गंभीर अपराध की घटना है।"
        processed_summary = processor.process_summary(test_summary, "")
        
        if processed_summary and "गंभीर अपराध" in processed_summary:
            print("✅ Summary processing - OK")
        else:
            print(f"❌ Summary processing - FAILED: {processed_summary}")
            return False
        
        # Test quality scoring
        test_story = {
            'headline': 'Test headline for quality scoring',
            'summary': 'Test summary content',
            'image_url': 'https://example.com/image.jpg',
            'crime_type': 'fraud'
        }
        
        score = processor.calculate_quality_score(test_story)
        if score > 0:
            print("✅ Quality scoring - OK")
        else:
            print(f"❌ Quality scoring - FAILED: Score {score}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Content processor test - FAILED: {e}")
        return False

def test_video_creator():
    """Test the video creator"""
    print("\n🧪 Testing video creator...")
    
    try:
        from canva_integration import CanvaVideoCreator
        creator = CanvaVideoCreator()
        
        # Test with sample data
        test_story = {
            'id': 1,
            'headline': 'नोएडा में फ्रॉड गैंग का पर्दाफाश',
            'summary': 'पुलिस ने बड़े गिरोह का भंडाफोड़ किया और आठ लोगों को गिरफ्तार किया गया। यह एक संगठित अपराध का मामला है जिसमें कई लोगों को ठगी का शिकार बनाया गया था।',
            'source': 'aajtak',
            'crime_type': 'fraud',
            'image_path': ''
        }
        
        video_path = creator.create_static_video(test_story)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            print(f"✅ Video creation - OK")
            print(f"   📁 File: {video_path}")
            print(f"   📊 Size: {file_size / 1024:.1f} KB")
            
            # Clean up test file
            os.remove(video_path)
            return True
        else:
            print("❌ Video creation - FAILED: No file created")
            return False
        
    except Exception as e:
        print(f"❌ Video creator test - FAILED: {e}")
        return False

def test_configuration():
    """Test configuration settings"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import (
            NEWS_SOURCES, CANVA_CONFIG, SCHEDULE_CONFIG,
            CONTENT_CONFIG, OUTPUT_CONFIG
        )
        
        # Test news sources configuration
        if len(NEWS_SOURCES) > 0:
            print(f"✅ News sources config - OK ({len(NEWS_SOURCES)} sources)")
        else:
            print("❌ News sources config - FAILED: No sources configured")
            return False
        
        # Test schedule configuration
        if SCHEDULE_CONFIG.get('daily_time'):
            print(f"✅ Schedule config - OK ({SCHEDULE_CONFIG['daily_time']} IST)")
        else:
            print("❌ Schedule config - FAILED")
            return False
        
        # Test output configuration
        if OUTPUT_CONFIG.get('base_dir'):
            print(f"✅ Output config - OK ({OUTPUT_CONFIG['base_dir']})")
        else:
            print("❌ Output config - FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test - FAILED: {e}")
        return False

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("SYSTEM TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The system is ready for use.")
        print("\n🚀 Next steps:")
        print("   1. Run: python main.py --test-scraper")
        print("   2. Run: python main.py --run")
        print("   3. Run: python main.py --schedule")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\n🔧 Troubleshooting:")
        print("   • Check Python dependencies are installed")
        print("   • Verify directory permissions")
        print("   • Check system requirements")
    
    print("="*60)

def main():
    """Run all tests"""
    print("🔍 YouTube Shorts Crime Stories Automation System - Test Suite")
    print("="*60)
    
    # Run all tests
    results = {
        'Module Imports': test_imports(),
        'Directory Structure': test_directories(),
        'Configuration': test_configuration(),
        'News Scraper': test_scraper(),
        'Content Processor': test_content_processor(),
        'Video Creator': test_video_creator()
    }
    
    # Generate report
    generate_test_report(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed

if __name__ == "__main__":
    main()