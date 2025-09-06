import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Parámetros de conexión
server = "DEVROMO\SQLEXPRESS"        # o el nombre/IP de tu servidor SQL
database = "PrimeFireCorp"  # cambia por el nombre de tu BD
username = "sa"             # tu usuario SQL Server
password = "$Iedo1914"  # tu contraseña
driver = "ODBC Driver 17 for SQL Server"  # debe estar instalado en Windows/Linux

# URL de conexión para SQL Server
database_url = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"

# Crear el engine
engine = create_engine(database_url)

# Crear la sesión
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Declarative Base
Base = declarative_base()
