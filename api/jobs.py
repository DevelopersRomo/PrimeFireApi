from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlmodel import Session, select

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.countries import Countries
from models.jobs import Jobs
from schemas.jobs import Job, JobCreate, JobUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


def job_to_schema(db_job: Jobs, db: Session) -> Job:
    """Convert database Job model to response schema with Country ISO2."""
    country_iso2 = None
    if db_job.country_id:
        country = db.exec(select(Countries).where(Countries.country_id == db_job.country_id)).first()
        if country:
            country_iso2 = country.name

    return Job(
        job_id=db_job.job_id,
        title=db_job.title,
        description=db_job.description,
        requirements=db_job.requirements,
        location=db_job.location,
        salary_min=db_job.salary_min,
        salary_max=db_job.salary_max,
        status=db_job.status,
        posted_at=db_job.posted_at,
        employee_id=db_job.employee_id,
        country=country_iso2,
    )


# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=Job)
def create_job(job: JobCreate, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    # Resolve Country ISO2 to CountryId if provided
    country_id = None
    if job.country:
        country = db.exec(select(Countries).where(Countries.name == job.country.upper())).first()
        if not country:
            raise HTTPException(status_code=404, detail=f"Country with ISO2 code '{job.country}' not found")
        country_id = country.country_id

    # Create job data without Country field
    job_data = job.model_dump(exclude={"country"})
    job_data["country_id"] = country_id

    db_job = Jobs(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return job_to_schema(db_job, db)


# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=list[Job] | PaginatedResponse[Job])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=1000),
    with_meta: bool = Query(False),
    db: Session = Depends(get_db),
):
    jobs = db.exec(select(Jobs).order_by(Jobs.posted_at.desc(), Jobs.job_id.desc()).offset(skip).limit(limit)).all()
    items = [job_to_schema(job, db) for job in jobs]

    if not with_meta:
        return items

    total = db.exec(select(func.count()).select_from(Jobs)).one()
    return PaginatedResponse[Job](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    db_job = db.exec(select(Jobs).filter(Jobs.job_id == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_schema(db_job, db)


# ----------------------------
# 📌 READ BY STATUS
# ----------------------------
@router.get("/status/{status}", response_model=list[Job])
def get_jobs_by_status(
    status: str,
    db: Session = Depends(get_db),
):
    jobs = db.exec(select(Jobs).filter(Jobs.status == status)).all()
    return [job_to_schema(job, db) for job in jobs]


# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{job_id}", response_model=Job)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_job = db.exec(select(Jobs).filter(Jobs.job_id == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Resolve Country ISO2 to CountryId if provided
    job_data = job.model_dump(exclude_unset=True, exclude={"country"})

    if job.country is not None:
        country = db.exec(select(Countries).where(Countries.name == job.country.upper())).first()
        if not country:
            raise HTTPException(status_code=404, detail=f"Country with ISO2 code '{job.country}' not found")
        job_data["country_id"] = country.country_id

    for key, value in job_data.items():
        setattr(db_job, key, value)
    db.commit()
    db.refresh(db_job)
    return job_to_schema(db_job, db)


# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_job = db.exec(select(Jobs).filter(Jobs.job_id == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": "Job deleted successfully"}
