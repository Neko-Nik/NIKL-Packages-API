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
