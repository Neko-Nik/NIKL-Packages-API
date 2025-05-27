"""
All the Database related functions are defined here
"""

from .connections import PostgresDep, MemcachedDep, lifespan
from .user_handler import create_new_user


__version__ = "v2.8.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "PostgresDep": "PostgresSQL connection dependency for FastAPI",
    "MemcachedDep": "Memcached connection dependency for FastAPI",
    "lifespan": "Lifespan context manager for FastAPI to manage database connections",
    "create_new_user": "Function to create a new user in the database"
}


__all__ = [
    "PostgresDep",
    "MemcachedDep",
    "lifespan",
    "create_new_user"
]
