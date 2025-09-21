import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Parámetros de conexión desde variables de entorno
server = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
database = os.getenv("DB_DATABASE", "PrimeFireCorp")
username = os.getenv("DB_USERNAME", "sa")
password = os.getenv("DB_PASSWORD", "")
driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
echo = os.getenv("DB_ECHO", "False").lower() == "true"

# URL de conexión para SQL Server con autenticación Windows
if password:
    database_url = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
else:
    # Usar autenticación Windows (Trusted Connection)
    database_url = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"

# Crear el engine
engine = create_engine(database_url, echo=echo)

# Crear la sesión
SessionLocal = sessionmaker(bind=engine, class_=Session)

# Función para crear tablas
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
