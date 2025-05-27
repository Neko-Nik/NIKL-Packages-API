"""
All the models used in the API are defined here
"""

from .generic import All_Exceptions, Error
from .api_forms import UserRegForm


__version__ = "v1.0.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "All_Exceptions": "Class for handling wrong input exceptions",
    "Error": "Class for handling wrong input exceptions",
    "UserRegForm": "Model for user registration form"
}


__all__ = [
    "All_Exceptions",
    "Error",
    "UserRegForm"
]
