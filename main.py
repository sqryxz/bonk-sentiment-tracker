import os
import schedule
import time
import uvicorn
import multiprocessing
from datetime import datetime
from src.scrapers.reddit_scraper import RedditScraper
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.analysis.summary_sender import SummarySender

def run_scraper_and_analyzer():
    """Run the scraping and analysis process"""
    print(f"Starting data collection and analysis at {datetime.now()}")
    
    try:
        # Collect Reddit posts and comments
        scraper = RedditScraper()
        posts_file = scraper.collect_posts(hours_ago=1)
        
        if posts_file:
            # Analyze posts
            analyzer = SentimentAnalyzer()
            analyzed_df = analyzer.analyze_tweets(posts_file)  # We'll keep the same method name for compatibility
            summary = analyzer.generate_summary(analyzed_df)
            
            # Save results
            analyzer.save_analysis(analyzed_df, summary)
            print(f"Successfully completed analysis at {datetime.now()}")
        else:
            print("No Reddit posts collected in this run")
            
    except Exception as e:
        print(f"Error in scraper/analyzer process: {str(e)}")

def send_daily_summary():
    """Generate and send daily summary"""
    print(f"Generating daily summary at {datetime.now()}")
    try:
        sender = SummarySender()
        sender.send_email_summary()
    except Exception as e:
        print(f"Error sending daily summary: {str(e)}")

def run_api_server():
    """Run the FastAPI server"""
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8080, reload=True)

def schedule_jobs():
    """Schedule periodic jobs"""
    # Run scraper and analyzer every hour
    schedule.every(1).hours.do(run_scraper_and_analyzer)
    
    # Send daily summary at midnight UTC
    schedule.every().day.at("00:00").do(send_daily_summary)
    
    # Run initial collection
    run_scraper_and_analyzer()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/analyzed', exist_ok=True)
    os.makedirs('data/summaries', exist_ok=True)
    os.makedirs('frontend', exist_ok=True)
    
    # Start the API server in a separate process
    api_process = multiprocessing.Process(target=run_api_server)
    api_process.start()
    
    try:
        # Run the scheduler in the main process
        schedule_jobs()
    except KeyboardInterrupt:
        print("Shutting down...")
        api_process.terminate()
        api_process.join() 