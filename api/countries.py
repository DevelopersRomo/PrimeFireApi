from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.countries import Countries

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_countries(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """
    Get all countries from the database
    Returns a list of countries with their IDs and names
    """
    countries = db.exec(select(Countries)).all()

    # Convert to dict format for response
    return [
        {
            "CountryId": country.CountryId,
            "Name": country.Name
        }
        for country in countries
    ]
