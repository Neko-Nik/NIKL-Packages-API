"""
Basic functions required for the project are defined here
"""

from .utils.base.libraries import json, Request, status, Annotated, Depends
from .utils.models import All_Exceptions
from .database import MemcachedDep


async def get_current_user_session_details(request: Request, CacheDB: MemcachedDep) -> dict:
    """
    Get current user session details from the cache
    """
    session_id = request.cookies.get("SESSION_ID")
    if not session_id:
        raise All_Exceptions(message="Session ID not found", status_code=status.HTTP_406_NOT_ACCEPTABLE)

    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token:
        raise All_Exceptions(message="CSRF token not found", status_code=status.HTTP_406_NOT_ACCEPTABLE)

    user_data_bytes = await CacheDB.get(session_id.encode("utf-8"))
    if not user_data_bytes:
        raise All_Exceptions(message="Session expired", status_code=status.HTTP_401_UNAUTHORIZED)

    user_data = json.loads(user_data_bytes.decode("utf-8"))

    if user_data["csrf_token"] != csrf_token:
        raise All_Exceptions(message="CSRF token mismatch", status_code=status.HTTP_401_UNAUTHORIZED)

    return user_data


CurrentUser = Annotated[dict, Depends(get_current_user_session_details)]
