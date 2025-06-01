"""
All the Database related functions are defined here
"""

from .connections import PostgresDep, MemcachedDep, lifespan
from .user_handler import (
    create_new_user,
    get_user_by_name,
    get_user_profile_details_by_id,
    replace_user_profile_details_by_id,
    delete_user_by_id,
    create_api_key_for_user,
    list_api_keys_for_user,
    edit_api_key_details_by_id,
    delete_api_key_by_id,
    get_api_key_details
)


__version__ = "v2.8.0-phoenix-release"


__annotations__ = {
    "version": __version__,
    "PostgresDep": "PostgresSQL connection dependency for FastAPI",
    "MemcachedDep": "Memcached connection dependency for FastAPI",
    "lifespan": "Lifespan context manager for FastAPI to manage database connections",
    "create_new_user": "Function to create a new user in the database",
    "get_user_by_name": "Function to get user details by user name",
    "get_user_profile_details_by_id": "Function to get user profile details by user ID",
    "replace_user_profile_details_by_id": "Function to replace user profile details by user ID",
    "delete_user_by_id": "Function to delete user by user ID",
    "create_api_key_for_user": "Function to create a new API key for a user",
    "list_api_keys_for_user": "Function to list all API keys for a user",
    "edit_api_key_details_by_id": "Function to edit API key details by API key ID",
    "delete_api_key_by_id": "Function to delete an API key by API key ID",
    "get_api_key_details": "Function to get API key details by API key ID"
}


__all__ = [
    "PostgresDep",
    "MemcachedDep",
    "lifespan",
    "create_new_user",
    "get_user_by_name",
    "get_user_profile_details_by_id",
    "replace_user_profile_details_by_id",
    "delete_user_by_id",
    "create_api_key_for_user",
    "list_api_keys_for_user",
    "edit_api_key_details_by_id",
    "delete_api_key_by_id",
    "get_api_key_details"
]
