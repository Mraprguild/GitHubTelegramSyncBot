"""
Configuration module for the Telegram GitHub Bot.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for bot settings."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        # Telegram Bot Configuration
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
        
        # GitHub Configuration
        self.github_token = os.getenv('GITHUB_TOKEN', '')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        # GitHub username for personal repositories
        self.github_username = os.getenv('GITHUB_USERNAME', '')
        
        # Webhook Configuration
        self.webhook_port = int(os.getenv('WEBHOOK_PORT', '5000'))
        self.webhook_host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
        self.webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
        
        # GitHub API Configuration
        self.github_api_base = 'https://api.github.com'
        
        # Bot Configuration
        self.bot_admin_id = os.getenv('BOT_ADMIN_ID', '')
        
    def validate(self):
        """Validate required configuration values."""
        if not self.telegram_token:
            raise ValueError("Telegram bot token is required")
        if not self.github_token:
            raise ValueError("GitHub token is required")
        return True
