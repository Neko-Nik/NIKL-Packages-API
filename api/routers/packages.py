"""
User Management API Router
This module contains the API endpoints for user management, including user registration, login, security, and session management.
"""

from src.utils.base.libraries import (
    JSONResponse,
    UploadFile,
    APIRouter,
    Request,
    status
)
from src.database import (
    PostgresDep,
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
@router.post("/versioned/upload", response_class=JSONResponse, tags=["Packages"], summary="Create a new versioned package")
async def create_new_versioned_package(request: Request, file: UploadFile, PgDB: PostgresDep) -> JSONResponse:
    """
    Create a new versioned package
    """
    # TODO: Implement the logic for creating a new versioned package
    # Accept a file upload along with X-API-Key
    # Extract the file and get the metadata
    # Parse it properly and create the versioned package
    # Store the file in the file system

    # Header of X-API-Key is expected to be present in the request
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "API key is required"}
        )
    
    # TODO: Base package is assumed to be created already (do a check)

    api_key = api_key.strip()
    user = {"id": api_key}  # Simulating user retrieval based on API key

    await create_versioned_package(
        db_session=PgDB,
        user_id=str(user["id"]),
        base_package_id="example_base_package_id",
        version="1.0.0",
        file_path="path/to/file",
        metadata={"example_key": "example_value"}
    )

    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"message": "This endpoint is not implemented yet"}
    )


# Get base package details by ID
@router.get("/base/{package_id}", response_class=JSONResponse, tags=["Packages"], summary="Get base package details by ID")
async def get_base_package_details(package_id: str, PgDB: PostgresDep) -> JSONResponse:
    """
    Get base package details by ID
    """
    # Fetch the base package details from the database
    package_details = await get_base_package_details_by_id(db_session=PgDB, package_id=package_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=package_details
    )


# Search base packages
@router.get("/base/search", response_class=JSONResponse, tags=["Packages"], summary="Search base packages")
async def search_base_packages_endpoint(query: str, PgDB: PostgresDep, page: int = 1, limit: int = 10) -> JSONResponse:
    """
    Search base packages by query
    """
    # Search for base packages in the database
    packages, total_count = await search_base_packages(db_session=PgDB, search_query=query, page=page, page_size=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"packages": packages, "total_count": total_count, "total_pages": (total_count + limit - 1) // limit}
    )


# Get versioned package details
@router.get("/versioned/{package_id}", response_class=JSONResponse, tags=["Packages"], summary="Get versioned package details by ID")
async def get_versioned_package_details_endpoint(package_id: str, PgDB: PostgresDep) -> JSONResponse:
    """
    Get versioned package details by ID
    """
    # Fetch the versioned package details from the database
    package_details = await get_versioned_package_details(db_session=PgDB, package_id=package_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=package_details
    )


# Get all versioned packages
@router.get("/versioned-all", response_class=JSONResponse, tags=["Packages"], summary="Get all versioned packages")
async def get_all_versioned_packages_endpoint(base_package_id: str, PgDB: PostgresDep, page: int = 1, limit: int = 10) -> JSONResponse:
    """
    Get all versioned packages with pagination
    """
    # Fetch all versioned packages from the database
    packages, total_count = await get_all_versioned_packages(db_session=PgDB, base_package_id=base_package_id, page=page, page_size=limit)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"packages": packages, "total_count": total_count, "total_pages": (total_count + limit - 1) // limit}
    )
