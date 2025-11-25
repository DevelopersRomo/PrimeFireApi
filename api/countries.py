from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import func
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.countries import Countries

router = APIRouter()

@router.get("", response_model=List[dict])
async def get_countries(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """
    Get all countries from the database
    Returns only ISO2 format countries (2 characters)
    """
    # Filter only ISO2 format countries (2 characters)
    countries = db.exec(
        select(Countries).where(
            Countries.Name.isnot(None),
            func.len(Countries.Name) == 2
        )
    ).all()

    # Convert to dict format for response
    return [
        {
            "CountryId": country.CountryId,
            "Name": country.Name
        }
        for country in countries
    ]
