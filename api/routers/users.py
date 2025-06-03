"""
User Management API Router
This module contains the API endpoints for user management, including user registration, login, security, and session management.
"""

from src.utils.base.libraries import (
    BackgroundTasks,
    JSONResponse,
    APIRouter,
    requests,
    Request,
    bcrypt,
    base64,
    status,
    uuid,
    json,
    logging
)
from src.database import (
    PostgresDep,
    MemcachedDep,
    create_new_user,
    get_user_by_name,
    get_user_profile_details_by_id,
    replace_user_profile_details_by_id,
    delete_user_by_id,
    create_api_key_for_user,
    list_api_keys_for_user,
    edit_api_key_details_by_id,
    delete_api_key_by_id
)
from src.utils.base.constants import MAX_AGE_OF_CACHE, HCAPTCHA_SECRET_KEY
from src.utils.models import UserRegForm, UserLoginForm, ApiKeyForm
from src.main import CurrentUser


# Router
router = APIRouter()


def _verify_hcaptcha(remoteip: str, token: str) -> bool:
    """
    Verify hCaptcha token
    This function should implement the logic to verify the hCaptcha token with the hCaptcha service.
    For now, it returns True for demonstration purposes.
    """
    try:
        response = requests.post(
            url="https://hcaptcha.com/siteverify",
            data={
                "secret": HCAPTCHA_SECRET_KEY,
                "remoteip": remoteip,
                "response": token
            }
        )
        response_data = response.json()
        if response.status_code != 200:
            logging.error(f"hCaptcha verification failed with status code: {response.status_code}")
            return False

        return dict(response_data).get("success", False)

    except Exception as e:
        logging.error(f"Error verifying hCaptcha: {e}", exc_info=True)
        return False


def _hash_password(password: str) -> str:
    """
    Hash the base64 encoded password using a secure hashing algorithm
    """
    if not password:
        raise ValueError("Password cannot be empty")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters")
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    if not password.isprintable():
        raise ValueError("Password must be a printable string")
    if not password.isascii():
        raise ValueError("Password must be an ASCII string")

    # Convert password from Base64 to bytes
    password_bytes = base64.b64decode(s=password)

    return bcrypt.hashpw(password=password_bytes, salt=bcrypt.gensalt()).decode("utf-8")


# Create a new user
@router.post("/register", response_class=JSONResponse, tags=["Users", "Auth"], summary="Create a new user")
async def create_user(request: Request, data: UserRegForm, bg_task: BackgroundTasks, PgDB: PostgresDep) -> JSONResponse:
    """
    Create a new user
    """
    # Verify hCaptcha
    if not _verify_hcaptcha(remoteip=request.client.host, token=data.hcaptcha_token):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Invalid hCaptcha token"}
        )

    await create_new_user(
        db_session=PgDB,
        id=str(uuid.uuid4()),
        email=data.email.lower(),
        user_name=data.user_name,
        hashed_password=_hash_password(data.password),
        profile_data={
            "full_name": data.full_name
        }
    )

    # TODO: Background task to send email verification

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "User created successfully, please check your email for verification instructions"}
    )


# Login user
@router.post("/login", response_class=JSONResponse, tags=["Users", "Auth"], summary="Login user")
async def login_user(request: Request, data: UserLoginForm, CacheDB: MemcachedDep, PgDB: PostgresDep) -> JSONResponse:
    """
    Login user
    """
    # # Verify hCaptcha
    # if not _verify_hcaptcha(remoteip=request.client.host, token=data.hcaptcha_token):
    #     return JSONResponse(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         content={"message": "Invalid hCaptcha token"}
    #     )

    # Fetch user from database
    user = await get_user_by_name(db_session=PgDB, user_name=data.user_name)

    # Check if user is active
    if not user["is_active"]:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "User account is inactive"}
        )

    # Verify password
    if not bcrypt.checkpw(password=base64.b64decode(data.password), hashed_password=user["hashed_password"].encode("utf-8")):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid username or password"}
        )

    # Create a new session ID and CSRF token
    session_id, csrf_token = str(uuid.uuid4()), str(uuid.uuid4())

    # Store user session in cache
    await CacheDB.set(
        key=session_id.encode("utf-8"),
        value=json.dumps({
            "id": str(user["id"]),
            "user_name": user["user_name"],
            "email": user["email"],
            "csrf_token": csrf_token,
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat()  # Store created_at as ISO format string
        }).encode("utf-8"),
        exptime=600  # Set session expiration time (10 minutes)
    )

    # Set the session ID and CSRF token in the response cookies
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"User {user['profile_data']['full_name']} logged in successfully", "user": user["user_name"], "profile_data": user["profile_data"]}
    )

    response.set_cookie(
        key="SESSION_ID",
        value=session_id,
        max_age=MAX_AGE_OF_CACHE,
        httponly=True,
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )

    # Set the logged in status in the Cookie (for JS - to read)
    response.set_cookie(
        key="IS_SESSION_VALID",
        value="true",
        max_age=MAX_AGE_OF_CACHE,
        httponly=False,  # IMPORTANT: Let JS read it
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )

    # Set the CSRF token in the response header
    response.headers["X-CSRF-Token"] = csrf_token
    response.headers["X-Session-Expiry"] = str(MAX_AGE_OF_CACHE)
    # Allow Token and Expiry to be read by JS
    response.headers["Access-Control-Expose-Headers"] = "X-CSRF-Token, X-Session-Expiry"

    return response


