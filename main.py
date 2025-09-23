from fastapi import FastAPI
from bd.connection import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

from api.licenses import router as licenses_router
from api.employees import router as employees_router
from api.jobs import router as jobs_router
from api.curriculums import router as curriculums_router

# Create tables
create_db_and_tables()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(licenses_router, prefix="/licenses", tags=["licenses"])
app.include_router(employees_router, prefix="/employees", tags=["employees"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(curriculums_router, prefix="/curriculums", tags=["curriculums"])
