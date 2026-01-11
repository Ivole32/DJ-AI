"""
JWT Validator Service: dependencies to validate JWT tokens and user roles.
"""

import jwt

from fastapi import Depends, HTTPException, Request
from fastapi.security import APIKeyCookie

from api.services.JWT.JWT_handler import JWT_handler

# Define cookie security scheme for OpenAPI docs
cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

async def require_token(request: Request, token: str = Depends(cookie_scheme)):
    """
    Dependency to require a valid JWT token from the request cookies.
    Raises HTTPException if token is missing, expired, or invalid.
    Returns the decoded token payload if valid.
    """
    JWT_token = request.cookies.get("access_token")

    if not JWT_token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        payload = JWT_handler.decode_token(JWT_token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return payload

async def optional_token(request: Request, token: str = Depends(cookie_scheme)):
    """
    Dependency to optionally get a JWT token from the request cookies.
    Returns None if no token is provided or if the token is invalid/expired.
    Returns the decoded token payload if valid.
    """
    JWT_token = request.cookies.get("access_token")

    if not JWT_token:
        return None

    try:
        payload = JWT_handler.decode_token(JWT_token)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

    return payload