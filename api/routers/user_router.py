from fastapi import APIRouter, Depends, Request, HTTPException, Response
from api.rate_limit.limiter import limiter
from api.utils.readiness import ensure_ready

from api.database.user_database.user_database import user_database
from api.models.user import UserRegisterRequest, UserChangePasswordRequest
from api.services.JWT.JWT_validator import require_token
from api.services.JWT.JWT_handler import JWT_handler


# Dependency for ready-Check
check_database_ready = lambda: ensure_ready(user_database, name="UserDatabase")

router = APIRouter(prefix="/user", 
                   tags=["User"], 
                   dependencies=[Depends(check_database_ready)] # Only start when database is ready
                   )

@router.post("/register")
@limiter.limit("5/second")
async def register_user(request: Request, user: UserRegisterRequest):
    """
    Endpoint to register a new user.
    """
    existing_username = user_database.get_user_by_username(user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = user_database.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = user_database.create_account(user.username, user.email, user.password)
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    return {"message": "User registered successfully", "user_id": user_id}

@router.delete("/delete-account")
@limiter.limit("5/second")
async def delete_account(request: Request, response: Response, payload = Depends(require_token)):
    """
    Endpoint to delete the current logged-in user's account.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    success = user_database.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user account")
    
    # Clear tokens on client side, could also use /logout on frontend but this is less prone to errors
    JWT_handler.clear_tokens(response)
    return {"message": "User account deleted successfully"}

@router.get("/me")
@limiter.limit("10/second")
async def get_current_user(request: Request, payload = Depends(require_token)):
    """
    Endpoint to get the current logged-in user's information.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_data = user_database.get_user_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        #"email": user_data["email"], # Omitted for reasons of efficiency and usability., could be needed in the future
        "role_id": user_data["role_id"]
    }
    
@router.post("/change-password")
@limiter.limit("5/second")
async def change_password(request: Request, user: UserChangePasswordRequest, payload = Depends(require_token)):
    """
    Endpoint to change the current user's password.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Verify current password
    user_data = user_database.get_user_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user_database.authenticate_user(user_data["username"], user.current_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    if user.current_password == user.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")
    
    # Update to new password
    success = user_database.modify_user(user_id, new_password=user.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update password")
    
    return {"detail": "Password changed successfully"}