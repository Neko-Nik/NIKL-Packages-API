"""
All the Database related functions are defined here
"""

from .connections import PostgresDep, MemcachedDep, lifespan


__version__ = "v2.8.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "PostgresDep": "PostgresSQL connection dependency for FastAPI",
    "MemcachedDep": "Memcached connection dependency for FastAPI",
    "lifespan": "Lifespan context manager for FastAPI to manage database connections"
}


__all__ = [
    "PostgresDep",
    "MemcachedDep",
    "lifespan"
]
