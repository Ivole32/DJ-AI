"""
Playlist model definitions.
Defines the Playlist data models used for playlist management.
"""


# Pydantic for data validation
from pydantic import BaseModel, Field, field_validator

# Typing
from typing import Literal, Optional

# Config constants
from api.config.config import MIN_PLAYLIST_NAME_LENGTH, MAX_PLAYLIST_NAME_LENGTH, PLAYLIST_DESCRIPTION_MAX_LENGTH

class PlayListCreateRequest(BaseModel):
    """
    Request model for creating a new playlist.
    """
    name: str = Field(..., min_length=MIN_PLAYLIST_NAME_LENGTH, max_length=MAX_PLAYLIST_NAME_LENGTH)
    description: Optional[str] = Field(None, max_length=PLAYLIST_DESCRIPTION_MAX_LENGTH)
    tags: Optional[list[str]] = Field(default=None, description="List of tags for the playlist")
    is_public: bool = Field(default=False)

class PlayListUpdateRequest(BaseModel):
    """
    Request model for updating playlist details.
    All fields are optional; only provide the fields to be updated.
    """
    name: Optional[str] = Field(None, min_length=MIN_PLAYLIST_NAME_LENGTH, max_length=MAX_PLAYLIST_NAME_LENGTH)
    description: Optional[str] = Field(None, max_length=PLAYLIST_DESCRIPTION_MAX_LENGTH)
    tags: Optional[list[str]] = Field(None, description="List of tags for the playlist")
    is_public: Optional[bool] = Field(None)

class PlayListAddTrackRequest(BaseModel):
    """
    Request model for adding a track to a playlist.
    
    Position can be:
    - "start": Add track at the beginning of the playlist
    - "end": Add track at the end of the playlist  
    - "between": Add track between two existing tracks (requires prev_sort and next_sort)
    
    Note: playlist_id and youtube_track_id are provided in the URL path.
    Track metadata (title, artist, bpm, etc.) is loaded automatically from the dataset.
    """
    position: Literal["start", "end", "between"] = Field(..., description="Where to add the track")
    prev_sort: Optional[float] = Field(None, description="Sort key of the track before (required if position='between')")
    next_sort: Optional[float] = Field(None, description="Sort key of the track after (required if position='between')")
    
    @field_validator('prev_sort', 'next_sort')
    @classmethod
    def validate_between_fields(cls, v, info):
        """Validate that prev_sort and next_sort are provided when position is 'between'."""
        # Get all field values
        values = info.data
        position = values.get('position')
        
        if position == 'between':
            field_name = info.field_name
            if field_name == 'prev_sort' and v is None:
                raise ValueError("prev_sort is required when position is 'between'")
            if field_name == 'next_sort' and v is None:
                raise ValueError("next_sort is required when position is 'between'")
        
        return v