from fastapi import APIRouter, Depends, Request, Query
from api.rate_limit.limiter import limiter

from api.services.track_search import TrackSearcher
from api.models.search import TrackSearchRequest, TrackSearchResponse

from api.utils.readiness import ensure_ready

from typing import Annotated


# Initialize TrackSearcher instance
track_searcher = TrackSearcher()

# Dependency for ready-Check
check_searcher_ready = lambda: ensure_ready(track_searcher, name="TrackSearcher")

# Router for search-related endpoints
router = APIRouter(prefix="/search", 
                   tags=["Search"], 
                   dependencies=[Depends(check_searcher_ready)] # Only start when searcher is ready
                   ) 


@router.get("/track", response_model=TrackSearchResponse)
@limiter.limit("10/second")  # Limit to 10 requests per second
async def track_search(request: Request, params: Annotated[TrackSearchRequest, Query()]):
    """
    Endpoint to search for tracks by ID or title using fuzzy matching.

    Args:
        query (str): Track ID or title (may be misspelled).

    Returns:
        TrackSearchResponse: Response containing list of top matching tracks.
    """
    results = track_searcher.search_track(params.query, params.top)
    return TrackSearchResponse(results=results)