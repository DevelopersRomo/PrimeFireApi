import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection parameters from environment variables
server = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
database = os.getenv("DB_DATABASE", "PrimeFireCorp")
username = os.getenv("DB_USERNAME", "sa")
password = os.getenv("DB_PASSWORD", "")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
echo = os.getenv("DB_ECHO", "False").lower() == "true"

# Connection URL for SQL Server with Windows authentication
if password:
    database_url = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
else:
    # Use Windows authentication (Trusted Connection)
    database_url = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"

# Create the engine
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
