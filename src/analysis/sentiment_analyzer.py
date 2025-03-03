import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from datetime import datetime
import os

class SentimentAnalyzer:
    def __init__(self):
        self.model_name = "finiteautomata/bertweet-base-sentiment-analysis"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Move model to GPU if available
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)

    def analyze_text(self, text):
        """
        Analyze the sentiment of a single text
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
        # Convert predictions to sentiment scores
        scores = predictions[0].cpu().numpy()
        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
        sentiment = sentiment_map[scores.argmax()]
        confidence = float(scores.max())
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'negative': float(scores[0]),
                'neutral': float(scores[1]),
                'positive': float(scores[2])
            }
        }

    def analyze_tweets(self, csv_path):
        """
        Analyze sentiment for all tweets in a CSV file
        """
        df = pd.read_csv(csv_path)
        results = []
        
        for _, row in df.iterrows():
            analysis = self.analyze_text(row['text'])
            results.append({
                'tweet_id': row['id'],
                'text': row['text'],
                'created_at': row['created_at'],
                'sentiment': analysis['sentiment'],
                'confidence': analysis['confidence'],
                'negative_score': analysis['scores']['negative'],
                'neutral_score': analysis['scores']['neutral'],
                'positive_score': analysis['scores']['positive'],
                'metrics': {
                    'retweet_count': row['retweet_count'],
                    'like_count': row['like_count'],
                    'reply_count': row['reply_count']
                }
            })
        
        return pd.DataFrame(results)

    def generate_summary(self, analyzed_df):
        """
        Generate a summary of sentiment analysis results
        """
        total_tweets = len(analyzed_df)
        sentiment_counts = analyzed_df['sentiment'].value_counts()
        
        # Calculate weighted sentiment scores using engagement metrics
        analyzed_df['engagement_score'] = (
            analyzed_df['metrics'].apply(lambda x: 
                x['retweet_count'] * 2 + 
                x['like_count'] + 
                x['reply_count'] * 1.5
            )
        )
        
        weighted_sentiments = analyzed_df.groupby('sentiment')['engagement_score'].sum()
        total_engagement = weighted_sentiments.sum()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_tweets': total_tweets,
            'sentiment_distribution': {
                'positive': int(sentiment_counts.get('positive', 0)),
                'neutral': int(sentiment_counts.get('neutral', 0)),
                'negative': int(sentiment_counts.get('negative', 0))
            },
            'weighted_sentiment': {
                'positive': float(weighted_sentiments.get('positive', 0) / total_engagement if total_engagement > 0 else 0),
                'neutral': float(weighted_sentiments.get('neutral', 0) / total_engagement if total_engagement > 0 else 0),
                'negative': float(weighted_sentiments.get('negative', 0) / total_engagement if total_engagement > 0 else 0)
            },
            'total_engagement': float(total_engagement)
        }
        
        return summary

    def save_analysis(self, df, summary, base_filename=None):
        """
        Save analysis results and summary
        """
        if base_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            base_filename = f"sentiment_analysis_{timestamp}"
        
        os.makedirs('data/analyzed', exist_ok=True)
        
        # Save detailed analysis
        analysis_path = os.path.join('data/analyzed', f"{base_filename}_detailed.csv")
        df.to_csv(analysis_path, index=False)
        
        # Save summary
        summary_path = os.path.join('data/analyzed', f"{base_filename}_summary.csv")
        pd.DataFrame([summary]).to_csv(summary_path, index=False)
        
        return analysis_path, summary_path

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    # Test with the most recent tweet file
    data_dir = 'data/raw'
    if os.path.exists(data_dir):
        files = sorted([f for f in os.listdir(data_dir) if f.endswith('.csv')], reverse=True)
        if files:
            latest_file = os.path.join(data_dir, files[0])
            analyzed_df = analyzer.analyze_tweets(latest_file)
            summary = analyzer.generate_summary(analyzed_df)
            analyzer.save_analysis(analyzed_df, summary) 