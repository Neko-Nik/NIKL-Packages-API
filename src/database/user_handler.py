"""
Handler for user-related database operations
"""

from src.utils.base.libraries import aiomcache, asyncpg, TypeAlias, logging, status, json
from src.utils.models import All_Exceptions


PgSession: TypeAlias = asyncpg.Connection
MemCacheSession: TypeAlias = aiomcache.Client


async def _raise_check_user_exists(db_session: PgSession, user_name: str, user_email: str, raise_exception_if_exists: bool = False) -> None:
    """
    Check if the user already exists in the database
    """
    user_name_row = await db_session.fetchrow(
        "SELECT id FROM users WHERE user_name = $1",
        user_name
    )
    user_email_row = await db_session.fetchrow(
        "SELECT id FROM users WHERE email = $1",
        user_email
    )
    if user_name_row:
        # If user with the same username exists
        if raise_exception_if_exists:
            raise All_Exceptions(
                message=f"User with username {user_name} already exists.",
                status_code=status.HTTP_409_CONFLICT
            )

        # If user with the same username does not exist
        else:
            raise All_Exceptions(
                message=f"User with username {user_name} does not exist.",
                status_code=status.HTTP_404_NOT_FOUND
            )

    if user_email_row:
        # If user with the same email exists
        if raise_exception_if_exists:
            raise All_Exceptions(
                message=f"User with email {user_email} already exists.",
                status_code=status.HTTP_409_CONFLICT
            )

        # If user with the same email does not exist
        else:
            raise All_Exceptions(
                message=f"User with email {user_email} does not exist.",
                status_code=status.HTTP_404_NOT_FOUND
            )


async def create_new_user(db_session: PgSession, id: str, email: str, user_name: str, hashed_password: str, profile_data: dict) -> None:
    """
    Create a new user in the database
    """
    await _raise_check_user_exists(
        db_session=db_session,
        user_name=user_name,
        user_email=email,
        raise_exception_if_exists=True
    )

    try:
        await db_session.execute(
            "INSERT INTO users (id, user_name, email, hashed_password, profile_data) "
            "VALUES ($1, $2, $3, $4, $5)",
            id, user_name, email, hashed_password, json.dumps(profile_data)
        )

    except Exception as e:
        logging.error(f"Error while creating new user: {e}")
        raise All_Exceptions(
            message=f"Error while creating new user, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def get_user_by_name(db_session: PgSession, user_name: str) -> dict:
    """
    Get user by ID from the database
    """
    user_row = await db_session.fetchrow(
        "SELECT * FROM users WHERE user_name = $1",
        user_name
    )

    if not user_row:
        raise All_Exceptions(
            message=f"User with username {user_name} does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return {
        "id": user_row["id"],
        "user_name": user_row["user_name"],
        "email": user_row["email"],
        "hashed_password": user_row["hashed_password"],
        "profile_data": json.loads(user_row["profile_data"]),
        "is_active": user_row["is_active"],
        "created_at": user_row["created_at"]
    }


async def get_user_profile_details_by_id(db_session: PgSession, user_id: str) -> dict:
    """
    Get user profile details by ID from the database
    """
    user_row = await db_session.fetchrow(
        "SELECT profile_data FROM users WHERE id = $1",
        user_id
    )
    if not user_row:
        raise All_Exceptions(
            message=f"User with ID {user_id} does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return json.loads(user_row["profile_data"])


async def replace_user_profile_details_by_id(db_session: PgSession, user_id: str, profile_data: dict) -> None:
    """
    Replace user profile details by ID in the database
    """
    try:
        await db_session.execute(
            "UPDATE users SET profile_data = $1 WHERE id = $2",
            json.dumps(profile_data), user_id
        )
    except Exception as e:
        logging.error(f"Error while updating user profile details: {e}")
        raise All_Exceptions(
            message=f"Error while updating user profile details, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def delete_user_by_id(db_session: PgSession, user_id: str) -> None:
    """
    Delete user by ID from the database
    """
    try:
        await db_session.execute(
            "DELETE FROM users WHERE id = $1",
            user_id
        )
    except Exception as e:
        logging.error(f"Error while deleting user: {e}")
        raise All_Exceptions(
            message=f"Error while deleting user, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def create_api_key_for_user(db_session: PgSession, user_id: str, api_key_id: str, api_key: str, details: dict) -> None:
    """
    Create a new API key for a user in the database
    """
    try:
        await db_session.execute(
            "INSERT INTO api_keys (id, user_id, api_key, details) "
            "VALUES ($1, $2, $3, $4)",
            api_key_id, user_id, api_key, json.dumps(details)
        )

    except Exception as e:
        logging.error(f"Error while creating API key for user: {e}")
        raise All_Exceptions(
            message=f"Error while creating API key for user, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def list_api_keys_for_user(db_session: PgSession, user_id: str, page: int = 1, page_size: int = 10) -> list:
    """
    List API keys for a user from the database
    """
    offset = (page - 1) * page_size
    api_keys_rows = await db_session.fetch(
        "SELECT * FROM api_keys WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
        user_id, page_size, offset
    )
    if not api_keys_rows:
        raise All_Exceptions(
            message=f"No API keys found for user with ID {user_id}.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "api_key": row["api_key"][:4] + "****" + row["api_key"][-4:],
            "details": json.loads(row["details"]),
            "created_at": row["created_at"]
        } for row in api_keys_rows
    ]


async def edit_api_key_details_by_id(db_session: PgSession, api_key_id: str, user_id: str, new_details: dict) -> None:
    """
    Edit API key details by ID in the database
    """
    try:
        await db_session.execute(
            "UPDATE api_keys SET details = $1 WHERE id = $2 AND user_id = $3",
            json.dumps(new_details), api_key_id, user_id
        )
    except Exception as e:
        logging.error(f"Error while editing API key details: {e}")
        raise All_Exceptions(
            message=f"Error while editing API key details, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def delete_api_key_by_id(db_session: PgSession, api_key_id: str, user_id: str) -> None:
    """
    Delete API key by ID from the database
    """
    try:
        await db_session.execute(
            "DELETE FROM api_keys WHERE id = $1 AND user_id = $2",
            api_key_id, user_id
        )
    except Exception as e:
        logging.error(f"Error while deleting API key: {e}")
        raise All_Exceptions(
            message=f"Error while deleting API key, please contact support",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def get_api_key_details(db_session: PgSession, api_key: str) -> dict:
    """
    Get API key details from the database (Auth Middleware) [Internal Use Only]
    """
    api_key_row = await db_session.fetchrow(
        "SELECT * FROM api_keys WHERE api_key = $1",
        api_key
    )

    if not api_key_row:
        raise All_Exceptions(
            message=f"API key does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return {
        "id": api_key_row["id"],
        "user_id": api_key_row["user_id"],
        "api_key": api_key_row["api_key"],
        "details": json.loads(api_key_row["details"]),
        "created_at": api_key_row["created_at"]
    }
