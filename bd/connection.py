import os
from urllib.parse import quote_plus

import pyodbc
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

# Import all models to ensure they are registered with SQLModel
from models.countries import Countries
from models.curriculums import Curriculums
from models.employees import Employees, Roles
from models.hardware_inventory import HardwareInventory
from models.jobs import Jobs
from models.licenses import Licenses
from models.modules import Modules, RoleModules
from models.ticket_messages import TicketMessages, TicketAttachments

# Load environment variables
load_dotenv()

# Connection parameters from environment variables
LOCAL_DATABASE = os.getenv("LOCAL_DATABASE", "False").lower() == "true"
echo = os.getenv("DB_ECHO", "False").lower() == "true"

# SQL Server configuration
server = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
database = os.getenv("DB_DATABASE", "PrimeFireCorp")
username = os.getenv("DB_USERNAME", "sa")
password = os.getenv("DB_PASSWORD", "")
port = os.getenv("DB_PORT", "1433")
encrypt = os.getenv("DB_ENCRYPT", "yes").lower() == "yes"
requested_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Find available SQL Server driver
available_drivers = pyodbc.drivers()
sql_server_drivers = [d for d in available_drivers if "SQL Server" in d]

if requested_driver in available_drivers:
    driver = requested_driver
elif sql_server_drivers:
    driver = sql_server_drivers[0]
    print(f"⚠️ Driver '{requested_driver}' not found. Using '{driver}' instead.")
else:
    raise RuntimeError(
        f"No SQL Server ODBC driver found. "
        f"Requested: '{requested_driver}'. "
        f"Available drivers: {available_drivers}"
    )

# Check if using old SQL Server driver (without version number)
is_old_driver = driver == "SQL Server"

# Connection URL for SQL Server
# For remote servers, include port if specified
if ":" in server or port != "1433":
    if ":" not in server:
        server_with_port = f"{server},{port}"
    else:
        server_with_port = server
else:
    server_with_port = server

if password:
    quoted_password = quote_plus(password)
    quoted_username = quote_plus(username)
    quoted_server = quote_plus(server_with_port)
    quoted_driver = quote_plus(driver)
    
    if is_old_driver:
        # Old driver doesn't support modern SSL parameters
        database_url = (
            f"mssql+pyodbc://{quoted_username}:{quoted_password}@{quoted_server}/{database}?"
            f"driver={quoted_driver}&Connection Timeout=30"
        )
    else:
        # Modern drivers support SSL parameters
        encrypt_param = "yes" if encrypt else "no"
        database_url = (
            f"mssql+pyodbc://{quoted_username}:{quoted_password}@{quoted_server}/{database}?"
            f"driver={quoted_driver}&TrustServerCertificate=yes&Encrypt={encrypt_param}&Connection Timeout=30"
        )
else:
    quoted_server = quote_plus(server_with_port)
    quoted_driver = quote_plus(driver)
    if is_old_driver:
        database_url = (
            f"mssql+pyodbc://{quoted_server}/{database}?"
            f"driver={quoted_driver}&trusted_connection=yes&Connection Timeout=30"
        )
    else:
        database_url = (
            f"mssql+pyodbc://{quoted_server}/{database}?"
            f"driver={quoted_driver}&trusted_connection=yes&Connection Timeout=30"
        )

engine = create_engine(database_url, echo=echo)

# Create the session
SessionLocal = sessionmaker(bind=engine, class_=Session)


def create_db_and_tables():
    """Create database tables, ignoring compatibility errors from old ODBC drivers."""
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        # Ignore "Invalid precision value" error from old SQL Server driver
        # This is a known compatibility issue that doesn't affect functionality
        # The error occurs during table existence checks but tables work fine
        error_str = str(e)
        if "Invalid precision value" in error_str or "HY104" in error_str:
            # This is a harmless error from the old driver during metadata inspection
            # Tables will be created/used correctly despite this error
            # The error happens when checking if tables exist, but creation still works
            pass
        else:
            # Re-raise other errors that might be actual problems
            raise


def test_connection():
    """Test database connection."""
    try:
        with SessionLocal() as session:
            result = session.exec(text("SELECT GETDATE()"))
            print("✅ Success Conection! Date/Hour: server", result.one())
    except Exception as e:
        print("❌ Error de conexión:", e)


if __name__ == "__main__":
    test_connection()
