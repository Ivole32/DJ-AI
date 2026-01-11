"""
Data models for prediction actions.
"""


# Pydantic for data validation
from pydantic import BaseModel, Field

# Typing
from typing import List, Optional


class TrackPredictionRequest(BaseModel):
    """
    Data model for track prediction request.
    """
    track_id: str  = Field(..., min_length=11, max_length=11, description="Track ID")
    top_k: Optional[int] = Field(5, ge=1, le=25, description="Number of results to return")

class PredictedTrack(BaseModel):
    """
    Base data model for a predicted track in the response.
    """
    id: str = Field(..., description="Track ID (YouTube ID)")
    title: Optional[str] = Field(None, description="Track title")
    artist: Optional[str] = Field(None, description="Artist name")
    score: float = Field(..., description="Prediction confidence score")
    bpm: Optional[float] = Field(None, description="Beats per minute")
    key: Optional[str] = Field(None, description="Musical key")
    camelot: Optional[str] = Field(None, description="Camelot notation")
    energy: Optional[float] = Field(None, description="Energy level (0-1)")

class TrackPredictionResponse(BaseModel):
    """
    Data model for track prediction response.
    """
    results: List[PredictedTrack] = Field(..., description="List of predicted tracks")