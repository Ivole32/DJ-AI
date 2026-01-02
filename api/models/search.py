"""
Data models for search actions.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

# Data model for track search request
class TrackSearchRequest(BaseModel):
    query: str  = Field(..., min_length=3, max_length=35, description="Track ID or title")
    top: Optional[int] = Field(5, ge=1, le=50, description="Number of results to return")

# Base model for track match in search response
class TrackMatch(BaseModel):
    id: Optional[str] = Field(None, description="Track ID, e.g., YouTube ID")
    title: Optional[str] = Field(None, description="Track title")
    mix_id: Optional[str] = Field(None, description="ID of the mix this track belongs to")
    score: int | float = Field(..., description="Fuzzy matching score (0-100)")

# Data model for track search response
class TrackSearchResponse(BaseModel):
    results: List[TrackMatch] = Field(..., description="List of top matching tracks")