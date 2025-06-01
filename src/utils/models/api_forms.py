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
    hcaptcha_token: str = Field(..., title="hCaptcha Token", description="hCaptcha token for verification")

    class Config:
        """
        Configuration for the model
        """
        json_schema_extra = {
            "example": {
                "user_name": "niklang",
                "email": "admin@nekonik.com",
                "password": "Base64-Encoded-Password",
                "full_name": "Neko Nik",
                "hcaptcha_token": "hCaptcha-Token"
            }
        }


class UserLoginForm(BaseModel):
    """
    User Login Form model
    This model is used to validate the user login form data
    user_name: Username of the user
    base64_password: Base64 encoded password of the user
    """
    user_name: str = Field(..., title="Username", description="Username of the user")
    password: str = Field(..., title="Password", description="Base64 encoded password of the user")
    hcaptcha_token: str = Field(..., title="hCaptcha Token", description="hCaptcha token for verification")

    class Config:
        """
        Configuration for the model
        """
        json_schema_extra = {
            "example": {
                "user_name": "niklang",
                "password": "Base64-Encoded-Password",
                "hcaptcha_token": "hCaptcha-Token"
            }
        }


class ApiKeyForm(BaseModel):
    """
    API Key Form model
    This model is used to validate the API key form data
    api_key_id: Unique identifier for the API key
    api_key_name: Name of the API key
    api_key_description: Description of the API key
    """
    api_key_id: str = Field("", title="API Key ID", description="Unique identifier for the API key")
    api_key_name: str = Field(..., title="API Key Name", description="Name of the API key")
    api_key_description: str = Field(..., title="API Key Description", description="Description of the API key")

    class Config:
        """
        Configuration for the model
        """
        json_schema_extra = {
            "example": {
                "api_key_name": "My API Key",
                "api_key_description": "This is my API key for accessing the API"
            }
        }


class BasePackageForm(BaseModel):
    """
    Base Package Form model
    This model is used to validate the base package form data
    package_name: Name of the base package
    package_description: Description of the base package
    metadata: Additional metadata for the base package
    """
    package_name: str = Field(..., title="Package Name", description="Name of the base package")
    package_description: str = Field(..., title="Package Description", description="Description of the base package")
    metadata: dict = Field(..., title="Metadata", description="Additional metadata for the base package")

    class Config:
        """
        Configuration for the model
        """
        json_schema_extra = {
            "example": {
                "package_name": "My Base Package",
                "package_description": "This is my base package",
                "metadata": {
                    "website": "https://NekoNik.com",
                    "repository": "https://github.com/Neko-Nik"
                }
            }
        }
