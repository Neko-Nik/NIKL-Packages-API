"""
Handler for package-related database operations
"""

from src.utils.base.libraries import aiomcache, asyncpg, TypeAlias, logging, status, json, uuid
from src.utils.models import All_Exceptions


PgSession: TypeAlias = asyncpg.Connection
MemCacheSession: TypeAlias = aiomcache.Client


async def create_base_package(db_session: PgSession, user_id: str, package_name: str, package_description: str, metadata: dict) -> None:
    """
    Create a new base package in the database
    """
    # Check if package name is properly formatted
    if not package_name or len(package_name) < 4:
        raise All_Exceptions(
            message="Package name must be at least 4 characters long.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    if not package_description or len(package_description) < 21:
        raise All_Exceptions(
            message="Package description must be at least 21 characters long.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    try:
        await db_session.execute(
            "INSERT INTO base_packages (id, package_name, package_description, user_id, metadata) "
            "VALUES ($1, $2, $3, $4, $5)",
            str(uuid.uuid4()),
            package_name,
            package_description,
            user_id,
            json.dumps(metadata)
        )
    except Exception as e:
        logging.error(f"Error creating base package: {e}", exc_info=True)
        raise All_Exceptions(
            message="Failed to create base package.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


async def get_base_package_details_by_id(db_session: PgSession, package_id: str) -> dict:
    """
    Get base package details by ID from the database
    """
    package_row = await db_session.fetchrow(
        "SELECT * FROM base_packages WHERE id = $1",
        package_id
    )

    if not package_row:
        raise All_Exceptions(
            message=f"Base package with ID {package_id} does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return {
        "id": package_row["id"],
        "package_name": package_row["package_name"],
        "package_description": package_row["package_description"],
        "registered_at": package_row["registered_at"],
        "metadata": json.loads(package_row["metadata"]),
        "user_id": package_row["user_id"]
    }


async def search_base_packages(db_session: PgSession, search_query: str, page: int = 1, page_size: int = 10) -> tuple[list, int]:
    """
    Search for base packages by name or description
    """
    offset = (page - 1) * page_size

    if search_query:
        if len(search_query) < 3:
            raise All_Exceptions(
                message="Search query must be at least 3 characters long.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        search_pattern = f"%{search_query}%"
        packages = await db_session.fetch(
            "SELECT * FROM base_packages WHERE package_name ILIKE $1 OR package_description ILIKE $1 "
            "ORDER BY registered_at DESC LIMIT $2 OFFSET $3",
            search_pattern,
            page_size,
            offset
        )
        total_count_row = await db_session.fetchrow(
            "SELECT COUNT(*) FROM base_packages WHERE package_name ILIKE $1 OR package_description ILIKE $1",
            search_pattern
        )
        total_count = total_count_row["count"]
        if total_count is None:
            total_count = 0

    else:
        # If no search query is provided, return all packages
        packages = await db_session.fetch(
            "SELECT * FROM base_packages ORDER BY registered_at DESC LIMIT $1 OFFSET $2",
            page_size,
            offset
        )
        total_count_row = await db_session.fetchrow(
            "SELECT COUNT(*) FROM base_packages"
        )
        total_count = total_count_row["count"]
        if total_count is None:
            total_count = 0

    return [
        {
            "id": row["id"],
            "package_name": row["package_name"],
            "package_description": row["package_description"],
            "registered_at": row["registered_at"],
            "latest_version": row["latest_version_id"]
        } for row in packages
    ], total_count


async def create_versioned_package(db_session: PgSession, user_id: str, base_package_id: str, version: str, file_path: str, metadata: dict) -> None:
    """
    Create a new versioned package in the database
    """
    # Check if base package exists and belongs to the user
    base_package = await db_session.fetchrow(
        "SELECT id FROM base_packages WHERE id = $1 AND user_id = $2",
        base_package_id,
        user_id
    )
    if not base_package:
        raise All_Exceptions(
            message=f"Base package with ID {base_package_id} does not exist or does not belong to user {user_id}.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    try:
        await db_session.execute(
            "INSERT INTO versioned_packages (id, base_package_id, version, file_path, metadata) "
            "VALUES ($1, $2, $3, $4, $5)",
            str(uuid.uuid4()),
            base_package_id,
            version,
            file_path,
            json.dumps(metadata)
        )
    except Exception as e:
        logging.error(f"Error creating versioned package: {e}", exc_info=True)
        raise All_Exceptions(
            message="Failed to create versioned package.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


async def get_versioned_package_details(db_session: PgSession, package_id: str) -> dict:
    """
    Get versioned package details by ID from the database
    """
    package_row = await db_session.fetchrow(
        "SELECT * FROM versioned_packages WHERE id = $1",
        package_id
    )

    if not package_row:
        raise All_Exceptions(
            message=f"Versioned package with ID {package_id} does not exist.",
            status_code=status.HTTP_404_NOT_FOUND
        )

    return {
        "id": package_row["id"],
        "base_package_id": package_row["base_package_id"],
        "version": package_row["version"],
        "file_path": package_row["file_path"],
        "metadata": json.loads(package_row["metadata"]),
        "created_at": package_row["created_at"]
    }


async def get_all_versioned_packages(db_session: PgSession, base_package_id: str, page: int = 1, page_size: int = 10) -> list:
    """
    Get all versioned packages for a base package
    """
    offset = (page - 1) * page_size

    packages = await db_session.fetch(
        "SELECT * FROM versioned_packages WHERE base_package_id = $1 "
        "ORDER BY created_at DESC LIMIT $2 OFFSET $3",
        base_package_id,
        page_size,
        offset
    )

    return [
        {
            "id": row["id"],
            "base_package_id": row["base_package_id"],
            "version": row["version"],
            "file_path": row["file_path"],
            "metadata": json.loads(row["metadata"]),
            "created_at": row["created_at"]
        } for row in packages
    ]
