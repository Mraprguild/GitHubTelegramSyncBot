# Telegram GitHub Bot

## Overview

This is a Telegram bot that integrates with GitHub to provide repository management, monitoring, and notification capabilities. The bot allows users to interact with GitHub repositories through Telegram commands and receives real-time notifications via GitHub webhooks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

1. **Telegram Bot Layer**: Handles user interactions and command processing
2. **GitHub API Client**: Manages all GitHub API communications
3. **Webhook Handler**: Processes GitHub webhook events and sends notifications
4. **Configuration Management**: Centralized configuration handling
5. **Utility Layer**: Common helper functions and text processing

The system is designed as a single-process application with threading for concurrent webhook handling.

## Key Components

### Configuration (`config.py`)
- Centralizes all environment variable management
- Validates required credentials and settings
- Handles Telegram bot token, GitHub token, webhook configuration, and admin settings
- Implements validation to ensure all required tokens are present

### GitHub Client (`github_client.py`)
- Provides abstraction layer for GitHub API interactions
- Handles authentication using personal access tokens
- Implements rate limiting awareness and error handling
- Supports repository operations, user profile queries, and commit history retrieval

### Telegram Bot (`telegram_bot.py`)
- Implements the main bot logic using python-telegram-bot library
- Provides command handlers for user interactions (`/start`, `/help`, `/profile`, `/repos`, `/repo`, `/commits`, `/issues`, `/search`)
- Supports inline keyboard interactions for enhanced user experience
- Uses MarkdownV2 formatting for rich message presentation

### Webhook Handler (`webhook_handler.py`)
- Flask-based webhook server for GitHub event processing
- Implements signature verification for security
- Processes GitHub events and converts them to Telegram notifications
- Provides health check endpoint for monitoring
- Runs in a separate thread to avoid blocking the main bot

### Utilities (`utils.py`)
- Text processing functions for Telegram markdown escaping
- Text truncation utilities for message formatting
- Common helper functions used across the application

## Data Flow

1. **User Commands**: Users send commands to Telegram bot → Bot processes command → GitHub API calls → Formatted response sent back to user
2. **GitHub Events**: GitHub webhook triggers → Flask server receives event → Signature verification → Event processing → Telegram notification sent
3. **Bot Initialization**: Configuration validation → GitHub client setup → Telegram bot initialization → Webhook server startup

## External Dependencies

### APIs and Services
- **Telegram Bot API**: For bot messaging and command handling
- **GitHub API v3**: For repository management and data retrieval
- **GitHub Webhooks**: For real-time event notifications

### Python Libraries
- `python-telegram-bot`: Telegram bot framework
- `requests`: HTTP client for GitHub API calls
- `flask`: Web framework for webhook handling
- `python-dotenv`: Environment variable management

### Authentication Requirements
- Telegram Bot Token (from BotFather)
- GitHub Personal Access Token
- GitHub Webhook Secret (optional but recommended)

## Deployment Strategy

The application is designed for simple deployment scenarios:

1. **Environment Setup**: Requires `.env` file with necessary tokens and configuration
2. **Single Process**: Runs as a single Python process with internal threading
3. **Port Configuration**: Configurable webhook port (default: 8000)
4. **Health Monitoring**: Includes health check endpoint at `/health`
5. **Logging**: Structured logging for debugging and monitoring

The architecture supports containerization and can be easily deployed on platforms like Heroku, Railway, or any VPS with Python support. The webhook handler requires a publicly accessible URL for GitHub to send events.

### Security Considerations
- Implements webhook signature verification
- Uses secure token-based authentication for both Telegram and GitHub
- Validates all configuration on startup
- Implements proper error handling and logging

The system is designed to be lightweight, maintainable, and easily extensible for additional GitHub operations or Telegram features.