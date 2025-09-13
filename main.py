from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from bd.connection import Base, engine, SessionLocal

from models.licenses import Licences
from schemas.licenses import Licence, LicenceCreate
from models.employees import Employees
from schemas.employees import Employee, EmployeeCreate
from typing import List

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependencia para obtener DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------
# 📌 CREATE
# ----------------------------
@app.post("/licenses/", response_model=Licence)
def create_license(license: LicenceCreate, db: Session = Depends(get_db)):
    db_license = Licences(**license.dict())
    db.add(db_license)
    db.commit()
    db.refresh(db_license)
    return db_license

# ----------------------------
# 📌 READ ALL
# ----------------------------
@app.get("/licenses/", response_model=List[Licence])
def get_licenses(db: Session = Depends(get_db)):
    return db.query(Licences).all()

# ----------------------------
# 📌 READ ONE
# ----------------------------
@app.get("/licenses/{license_id}", response_model=Licence)
def get_license(license_id: int, db: Session = Depends(get_db)):
    db_license = db.query(Licences).filter(Licences.LicenceID == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")
    return db_license

# ----------------------------
# 📌 UPDATE
# ----------------------------
@app.put("/licenses/{license_id}", response_model=Licence)
def update_license(license_id: int, license: LicenceCreate, db: Session = Depends(get_db)):
    db_license = db.query(Licences).filter(Licences.LicenceID == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    for key, value in license.dict().items():
        setattr(db_license, key, value)

    db.commit()
    db.refresh(db_license)
    return db_license

# ----------------------------
# 📌 DELETE
# ----------------------------
@app.delete("/licenses/{license_id}")
def delete_license(license_id: int, db: Session = Depends(get_db)):
    db_license = db.query(Licences).filter(Licences.LicenceID == license_id).first()
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    db.delete(db_license)
    db.commit()
    return {"message": "License deleted successfully"}


# -----------------------------
# Endpoints de Employees CRUD
# -----------------------------

# Crear un empleado
@app.post("/employees/", response_model=Employee)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = Employees(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Listar todos los empleados
@app.get("/employees/", response_model=List[Employee])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employees).all()

# Obtener un empleado por ID
@app.get("/employees/{employee_id}", response_model=Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employees).filter(Employees.EmployeeId == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# Actualizar un empleado por ID
@app.put("/employees/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee: EmployeeCreate, db: Session = Depends(get_db)):
    db_employee = db.query(Employees).filter(Employees.EmployeeId == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for key, value in employee.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)
    db.commit()
    db.refresh(db_employee)
    return db_employee

# Eliminar un empleado por ID
@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employees).filter(Employees.EmployeeId == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(db_employee)
    db.commit()
    return {"detail": "Employee deleted successfully"}
