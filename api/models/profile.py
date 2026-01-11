"""
Profile models for user profile operations.
"""

# Regex for input validation
import re

# Pydantic for data validation
from pydantic import BaseModel, Field, field_validator

# Config constants
from api.config.config import BIO_MAX_LENGTH, PREFERED_GENRES_MAX_LENGTH, PREFERED_MAX_LENGHT_PER_GENRE, PREFERED_BPM_MIN, PREFERED_BPM_MAX


class UserProfileModify(BaseModel):
    """
    Model for modifying user profile information.
    """
    bio: str = Field(..., max_length=BIO_MAX_LENGTH, description="User biography")
    prefered_bpm_range: list[int] = Field(..., description="Preferred BPM range as [min_bpm, max_bpm]")
    prefered_genres: list[str] = Field(..., max_length=PREFERED_GENRES_MAX_LENGTH, description="List of preferred music genres")
    
    @field_validator('bio')
    @classmethod
    def validate_bio(cls, v: str) -> str:
        """Validate bio content."""
        if v is None:
            return v
        # Just strip whitespace, no HTML escaping (frontend handles display safely with .value)
        return v.strip()
    
    @field_validator('prefered_genres')
    @classmethod
    def validate_genres(cls, v: list[str]) -> list[str]:
        """Validate and sanitize genre names."""
        if not v:
            return v
        
        sanitized = []
        for genre in v[:PREFERED_GENRES_MAX_LENGTH]:  # Limit to max length
            # Remove any HTML/special characters, allow only letters, numbers, spaces, hyphens, and ampersands
            cleaned = re.sub(r'[^a-zA-Z0-9\s\-&/]', '', genre.strip())
            if cleaned:  # Only add non-empty genres
                sanitized.append(cleaned[:PREFERED_MAX_LENGHT_PER_GENRE])  # Limit length per genre
        
        return sanitized
    
    @field_validator('prefered_bpm_range')
    @classmethod
    def validate_bpm_range(cls, v: list[int]) -> list[int]:
        """Validate BPM range values."""
        if not v or len(v) != 2:
            raise ValueError('BPM range must contain exactly 2 values [min, max]')
        
        min_bpm, max_bpm = v[0], v[1]
        
        # Validate range bounds
        if not (PREFERED_BPM_MIN <= min_bpm <= PREFERED_BPM_MAX):
            raise ValueError(f'Minimum BPM must be between {PREFERED_BPM_MIN} and {PREFERED_BPM_MAX}')
        if not (PREFERED_BPM_MIN <= max_bpm <= PREFERED_BPM_MAX):
            raise ValueError(f'Maximum BPM must be between {PREFERED_BPM_MIN} and {PREFERED_BPM_MAX}')
        if min_bpm >= max_bpm:
            raise ValueError('Minimum BPM must be less than maximum BPM')
        
        return [min_bpm, max_bpm]