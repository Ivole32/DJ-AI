"""
Main configuration file for the API.
"""

# OS and path utilities
import os
from pathlib import Path

# Environment variable loader
from dotenv import load_dotenv

# Load environment variables from .env file
ROOT_DIR = Path(__file__).resolve().parent.parent  # Go up to api directory
load_dotenv(ROOT_DIR / ".env") # Load .env file

# API configuration
API_TITLE = "AI for DJs" # Short title for the API
API_DESCRIPTION = "API for AI-powered track searching and recommendations for DJs." # Description of the API
API_VERSION = "v1" # Version of the API
API_PREFIX = f"/api/{API_VERSION}" # Prefix for all API endpoints
API_RATE_LIMIT_ENABLED = False # Enable or disable rate limiting
API_DEFAULT_RATE_LIMITS = ["100/minute"] # Default rate limits
API_DOCS_ENABLED = True # Enable or disable API documentation

# Password hashing configuration
PEPPER = os.getenv("PEPPER", None)  # Use None if not set in .env to raise error later
ARGON_TIME_COST = 3  # Argon2 time cost parameter
ARGON_MEMORY_COST = 1024  # Argon2 memory cost parameter (in KB)
ARGON_PARALLELISM = 4  # Argon2 parallelism parameter
ARGON_HASH_LENGTH = 32  # Length of the generated hash
ARGON_SALT_LENGTH = 16  # Length of the random salt used

# User input constraints
USERNAME_MIN_LENGTH = 4 # Minimum length for usernames
USERNAME_MAX_LENGTH = 16 # Maximum length for usernames
PASSWORD_MIN_LENGTH = 8 # Minimum length for passwords
PASSWORD_MAX_LENGTH = 64 # Maximum length for passwords

PROFILE_DEFAULT_BIO = "This bio is in progress, like everything else." # Default bio for new users
PROFILE_DEFAULT_AVATAR_URL = "https://api.dicebear.com/7.x/initials/png?seed=" # Default avatar URL prefix, append <username> in backend
PROFILE_PICTURE_MAX_SIZE_MB = 5 # Maximum size for profile pictures in megabytes
PROFILE_PICTURE_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"} # Allowed image formats for profile pictures
BIO_MAX_LENGTH = 500 # Maximum length for user bios
PREFERED_GENRES_MAX_LENGTH = 10 # Maximum number of preferred genres
PREFERED_MAX_LENGHT_PER_GENRE = 15 # Maximum length for each preferred genre
PREFERED_BPM_MIN = 50 # Minimum BPM value for preferred BPM range
PREFERED_BPM_MAX = 250 # Maximum BPM value for preferred BPM range

MIN_PLAYLIST_NAME_LENGTH = 3 # Minimum length for playlist names
MAX_PLAYLIST_NAME_LENGTH = 25 # Maximum length for playlist names
PLAYLIST_SORT_GAP = 1000 # Gap between sort values in playlists
PLAYLIST_MIN_GAP = 0.000001 # Minimum gap to avoid sort value collisions
PLAYLIST_DESCRIPTION_MAX_LENGTH = 200 # Maximum length for playlist descriptions

# Whitelist of fields to return in public profile, for security reasons so we don't leak sensitive info when adding new fields later
PUBLIC_PROFILE_FIELDS = [
    'username',
    'role_id',
    'bio',
    'avatar_url',
    'prefered_bpm_range',
    'prefered_genres'
]

# PostgreSQL configuration
# (Floats must stay as floats)
POSTGRES_HOST = "postgres" # Hostname of the PostgreSQL server (Docker Compose service name)
POSTGRES_PORT = 5432 # Port number of the PostgreSQL server
POSGRES_USER = os.getenv("POSTGRES_USER", None)  # Use None if not set in .env to raise error later
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", None)  # Use None if not set in .env to raise error later
POSTGRES_DATABSE = os.getenv("POSTGRES_DATABASE", None)  # Use None if not set in .env to raise error later
POSGRES_MIN_CONNECTIONS = 1 # Minimum number of connections in the pool
POSTGRES_MAX_CONNECTIONS = 5 # Maximum number of connections in the pool
POSTGRES_CONNECT_TIMEOUT = 5.0 # Connection timeout for PostgreSQL (in seconds)
POSTGRES_RETRIES = 3 # Number of retries for PostgreSQL connection
POSTGRES_RETRY_DELAY = 2.0 # Delay between PostgreSQL connection retries (in seconds)
POSTGRES_HEALTHCHECK_TIMEOUT = 15.0 # Timeout for PostgreSQL health checks (in seconds)

# JWT configuration
JWT_ALGORITHM = "HS256" # Algorithm used for JWT encoding/decoding
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Time in minutes for access token expiration
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Time in days for refresh token expiration
JWT_SECRET = os.getenv("JWT_SECRET", None)  # JWT secret key, use None if not set in .env to raise error later

# CORS configuration
CORS_ALLOWED_ORIGINS = ["*"] # Allow all origins for now, can be adjusted later
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT","PATCH", "DELETE", "OPTIONS"] # Only allow specific methods, can be adjusted later
CORS_ALLOWED_HEADERS = ["*"] # Allow all headers
CORS_MAX_AGE = 600 # Cache preflight (OPTIONS) requests for 10 minutes

# Cookie security settings
COOKIE_SECURE = False  # Cookie secure flag, set to True in production with HTTPS

# Dataset path
DATASET_PATH = "../dataset/dataset.json" # Path to the main dataset file
TRACKS_CSV_PATH = "../dataset/tracks.csv" # Path to the tracks CSV file

# Debug settings
DEBUG = False # Enable or disable debug mode
ENABLE_DEMO_LOGIN = False # Enable or disable demo login for testing

# Server configuration
HOST = "0.0.0.0" # Server host (listen on all interfaces)
PORT = 8080 # Server port