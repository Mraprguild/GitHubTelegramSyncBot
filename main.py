#!/usr/bin/env python3
"""
Main entry point for the Telegram GitHub Bot.
Starts both the Telegram bot and the Flask webhook server.
"""

import logging
import threading
import time
from config import Config
from telegram_bot import TelegramBot
from webhook_handler import WebhookHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot and webhook server."""
    try:
        # Initialize configuration
        config = Config()
        config.validate()
        
        # Initialize Telegram bot
        telegram_bot = TelegramBot(config)
        
        # Initialize webhook handler
        webhook_handler = WebhookHandler(config, telegram_bot)
        
        # Start Flask webhook server in a separate thread
        webhook_thread = threading.Thread(
            target=webhook_handler.run_server,
            daemon=True
        )
        webhook_thread.start()
        
        # Give the webhook server time to start
        time.sleep(2)
        
        logger.info("Starting Telegram bot...")
        
        # Start the Telegram bot
        telegram_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
