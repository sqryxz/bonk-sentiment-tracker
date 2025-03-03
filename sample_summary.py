from src.analysis.summary_sender import SummarySender
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import random

def generate_bonk_title():
    templates = [
        "BONK just hit {price}!",
        "Why BONK is {action} today",
        "BONK vs {other_coin}: The meme coin battle",
        "Breaking: BONK {news}",
        "{exchange} lists BONK!",
        "BONK community milestone: {milestone}"
    ]
    
    actions = ["pumping", "trending", "gaining traction", "making moves"]
    prices = ["$0.00002", "$0.00003", "new ATH", "support level"]
    other_coins = ["DOGE", "SHIB", "PEPE"]
    news = ["partners with major platform", "reaches 1M holders", "trending on Twitter"]
    exchanges = ["Binance", "KuCoin", "OKX", "Bybit"]
    milestones = ["100K holders", "1B market cap", "$5M trading volume"]
    
    template = random.choice(templates)
    return template.format(
        action=random.choice(actions),
        price=random.choice(prices),
        other_coin=random.choice(other_coins),
        news=random.choice(news),
        exchange=random.choice(exchanges),
        milestone=random.choice(milestones)
    )

def generate_non_bonk_title(subreddit):
    templates = [
        "Daily Discussion - {date}",
        "What's your take on {coin}?",
        "Market Analysis: {trend}",
        "Breaking: {news}",
        "Technical Analysis: {coin} looks {direction}"
    ]
    
    coins = ["SOL", "ETH", "BTC", "ADA"]
    trends = ["Bull run incoming?", "Bear market bottom?", "Sideways movement"]
    news = ["New regulation proposed", "Major partnership announced", "Market volatility increases"]
    directions = ["bullish", "bearish", "ready for breakout"]
    
    template = random.choice(templates)
    return template.format(
        date=datetime.now().strftime("%B %d"),
        coin=random.choice(coins),
        trend=random.choice(trends),
        news=random.choice(news),
        direction=random.choice(directions)
    )

def generate_bonk_content():
    templates = [
        "Just analyzed $BONK's performance today. {analysis}. {prediction}. {sentiment}",
        "Breaking news for BONK holders! {news}. {impact}. {action}",
        "Comparing BONK to other meme coins: {comparison}. {metrics}. {conclusion}",
        "Technical analysis of BONK: {ta_points}. {support_resistance}. {outlook}",
        "BONK community update: {update}. {growth}. {next_steps}"
    ]
    
    analysis = [
        "Volume is up 150% from yesterday",
        "Social mentions have doubled",
        "Price action shows strong momentum",
        "Whale wallets are accumulating"
    ]
    
    predictions = [
        "Looking bullish for the next week",
        "Expecting increased volatility",
        "Support level seems strong",
        "Resistance might be tested soon"
    ]
    
    sentiments = [
        "Community sentiment is overwhelmingly positive",
        "Traders are cautiously optimistic",
        "Social metrics indicate growing interest",
        "Market makers showing increased activity"
    ]
    
    news = [
        "Major exchange listing confirmed",
        "New partnership announced",
        "Development roadmap updated",
        "Community governance proposal passed"
    ]
    
    impacts = [
        "This could drive significant volume",
        "Expected to boost market visibility",
        "Should strengthen market position",
        "May attract institutional interest"
    ]
    
    actions = [
        "Worth keeping an eye on the daily charts",
        "Consider reviewing your position",
        "Stay tuned for more updates",
        "Join the community discussion"
    ]
    
    template = random.choice(templates)
    return template.format(
        analysis=random.choice(analysis),
        prediction=random.choice(predictions),
        sentiment=random.choice(sentiments),
        news=random.choice(news),
        impact=random.choice(impacts),
        action=random.choice(actions),
        comparison="BONK shows stronger community engagement",
        metrics="Trading volume exceeds similar tokens",
        conclusion="Fundamentals remain strong",
        ta_points="Moving averages show upward trend",
        support_resistance="Support at $0.00002, resistance at $0.00003",
        outlook="Short-term momentum looks positive",
        update="New features being rolled out",
        growth="Holder count up 25%",
        next_steps="Community events planned for next week"
    )

