"""
All Routers are imported here and are exposed to the main app file
"""

from .users import router as users_router


__version__ = "v1.0.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "users_router": "Users router for handling user-related endpoints"
}


__all__ = [
    "users_router"
]
