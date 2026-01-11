
# FastAPI core imports
from fastapi import APIRouter, Request

# Models
from api.models.config import ServerConfigResponse

# Rate limiting
from api.rate_limit.limiter import limiter

# Config constants
from api.config.config import (
    USERNAME_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    BIO_MAX_LENGTH,
    PREFERED_GENRES_MAX_LENGTH,
    PREFERED_MAX_LENGHT_PER_GENRE,
    PREFERED_BPM_MIN,
    PREFERED_BPM_MAX,
    MIN_PLAYLIST_NAME_LENGTH,
    MAX_PLAYLIST_NAME_LENGTH,
    PLAYLIST_DESCRIPTION_MAX_LENGTH
)

# Router for config-related endpoints
router = APIRouter(prefix="/config", tags=["Config"]) 


@router.get("/get", response_model=ServerConfigResponse)
@limiter.limit("10/second")
async def get_server_config(request: Request):
    """
    Endpoint to get server configuration constraints.
    Returns:
        ServerConfigResponse: Configuration constraints for user inputs.
    Note: This endpoint is cached by header middleware to reduce load.
    """
    return ServerConfigResponse(
        username_min_length=USERNAME_MIN_LENGTH,
        username_max_length=USERNAME_MAX_LENGTH,
        password_min_length=PASSWORD_MIN_LENGTH,
        password_max_length=PASSWORD_MAX_LENGTH,
        bio_max_length=BIO_MAX_LENGTH,
        prefered_genres_max_length=PREFERED_GENRES_MAX_LENGTH,
        prefered_max_length_per_genre=PREFERED_MAX_LENGHT_PER_GENRE,
        prefered_bpm_min=PREFERED_BPM_MIN,
        prefered_bpm_max=PREFERED_BPM_MAX,
        min_playlist_name_length=MIN_PLAYLIST_NAME_LENGTH,
        max_playlist_name_length=MAX_PLAYLIST_NAME_LENGTH,
        playlist_description_max_length=PLAYLIST_DESCRIPTION_MAX_LENGTH
    )