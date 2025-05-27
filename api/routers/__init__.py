"""
All Routers are imported here and are exposed to the main app file
"""

from .neko import router as neko_router


__version__ = "v1.0.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "neko_router": "Neko of API"
}


__all__ = [
    "neko_router"
]