# Validate session
@router.get("/validate-session", response_class=JSONResponse, tags=["Users", "Auth"], summary="Validate user session")
async def validate_session(user: CurrentUser) -> JSONResponse:
    """
    Validate user session
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Session is valid, user is authenticated",
            "user_name": user["user_name"]
        }
    )


# Logout user
@router.delete("/logout", response_class=JSONResponse, tags=["Users", "Auth"], summary="Logout user")
async def logout_user(user: CurrentUser, CacheDB: MemcachedDep) -> JSONResponse:
    """
    Logout user
    """
    # Invalidate the session by deleting it from the cache
    await CacheDB.delete(key=str(user["id"]).encode("utf-8"))

    # Clear cookies in the response
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Logout successful, session destroyed"}
    )

    response.delete_cookie(
        key="SESSION_ID",
        httponly=True,
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )
    response.delete_cookie(
        key="IS_SESSION_VALID",
        httponly=False,
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )

    return response


# Get user profile details
@router.get("/profile", response_class=JSONResponse, tags=["Users", "Profile"], summary="Get user profile details")
async def get_user_profile_details(user: CurrentUser, PgDB: PostgresDep) -> JSONResponse:
    """
    Get user profile details
    """
    # Fetch user profile details from the database
    profile_data = await get_user_profile_details_by_id(db_session=PgDB, user_id=str(user["id"]))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "User profile details retrieved successfully",
            "user_name": user["user_name"],
            "email": user["email"],
            "profile_data": profile_data
        }
    )


# Update user profile details
@router.put("/profile", response_class=JSONResponse, tags=["Users", "Profile"], summary="Update user profile details")
async def update_user_profile_details(user: CurrentUser, data: dict) -> JSONResponse:
    """
    Update user profile details
    """
    # Replace user profile details in the database
    await replace_user_profile_details_by_id(db_session=PostgresDep(), user_id=str(user["id"]), profile_data=data)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "User profile details updated successfully",
            "profile_data": data
        }
    )


# Delete user account
@router.delete("/self", response_class=JSONResponse, tags=["Users", "Auth"], summary="Delete user account")
async def delete_user_account(user: CurrentUser, CacheDB: MemcachedDep, PgDB: PostgresDep) -> JSONResponse:
    """
    Delete user account
    """
    # Delete user from the database
    await delete_user_by_id(db_session=PgDB, user_id=str(user["id"]))

    # Invalidate the session by deleting it from the cache
    await CacheDB.delete(key=str(user["id"]).encode("utf-8"))

    # Clear cookies in the response
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "User account deleted successfully"}
    )

    response.delete_cookie(
        key="SESSION_ID",
        httponly=True,
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )
    response.delete_cookie(
        key="IS_SESSION_VALID",
        httponly=False,
        secure=True,
        samesite="strict",
        # domain=".nekonik.com"
    )

    return response


# List API keys for user
@router.get("/api-keys", response_class=JSONResponse, tags=["Users", "API Keys"], summary="List API keys for user")
async def list_api_keys_for_user_paginated(user: CurrentUser, PgDB: PostgresDep, page: int = 1, limit: int = 10) -> JSONResponse:
    """
    List API keys for user with pagination
    """
    api_keys = await list_api_keys_for_user(db_session=PgDB, user_id=str(user["id"]), page=page, limit=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "API keys retrieved successfully",
            "api_keys": api_keys
        }
    )


# Create a new API key for user
@router.post("/api-keys", response_class=JSONResponse, tags=["Users", "API Keys"], summary="Create a new API key for user")
async def create_api_key_for_user(user: CurrentUser, data: ApiKeyForm, PgDB: PostgresDep) -> JSONResponse:
    """
    Create a new API key for user
    """
    # Generate a new API key ID
    api_key_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())
    details = {
        "name": data.api_key_name,
        "description": data.api_key_description
    }

    # Create a new API key for the user in the database
    await create_api_key_for_user(
        db_session=PgDB,
        user_id=str(user["id"]),
        api_key_id=api_key_id,
        api_key=api_key,
        details=details
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "API key created successfully, please store it securely. It will not be shown again.",
            "api_key_id": api_key_id,
            "api_key": api_key,
            "details": details
        }
    )


# Edit API key details
@router.put("/api-keys/{api_key_id}", response_class=JSONResponse, tags=["Users", "API Keys"], summary="Edit API key details")
async def replace_api_key_details(user: CurrentUser, api_key_id: str, data: ApiKeyForm, PgDB: PostgresDep) -> JSONResponse:
    """
    Edit API key details
    """
    # Update API key details in the database
    await edit_api_key_details_by_id(
        db_session=PgDB,
        user_id=str(user["id"]),
        api_key_id=api_key_id,
        new_details={
            "name": data.api_key_name,
            "description": data.api_key_description
        }
    )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "API key details updated successfully",
            "api_key_id": api_key_id,
            "details": {
                "name": data.api_key_name,
                "description": data.api_key_description
            }
        }
    )


# Delete API key
@router.delete("/api-keys/{api_key_id}", response_class=JSONResponse, tags=["Users", "API Keys"], summary="Delete API key")
async def delete_api_key(user: CurrentUser, api_key_id: str, PgDB: PostgresDep) -> JSONResponse:
    """
    Delete API key
    """
    # Delete API key from the database
    await delete_api_key_by_id(db_session=PgDB, user_id=str(user["id"]), api_key_id=api_key_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "API key deleted successfully",
            "api_key_id": api_key_id
        }
    )
