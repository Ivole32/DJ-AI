
# FastAPI core imports
from fastapi import APIRouter, Depends, Request, Response, HTTPException

# Rate limiting
from api.rate_limit.limiter import limiter

# Readiness check utility
from api.utils.readiness import ensure_ready

# JWT authentication
from api.services.JWT.JWT_validator import require_token
from api.services.JWT.JWT_handler import JWT_handler

# Database access
from api.database.user_database.user_database import user_database

# Config and models
from api.config.config import ENABLE_DEMO_LOGIN
from api.models.user import UserLoginRequest

user_database.init_db()


# Dependency for ready-Check
check_database_ready = lambda: ensure_ready(user_database, name="UserDatabase")


router = APIRouter(prefix="/auth", 
                   tags=["Auth"], 
                   dependencies=[Depends(check_database_ready)] # Only start when database is ready
                   )


@router.post("/login")
@limiter.limit("5/second")
async def login(request: Request, user: UserLoginRequest, response: Response):
    # Demo login bypass, not recommanded as there is no database entry for this user and is only for login testing
    if ENABLE_DEMO_LOGIN:
        if user.username == "demo" and user.password == "demo_password":
            user_payload = {
                "user_id": "demo_user_12345",
                "username": "demo",
                "role_id": 1
            }
            return JWT_handler.issue_tokens(response, user_payload)

    authorized = user_database.authenticate_user(user.username, user.password)

    if not authorized:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_data = user_database.get_user_by_username(user.username)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    user_payload = {
        "user_id": user_data["user_id"],
        "username": user_data["username"],
        "role_id": user_data["role_id"]
    }
    return JWT_handler.issue_tokens(response, user_payload)
    
@router.post("/logout")
@limiter.limit("5/second")
async def logout(request: Request, response: Response):
    """
    Logout endpoint. Invalidate the JWT token on the client side by removing the cookie.
    """
    response.set_cookie(key="access_token", value="", httponly=True, max_age=0)
    response.set_cookie(key="refresh_token", value="", httponly=True, max_age=0)
    return {"message": "Logged out successfully"}

@router.get("/refresh")
@limiter.limit("3/15 minutes")
async def refresh_token(request: Request, response: Response):
    """
    Refresh the access token using the refresh token.
    """
    return JWT_handler.refresh_access_token(request, response)

@router.get("/verify")
@limiter.limit("5/second")
async def verify_token(request: Request, payload = Depends(require_token)):
    """
    Verify the validity of the access token.
    """
    return {"message": "Token is valid", "user": payload}