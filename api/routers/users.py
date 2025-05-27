"""
Template for creating a new router
"""

from src.utils.base.libraries import (
    BackgroundTasks,
    JSONResponse,
    APIRouter,
    Request,
    status
)
from src.database import PostgresDep
from src.main import CurrentUser


# Router
router = APIRouter()


# Add sample data in the database
@router.post("/sample-data", response_class=JSONResponse, tags=["Users"], summary="Add sample data in the database")
async def add_sample_data(request: Request, data: dict, bg_task: BackgroundTasks, user: CurrentUser, PgDB: PostgresDep) -> JSONResponse:
    """
    Add sample data in the database
    """
    pass
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"message": "Sample data added in the database"}
    )
