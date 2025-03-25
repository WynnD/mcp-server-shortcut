"""
Configuration module for Shortcut MCP Server.

This module manages loading and accessing configuration values.
"""

import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Shortcut API configuration
SHORTCUT_API_TOKEN = os.getenv("SHORTCUT_API_TOKEN")
SHORTCUT_API_BASE_URL = "https://api.app.shortcut.com/api/v3"

# Server configuration
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

# Verify required configuration is present
if not SHORTCUT_API_TOKEN:
    raise ValueError("SHORTCUT_API_TOKEN environment variable is required")
