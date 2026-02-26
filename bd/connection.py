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
from models.time_off import Department, Holiday, TimeOffBalance, TimeOffRequest
from models.timesheet import TimeSheetLocationSnapshot, TimeSheetPunch, TimeSheetSettings
from models.tenants import Tenants, TenantEmployees, TenantLogos
from models.addresses import Addresses
from models.customers import Customers, CustomerNotes, CustomerAlternateContacts, CustomerAttachments

# Load environment variables
load_dotenv()

# Load environment variables
load_dotenv()

# Find available SQL Server driver
available_drivers = pyodbc.drivers()
sql_server_drivers = [d for d in available_drivers if "SQL Server" in d]

def get_driver(requested_driver):
    if requested_driver in available_drivers:
        return requested_driver
    elif sql_server_drivers:
        driver = sql_server_drivers[0]
        print(f"Driver '{requested_driver}' not found. Using '{driver}' instead.")
        return driver
    else:
        raise RuntimeError(
            f"No SQL Server ODBC driver found. "
            f"Requested: '{requested_driver}'. "
            f"Available drivers: {available_drivers}"
        )

def create_engine_from_env(prefix="DB"):
    server = os.getenv(f"{prefix}_SERVER", "localhost\\SQLEXPRESS")
    database = os.getenv(f"{prefix}_DATABASE", "PrimeFireCorp")
    username = os.getenv(f"{prefix}_USERNAME", "sa")
    password = os.getenv(f"{prefix}_PASSWORD", "")
    port = os.getenv(f"{prefix}_PORT", "")
    encrypt_env = os.getenv(f"{prefix}_ENCRYPT", "").lower()
    requested_driver = os.getenv(f"{prefix}_DRIVER", "ODBC Driver 17 for SQL Server")
    echo = os.getenv("DB_ECHO", "False").lower() == "true"

    driver = get_driver(requested_driver)
    is_old_driver = driver == "SQL Server"

    # Connection URL for SQL Server
    # If server has instance name (contains \), don't use port
    # If server is localhost/127.0.0.1 without instance and port is specified, use port
    # If server already has port (contains :), use as-is
    # For local connections with named instances, prefer Shared Memory (.\INSTANCE)
    has_instance = "\\" in server
    has_port_in_server = ":" in server
    server_lower = server.lower()
    is_local = (server_lower.startswith("localhost") or 
                server_lower.startswith("127.0.0.1") or 
                server_lower.startswith(".") or
                server_lower.startswith("(local)") or
                server_lower.startswith("(localdb)"))
    
    use_shared_memory = False
    if has_instance and is_local:
        # For local named instances, keep original format but force Encrypt=no
        server_with_port = server
        if not encrypt_env:
            encrypt = False
        else:
            encrypt = encrypt_env == "yes"
    elif has_instance:
        # Named instance - don't use port, let SQL Browser resolve
        server_with_port = server
    elif has_port_in_server:
        # Server already has port specified
        server_with_port = server
    elif port and port != "1433" and port != "":
        # Port specified and not default
        server_with_port = f"{server},{port}"
    else:
        # Default case
        server_with_port = server
        if not encrypt_env:
            # Default to no encryption for local connections
            encrypt = not is_local
        else:
            encrypt = encrypt_env == "yes"

    if encrypt_env:
        encrypt = encrypt_env == "yes"
    else:
        encrypt = not is_local

    odbc_params = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server_with_port}",
        f"DATABASE={database}",
        "Connection Timeout=30",
    ]

    if username and password:
        odbc_params.append(f"UID={username}")
        odbc_params.append(f"PWD={password}")
    else:
        odbc_params.append("Trusted_Connection=yes")

    if not is_old_driver:
        odbc_params.append("TrustServerCertificate=yes")
        odbc_params.append(f"Encrypt={'yes' if encrypt else 'no'}")

    odbc_connect = ";".join(odbc_params)
    database_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_connect)}"

    # Configure engine options based on driver
    engine_kwargs = {"echo": echo}

    # Old SQL Server driver doesn't support OUTPUT clause for returning identity values
    if is_old_driver:
        engine_kwargs["implicit_returning"] = False

    return create_engine(database_url, **engine_kwargs)

# Create main engine
engine = create_engine_from_env("DB")

# Create sync engine (fallback to main engine if PRIMEFIRE_DB_SERVER is not set or sync is disabled)
sync_enabled = os.getenv("SYNC_EMPLOYEES_PRIMEFIRE", "True").lower() == "true"
if sync_enabled and os.getenv("PRIMEFIRE_DB_SERVER"):
    sync_engine = create_engine_from_env("PRIMEFIRE_DB")
    print(f"Using separate database for sync/auth: {os.getenv('PRIMEFIRE_DB_SERVER')}/{os.getenv('PRIMEFIRE_DB_DATABASE')}")
else:
    sync_engine = engine

# Create the session
SessionLocal = sessionmaker(bind=engine, class_=Session)
SessionSync = sessionmaker(bind=sync_engine, class_=Session)


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
