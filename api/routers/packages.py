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
    # Create the base package in the database
    await create_base_package(
        db_session=PgDB,
        user_id=str(user["id"]),
        package_name=data.package_name,
        package_description=data.package_description,
        metadata=data.metadata
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"message": "Base package created successfully"}
    )


# Create a new versioned package
@router.post("/versioned", response_class=JSONResponse, tags=["Packages"], summary="Create a new versioned package")
async def create_new_versioned_package() -> JSONResponse:
    """
    Create a new versioned package
    """
    # TODO: Implement the logic for creating a new versioned package
    # Accept a file upload along with X-API-Key
    # Extract the file and get the metadata
    # Parse it properly and create the versioned package
    # Store the file in the file system
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"message": "This endpoint is not implemented yet"}
    )
