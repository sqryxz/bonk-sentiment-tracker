import os
import requests
from datetime import datetime

class DiscordWebhook:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.username = "Bonk Sentiment Bot"
        self.avatar_url = "https://raw.githubusercontent.com/sqryxz/bonk-sentiment-tracker/main/assets/bonk_logo.png"

    def format_for_discord(self, summary_text):
        """Format the summary text to fit Discord's message limits and formatting"""
        # Split the summary into sections
        sections = summary_text.split('\n\n')
        
        # Format for Discord markdown
        formatted_sections = []
        for section in sections:
            if section.strip():
                # Convert section titles to bold
                if ':' in section.split('\n')[0]:
                    title, content = section.split('\n', 1)
                    section = f"**{title}**\n{content}"
                formatted_sections.append(section)

        # Discord has a 2000 character limit per message
        messages = []
        current_message = ""
        
        for section in formatted_sections:
            if len(current_message) + len(section) + 2 > 1900:  # Leave some buffer
                messages.append(current_message)
                current_message = section
            else:
                current_message += "\n\n" + section if current_message else section
        
        if current_message:
            messages.append(current_message)
            
        return messages

    def send_report(self, summary_text):
        """Send the daily report to Discord channel"""
        if not self.webhook_url:
            print("Discord webhook URL not configured. Skipping Discord notification.")
            return False

        try:
            # Format the summary for Discord
            messages = self.format_for_discord(summary_text)
            
            # Send each part as a separate message
            for i, message in enumerate(messages):
                payload = {
                    "username": self.username,
                    "avatar_url": self.avatar_url,
                    "content": message if i > 0 else f"🔔 **Daily Bonk Sentiment Report** - {datetime.now().strftime('%Y-%m-%d')}\n\n{message}"
                }
                
                response = requests.post(self.webhook_url, json=payload)
                response.raise_for_status()
                
            print("Daily summary sent to Discord successfully")
            return True
            
        except Exception as e:
            print(f"Error sending to Discord: {str(e)}")
            return False 