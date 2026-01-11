
# FastAPI core imports
from fastapi import APIRouter, Depends, Request, HTTPException

# Rate limiting
from api.rate_limit.limiter import limiter

# Readiness check utility
from api.utils.readiness import ensure_ready

# Database access
from api.database.playlist_database.playlist_database import playlist_database
from api.database.user_database.user_database import user_database

# Models
from api.models.playlist import PlayListCreateRequest, PlayListUpdateRequest, PlayListAddTrackRequest

# JWT authentication
from api.services.JWT.JWT_validator import require_token, optional_token



# Dependency for ready-Check
check_user_database_ready = lambda: ensure_ready(user_database, name="UserDatabase")
check_playlist_database_ready = lambda: ensure_ready(playlist_database, name="PlaylistDatabase")


router = APIRouter(prefix="/playlist", 
                   tags=["Playlist"], 
                   dependencies=[
                                    Depends(check_user_database_ready), # Only start when user database is ready
                                    Depends(check_playlist_database_ready) # Only start when profile database is ready
                                ] 
                   )

@router.get("/list")
@limiter.limit("10/second")
async def list_playlists(request: Request, payload = Depends(require_token)):
    """
    Endpoint to list all playlists for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    playlists = playlist_database.get_users_playlists(user_id=user_id, include_private=True)
    return {"playlists": playlists}

@router.post("/create")
@limiter.limit("5/second")
async def create_playlist(request: Request, playlist_data: PlayListCreateRequest, payload = Depends(require_token)):
    """
    Endpoint to create a new playlist for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    playlist_id = playlist_database.create_playlist(
        user_id=user_id,
        name=playlist_data.name,
        description=playlist_data.description,
        tags=playlist_data.tags,
        public=playlist_data.is_public
    )
    if not playlist_id:
        raise HTTPException(status_code=500, detail="Failed to create playlist")
    
    return {"message": "Playlist created successfully", "playlist_id": playlist_id}

@router.delete("/delete/{playlist_id}")
@limiter.limit("5/second")
async def delete_playlist(request: Request, playlist_id: str, payload = Depends(require_token)):
    """
    Endpoint to delete a playlist by its ID for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = playlist_database.delete_playlist(playlist_id=playlist_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to delete playlist, playlist not found or unauthorized")
    
    return {"message": "Playlist deleted successfully"}

@router.put("/update/{playlist_id}")
@limiter.limit("5/second")
async def update_playlist(request: Request, playlist_id: str, playlist_data: PlayListUpdateRequest, payload = Depends(require_token)):
    """
    Endpoint to update a playlist for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = playlist_database.update_playlist(
        playlist_id=playlist_id,
        user_id=user_id,
        name=playlist_data.name,
        description=playlist_data.description,
        tags=playlist_data.tags,
        public=playlist_data.is_public
    )
    if not success:
        raise HTTPException(status_code=404, detail="Failed to update playlist, playlist not found or unauthorized")
    
    return {"message": "Playlist updated successfully"}

@router.get("/get/{playlist_id}")
@limiter.limit("10/second")
async def get_playlist(request: Request, playlist_id: str, payload = Depends(require_token)):
    """
    Endpoint to get a playlist by its ID for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    allowed = playlist_database.user_modify_allowed(playlist_id=playlist_id,user_id=user_id)
    if not allowed:
        playlist_public = playlist_database.is_playlist_public(playlist_id=playlist_id)
        if not playlist_public:
            raise HTTPException(status_code=404, detail="Playlist not found")
        else:
            raise HTTPException(status_code=403, detail="Unauthorized to view this playlist")

    playlist = playlist_database.get_playlist_by_id(playlist_id=playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    return {"playlist": playlist}

@router.get("/get-tracks/{playlist_id}")
@limiter.limit("10/second")
async def get_playlist_tracks(request: Request, playlist_id: str, payload = Depends(optional_token)):
    """
    Endpoint to get tracks of a playlist by its ID for the current logged-in user OR if the playlist is public (no Auth required).
    """
    user_id = payload.get("user_id", None) if payload else None
    allowed = False
    if user_id:
        allowed = playlist_database.user_modify_allowed(playlist_id=playlist_id, user_id=user_id)

    if not allowed:
        playlist_public = playlist_database.is_playlist_public(playlist_id=playlist_id)
        if not playlist_public:
            raise HTTPException(status_code=404, detail="Playlist not found or not public")

    tracks = playlist_database.get_tracks(playlist_id=playlist_id)

    return {"tracks": tracks if tracks else []}

@router.post("/add-track/{playlist_id}/{youtube_id}")
@limiter.limit("5/second")
async def add_track_to_playlist(request: Request, playlist_id: str, youtube_id: str, insert_data: PlayListAddTrackRequest, payload = Depends(require_token)):
    """
    Endpoint to add a track to a playlist by its ID for the current logged-in user.
    Track metadata is automatically loaded from the dataset.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    allowed = playlist_database.user_modify_allowed(playlist_id=playlist_id,user_id=user_id)
    if not allowed:
        playlist_public = playlist_database.is_playlist_public(playlist_id=playlist_id)
        if not playlist_public:
            raise HTTPException(status_code=404, detail="Playlist not found")
        else:
            raise HTTPException(status_code=403, detail="Unauthorized to modify this playlist")

    if insert_data.position == "between":
        # If prev_sort or next_sort are None, fall back to adding at the end
        if insert_data.prev_sort is None or insert_data.next_sort is None:
            playlist_database.add_track_to_end(
                playlist_id=playlist_id,
                youtube_track_id=youtube_id
            )
        else:
            playlist_database.add_track_between(
                playlist_id=playlist_id,
                youtube_track_id=youtube_id,
                prev_sort=insert_data.prev_sort,
                next_sort=insert_data.next_sort
            )
    elif insert_data.position == "start":
        playlist_database.add_track_to_start(
            playlist_id=playlist_id,
            youtube_track_id=youtube_id
        )

    elif insert_data.position == "end":
        playlist_database.add_track_to_end(
            playlist_id=playlist_id,
            youtube_track_id=youtube_id
        )

    return {"message": "Track added to playlist successfully"}

@router.delete("/remove-track/{playlist_id}/{playlist_track_id}")
@limiter.limit("5/second")
async def remove_track_from_playlist(request: Request, playlist_id: str, playlist_track_id: str, payload = Depends(require_token)):
    """
    Endpoint to remove a track from a playlist by its ID and sort key for the current logged-in user.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    allowed = playlist_database.user_modify_allowed(playlist_id=playlist_id,user_id=user_id)
    if not allowed:
        playlist_public = playlist_database.is_playlist_public(playlist_id=playlist_id)
        if not playlist_public:
            raise HTTPException(status_code=404, detail="Playlist not found")
        else:
            raise HTTPException(status_code=403, detail="Unauthorized to modify this playlist")

    success = playlist_database.delete_track_from_playlists(playlist_id=playlist_id, playlist_track_id=playlist_track_id)
    if not success:
        raise HTTPException(status_code=404, detail="Failed to remove track, track or playlist not found")
    
    return {"message": "Track removed from playlist successfully"}

@router.get("/public/{username}")
@limiter.limit("10/second")
async def get_public_playlists_by_username(request: Request, username: str):
    """
    Endpoint to list all public playlists for a given username (no Auth required).
    """
    user = user_database.get_user_by_username(username)
    if not user or not user.get("user_id"):
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user["user_id"]
    playlists = playlist_database.get_users_playlists(user_id=user_id, include_private=False)
    return {"playlists": playlists}