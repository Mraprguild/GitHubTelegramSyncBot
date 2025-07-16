"""
GitHub API client for the Telegram bot.
Handles all GitHub API interactions and data formatting.
"""

import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class GitHubClient:
    """GitHub API client for repository and user operations."""
    
    def __init__(self, token: str, username: str = ''):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub personal access token
            username: GitHub username for personal operations
        """
        self.token = token
        self.username = username
        self.base_url = 'https://api.github.com'
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'TelegramGitHubBot/1.0'
        }
        
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Optional[Dict]:
        """
        Make authenticated request to GitHub API.
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
            
        Returns:
            Response data or None if error
        """
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params or {},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Resource not found: {endpoint}")
                return None
            else:
                logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_user_info(self, username: str = None) -> Optional[Dict]:
        """
        Get user information from GitHub.
        
        Args:
            username: GitHub username (uses configured username if None)
            
        Returns:
            User information dictionary
        """
        user = username or self.username
        if not user:
            return None
            
        return self._make_request(f'users/{user}')
    
    def get_user_repositories(self, username: str = None, limit: int = 10) -> List[Dict]:
        """
        Get user's repositories.
        
        Args:
            username: GitHub username
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository dictionaries
        """
        user = username or self.username
        if not user:
            return []
            
        params = {
            'sort': 'updated',
            'direction': 'desc',
            'per_page': limit,
            'type': 'owner'
        }
        
        data = self._make_request(f'users/{user}/repos', params=params)
        return data if data else []
    
    def get_repository_details(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Get detailed information about a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository details dictionary
        """
        return self._make_request(f'repos/{owner}/{repo}')
    
    def get_repository_commits(self, owner: str, repo: str, limit: int = 5) -> List[Dict]:
        """
        Get recent commits for a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of commits to return
            
        Returns:
            List of commit dictionaries
        """
        params = {
            'per_page': limit,
            'page': 1
        }
        
        data = self._make_request(f'repos/{owner}/{repo}/commits', params=params)
        return data if data else []
    
    def get_repository_issues(self, owner: str, repo: str, state: str = 'open', limit: int = 5) -> List[Dict]:
        """
        Get repository issues.
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            limit: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        params = {
            'state': state,
            'per_page': limit,
            'sort': 'updated',
            'direction': 'desc'
        }
        
        data = self._make_request(f'repos/{owner}/{repo}/issues', params=params)
        return data if data else []
    
    def search_repositories(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for repositories.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of repository dictionaries
        """
        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': limit
        }
        
        data = self._make_request('search/repositories', params=params)
        return data.get('items', []) if data else []
    
    def format_repository_info(self, repo: Dict) -> str:
        """
        Format repository information for display.
        
        Args:
            repo: Repository dictionary
            
        Returns:
            Formatted repository information string
        """
        name = repo.get('name', 'Unknown')
        full_name = repo.get('full_name', 'Unknown')
        description = repo.get('description', 'No description')
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)
        language = repo.get('language', 'Unknown')
        url = repo.get('html_url', '')
        
        updated_at = repo.get('updated_at', '')
        if updated_at:
            updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            updated_str = updated_date.strftime('%Y-%m-%d %H:%M UTC')
        else:
            updated_str = 'Unknown'
        
        return f"""
📦 **{name}**
🔗 {full_name}
📝 {description}

⭐ Stars: {stars}
🍴 Forks: {forks}
💻 Language: {language}
🕒 Updated: {updated_str}

🌐 [View on GitHub]({url})
"""
    
    def format_user_info(self, user: Dict) -> str:
        """
        Format user information for display.
        
        Args:
            user: User dictionary
            
        Returns:
            Formatted user information string
        """
        name = user.get('name', user.get('login', 'Unknown'))
        login = user.get('login', 'Unknown')
        bio = user.get('bio', 'No bio')
        location = user.get('location', 'Unknown')
        public_repos = user.get('public_repos', 0)
        followers = user.get('followers', 0)
        following = user.get('following', 0)
        url = user.get('html_url', '')
        
        return f"""
👤 **{name}** (@{login})
📍 {location}
📖 {bio}

📦 Public Repositories: {public_repos}
👥 Followers: {followers}
➡️ Following: {following}

🌐 [View Profile]({url})
"""
