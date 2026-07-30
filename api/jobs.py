from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlmodel import Session, select

from api.dependencies import require_module_permission
from bd.dependencies import get_db
from models.countries import Countries
from models.jobs import Jobs
from schemas.jobs import Job, JobCreate, JobUpdate
from schemas.pagination import PaginatedResponse

router = APIRouter()


def _public_job_filters(search: str | None, location: str | None, country: str | None):
    filters = [Jobs.status == "active"]
    if search and search.strip():
        term = f"%{search.strip()}%"
        filters.append(or_(Jobs.title.ilike(term), Jobs.description.ilike(term)))
    if location:
        filters.append(Jobs.location == location)
    if country:
        filters.append(Countries.name == country)
    return filters


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
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("jobs", "can_create")),
):
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
    search: str | None = Query(None),
    country: str | None = Query(None),
    db: Session = Depends(get_db),
):
    filters = []
    if search and search.strip():
        term = f"%{search.strip()}%"
        filters.append(or_(Jobs.title.ilike(term), Jobs.description.ilike(term), Jobs.location.ilike(term)))
    if country:
        filters.append(Countries.name == country)

    query = select(Jobs).join(Countries, Jobs.country_id == Countries.country_id, isouter=True)
    if filters:
        query = query.where(*filters)
    query = query.order_by(Jobs.posted_at.desc(), Jobs.job_id.desc()).offset(skip).limit(limit)
    jobs = db.exec(query).all()
    items = [job_to_schema(job, db) for job in jobs]

    if not with_meta:
        return items

    count_query = (
        select(func.count()).select_from(Jobs).join(Countries, Jobs.country_id == Countries.country_id, isouter=True)
    )
    if filters:
        count_query = count_query.where(*filters)
    total = db.exec(count_query).one()
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
@router.get("/public/locations", response_model=list[str])
def get_public_job_locations(
    country: str | None = Query(None),
    db: Session = Depends(get_db),
):
    filters = _public_job_filters(None, None, country)
    query = (
        select(Jobs.location)
        .join(Countries, Jobs.country_id == Countries.country_id, isouter=True)
        .where(*filters, func.nullif(func.trim(Jobs.location), "").is_not(None))
        .distinct()
        .order_by(Jobs.location)
    )
    return list(db.exec(query).all())


@router.get("/public", response_model=PaginatedResponse[Job])
def get_public_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(24, ge=1, le=100),
    search: str | None = Query(None),
    location: str | None = Query(None),
    country: str | None = Query(None),
    sort_dir: Literal["asc", "desc"] = Query("desc"),
    db: Session = Depends(get_db),
):
    filters = _public_job_filters(search, location, country)
    posted_order = Jobs.posted_at.asc() if sort_dir == "asc" else Jobs.posted_at.desc()
    id_order = Jobs.job_id.asc() if sort_dir == "asc" else Jobs.job_id.desc()
    query = (
        select(Jobs)
        .join(Countries, Jobs.country_id == Countries.country_id, isouter=True)
        .where(*filters)
        .order_by(posted_order, id_order)
        .offset(skip)
        .limit(limit)
    )
    jobs = db.exec(query).all()
    count_query = (
        select(func.count())
        .select_from(Jobs)
        .join(Countries, Jobs.country_id == Countries.country_id, isouter=True)
        .where(*filters)
    )
    total = db.exec(count_query).one()
    items = [job_to_schema(job, db) for job in jobs]
    return PaginatedResponse[Job](
        items=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(items) < total,
    )


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
def update_job(
    job_id: int,
    job: JobUpdate,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("jobs", "can_edit")),
):
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
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    _permissions: dict = Depends(require_module_permission("jobs", "can_delete")),
):
    db_job = db.exec(select(Jobs).filter(Jobs.job_id == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": "Job deleted successfully"}
