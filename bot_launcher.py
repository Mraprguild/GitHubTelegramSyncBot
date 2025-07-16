#!/usr/bin/env python3
"""
Simple launcher for the Telegram GitHub Bot.
Starts the bot with proper error handling and web interface.
"""

import logging
import asyncio
import threading
import time
from flask import Flask, render_template_string, jsonify
from config import Config
from telegram_bot import TelegramBot

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for web interface
app = Flask(__name__)

# Global bot instance
bot_instance = None
bot_status = "Starting..."

# HTML template for the status page
STATUS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram GitHub Bot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .status { padding: 20px; margin: 20px 0; border-radius: 5px; }
        .status.running { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status.error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status.starting { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .info { background-color: #e2f3ff; padding: 15px; margin: 20px 0; border-radius: 5px; border: 1px solid #b8daff; }
        .commands { background-color: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .command { margin: 10px 0; padding: 8px; background: white; border-radius: 3px; font-family: monospace; }
        code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
        .footer { text-align: center; margin-top: 40px; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram GitHub Bot</h1>
        
        <div class="status {{ status_class }}">
            <strong>{{ status_icon }} Bot Status: {{ bot_status }}</strong><br>
            {{ status_message }}
        </div>
        
        <div class="info">
            <strong>📋 Bot Information:</strong><br>
            • GitHub Username: {{ github_username }}<br>
            • Bot Token: {{ bot_token_masked }}<br>
            • Configuration: {{ config_status }}<br>
        </div>
        
        <div class="commands">
            <h3>📝 Available Commands:</h3>
            <div class="command"><code>/start</code> - Welcome message and bot introduction</div>
            <div class="command"><code>/help</code> - Show all available commands</div>
            <div class="command"><code>/profile [username]</code> - Show GitHub profile information</div>
            <div class="command"><code>/repos [username]</code> - List repositories</div>
            <div class="command"><code>/repo owner/repo</code> - Get repository details</div>
            <div class="command"><code>/commits owner/repo</code> - Show recent commits</div>
            <div class="command"><code>/issues owner/repo</code> - Show repository issues</div>
            <div class="command"><code>/search query</code> - Search repositories</div>
        </div>
        
        <div class="info">
            <strong>🚀 Getting Started:</strong><br>
            1. Open Telegram and search for your bot<br>
            2. Start a conversation with your bot<br>
            3. Send <code>/start</code> to begin<br>
            4. Use <code>/help</code> to see all commands<br>
        </div>
        
        <div class="footer">
            <p>Telegram GitHub Bot - Connecting your GitHub repositories to Telegram</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def status():
    """Show bot status page."""
    try:
        config = Config()
        config.validate()
        
        # Determine status class and message
        if bot_status == "Running":
            status_class = "running"
            status_icon = "✅"
            status_message = "The Telegram bot is active and listening for messages."
        elif "Error" in bot_status:
            status_class = "error"
            status_icon = "❌"
            status_message = "There was an error starting the bot. Check the logs for details."
        else:
            status_class = "starting"
            status_icon = "🟡"
            status_message = "The bot is starting up. Please wait a moment."
        
        return render_template_string(STATUS_PAGE,
            bot_status=bot_status,
            status_class=status_class,
            status_icon=status_icon,
            status_message=status_message,
            github_username=config.github_username or 'Not configured',
            bot_token_masked=config.telegram_token[:10] + '...' if config.telegram_token else 'Not configured',
            config_status='✅ Valid' if config.telegram_token and config.github_token else '❌ Invalid'
        )
    except Exception as e:
        logger.error(f"Error in status page: {e}")
        return f"Error loading status: {e}"

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'bot_status': bot_status,
        'service': 'telegram-github-bot',
        'timestamp': time.time()
    })

def run_bot():
    """Run the Telegram bot in a separate thread."""
    global bot_status, bot_instance
    
    try:
        bot_status = "Initializing..."
        config = Config()
        config.validate()
        
        bot_status = "Starting bot..."
        bot_instance = TelegramBot(config)
        
        bot_status = "Running"
        logger.info("Bot started successfully")
        
        # Start the bot
        bot_instance.start()
        
    except Exception as e:
        logger.error(f"Error in bot thread: {e}")
        bot_status = f"Error: {str(e)}"

def main():
    """Main function to start the bot and web interface."""
    global bot_status
    
    try:
        # Start the bot in a background thread
        bot_thread = threading.Thread(target=run_bot, daemon=True)
        bot_thread.start()
        
        # Give the bot a moment to start
        time.sleep(2)
        
        # Start the Flask web interface
        logger.info("Starting web interface on port 5000")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        bot_status = f"Fatal Error: {str(e)}"
        raise

if __name__ == '__main__':
    main()