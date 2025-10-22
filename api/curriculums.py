from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List, Optional
import os
import uuid
from pathlib import Path

from api.dependencies import require_authentication
from bd.dependencies import get_db
from models.curriculums import Curriculums
from models.jobs import Jobs
from schemas.curriculums import Curriculum, CurriculumCreate, CurriculumUpdate

router = APIRouter()

# Directory to store Curriculums
UPLOAD_DIR = Path("uploads/curriculums")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return relative path"""
    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Full path where file will be saved
    file_path = UPLOAD_DIR / unique_filename

    # Save the file
    with open(file_path, "wb") as buffer:
        content = upload_file.file.read()
        buffer.write(content)

    # Return relative path (to store in DB)
    return f"uploads/curriculums/{unique_filename}"

# ----------------------------
# 📌 CREATE (with file)
# ----------------------------
@router.post("/upload", response_model=Curriculum)
def create_curriculum_with_file(
    job_id: int = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    cover_letter: Optional[str] = Form(None),
    status: str = Form("pending"),
    employee_id: Optional[int] = Form(None),
    resume_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    # Validate job exists
    job = db.exec(select(Jobs).filter(Jobs.JobId == job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_extension = Path(resume_file.filename).suffix.lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF, DOC, DOCX, and TXT files are allowed."
        )

    # Save the file
    resume_path = save_upload_file(resume_file)

    # Create Curriculum in database
    curriculum_data = CurriculumCreate(
        JobId=job_id,
        Name=name,
        Email=email,
        Phone=phone,
        CoverLetter=cover_letter,
        Status=status,
        EmployeeId=employee_id
    )

    db_curriculum = Curriculums(**curriculum_data.model_dump(), CurriculumPath=resume_path)
    db.add(db_curriculum)
    db.commit()
    db.refresh(db_curriculum)
    return db_curriculum

# ----------------------------
# 📌 CREATE (without file)
# ----------------------------
@router.post("/", response_model=Curriculum)
def create_curriculum(
    curriculum: CurriculumCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    # Validate job exists
    job = db.exec(select(Jobs).filter(Jobs.JobId == curriculum.JobId)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    db_curriculum = Curriculums(**curriculum.model_dump())
    db.add(db_curriculum)
    db.commit()
    db.refresh(db_curriculum)
    return db_curriculum

# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("/", response_model=List[Curriculum])
def get_curriculums(
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    return db.exec(select(Curriculums)).all()

# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{curriculum_id}", response_model=Curriculum)
def get_curriculum(
    curriculum_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_curriculum = db.exec(select(Curriculums).filter(Curriculums.CurriculumId == curriculum_id)).first()
    if not db_curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return db_curriculum

# ----------------------------
# 📌 READ BY JOB
# ----------------------------
@router.get("/job/{job_id}", response_model=List[Curriculum])
def get_curriculums_by_job(
    job_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    return db.exec(select(Curriculums).filter(Curriculums.JobId == job_id)).all()

# ----------------------------
# 📌 READ BY STATUS
# ----------------------------
@router.get("/status/{status}", response_model=List[Curriculum])
def get_curriculums_by_status(
    status: str,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    return db.exec(select(Curriculums).filter(Curriculums.Status == status)).all()

# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{curriculum_id}", response_model=Curriculum)
def update_curriculum(
    curriculum_id: int,
    curriculum: CurriculumUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_curriculum = db.exec(select(Curriculums).filter(Curriculums.CurriculumId == curriculum_id)).first()
    if not db_curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    for key, value in curriculum.model_dump(exclude_unset=True).items():
        setattr(db_curriculum, key, value)
    db.commit()
    db.refresh(db_curriculum)
    return db_curriculum

# ----------------------------
# 📌 DOWNLOAD CURRICULUM FILE
# ----------------------------
@router.get("/{curriculum_id}/download")
def download_curriculum_file(
    curriculum_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    """Download the curriculum file"""
    db_curriculum = db.exec(select(Curriculums).filter(Curriculums.CurriculumId == curriculum_id)).first()
    if not db_curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    if not db_curriculum.CurriculumPath or not Path(db_curriculum.CurriculumPath).exists():
        raise HTTPException(status_code=404, detail="Curriculum file not found")

    return FileResponse(
        path=db_curriculum.CurriculumPath,
        filename=f"{db_curriculum.Name.replace(' ', '_')}_Curriculum{Path(db_curriculum.CurriculumPath).suffix}",
        media_type='application/octet-stream'
    )

# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{curriculum_id}")
def delete_curriculum(
    curriculum_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_authentication)
):
    db_curriculum = db.exec(select(Curriculums).filter(Curriculums.CurriculumId == curriculum_id)).first()
    if not db_curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    # Delete physical file if it exists
    if db_curriculum.CurriculumPath and Path(db_curriculum.CurriculumPath).exists():
        Path(db_curriculum.CurriculumPath).unlink()

    db.delete(db_curriculum)
    db.commit()
    return {"detail": "Curriculum deleted successfully"}

