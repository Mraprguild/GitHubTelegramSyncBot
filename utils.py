"""
Utility functions for the Telegram GitHub Bot.
"""

import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped text safe for Telegram markdown
    """
    if not text:
        return ""
    
    # Characters that need to be escaped in MarkdownV2
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    
    # Escape each character
    escaped = ""
    for char in text:
        if char in escape_chars:
            escaped += f"\\{char}"
        else:
            escaped += char
    
    return escaped

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of text
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_number(number: int) -> str:
    """
    Format large numbers with appropriate suffixes.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    if number >= 1000000:
        return f"{number / 1000000:.1f}M"
    elif number >= 1000:
        return f"{number / 1000:.1f}K"
    else:
        return str(number)

def extract_repo_info(repo_url: str) -> Dict[str, str]:
    """
    Extract owner and repository name from GitHub URL.
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        Dictionary with 'owner' and 'repo' keys
    """
    # Regular expression to match GitHub repository URLs
    patterns = [
        r'https://github\.com/([^/]+)/([^/]+)/?',
        r'git@github\.com:([^/]+)/([^/]+)\.git',
        r'([^/]+)/([^/]+)'  # Simple owner/repo format
    ]
    
    for pattern in patterns:
        match = re.match(pattern, repo_url.strip())
        if match:
            owner, repo = match.groups()
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            return {'owner': owner, 'repo': repo}
    
    return {'owner': '', 'repo': ''}

def validate_github_token(token: str) -> bool:
    """
    Validate GitHub personal access token format.
    
    Args:
        token: GitHub token to validate
        
    Returns:
        True if token format is valid
    """
    if not token:
        return False
    
    # GitHub personal access tokens start with 'ghp_' (new format)
    # or are 40 characters long (classic format)
    if token.startswith('ghp_'):
        return len(token) == 36
    else:
        return len(token) == 40 and token.isalnum()

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    return sanitized or 'untitled'

def parse_webhook_signature(signature: str) -> str:
    """
    Parse webhook signature header.
    
    Args:
        signature: Raw signature header
        
    Returns:
        Parsed signature hash
    """
    if not signature:
        return ""
    
    # Remove algorithm prefix (e.g., 'sha256=')
    if '=' in signature:
        return signature.split('=', 1)[1]
    
    return signature

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def is_valid_repo_path(repo_path: str) -> bool:
    """
    Validate repository path format (owner/repo).
    
    Args:
        repo_path: Repository path to validate
        
    Returns:
        True if path is valid
    """
    if not repo_path or '/' not in repo_path:
        return False
    
    parts = repo_path.split('/')
    if len(parts) != 2:
        return False
    
    owner, repo = parts
    
    # Basic validation for GitHub username/repo name
    if not owner or not repo:
        return False
    
    # Check for invalid characters
    invalid_chars = r'[<>:"/\\|?*\s]'
    if re.search(invalid_chars, owner) or re.search(invalid_chars, repo):
        return False
    
    return True

def get_error_message(error_code: int) -> str:
    """
    Get user-friendly error message for common HTTP status codes.
    
    Args:
        error_code: HTTP status code
        
    Returns:
        User-friendly error message
    """
    error_messages = {
        400: "Bad request - please check your input",
        401: "Unauthorized - please check your GitHub token",
        403: "Forbidden - you don't have permission to access this resource",
        404: "Not found - the requested resource doesn't exist",
        422: "Unprocessable entity - the request was well-formed but unable to be followed",
        500: "Internal server error - please try again later",
        502: "Bad gateway - GitHub API is temporarily unavailable",
        503: "Service unavailable - GitHub API is temporarily unavailable"
    }
    
    return error_messages.get(error_code, f"Unknown error (code: {error_code})")
