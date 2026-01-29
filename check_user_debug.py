from sqlmodel import select
from bd.connection import SessionLocal, SessionSync
from models.employees import Employees
import os

# Check env vars loaded
print(f"SYNC_EMPLOYEES_PRIMEFIRE: {os.getenv('SYNC_EMPLOYEES_PRIMEFIRE')}")
print(f"DB_DATABASE: {os.getenv('DB_DATABASE')}")
print(f"PRIMEFIRE_DB_DATABASE: {os.getenv('PRIMEFIRE_DB_DATABASE')}")

oid = "0523631c-d286-4be5-9aaf-e33ac83b587c"

print(f"\nChecking for user with AzureOid: {oid}")

# Check in SessionLocal (Main DB - DevRomo)
print("\n--- Checking in SessionLocal (Main DB) ---")
try:
    with SessionLocal() as session:
        # List all employees to see what's there
        all_emps = session.exec(select(Employees)).all()
        print(f"Total employees in DB: {len(all_emps)}")
        for e in all_emps:
            print(f"  - ID: {e.EmployeeId}, Name: {e.DisplayName}, OID: {e.AzureOid}")
            
        emp = session.exec(select(Employees).where(Employees.AzureOid == oid)).first()
        if emp:
            print(f"FOUND in SessionLocal: {emp.DisplayName} (ID: {emp.EmployeeId})")
        else:
            print("NOT FOUND in SessionLocal")
except Exception as e:
    print(f"Error in SessionLocal: {e}")

# Check in SessionSync (Sync DB - PrimeFireCorp or DevRomo depending on config)
print("\n--- Checking in SessionSync (Sync DB) ---")
try:
    with SessionSync() as session:
        emp = session.exec(select(Employees).where(Employees.AzureOid == oid)).first()
        if emp:
            print(f"FOUND in SessionSync: {emp.DisplayName} (ID: {emp.EmployeeId})")
        else:
            print("NOT FOUND in SessionSync")
except Exception as e:
    print(f"Error in SessionSync: {e}")
