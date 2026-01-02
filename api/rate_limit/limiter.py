"""
Main rate limiter configuration for the API.
"""

# Import necessary libraries
from slowapi import Limiter
from slowapi.util import get_remote_address

# Import configuration settings
from api.config.config import API_RATE_LIMIT_ENABLED, API_DEFAULT_RATE_LIMITS

# Limiter configuration
limiter = Limiter(enabled=API_RATE_LIMIT_ENABLED, key_func=get_remote_address, default_limits=API_DEFAULT_RATE_LIMITS)