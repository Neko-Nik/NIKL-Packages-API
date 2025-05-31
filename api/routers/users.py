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
from src.database import PostgresDep, MemcachedDep, create_new_user, get_user_by_name
from src.utils.base.constants import MAX_AGE_OF_CACHE, HCAPTCHA_SECRET_KEY
from src.utils.models import UserRegForm, UserLoginForm
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
@router.post("/register", response_class=JSONResponse, tags=["Users"], summary="Create a new user")
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
        email=data.email,
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
@router.post("/login", response_class=JSONResponse, tags=["Users"], summary="Login user")
async def login_user(request: Request, data: UserLoginForm, CacheDB: MemcachedDep, PgDB: PostgresDep) -> JSONResponse:
    """
    Login user
    """
    # Verify hCaptcha
    if not _verify_hcaptcha(remoteip=request.client.host, token=data.hcaptcha_token):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Invalid hCaptcha token"}
        )

    # Fetch user from database
    user = await get_user_by_name(db_session=PgDB, user_name=data.user_name)
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "User not found"}
        )

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
            "profile_data": user["profile_data"],
            "csrf_token": csrf_token,
            "is_active": user["is_active"],
            "created_at": user["created_at"].isoformat()  # Store created_at as ISO format string
            
        }).encode("utf-8"),
        exptime=600  # Set session expiration time (10 minutes)
    )

    # Set the session ID and CSRF token in the response cookies
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"User {user['profile_data']['full_name']} logged in successfully", "user": user["user_name"]}
    )

    response.set_cookie(
        key="SESSION_ID",
        value=session_id,
        max_age=MAX_AGE_OF_CACHE,
        httponly=True,
        secure=True,
        samesite="strict",
        domain=".nekonik.com"
    )

    # Set the logged in status in the Cookie (for JS - to read)
    response.set_cookie(
        key="IS_SESSION_VALID",
        value="true",
        max_age=MAX_AGE_OF_CACHE,
        httponly=False,  # IMPORTANT: Let JS read it
        secure=True,
        samesite="strict",
        domain=".nekonik.com"
    )

    # Set the CSRF token in the response header
    response.headers["X-CSRF-Token"] = csrf_token
    response.headers["X-Session-Expiry"] = str(MAX_AGE_OF_CACHE)
    # Allow Token and Expiry to be read by JS
    response.headers["Access-Control-Expose-Headers"] = "X-CSRF-Token, X-Session-Expiry"

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
            content={"message": "Session is valid, user is authenticated", "user_name": user["user_name"], "profile_data": user["profile_data"]}
        )

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Session is invalid"}
    )




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
