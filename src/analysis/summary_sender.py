import os
import pandas as pd
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class SummarySender:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.recipient_emails = os.getenv('RECIPIENT_EMAILS', '').split(',')

    def get_top_posts(self, df, n=3):
        """Get top n posts by engagement"""
        if 'engagement' not in df.columns:
            df['engagement'] = df['total_engagement']
        return df.nlargest(n, 'engagement')

    def summarize_key_topics(self, df):
        """Extract key topics and themes from Bonk-related posts"""
        # Common themes to look for
        themes = {
            'price': ['price', 'ATH', 'support', 'resistance', '$'],
            'technical': ['trend', 'momentum', 'volume', 'analysis'],
            'community': ['holder', 'community', 'governance', 'milestone'],
            'development': ['feature', 'roadmap', 'update', 'partnership'],
            'market': ['exchange', 'listing', 'trading', 'market']
        }
        
        theme_counts = {k: 0 for k in themes}
        total_posts = len(df)
        
        for _, row in df.iterrows():
            content = str(row['content']).lower()
            for theme, keywords in themes.items():
                if any(keyword in content for keyword in keywords):
                    theme_counts[theme] += 1
        
        # Convert to percentages and sort by frequency
        theme_percentages = {k: (v / total_posts * 100) for k, v in theme_counts.items()}
        return dict(sorted(theme_percentages.items(), key=lambda x: x[1], reverse=True))

    def extract_key_metrics(self, content):
        """Extract key metrics and numbers from post content"""
        metrics = []
        if 'volume' in content.lower():
            metrics.append('Trading volume mentioned')
        if '%' in content:
            metrics.append('Percentage changes discussed')
        if '$' in content:
            metrics.append('Price points referenced')
        return metrics

    def is_bonk_related(self, title):
        """Check if a post is Bonk-related based on its title"""
        return 'BONK' in title.upper() or 'is_bonk_related' in title

    def filter_bonk_posts(self, df):
        """Filter dataframe for Bonk-related posts"""
        if 'is_bonk_related' in df.columns:
            return df[df['is_bonk_related']]
        return df[df['title'].str.contains('BONK', case=False, na=False)]

    def get_sentiment_trend(self, df):
        """Calculate sentiment trend compared to previous day"""
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Handle both string and dict sentiment distributions
        def process_sentiment(sent):
            if isinstance(sent, str):
                return json.loads(sent)
            return sent
        
        today_data = df[df['date'] == today]
        yesterday_data = df[df['date'] == yesterday]
        
        if len(today_data) == 0 or len(yesterday_data) == 0:
            return None
            
        today_sentiment = today_data['sentiment_distribution'].apply(process_sentiment).mean()
        yesterday_sentiment = yesterday_data['sentiment_distribution'].apply(process_sentiment).mean()
        
        if not isinstance(today_sentiment, dict):
            return None
            
        trend = {k: today_sentiment.get(k, 0) - yesterday_sentiment.get(k, 0) for k in today_sentiment}
        return trend

    def generate_daily_summary(self):
        """Generate a summary of the last 24 hours of analysis"""
        try:
            # Get all summary files from the last 24 hours
            data_dir = 'data/analyzed'
            cutoff_time = datetime.now() - timedelta(days=1)
            summary_files = []
            
            for file in os.listdir(data_dir):
                if file.endswith('_summary.csv'):
                    file_time = datetime.strptime(file.split('_')[2], '%Y%m%d')
                    if file_time >= cutoff_time:
                        summary_files.append(os.path.join(data_dir, file))
            
            if not summary_files:
                return "No data available for the last 24 hours"
            
            # Combine all summaries
            all_summaries = []
            for file in summary_files:
                df = pd.read_csv(file)
                for col in ['sentiment_distribution', 'weighted_sentiment']:
                    if isinstance(df[col].iloc[0], str):
                        df[col] = df[col].apply(json.loads)
                all_summaries.append(df)
            
            combined_df = pd.concat(all_summaries)
            
            # Filter for Bonk-related posts
            bonk_df = self.filter_bonk_posts(combined_df)
            
            if len(bonk_df) == 0:
                return "No Bonk-related posts found in the last 24 hours"
            
            # Calculate aggregate metrics
            total_posts = len(bonk_df)
            avg_engagement = bonk_df['total_engagement'].mean()
            max_engagement = bonk_df['total_engagement'].max()
            
            # Calculate average sentiment distributions
            sentiment_dist = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            weighted_sent = {
                'positive': 0,
                'neutral': 0,
                'negative': 0
            }
            
            for _, row in bonk_df.iterrows():
                for sentiment in ['positive', 'neutral', 'negative']:
                    sentiment_dist[sentiment] += row['sentiment_distribution'][sentiment]
                    weighted_sent[sentiment] += row['weighted_sentiment'][sentiment]
            
            # Average the sentiments
            n_rows = len(bonk_df)
            for k in sentiment_dist:
                sentiment_dist[k] /= n_rows
                weighted_sent[k] /= n_rows
            
            # Get sentiment trend
            sentiment_trend = self.get_sentiment_trend(bonk_df)
            trend_indicators = {
                'positive': '↑' if sentiment_trend and sentiment_trend['positive'] > 0 else '↓' if sentiment_trend and sentiment_trend['positive'] < 0 else '→',
                'neutral': '↑' if sentiment_trend and sentiment_trend['neutral'] > 0 else '↓' if sentiment_trend and sentiment_trend['neutral'] < 0 else '→',
                'negative': '↑' if sentiment_trend and sentiment_trend['negative'] > 0 else '↓' if sentiment_trend and sentiment_trend['negative'] < 0 else '→'
            }
            
            # Get top posts
            top_posts = self.get_top_posts(bonk_df)
            
            # Analyze key topics and themes
            key_themes = self.summarize_key_topics(bonk_df)
            
            # Format the summary
            summary = f"""
Daily Bonk Sentiment Summary
{datetime.now().strftime('%Y-%m-%d')}

VOLUME METRICS:
Bonk-Related Posts/Comments: {total_posts:,}
Average Engagement Score: {avg_engagement:.2f}
Peak Engagement Score: {max_engagement:,}
Active Communities: {len(bonk_df['subreddit'].unique())}

SENTIMENT ANALYSIS:
Raw Sentiment Distribution (with 24h trend):
- Positive: {sentiment_dist['positive']:.1%} {trend_indicators['positive']}
- Neutral: {sentiment_dist['neutral']:.1%} {trend_indicators['neutral']}
- Negative: {sentiment_dist['negative']:.1%} {trend_indicators['negative']}

Engagement-Weighted Sentiment:
- Positive: {weighted_sent['positive']:.1%}
- Neutral: {weighted_sent['neutral']:.1%}
- Negative: {weighted_sent['negative']:.1%}

KEY DISCUSSION THEMES:
{chr(10).join(f"- {theme.title()}: {percentage:.1f}% of discussions" for theme, percentage in key_themes.items())}

COMMUNITY ACTIVITY:
Most Active Subreddits (Bonk posts):
{bonk_df.groupby('subreddit')['total_tweets'].sum().sort_values(ascending=False).head(5).to_string()}

TOP BONK POSTS BY ENGAGEMENT:
{top_posts[['subreddit', 'title', 'content']].to_string(index=False, max_colwidth=70)}

HOURLY ACTIVITY:
Peak Hours (UTC): {bonk_df.groupby(pd.to_datetime(bonk_df['timestamp']).dt.hour)['total_tweets'].sum().nlargest(3).index.tolist()}

View detailed analysis at: http://localhost:8080
"""
            return summary
            
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def send_email_summary(self):
        """Send the daily summary via email"""
        if not all([self.smtp_username, self.smtp_password, self.recipient_emails]):
            print("Email credentials not configured. Saving summary to file instead.")
            return self.save_summary_to_file()
        
        try:
            summary_text = self.generate_daily_summary()
            
            msg = MIMEMultipart()
            msg['Subject'] = f'Bonk Sentiment Daily Summary - {datetime.now().strftime("%Y-%m-%d")}'
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(self.recipient_emails)
            
            msg.attach(MIMEText(summary_text, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print("Daily summary email sent successfully")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def save_summary_to_file(self):
        """Save the daily summary to a file if email sending fails"""
        try:
            summary_text = self.generate_daily_summary()
            
            os.makedirs('data/summaries', exist_ok=True)
            filename = f'daily_summary_{datetime.now().strftime("%Y%m%d")}.txt'
            filepath = os.path.join('data/summaries', filename)
            
            with open(filepath, 'w') as f:
                f.write(summary_text)
            
            print(f"Daily summary saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving summary: {str(e)}")
            return False 