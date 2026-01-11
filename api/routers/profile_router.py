
# FastAPI core imports
from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File

# Rate limiting
from api.rate_limit.limiter import limiter

# Readiness check utility
from api.utils.readiness import ensure_ready

# Database access
from api.database.user_database.user_database import user_database
from api.database.profile_database.profile_database import profile_database

# Models
from api.models.profile import UserProfileModify

# JWT authentication
from api.services.JWT.JWT_validator import require_token

# Data filtering utility
from api.utils.filter_data import filter_data

# Config constants
from api.config.config import PUBLIC_PROFILE_FIELDS, PROFILE_PICTURE_MAX_SIZE_MB, PROFILE_PICTURE_ALLOWED_FORMATS, PROFILE_DEFAULT_AVATAR_URL

# File upload service
from api.services.file_upload_service import img_upload

# Standard library
from urllib.parse import urlparse
from pathlib import Path

# Dependency for ready-Check
check_user_database_ready = lambda: ensure_ready(user_database, name="UserDatabase")
check_profile_database_ready = lambda: ensure_ready(profile_database, name="ProfileDatabase")
check_uploader_service_ready = lambda: ensure_ready(img_upload, name="UploadService")

router = APIRouter(prefix="/profile", 
                   tags=["Profile"], 
                   dependencies=[
                                    Depends(check_user_database_ready),# Only start when user database is ready
                                    Depends(check_profile_database_ready), # Only start when profile database is ready
                                    Depends(check_uploader_service_ready) # Only start when uploader service is ready

                                ] 
                   )


@router.get("/{username}")
@limiter.limit("10/second")
async def get_user_profile(request: Request, username: str):
    """
    Endpoint to get a user's profile information by user ID.
    """

    user = user_database.get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user["user_id"]:
        raise HTTPException(status_code=404, detail="Unable to retrieve user ID")

    user_id = user["user_id"]

    profile_data = profile_database.get_user_profile(user_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Return only whitelisted fields
    return filter_data(profile_data, PUBLIC_PROFILE_FIELDS) 

@router.patch("/update-profile")
@limiter.limit("5/second")
async def update_profile(request: Request, profile_data: UserProfileModify, payload = Depends(require_token)):
    """
    Endpoint to update the current logged-in user's profile.
    Note: Profile picture updates are handled separately.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = profile_database.modify_user_profile(
        user_id,
        bio=profile_data.bio,
        prefered_bpm_range=profile_data.prefered_bpm_range,
        prefered_genres=profile_data.prefered_genres
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    
    return {"message": "Profile updated successfully"}

@router.post("/profile-picture")
@limiter.limit("2/second")
async def upload_cover_image(request: Request, file: UploadFile = File(...), payload = Depends(require_token)):
    """
    Endpoint to upload or update the current logged-in user's profile picture.
    Args:
        file (UploadFile): The image file to upload.
    Returns:
        dict: Information about the uploaded profile picture.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Read file
    contents = await file.read()

    # Save image using UploadService
    filename, url_path = img_upload.save_img_file("profile_pictures", contents, PROFILE_PICTURE_MAX_SIZE_MB, PROFILE_PICTURE_ALLOWED_FORMATS)

    # Update user's profile with new avatar URL
    profile_database.modify_user_profile(user_id=user_id, avatar_url=url_path)

    return {"filename": filename, "avatar_url": url_path}

from urllib.parse import urlparse
from fastapi import HTTPException, Request, Depends

@router.delete("/profile-picture")
@limiter.limit("2/second")
async def delete_profile_picture(
    request: Request,
    payload: dict = Depends(require_token),
):
    user_id = payload.get("user_id")
    username = payload.get("username")

    if not user_id or not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    profile_data = profile_database.get_user_profile(user_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")

    avatar_url: str | None = profile_data.get("avatar_url")
    file_path: Path | None = None

    if avatar_url:
        # Case 1: file:// URI
        if avatar_url.startswith("file://"):
            parsed = urlparse(avatar_url)
            file_path = Path(parsed.path)

        # Case 2: local uploads path
        elif avatar_url.startswith("/uploads/profile_pictures/"):
            relative_path = avatar_url.removeprefix("/uploads/")
            file_path = img_upload.base_dir / relative_path

    if file_path:
        try:
            resolved = file_path.resolve()
            uploads_base = img_upload.base_dir.resolve()

            # 🔒 Must be inside api/uploads
            resolved.relative_to(uploads_base)

            if resolved.exists():
                resolved.unlink()

        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid avatar file path"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete profile picture file: {str(e)}"
            )

    # Reset to default external avatar
    default_avatar_url = f"{PROFILE_DEFAULT_AVATAR_URL}{username}"

    if not profile_database.modify_user_profile(
        user_id=user_id,
        avatar_url=default_avatar_url
    ):
        raise HTTPException(
            status_code=500,
            detail="Failed to reset profile picture"
        )

    return {"message": "Profile picture reset to default"}