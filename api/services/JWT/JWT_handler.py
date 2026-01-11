"""
JWT handling service: create, issue and decode JWT tokens.
""" 

import sys
import jwt
from datetime import datetime, timedelta, timezone

from fastapi import Request, HTTPException
from fastapi.responses import Response

from api.config.config import JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from api.config.config import JWT_SECRET, COOKIE_SECURE

class JWTHandler:
    def __init__(self):
        if not JWT_SECRET:
            from api.logger.logger import logger
            logger.error("Missing JWT_SECRET environment variable in JWT handler")
            sys.exit(1)

    def create_access_token(self, data: dict):
        """
        Create a JWT access token with an expiration time.
        Args:
            data (dict): The payload data to include in the token.
        Returns:
            str: The encoded JWT access token.
        """
        payload = data.copy()
        headers = {"typ": "JWT"}
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Use UTC time to avoid issues caused by time zone shifts
    
        payload.update({"exp": expire})
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM, headers=headers)

    def create_refresh_token(self, data: dict):
        """
        Create a JWT refresh token with a longer expiration time.
        Args:
            data (dict): The payload data to include in the token.
        Returns:
            str: The encoded JWT refresh token.
        """
        payload = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload.update({"exp": expire})
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str):
        """
        Decode and validate a JWT token.
        Args:
            token (str): The JWT token to decode.
        Returns:
            dict: The decoded token payload.
        Raises:
            HTTPException: If an unexpected error occurs during decoding.
            Other exceptions (jwt.ExpiredSignatureError, jwt.InvalidTokenError) are rerouted to the caller.
        """
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise # reroute the exception to be handled by caller
        except Exception as e:
            # all other exceptions
            from api.logger.logger import logger
            logger.error(f"Unexpected error during token decoding: {e}")
            raise HTTPException(status_code=400, detail="Bad request")

    def issue_tokens(self, response: Response, user_payload: dict) -> dict:
        """
        Issue access and refresh tokens as HTTP-only cookies in the response.
        Args:
            response (Response): FastAPI Response object to set cookies on.
            user_payload (dict): Payload containing user information for the tokens.
        Returns:
            dict: A dictionary indicating success and token type.
        """
        access_token = self.create_access_token(
            {
                "user_id": user_payload["user_id"],
                "username": user_payload["username"],
                "role_id": user_payload["role_id"],
            }
        )
        refresh_token = self.create_refresh_token(
            {
                "user_id": user_payload["user_id"]
            }
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite="Lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite="Lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60, # in seconds
        )

        return {"status": "success", "token_type": "JWT"}
    
    def clear_tokens(self, response: Response) -> None:
        """
        Clear the access and refresh token cookies in the response.
        Args:
            response (Response): FastAPI Response object to clear cookies on.
        """
        response.set_cookie(key="access_token", value="", httponly=True, max_age=0)
        response.set_cookie(key="refresh_token", value="", httponly=True, max_age=0)
 
    def refresh_access_token(self, request: Request, response: Response) -> dict:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(status_code=401, detail="Missing refresh token")
            
        try:
            payload = self.decode_token(refresh_token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Get user_id from refresh token payload
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token payload")
        
        # Fetch full user data from database to include in new access token
        from api.database.user_database.user_database import user_database
        user_data = user_database.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_access_token = self.create_access_token(
            {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "role_id": user_data["role_id"]
            }
        )

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=COOKIE_SECURE,
            samesite="Lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {"message": "Token refreshed successfully"}

JWT_handler = JWTHandler()