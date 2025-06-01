"""
All Routers are imported here and are exposed to the main app file
"""

from .users import router as users_router
from .packages import router as packages_router


__version__ = "v1.0.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "users_router": "Users router for handling user-related endpoints",
    "packages_router": "Packages router for handling package-related endpoints"
}


__all__ = [
    "users_router",
    "packages_router"
]
