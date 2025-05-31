"""
This is the main app file which contains all the endpoints of the API
This file is used to run the API
"""

from src.utils.base.libraries import (
    CORSMiddleware,
    JSONResponse,
    FastAPI,
    Request
)
from .routers import users_router
from src.utils.models import All_Exceptions
from src.database import lifespan


# Initialization
app = FastAPI(
    title="Nik-Lang Package Management API",
    description="This is the API for the Nik-Lang Package Management System",
    version="1.0.0",
    # docs_url=None,
    # redoc_url=None,
    docs_url="/docs",
    redoc_url="/redoc",
    include_in_schema=True,
    lifespan=lifespan
)

# Add CROCS middle ware to allow cross origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nikl-pkg.nekonik.com", "http://localhost:3000", "https://api.nikl-pkg.nekonik.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Exception handler for wrong input
@app.exception_handler(All_Exceptions)
async def input_data_exception_handler(request: Request, exc: All_Exceptions):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": f"Oops! {exc.message}"}
    )


#    Endpoints    #
app.include_router(router=users_router, prefix="/users")
