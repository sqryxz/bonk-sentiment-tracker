import os
import tweepy
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class TwitterScraper:
    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Twitter credentials not found in .env file")
        
        self.client = tweepy.Client(
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret
        )

    def search_tweets(self, hours_ago=1):
        """
        Search for Bonk-related tweets from the past specified hours
        """
        query = "(#bonk OR $bonk OR bonkcoin) -is:retweet lang:en"
        start_time = datetime.utcnow() - timedelta(hours=hours_ago)
        
        tweets = []
        for tweet in tweepy.Paginator(
            self.client.search_recent_tweets,
            query=query,
            start_time=start_time,
            tweet_fields=['created_at', 'public_metrics', 'author_id'],
            max_results=100
        ).flatten(limit=500):
            tweets.append({
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'author_id': tweet.author_id,
                'retweet_count': tweet.public_metrics['retweet_count'],
                'like_count': tweet.public_metrics['like_count'],
                'reply_count': tweet.public_metrics['reply_count']
            })
        
        return pd.DataFrame(tweets)

    def save_tweets(self, df, filename=None):
        """
        Save tweets to a CSV file in the data directory
        """
        if filename is None:
            filename = f"bonk_tweets_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        os.makedirs('data/raw', exist_ok=True)
        filepath = os.path.join('data/raw', filename)
        df.to_csv(filepath, index=False)
        return filepath

    def collect_tweets(self, hours_ago=1):
        """
        Main method to collect and save tweets
        """
        try:
            tweets_df = self.search_tweets(hours_ago)
            if not tweets_df.empty:
                filepath = self.save_tweets(tweets_df)
                print(f"Collected {len(tweets_df)} tweets and saved to {filepath}")
                return filepath
            else:
                print("No tweets found in the specified time period")
                return None
        except Exception as e:
            print(f"Error collecting tweets: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = TwitterScraper()
    scraper.collect_tweets() 