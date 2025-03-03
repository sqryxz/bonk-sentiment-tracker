from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import os
import json

app = FastAPI(title="Bonk Sentiment Tracker API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentSummary(BaseModel):
    timestamp: str
    total_tweets: int
    sentiment_distribution: dict
    weighted_sentiment: dict
    total_engagement: float

@app.get("/api/latest-summary")
async def get_latest_summary():
    """Get the most recent sentiment analysis summary"""
    try:
        data_dir = 'data/analyzed'
        if not os.path.exists(data_dir):
            raise HTTPException(status_code=404, detail="No analysis data found")
        
        # Find the most recent summary file
        summary_files = [f for f in os.listdir(data_dir) if f.endswith('_summary.csv')]
        if not summary_files:
            raise HTTPException(status_code=404, detail="No summary files found")
        
        latest_file = sorted(summary_files, reverse=True)[0]
        df = pd.read_csv(os.path.join(data_dir, latest_file))
        
        # Convert the first row to a dictionary
        summary_dict = df.iloc[0].to_dict()
        
        # Parse nested JSON strings if they exist
        for key in ['sentiment_distribution', 'weighted_sentiment']:
            if isinstance(summary_dict[key], str):
                summary_dict[key] = json.loads(summary_dict[key])
        
        return SentimentSummary(**summary_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/historical-summaries/{days}")
async def get_historical_summaries(days: int = 7):
    """Get historical sentiment summaries for the specified number of days"""
    try:
        data_dir = 'data/analyzed'
        if not os.path.exists(data_dir):
            raise HTTPException(status_code=404, detail="No analysis data found")
        
        summary_files = [f for f in os.listdir(data_dir) if f.endswith('_summary.csv')]
        if not summary_files:
            raise HTTPException(status_code=404, detail="No summary files found")
        
        # Sort files by date and take the last 'days' number of files
        sorted_files = sorted(summary_files, reverse=True)[:days]
        
        summaries = []
        for file in sorted_files:
            df = pd.read_csv(os.path.join(data_dir, file))
            summary_dict = df.iloc[0].to_dict()
            
            # Parse nested JSON strings
            for key in ['sentiment_distribution', 'weighted_sentiment']:
                if isinstance(summary_dict[key], str):
                    summary_dict[key] = json.loads(summary_dict[key])
            
            summaries.append(summary_dict)
        
        return summaries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/detailed-analysis/{date}")
async def get_detailed_analysis(date: str):
    """Get detailed sentiment analysis for a specific date"""
    try:
        data_dir = 'data/analyzed'
        if not os.path.exists(data_dir):
            raise HTTPException(status_code=404, detail="No analysis data found")
        
        # Find the detailed analysis file for the specified date
        detailed_file = f"sentiment_analysis_{date}_detailed.csv"
        file_path = os.path.join(data_dir, detailed_file)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"No analysis found for date {date}")
        
        df = pd.read_csv(file_path)
        return df.to_dict(orient='records')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the static files directory for the frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="static") 