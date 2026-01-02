"""
Data models for prediction actions.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# Data model for track search request
class TrackPredictionRequest(BaseModel):
    track_id: str  = Field(..., min_length=11, max_length=11, description="Track ID")
    top_k: Optional[int] = Field(5, ge=1, le=25, description="Number of results to return")

# Data model for track prediction response
class TrackPredictionResponse(BaseModel):
    results: List[tuple] = Field(..., description="List of predicted tracks")