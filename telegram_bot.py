"""
Telegram bot implementation for GitHub integration.
Handles all Telegram bot commands and interactions.
"""

import logging
import asyncio
from telegram._update import Update
from telegram._inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram._inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram._bot import Bot
from telegram.constants import ParseMode
from github_client import GitHubClient
from config import Config
from utils import escape_markdown

logger = logging.getLogger(__name__)

class TelegramBot:
    """Telegram bot for GitHub integration."""
    
    def __init__(self, config: Config):
        """
        Initialize Telegram bot.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.github_client = GitHubClient(config.github_token, config.github_username)
        self.bot = Bot(token=config.telegram_token)
        self.running = False
        
    async def start_command(self, update: Update, context=None):
        """Handle /start command."""
        welcome_message = """
🚀 **Welcome to GitHub Bot!**

I can help you manage and monitor your GitHub repositories right from Telegram.

Available commands:
• /profile - Show your GitHub profile
• /repos - List your repositories
• /repo <owner/repo> - Get repository details
• /commits <owner/repo> - Show recent commits
• /issues <owner/repo> - Show repository issues
• /search <query> - Search repositories
• /help - Show this help message

Get started by using /profile to see your GitHub information!
"""
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context=None):
        """Handle /help command."""
        help_message = """
🔧 **GitHub Bot Commands**

**Profile & Repositories:**
• `/profile [username]` - Show GitHub profile info
• `/repos [username]` - List repositories (default: your repos)
• `/repo <owner/repo>` - Get detailed repository information

**Repository Details:**
• `/commits <owner/repo>` - Show recent commits
• `/issues <owner/repo>` - Show repository issues
• `/search <query>` - Search public repositories

**Examples:**
• `/repo octocat/Hello-World`
• `/commits microsoft/vscode`
• `/issues facebook/react`
• `/search machine learning python`

