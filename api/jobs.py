from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.jobs import Jobs
from models.countries import Countries
from schemas.jobs import Job, JobCreate, JobUpdate

router = APIRouter()

def job_to_schema(db_job: Jobs, db: Session) -> Job:
    """Convert database Job model to response schema with Country ISO2"""
    country_iso2 = None
    if db_job.CountryId:
        country = db.exec(select(Countries).where(Countries.CountryId == db_job.CountryId)).first()
        if country:
            country_iso2 = country.Name
    
    return Job(
        JobId=db_job.JobId,
        Title=db_job.Title,
        Description=db_job.Description,
        Requirements=db_job.Requirements,
        Location=db_job.Location,
        SalaryMin=db_job.SalaryMin,
        SalaryMax=db_job.SalaryMax,
        Status=db_job.Status,
        PostedAt=db_job.PostedAt,
        EmployeeId=db_job.EmployeeId,
        Country=country_iso2
    )

# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("", response_model=Job)
def create_job(job: JobCreate, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    # Resolve Country ISO2 to CountryId if provided
    country_id = None
    if job.Country:
        country = db.exec(
            select(Countries).where(Countries.Name == job.Country.upper())
        ).first()
        if not country:
            raise HTTPException(status_code=404, detail=f"Country with ISO2 code '{job.Country}' not found")
        country_id = country.CountryId
    
    # Create job data without Country field
    job_data = job.model_dump(exclude={'Country'})
    job_data['CountryId'] = country_id
    
    db_job = Jobs(**job_data)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return job_to_schema(db_job, db)

# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("", response_model=List[Job])
def get_jobs(
    db: Session = Depends(get_db),
):
    jobs = db.exec(select(Jobs)).all()
    return [job_to_schema(job, db) for job in jobs]

# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{job_id}", response_model=Job)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_schema(db_job, db)

# ----------------------------
# 📌 READ BY STATUS
# ----------------------------
@router.get("/status/{status}", response_model=List[Job])
def get_jobs_by_status(
    status: str,
    db: Session = Depends(get_db),
):
    jobs = db.exec(select(Jobs).filter(Jobs.Status == status)).all()
    return [job_to_schema(job, db) for job in jobs]

# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{job_id}", response_model=Job)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db), _auth=Depends(require_authentication)):
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Resolve Country ISO2 to CountryId if provided
    job_data = job.model_dump(exclude_unset=True, exclude={'Country'})
    
    if job.Country is not None:
        country = db.exec(
            select(Countries).where(Countries.Name == job.Country.upper())
        ).first()
        if not country:
            raise HTTPException(status_code=404, detail=f"Country with ISO2 code '{job.Country}' not found")
        job_data['CountryId'] = country.CountryId
    
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
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": "Job deleted successfully"}