def generate_non_bonk_content(subreddit):
    templates = [
        "Market analysis for {coin}: {analysis}. {outlook}. {recommendation}",
        "Daily {coin} thread: {price_action}. {volume}. {sentiment}",
        "Breaking: {news}. {impact}. {market_reaction}"
    ]
    
    coins = ["SOL", "ETH", "BTC", "ADA"]
    
    return random.choice(templates).format(
        coin=random.choice(coins),
        analysis="Technical indicators showing mixed signals",
        outlook="Market sentiment remains neutral",
        recommendation="Watch key support levels",
        price_action="Sideways trading continues",
        volume="Volume below weekly average",
        sentiment="Mixed reactions from traders",
        news="New protocol upgrade announced",
        impact="Minor price impact expected",
        market_reaction="Trading within expected range"
    )

def generate_sample_data(timestamp, subreddit):
    # 30% chance of Bonk-related content
    is_bonk = random.random() < 0.3
    
    title = generate_bonk_title() if is_bonk else generate_non_bonk_title(subreddit)
    content = generate_bonk_content() if is_bonk else generate_non_bonk_content(subreddit)
    engagement = random.randint(1000, 10000) if is_bonk else random.randint(100, 3000)
    
    # Bonk posts tend to have more positive sentiment
    if is_bonk:
        positive = round(random.uniform(0.4, 0.8), 2)
        negative = round(random.uniform(0.1, 0.3), 2)
        neutral = round(1 - positive - negative, 2)
    else:
        positive = round(random.uniform(0.2, 0.5), 2)
        negative = round(random.uniform(0.2, 0.4), 2)
        neutral = round(1 - positive - negative, 2)
    
    return {
        'timestamp': timestamp.isoformat(),
        'total_tweets': random.randint(150, 300),
        'total_engagement': engagement,
        'sentiment_distribution': json.dumps({
            'positive': positive,
            'neutral': neutral,
            'negative': negative
        }),
        'weighted_sentiment': json.dumps({
            'positive': round(positive * 1.2, 2),
            'neutral': round(neutral * 0.8, 2),
            'negative': round(negative * 0.9, 2)
        }),
        'subreddit': subreddit,
        'title': title,
        'content': content,
        'url': f'https://reddit.com/r/{subreddit}/sample',
        'engagement': engagement,
        'is_bonk_related': is_bonk
    }

# Create sample data for today and yesterday
subreddits = ['solana', 'CryptoCurrency', 'SatoshiStreetBets', 'CryptoMarkets', 'memecoin']
now = datetime.now()
yesterday = now - timedelta(days=1)

sample_entries = []

# Generate data for yesterday
for hour in range(24):
    timestamp = yesterday.replace(hour=hour)
    for subreddit in subreddits:
        for _ in range(random.randint(2, 5)):  # Multiple entries per hour
            sample_entries.append(generate_sample_data(timestamp, subreddit))

# Generate data for today
for hour in range(now.hour + 1):
    timestamp = now.replace(hour=hour)
    for subreddit in subreddits:
        for _ in range(random.randint(2, 5)):  # Multiple entries per hour
            sample_entries.append(generate_sample_data(timestamp, subreddit))

# Create the data directory and save sample data
os.makedirs('data/analyzed', exist_ok=True)

# Save yesterday's data
yesterday_df = pd.DataFrame([entry for entry in sample_entries if datetime.fromisoformat(entry['timestamp']).date() == yesterday.date()])
yesterday_df.to_csv(f'data/analyzed/sentiment_analysis_{yesterday.strftime("%Y%m%d")}_summary.csv', index=False)

# Save today's data
today_df = pd.DataFrame([entry for entry in sample_entries if datetime.fromisoformat(entry['timestamp']).date() == now.date()])
today_df.to_csv(f'data/analyzed/sentiment_analysis_{now.strftime("%Y%m%d")}_summary.csv', index=False)

# Generate and print sample summary
sender = SummarySender()
print(sender.generate_daily_summary()) 