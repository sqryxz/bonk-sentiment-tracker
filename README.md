# Bonk Sentiment Tracker

An AI-powered sentiment analysis tool that tracks and analyzes social media sentiment for the Bonk cryptocurrency.

## Platforms Covered

- **Reddit Communities**:
  - r/solana - Primary Solana ecosystem discussions
  - r/CryptoCurrency - General cryptocurrency discussions
  - r/SatoshiStreetBets - Trading and market discussions
  - r/CryptoMarkets - Market analysis and trends
  - r/memecoin - Meme coin specific discussions

## Features

- Real-time Reddit data scraping for Bonk-related content
- AI-powered sentiment analysis using transformer models
- Comprehensive daily sentiment reports
- Multi-channel reporting (Email, Discord, Web)
- Web interface for viewing analysis results
- Optional tipping system for community support

## Daily Report Analysis

The daily sentiment report includes:

1. **Volume Metrics**
   - Total Bonk-related posts and comments
   - Average engagement scores
   - Peak engagement metrics
   - Active community count

2. **Sentiment Analysis**
   - Raw sentiment distribution (Positive/Neutral/Negative)
   - Engagement-weighted sentiment
   - Day-over-day sentiment trends with directional indicators

3. **Key Discussion Themes**
   - Price discussions (ATH, support/resistance levels)
   - Technical analysis (trends, momentum, volume)
   - Community updates (holder count, governance)
   - Development news (features, roadmap, partnerships)
   - Market activity (exchange listings, trading)

4. **Community Activity**
   - Most active subreddits
   - Top posts by engagement
   - Peak activity hours (UTC)

5. **Top Content**
   - Highest engaging posts with full titles
   - Post content previews
   - Source subreddit and engagement metrics

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure your settings:
   ```bash
   cp .env.example .env
   ```

4. Configure notification channels (optional):
   
   **Email Reports:**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   RECIPIENT_EMAILS=email1@example.com,email2@example.com
   ```
   
   **Discord Reports:**
   ```env
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your_webhook_url
   ```
   
   To set up Discord integration:
   1. Create a Discord server or use an existing one
   2. Go to Server Settings > Integrations > Webhooks
   3. Create a new webhook and copy the webhook URL
   4. Add the URL to your `.env` file

5. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `src/scrapers/` - Reddit data collection and processing
- `src/analysis/` - Sentiment analysis and report generation
- `src/api/` - FastAPI web server
- `src/models/` - Data models and schemas
- `src/integrations/` - External platform integrations (Discord, Email)
- `frontend/` - Web interface
- `data/` - Storage for collected data and analysis results

## Usage

1. The scraper runs automatically every hour to collect new data
2. Sentiment analysis is performed on collected data
3. Daily summaries are generated at midnight UTC
4. Reports are sent to configured channels (Email, Discord)
5. Access the web interface at `http://localhost:8080` to view results

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 