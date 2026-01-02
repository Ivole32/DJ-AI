from fastapi import APIRouter, Depends, Request, Query
from api.rate_limit.limiter import limiter

from api.utils.readiness import ensure_ready

from typing import Annotated

from api.prediction_models.prediction_model import PredictionModel

from api.models.prediction import TrackPredictionRequest, TrackPredictionResponse

# Initialize PredictionModel instance
prediction_model = PredictionModel()

# Dependency for ready-Check
check_prediction_ready = lambda: ensure_ready(prediction_model, name="PredictionModel")

# Router for search-related endpoints
router = APIRouter(prefix="/prediction", 
                   tags=["Prediction"], 
                   dependencies=[Depends(check_prediction_ready)] # Only start when predictor is ready
                   ) 

@router.get("/next_track", response_model=TrackPredictionResponse)
@limiter.limit("5/second")  # Limit to 5 requests per second as it may be resource intensive
async def recommend_next_track(request: Request, params: Annotated[TrackPredictionRequest, Query()]):
    """
    Endpoint to recommend next tracks based on the current track ID.

    Args:
        track_id (str): Current track ID.
        top_k (int): Number of top recommendations to return.

    Returns:
        dict: Recommended track IDs with their scores.
    """
    recommendations = prediction_model.recommend_next(params.track_id, params.top_k)
    return TrackPredictionResponse(results=recommendations)