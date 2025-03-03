import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class RedditScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'BonkSentimentBot/1.0 (Script)'
        }
        
        # Subreddits to monitor
        self.subreddits = [
            'solana',              # Main Solana subreddit
            'SolanaNews',          # Solana news and updates
            'CryptoCurrency',      # General crypto discussion
            'SatoshiStreetBets',   # Crypto trading and speculation
            'CryptoMarkets',       # Crypto market discussion
            'altcoin',             # Alternative cryptocurrency discussion
            'CryptoMoonShots',     # New crypto projects
            'memecoin',            # Meme coin discussion
            'dogecoin',            # Similar meme coin community
            'SolanaNFT'            # Solana NFT ecosystem
        ]

    def get_subreddit_posts(self, subreddit, limit=100):
        """
        Get posts from a subreddit using Reddit's JSON API
        """
        url = f'https://www.reddit.com/r/{subreddit}/new.json?limit={limit}'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()['data']['children']
        else:
            print(f"Error fetching from r/{subreddit}: {response.status_code}")
            return []

    def get_post_comments(self, post_id, subreddit):
        """
        Get comments for a specific post
        """
        url = f'https://www.reddit.com/r/{subreddit}/comments/{post_id}.json'
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            try:
                return response.json()[1]['data']['children']
            except (IndexError, KeyError):
                return []
        else:
            print(f"Error fetching comments for post {post_id}: {response.status_code}")
            return []

    def search_posts(self, hours_ago=1):
        """
        Search for Bonk-related posts and comments from the past specified hours
        """
        posts = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_ago)
        
        # Search in each subreddit
        for subreddit_name in self.subreddits:
            try:
                subreddit_posts = self.get_subreddit_posts(subreddit_name)
                
                for post_data in subreddit_posts:
                    post = post_data['data']
                    
                    # Check if post is relevant to Bonk
                    title_lower = post['title'].lower()
                    selftext_lower = post.get('selftext', '').lower()
                    
                    if not any(keyword in title_lower or keyword in selftext_lower
                             for keyword in ['bonk', '$bonk', 'bonkcoin']):
                        continue
                    
                    created_time = datetime.fromtimestamp(post['created_utc'])
                    if created_time < cutoff_time:
                        continue
                    
                    posts.append({
                        'id': post['id'],
                        'type': 'post',
                        'text': post.get('selftext', post['title']),
                        'title': post['title'],
                        'created_at': created_time.isoformat(),
                        'author': post.get('author', '[deleted]'),
                        'subreddit': subreddit_name,
                        'score': post['score'],
                        'upvote_ratio': post.get('upvote_ratio', None),
                        'num_comments': post['num_comments'],
                        'url': f"https://reddit.com{post['permalink']}"
                    })
                    
                    # Get comments
                    comments = self.get_post_comments(post['id'], subreddit_name)
                    for comment_data in comments:
                        try:
                            comment = comment_data['data']
                            comment_time = datetime.fromtimestamp(comment['created_utc'])
                            
                            if comment_time >= cutoff_time:
                                posts.append({
                                    'id': comment['id'],
                                    'type': 'comment',
                                    'text': comment.get('body', ''),
                                    'title': '',  # Comments don't have titles
                                    'created_at': comment_time.isoformat(),
                                    'author': comment.get('author', '[deleted]'),
                                    'subreddit': subreddit_name,
                                    'score': comment.get('score', 0),
                                    'upvote_ratio': None,  # Comments don't have upvote ratios
                                    'num_comments': 0,
                                    'url': f"https://reddit.com{post['permalink']}{comment['id']}/"
                                })
                        except Exception as comment_error:
                            print(f"Error processing comment: {str(comment_error)}")
                            continue
                    
                    # Sleep briefly to avoid hitting rate limits
                    time.sleep(0.5)
                
            except Exception as e:
                print(f"Error scraping subreddit {subreddit_name}: {str(e)}")
                continue
        
        return pd.DataFrame(posts)

    def save_posts(self, df, filename=None):
        """
        Save Reddit posts and comments to a CSV file in the data directory
        """
        if filename is None:
            filename = f"bonk_reddit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        
        os.makedirs('data/raw', exist_ok=True)
        filepath = os.path.join('data/raw', filename)
        df.to_csv(filepath, index=False)
        return filepath

    def collect_posts(self, hours_ago=1):
        """
        Main method to collect and save Reddit posts and comments
        """
        try:
            posts_df = self.search_posts(hours_ago)
            if not posts_df.empty:
                filepath = self.save_posts(posts_df)
                print(f"Collected {len(posts_df)} Reddit items and saved to {filepath}")
                return filepath
            else:
                print("No Reddit posts found in the specified time period")
                return None
        except Exception as e:
            print(f"Error collecting Reddit posts: {str(e)}")
            return None

if __name__ == "__main__":
    scraper = RedditScraper()
    scraper.collect_posts() 