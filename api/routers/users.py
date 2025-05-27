"""
User Management API Router
This module contains the API endpoints for user management, including user registration, login, security, and session management.
"""

from src.utils.base.libraries import (
    BackgroundTasks,
    JSONResponse,
    APIRouter,
    Request,
    status
)
from src.database import PostgresDep, MemcachedDep, create_new_user
from src.utils.models import UserRegForm
from src.main import CurrentUser


# Router
router = APIRouter()


# For initial version we will keep all things simple (Keep it simple stupid)

# TODO: User Management
# - Create new user (Registration) with email verification and captcha
# - Login user with username and password (not email)
# - Validate session 
# - Logout user

# - Get user profile details
# - Update user profile details
# - Delete user and all related data

# - Generate API key for user
# - Validate API key


def _hash_password(password: str) -> str:
    """
    Hash the base64 encoded password using a secure hashing algorithm
    """
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


# Create a new user
@router.post("/register", response_class=JSONResponse, tags=["Users"], summary="Create a new user")
async def create_user(request: Request, data: UserRegForm, bg_task: BackgroundTasks, PgDB: PostgresDep) -> JSONResponse:
    """
    Create a new user
    """
    # TODO: Validate hCaptcha (https://docs.hcaptcha.com/configuration)

    await create_new_user(db_session=PgDB, id=data.id, email=data.email, user_name=data.username, hashed_password=_hash_password(data.password))

    # TODO: Background task to send email verification

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully"}
    )


# Login user
@router.post("/login", response_class=JSONResponse, tags=["Users"], summary="Login user")
async def login_user(request: Request, data: dict, CacheDB: MemcachedDep, PgDB: PostgresDep) -> JSONResponse:
    """
    Login user
    """
    pass

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User logged in successfully"}
    )

    # TODO: Add cookie with session token

    return response


# Validate session
@router.get("/validate-session", response_class=JSONResponse, tags=["Users"], summary="Validate user session")
async def validate_session(user: CurrentUser) -> JSONResponse:
    """
    Validate user session
    """
    if user:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Session is valid, user is authenticated", "user": user["username"]}
        )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Session is invalid"}
    )
