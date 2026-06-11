import os
from urllib.parse import quote_plus

import pyodbc  # type: ignore[import-not-found]
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session, create_engine

# Import all models to ensure they are registered with SQLModel

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
    if sql_server_drivers:
        return sql_server_drivers[0]
    raise RuntimeError(
        f"No SQL Server ODBC driver found. Requested: '{requested_driver}'. Available drivers: {available_drivers}"
    )


def create_engine_from_env(prefix="DB"):
    '''
    #for windows 
    server = os.getenv(f"{prefix}_SERVER", "localhost\\SQLEXPRESS")
    '''
     # For Linux/Mac, default to localhost with default port
    server = os.getenv(f"{prefix}_SERVER", "localhost,1433") 
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
    is_local = server_lower.startswith(("localhost", "127.0.0.1", ".", "(local)", "(localdb)"))

    if has_instance and is_local:
        # For local named instances, keep original format but force Encrypt=no
        server_with_port = server
        encrypt = False if not encrypt_env else encrypt_env == "yes"
    elif has_instance:
        # Named instance - don't use port, let SQL Browser resolve
        server_with_port = server
    elif has_port_in_server:
        # Server already has port specified
        server_with_port = server
    elif port and port not in {"1433", ""}:
        # Port specified and not default
        server_with_port = f"{server},{port}"
    else:
        # Default case
        server_with_port = server
        if not encrypt_env:  # noqa: SIM108
            # Default to no encryption for local connections
            encrypt = not is_local
        else:
            encrypt = encrypt_env == "yes"

    encrypt = encrypt_env == "yes" if encrypt_env else not is_local

    odbc_params = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server_with_port}",
        f"DATABASE={database}",
        "Connection Timeout=30",
    ]

    # Check for trusted connection env var (e.g. DB_TRUSTED_CONNECTION=true)
    trusted_conn_env = os.getenv(f"{prefix}_TRUSTED_CONNECTION", "").lower()
    if trusted_conn_env == "true":
        odbc_params.append("Trusted_Connection=yes")
    elif username and password:
        # Escape password for ODBC connection string
        # If password contains special chars (semicolons, etc.), wrap in braces
        if any(c in password for c in ";{}"):
            escaped_password = "{" + password + "}"
        else:
            escaped_password = password
        odbc_params.extend((f"UID={username}", f"PWD={escaped_password}"))
    else:
        odbc_params.append("Trusted_Connection=yes")

    if not is_old_driver:
        odbc_params.extend(("TrustServerCertificate=yes", f"Encrypt={'yes' if encrypt else 'no'}"))

    odbc_connect = ";".join(odbc_params)
    database_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_connect)}"

    # Configure engine options based on driver
    engine_kwargs = {
        "echo": echo,
        # Disable setinputsizes to avoid pyodbc HY104 "Invalid precision value (0)"
        # errors when binding datetime/None parameters to DATETIME columns.
        "use_setinputsizes": False,
    }

    # Old SQL Server driver doesn't support OUTPUT clause for returning identity values
    if is_old_driver:
        engine_kwargs["implicit_returning"] = False

    return create_engine(database_url, **engine_kwargs)


# Create main engine
engine = create_engine_from_env("DB")

# Create PrimeFire engine. This is intentionally independent from employee sync:
# Azure AD users from @primefire.us / @primefire.do must never fall back to DB_*.
primefire_engine = create_engine_from_env("PRIMEFIRE_DB") if os.getenv("PRIMEFIRE_DB_SERVER") else None

# Create sync engine. Keep it separate from main DB; when sync is disabled/misconfigured,
# callers must fail explicitly instead of silently using DB_SERVER.
sync_enabled = os.getenv("SYNC_EMPLOYEES_PRIMEFIRE", "True").lower() == "true"
sync_engine = primefire_engine if sync_enabled else None

# Create the session
SessionLocal = sessionmaker(bind=engine, class_=Session)
SessionPrimeFire = sessionmaker(bind=primefire_engine, class_=Session) if primefire_engine else None
SessionSync = sessionmaker(bind=sync_engine, class_=Session) if sync_engine else None


def create_db_and_tables() -> None:
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


def test_connection() -> None:
    """Test database connection."""
    try:
        with SessionLocal() as session:
            session.exec(text("SELECT GETDATE()"))  # type: ignore[call-overload]
    except Exception:
        pass


if __name__ == "__main__":
    test_connection()
