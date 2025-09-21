from sqlmodel import Session
from bd.connection import SessionLocal

# Función de dependencia para obtener DB session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
