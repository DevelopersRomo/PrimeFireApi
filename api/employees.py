from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from bd.dependencies import get_db
from models.employees import Employees
from schemas.employees import Employee, EmployeeCreate

router = APIRouter()

# ----------------------------
# 📌 CREATE
# ----------------------------
@router.post("/", response_model=Employee)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employees(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# ----------------------------
# 📌 READ ALL
# ----------------------------
@router.get("/", response_model=List[Employee])
def get_employees(db: Session = Depends(get_db)):
    return db.exec(select(Employees)).all()

# ----------------------------
# 📌 READ ONE
# ----------------------------
@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# ----------------------------
# 📌 UPDATE
# ----------------------------
@router.put("/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee.model_dump(exclude_unset=True).items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# ----------------------------
# 📌 DELETE
# ----------------------------
@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.exec(select(Employees).filter(Employees.EmployeeId == employee_id)).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return {"detail": "Employee deleted successfully"}
