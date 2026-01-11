
# FastAPI core imports
from fastapi import APIRouter, Depends, Request, Query, HTTPException

# Rate limiting
from api.rate_limit.limiter import limiter

# Readiness check utility
from api.utils.readiness import ensure_ready

# Typing
from typing import Annotated

# Prediction model service
from api.services.prediction_model import PredictionModel

# Models
from api.models.prediction import TrackPredictionRequest, TrackPredictionResponse

# Create PredictionModel instance (non-blocking!)
prediction_model = PredictionModel()

# Start background training if needed
if not prediction_model.is_ready()[0]:
    prediction_model.start_background_training()

# Dependency for ready-Check
check_prediction_ready = lambda: ensure_ready(prediction_model, name="PredictionModel")

# Router for search-related endpoints
router = APIRouter(prefix="/prediction", 
                   tags=["Prediction"], 
                   dependencies=[Depends(check_prediction_ready)] # Only start when predictor is ready
                   )

@router.get("/status")
@limiter.limit("10/second")
async def get_model_status(request: Request):
    """
    Get current model status including training progress.
    """
    return prediction_model.get_status()

@router.get("/next_track", response_model=TrackPredictionResponse)
@limiter.limit("5/second")
async def recommend_next_track(request: Request, params: Annotated[TrackPredictionRequest, Query()]):
    """
    Endpoint to recommend next tracks based on the current track ID.

    Args:
        track_id (str): Current track ID.
        top_k (int): Number of top recommendations to return.

    Returns:
        dict: Recommended track IDs with their scores.
        Raises:
            HTTPException: If track_id is not found (404)
    """
    try:
        recommendations = prediction_model.recommend_next(params.track_id, params.top_k)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)[1:-1]) # Remove quotes from KeyError message and return 404
    return TrackPredictionResponse(results=recommendations)