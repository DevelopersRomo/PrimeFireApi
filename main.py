from fastapi import FastAPI
from bd.connection import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware

from api.licenses import router as licenses_router
from api.employees import router as employees_router

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
