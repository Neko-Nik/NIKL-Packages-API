"""
This module contains the API form models used for all endpoints
"""

from src.utils.base.libraries import BaseModel, Field


class UserRegForm(BaseModel):
    """
    User Registration Form model
    This model is used to validate the user registration form data
    user_name: Username of the user
    email: Email of the user
    base64_password: Base64 encoded password of the user
    """
    user_name: str = Field(..., title="Username", description="Username of the user")
    email: str = Field(..., title="Email", description="Email of the user")
    password: str = Field(..., title="Password", description="Base64 encoded password of the user")
    full_name: str = Field(..., title="Full Name", description="Full name of the user")

    class Config:
        """
        Configuration for the model
        """
        json_schema_extra = {
            "example": {
                "user_name": "niklang",
                "email": "nik@nekonik.com",
                "password": "TmVrbw=="  # base64 encoded password
            }
        }
