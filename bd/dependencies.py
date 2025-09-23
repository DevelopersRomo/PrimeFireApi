from sqlmodel import Session
from bd.connection import SessionLocal

# Dependency function to get DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
