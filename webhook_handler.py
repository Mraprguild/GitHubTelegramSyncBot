"""
Webhook handler for GitHub events.
Processes GitHub webhooks and sends notifications to Telegram.
"""

import logging
import json
import hmac
import hashlib
from flask import Flask, request, jsonify
from typing import Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class WebhookHandler:
    """Handles GitHub webhook events and sends Telegram notifications."""
    
    def __init__(self, config: Config, telegram_bot):
        """
        Initialize webhook handler.
        
        Args:
            config: Configuration object
            telegram_bot: Telegram bot instance
        """
        self.config = config
        self.telegram_bot = telegram_bot
        self.app = Flask(__name__)
        self.app.logger.setLevel(logging.INFO)
        
        # Register webhook routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes for webhook handling."""
        self.app.route('/webhook', methods=['POST'])(self.handle_webhook)
        self.app.route('/health', methods=['GET'])(self.health_check)
    
    def _verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify GitHub webhook signature.
        
        Args:
            payload: Raw request payload
            signature: GitHub signature from headers
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not self.config.webhook_secret:
            logger.warning("No webhook secret configured, skipping signature verification")
            return True
        
        if not signature:
            logger.error("No signature provided in webhook request")
            return False
        
        expected_signature = hmac.new(
            self.config.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        signature_header = signature.replace('sha256=', '')
        
        return hmac.compare_digest(expected_signature, signature_header)
    
    def handle_webhook(self):
        """Handle incoming GitHub webhook requests."""
        try:
            # Get request data
            payload = request.get_data()
            signature = request.headers.get('X-Hub-Signature-256', '')
            event_type = request.headers.get('X-GitHub-Event', '')
            
            # Verify signature
            if not self._verify_signature(payload, signature):
                logger.error("Invalid webhook signature")
                return jsonify({'error': 'Invalid signature'}), 403
            
            # Parse JSON payload
            try:
                data = json.loads(payload.decode('utf-8'))
            except json.JSONDecodeError:
                logger.error("Invalid JSON payload")
                return jsonify({'error': 'Invalid JSON'}), 400
            
            # Process different event types
            message = self._process_event(event_type, data)
            
            if message and self.config.bot_admin_id:
                # Send notification to admin (you can modify this to send to specific chats)
                self._send_notification(message)
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    def _process_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Process different GitHub event types.
        
        Args:
            event_type: Type of GitHub event
            data: Event data
            
        Returns:
            Formatted notification message
        """
        try:
            if event_type == 'push':
                return self._process_push_event(data)
            elif event_type == 'pull_request':
                return self._process_pull_request_event(data)
            elif event_type == 'issues':
                return self._process_issues_event(data)
            elif event_type == 'star':
                return self._process_star_event(data)
            elif event_type == 'fork':
                return self._process_fork_event(data)
            elif event_type == 'release':
                return self._process_release_event(data)
            else:
                logger.info(f"Unhandled event type: {event_type}")
                return ""
        except Exception as e:
            logger.error(f"Error processing {event_type} event: {e}")
            return ""
    
    def _process_push_event(self, data: Dict[str, Any]) -> str:
        """Process push event."""
        try:
            repository = data.get('repository', {})
            pusher = data.get('pusher', {})
            commits = data.get('commits', [])
            ref = data.get('ref', '')
            
            repo_name = repository.get('full_name', 'Unknown')
            pusher_name = pusher.get('name', 'Unknown')
            branch = ref.replace('refs/heads/', '') if ref.startswith('refs/heads/') else ref
            
            if not commits:
                return ""
            
            commit_count = len(commits)
            commit_word = "commit" if commit_count == 1 else "commits"
            
            message = f"📝 **New {commit_word} to {repo_name}**\n\n"
            message += f"🌿 Branch: `{branch}`\n"
            message += f"👤 Pusher: {pusher_name}\n"
            message += f"📊 {commit_count} {commit_word}\n\n"
            
            # Show details of recent commits (max 3)
            for commit in commits[:3]:
                commit_message = commit.get('message', 'No message')
                author_name = commit.get('author', {}).get('name', 'Unknown')
                commit_id = commit.get('id', '')[:7]
                
                message += f"🔸 **{commit_message}**\n"
                message += f"👤 {author_name} • `{commit_id}`\n\n"
            
            if len(commits) > 3:
                message += f"... and {len(commits) - 3} more commits\n\n"
            
            repo_url = repository.get('html_url', '')
            message += f"🔗 [View Repository]({repo_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing push event: {e}")
            return ""
    
    def _process_pull_request_event(self, data: Dict[str, Any]) -> str:
        """Process pull request event."""
        try:
            action = data.get('action', '')
            pull_request = data.get('pull_request', {})
            repository = data.get('repository', {})
            
            if action not in ['opened', 'closed', 'merged']:
                return ""
            
            repo_name = repository.get('full_name', 'Unknown')
            pr_title = pull_request.get('title', 'No title')
            pr_number = pull_request.get('number', 0)
            pr_user = pull_request.get('user', {}).get('login', 'Unknown')
            pr_url = pull_request.get('html_url', '')
            
            action_emoji = {
                'opened': '🟢',
                'closed': '🔴',
                'merged': '🟣'
            }.get(action, '📋')
            
            message = f"{action_emoji} **Pull Request {action.title()}**\n\n"
            message += f"📦 Repository: {repo_name}\n"
            message += f"🔧 PR #{pr_number}: {pr_title}\n"
            message += f"👤 Author: {pr_user}\n\n"
            message += f"🔗 [View Pull Request]({pr_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing pull request event: {e}")
            return ""
    
    def _process_issues_event(self, data: Dict[str, Any]) -> str:
        """Process issues event."""
        try:
            action = data.get('action', '')
            issue = data.get('issue', {})
            repository = data.get('repository', {})
            
            if action not in ['opened', 'closed', 'reopened']:
                return ""
            
            repo_name = repository.get('full_name', 'Unknown')
            issue_title = issue.get('title', 'No title')
            issue_number = issue.get('number', 0)
            issue_user = issue.get('user', {}).get('login', 'Unknown')
            issue_url = issue.get('html_url', '')
            
            action_emoji = {
                'opened': '🟢',
                'closed': '🔴',
                'reopened': '🟡'
            }.get(action, '🐛')
            
            message = f"{action_emoji} **Issue {action.title()}**\n\n"
            message += f"📦 Repository: {repo_name}\n"
            message += f"🐛 Issue #{issue_number}: {issue_title}\n"
            message += f"👤 Author: {issue_user}\n\n"
            message += f"🔗 [View Issue]({issue_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing issues event: {e}")
            return ""
    
    def _process_star_event(self, data: Dict[str, Any]) -> str:
        """Process star event."""
        try:
            action = data.get('action', '')
            repository = data.get('repository', {})
            sender = data.get('sender', {})
            
            if action != 'created':
                return ""
            
            repo_name = repository.get('full_name', 'Unknown')
            star_count = repository.get('stargazers_count', 0)
            user_name = sender.get('login', 'Unknown')
            repo_url = repository.get('html_url', '')
            
            message = f"⭐ **New Star!**\n\n"
            message += f"📦 Repository: {repo_name}\n"
            message += f"👤 Starred by: {user_name}\n"
            message += f"📊 Total stars: {star_count}\n\n"
            message += f"🔗 [View Repository]({repo_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing star event: {e}")
            return ""
    
    def _process_fork_event(self, data: Dict[str, Any]) -> str:
        """Process fork event."""
        try:
            repository = data.get('repository', {})
            forkee = data.get('forkee', {})
            sender = data.get('sender', {})
            
            repo_name = repository.get('full_name', 'Unknown')
            fork_count = repository.get('forks_count', 0)
            user_name = sender.get('login', 'Unknown')
            fork_url = forkee.get('html_url', '')
            
            message = f"🍴 **New Fork!**\n\n"
            message += f"📦 Repository: {repo_name}\n"
            message += f"👤 Forked by: {user_name}\n"
            message += f"📊 Total forks: {fork_count}\n\n"
            message += f"🔗 [View Fork]({fork_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing fork event: {e}")
            return ""
    
    def _process_release_event(self, data: Dict[str, Any]) -> str:
        """Process release event."""
        try:
            action = data.get('action', '')
            release = data.get('release', {})
            repository = data.get('repository', {})
            
            if action != 'published':
                return ""
            
            repo_name = repository.get('full_name', 'Unknown')
            release_name = release.get('name', release.get('tag_name', 'Unknown'))
            release_tag = release.get('tag_name', 'Unknown')
            release_url = release.get('html_url', '')
            author_name = release.get('author', {}).get('login', 'Unknown')
            
            message = f"🚀 **New Release!**\n\n"
            message += f"📦 Repository: {repo_name}\n"
            message += f"🏷️ Release: {release_name} ({release_tag})\n"
            message += f"👤 Author: {author_name}\n\n"
            message += f"🔗 [View Release]({release_url})"
            
            return message
            
        except Exception as e:
            logger.error(f"Error processing release event: {e}")
            return ""
    
    def _send_notification(self, message: str):
        """
        Send notification message to Telegram.
        
        Args:
            message: Formatted notification message
        """
        try:
            # This is a simplified version - in practice, you'd want to:
            # 1. Store chat IDs in a database
            # 2. Allow users to subscribe/unsubscribe from notifications
            # 3. Handle different notification preferences
            
            # For now, just log the message
            logger.info(f"Webhook notification: {message}")
            
            # You can implement actual Telegram message sending here
            # using the telegram bot instance
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def health_check(self):
        """Health check endpoint for webhook server."""
        return jsonify({'status': 'healthy', 'service': 'github-webhook-handler'}), 200
    
    def run_server(self):
        """Run the Flask webhook server."""
        try:
            logger.info(f"Starting webhook server on {self.config.webhook_host}:{self.config.webhook_port}")
            self.app.run(
                host=self.config.webhook_host,
                port=self.config.webhook_port,
                debug=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Error running webhook server: {e}")
            raise
