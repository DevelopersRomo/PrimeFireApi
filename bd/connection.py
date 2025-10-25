import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

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
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

# Connection URL for SQL Server
if password:
    quoted_password = password.replace("@", "%40")
    database_url = (
        f"mssql+pyodbc://{username}:{quoted_password}@{server}/{database}?"
        f"driver={driver}&TrustServerCertificate=yes&Encrypt=yes"
    )
else:
    database_url = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"


engine = create_engine(database_url, echo=echo)

# Create the session
SessionLocal = sessionmaker(bind=engine, class_=Session)

# Import all models to ensure they are registered with SQLModel
from models.employees import Employees, Roles
from models.jobs import Jobs
from models.licenses import Licences
from models.countries import Countries
from models.curriculums import Curriculums
from models.modules import Modules, RoleModules

# Function to create tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
