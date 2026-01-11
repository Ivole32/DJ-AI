"""
Data models for search actions.
"""


# Pydantic for data validation
from pydantic import BaseModel, Field

# Typing
from typing import List, Optional


class TrackSearchRequest(BaseModel):
    """
    Data model for track search request.
    """
    query: str  = Field(..., min_length=3, max_length=35, description="Track ID or title")
    top: Optional[int] = Field(5, ge=1, le=50, description="Number of results to return")

class TrackMatch(BaseModel):
    """
    Data model for a single track match in search response.
    """
    id: Optional[str] = Field(None, description="Track ID, e.g., YouTube ID")
    title: Optional[str] = Field(None, description="Track title")
    artist: Optional[str] = Field(None, description="Artist name")
    mix_id: Optional[str] = Field(None, description="ID of the mix this track belongs to")
    score: int | float = Field(..., description="Fuzzy matching score (0-100)")
    bpm: Optional[float] = Field(None, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key")
    camelot: Optional[str] = Field(None, description="Camelot notation")
    energy: Optional[float] = Field(None, description="Energy level (0-1)")

class TrackSearchResponse(BaseModel):
    """
    Data model for track search response.
    """
    results: List[TrackMatch] = Field(..., description="List of top matching tracks")