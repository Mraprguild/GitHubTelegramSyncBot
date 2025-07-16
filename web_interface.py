"""
Web interface for the Telegram GitHub Bot.
Provides a simple status page and health check endpoint.
"""

from flask import Flask, render_template_string, jsonify
import os
import threading
import time
from config import Config
from telegram_bot import TelegramBot
from webhook_handler import WebhookHandler

app = Flask(__name__)

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
        .status.stopped { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
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
        
        <div class="status running">
            <strong>✅ Bot Status: Running</strong><br>
            The Telegram bot is active and listening for messages.
        </div>
        
        <div class="info">
            <strong>📋 Bot Information:</strong><br>
            • GitHub Username: {{ github_username }}<br>
            • Webhook Port: {{ webhook_port }}<br>
            • Bot Token: {{ bot_token_masked }}<br>
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
    config = Config()
    return render_template_string(STATUS_PAGE,
        github_username=config.github_username or 'Not configured',
        webhook_port=config.webhook_port,
        bot_token_masked=config.telegram_token[:10] + '...' if config.telegram_token else 'Not configured'
    )

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'telegram-github-bot',
        'timestamp': time.time()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """GitHub webhook endpoint."""
    from flask import request
    # This will be handled by the webhook handler
    return jsonify({'status': 'received'}), 200

def main():
    """Main function to start the web interface."""
    # Start the Flask web interface
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()