**Tips:**
• Use repository full names (owner/repo)
• Commands work with any public repository
• Some commands show your personal data when no username is specified
"""
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def profile_command(self, update: Update, context=None):
        """Handle /profile command."""
        try:
            # Extract username from message text
            message_text = update.message.text
            parts = message_text.split()
            username = parts[1] if len(parts) > 1 else None
            
            user_info = self.github_client.get_user_info(username)
            if not user_info:
                await update.message.reply_text(
                    "❌ User not found or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            formatted_info = self.github_client.format_user_info(user_info)
            await update.message.reply_text(formatted_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in profile command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching profile information.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def repos_command(self, update: Update, context=None):
        """Handle /repos command."""
        try:
            # Extract username from message text
            message_text = update.message.text
            parts = message_text.split()
            username = parts[1] if len(parts) > 1 else None
            
            repositories = self.github_client.get_user_repositories(username, limit=10)
            if not repositories:
                await update.message.reply_text(
                    "❌ No repositories found or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_list = "\n".join([
                f"📦 **{repo['name']}** - ⭐ {repo['stargazers_count']} stars"
                for repo in repositories
            ])
            
            message = f"📚 **Repositories:**\n\n{repo_list}"
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in repos command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching repositories.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def repo_command(self, update: Update, context=None):
        """Handle /repo command."""
        try:
            # Extract repo path from message text
            message_text = update.message.text
            parts = message_text.split()
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a repository: `/repo owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/repo owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            owner, repo = repo_path.split('/', 1)
            repo_info = self.github_client.get_repository_details(owner, repo)
            
            if not repo_info:
                await update.message.reply_text(
                    f"❌ Repository `{repo_path}` not found or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            formatted_info = self.github_client.format_repository_info(repo_info)
            await update.message.reply_text(formatted_info, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in repo command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching repository information.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def commits_command(self, update: Update, context=None):
        """Handle /commits command."""
        try:
            # Extract repo path from message text
            message_text = update.message.text
            parts = message_text.split()
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a repository: `/commits owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/commits owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            owner, repo = repo_path.split('/', 1)
            commits = self.github_client.get_repository_commits(owner, repo, limit=5)
            
            if not commits:
                await update.message.reply_text(
                    f"❌ No commits found for `{repo_path}` or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"📝 **Recent Commits for {repo_path}:**\n\n"
            for commit in commits:
                commit_info = commit.get('commit', {})
                author = commit_info.get('author', {})
                message_text = commit_info.get('message', 'No message')
                author_name = author.get('name', 'Unknown')
                commit_date = author.get('date', '')
                
                if commit_date:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                    date_str = date_obj.strftime('%Y-%m-%d %H:%M')
                else:
                    date_str = 'Unknown date'
                
                sha = commit.get('sha', '')[:7]
                url = commit.get('html_url', '')
                
                message += f"🔸 **{escape_markdown(message_text)}**\n"
                message += f"👤 {escape_markdown(author_name)} • 🕒 {date_str}\n"
                message += f"🔗 [`{sha}`]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in commits command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching commits.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def issues_command(self, update: Update, context=None):
        """Handle /issues command."""
        try:
            # Extract repo path from message text
            message_text = update.message.text
            parts = message_text.split()
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a repository: `/issues owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            repo_path = parts[1]
            if '/' not in repo_path:
                await update.message.reply_text(
                    "❌ Invalid format. Use: `/issues owner/repo`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            owner, repo = repo_path.split('/', 1)
            issues = self.github_client.get_repository_issues(owner, repo, limit=5)
            
            if not issues:
                await update.message.reply_text(
                    f"❌ No issues found for `{repo_path}` or API error occurred.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"🐛 **Issues for {repo_path}:**\n\n"
            for issue in issues:
                title = issue.get('title', 'No title')
                number = issue.get('number', 0)
                state = issue.get('state', 'unknown')
                user = issue.get('user', {}).get('login', 'Unknown')
                url = issue.get('html_url', '')
                
                state_emoji = "🟢" if state == "open" else "🔴"
                
                message += f"{state_emoji} **#{number}: {escape_markdown(title)}**\n"
                message += f"👤 {escape_markdown(user)} • 📋 {state}\n"
                message += f"🔗 [View Issue]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in issues command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while fetching issues.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def search_command(self, update: Update, context=None):
        """Handle /search command."""
        try:
            # Extract search query from message text
            message_text = update.message.text
            parts = message_text.split(maxsplit=1)
            
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Please specify a search query: `/search <query>`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            query = parts[1]
            repositories = self.github_client.search_repositories(query, limit=8)
            
            if not repositories:
                await update.message.reply_text(
                    f"❌ No repositories found for query: `{query}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            message = f"🔍 **Search Results for: {escape_markdown(query)}**\n\n"
            for repo in repositories:
                name = repo.get('name', 'Unknown')
                full_name = repo.get('full_name', 'Unknown')
                description = repo.get('description', 'No description')
                stars = repo.get('stargazers_count', 0)
                url = repo.get('html_url', '')
                
                message += f"📦 **{escape_markdown(name)}**\n"
                message += f"🔗 {escape_markdown(full_name)}\n"
                message += f"📝 {escape_markdown(description)}\n"
                message += f"⭐ {stars} stars • [View]({url})\n\n"
            
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in search command: {e}")
            await update.message.reply_text(
                "❌ An error occurred while searching repositories.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_message(self, update: Update):
        """Handle incoming messages."""
        try:
            message_text = update.message.text
            
            if message_text.startswith('/start'):
                await self.start_command(update)
            elif message_text.startswith('/help'):
                await self.help_command(update)
            elif message_text.startswith('/profile'):
                await self.profile_command(update)
            elif message_text.startswith('/repos'):
                await self.repos_command(update)
            elif message_text.startswith('/repo'):
                await self.repo_command(update)
            elif message_text.startswith('/commits'):
                await self.commits_command(update)
            elif message_text.startswith('/issues'):
                await self.issues_command(update)
            elif message_text.startswith('/search'):
                await self.search_command(update)
            else:
                await update.message.reply_text(
                    "❌ Unknown command. Use /help to see available commands.",
                    parse_mode=ParseMode.MARKDOWN
                )
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text(
                "❌ An error occurred while processing your message.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def run_polling(self):
        """Run the bot with long polling."""
        logger.info("Starting Telegram bot...")
        self.running = True
        last_update_id = 0
        
        try:
            while self.running:
                try:
                    # Get updates with offset
                    updates = await self.bot.get_updates(
                        offset=last_update_id + 1,
                        timeout=10
                    )
                    
                    for update in updates:
                        if update.message:
                            await self.handle_message(update)
                        
                        # Update the last processed update ID
                        last_update_id = update.update_id
                        
                except Exception as e:
                    logger.error(f"Error in polling loop: {e}")
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in bot: {e}")
            raise
        finally:
            self.running = False
    
    def start(self):
        """Start the Telegram bot."""
        try:
            asyncio.run(self.run_polling())
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    def stop(self):
        """Stop the Telegram bot."""
        self.running = False
        logger.info("Stopping Telegram bot...")