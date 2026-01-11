"""
User model definitions.
Defines the User data models used for authentication and user management.
"""

from pydantic import BaseModel, Field, EmailStr
from api.config.config import USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH


class UserLoginRequest(BaseModel):
    """
    Data model for user login request.
    """
    username: str = Field(..., min_length=USERNAME_MIN_LENGTH, max_length=USERNAME_MAX_LENGTH)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)

class UserRegisterRequest(UserLoginRequest):
    """
    Data model for user registration request.
    """
    email: EmailStr = Field(...)

class UserChangePasswordRequest(BaseModel):
    """
    Data model for user change password request.
    """
    current_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    new_password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)