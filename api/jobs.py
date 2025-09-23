from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from bd.dependencies import get_db
from models.jobs import Jobs
from schemas.jobs import Job, JobCreate, JobUpdate

router = APIRouter()

# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("/", response_model=Job)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Jobs(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("/", response_model=List[Job])
def get_jobs(db: Session = Depends(get_db)):
    return db.exec(select(Jobs)).all()

# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{job_id}", response_model=Job)
def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

# ----------------------------
# 📌 READ BY STATUS
# ----------------------------
@router.get("/status/{status}", response_model=List[Job])
def get_jobs_by_status(status: str, db: Session = Depends(get_db)):
    return db.exec(select(Jobs).filter(Jobs.Status == status)).all()

# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{job_id}", response_model=Job)
def update_job(job_id: int, job: JobUpdate, db: Session = Depends(get_db)):
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    for key, value in job.model_dump(exclude_unset=True).items():
        setattr(db_job, key, value)
    db.commit()
    db.refresh(db_job)
    return db_job

# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return {"detail": "Job deleted successfully"}

