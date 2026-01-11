"""
Models for getting server configuration and 
"""


# Pydantic for data validation
from pydantic import BaseModel, Field


class ServerConfigResponse(BaseModel):
    """
    Data model for server configuration response.
    """
    username_min_length: int = Field(..., description="Minimum length for usernames")
    username_max_length: int = Field(..., description="Maximum length for usernames")
    password_min_length: int = Field(..., description="Minimum length for passwords")
    password_max_length: int = Field(..., description="Maximum length for passwords")

    bio_max_length: int = Field(..., description="Maximum length for user bios")
    prefered_genres_max_length: int = Field(..., description="Maximum number of preferred genres")
    prefered_max_length_per_genre: int = Field(..., description="Maximum length for each preferred genre")
    prefered_bpm_min: int = Field(..., description="Minimum BPM value for preferred BPM range")
    prefered_bpm_max: int = Field(..., description="Maximum BPM value for preferred BPM range")

    min_playlist_name_length: int = Field(..., description="Minimum length for playlist names")
    max_playlist_name_length: int = Field(..., description="Maximum length for playlist names")
    playlist_description_max_length: int = Field(..., description="Maximum length for playlist descriptions")