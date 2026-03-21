from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.countries import Countries

router = APIRouter()


@router.get("", response_model=list[dict])
async def get_countries(db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    """
    Get all countries from the database
    Returns only ISO2 format countries (2 characters).
    """
    # Get all countries and filter in Python for SQLite compatibility
    all_countries = db.exec(select(Countries).where(Countries.name.isnot(None))).all()

    # Filter only 2-character ISO codes
    countries = [c for c in all_countries if c.name and len(c.name) == 2]

    # Convert to dict format for response
    return [{"country_id": country.country_id, "name": country.name} for country in countries]
