"""
User Management API Router
This module contains the API endpoints for user management, including user registration, login, security, and session management.
"""

from src.utils.base.libraries import (
    JSONResponse,
    APIRouter,
    status
)
from src.database import (
    PostgresDep,
    MemcachedDep,
    create_base_package,
    get_base_package_details_by_id,
    search_base_packages,
    create_versioned_package,
    get_versioned_package_details,
    get_all_versioned_packages
)
from src.utils.models import BasePackageForm
from src.main import CurrentUser


# Router
router = APIRouter()


# Create a new base package
@router.post("/base", response_class=JSONResponse, tags=["Packages"], summary="Create a new base package")
async def create_new_base_package(data: BasePackageForm, user: CurrentUser, PgDB: PostgresDep) -> JSONResponse:
    """
    Create a new base package
    """
    # Validate package name and description
    if not data.get("package_name") or len(data["package_name"]) < 4:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Package name must be at least 4 characters long."}
        )

    if not data.get("package_description") or len(data["package_description"]) < 21:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Package description must be at least 21 characters long."}
        )

    # Create the base package in the database
    await create_base_package(
        db_session=PgDB,
        user_id=str(user["id"]),
        package_name=data["package_name"],
        package_description=data["package_description"],
        metadata=data.get("metadata", {})
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Base package created successfully"}
    )
