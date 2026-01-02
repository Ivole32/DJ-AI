"""
Main configuration file for the API.
"""

# API configuration
API_TITLE = "AI for DJs"
API_DESCRIPTION = "API for AI-powered track searching and recommendations for DJs."
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
API_RATE_LIMIT_ENABLED = False
API_DEFAULT_RATE_LIMITS = ["100/minute"]

# CORS configuration
CORS_ALLOWED_ORIGINS = ["*"] # Allow all origins for now
CORS_ALLOWED_METHODS = ["GET", "POST", "OPTIONS"] # Only allow specific methods, can be adjusted later
CORS_ALLOWED_HEADERS = ["*"] # Allow all headers
CORS_MAX_AGE = 600 # Cache preflight requests for 10 minutes

# Dataset path
DATASET_PATH = r"dataset\dataset.json"

# Debug mode
DEBUG = True

# Server configuration
HOST = "localhost"
PORT = 8080