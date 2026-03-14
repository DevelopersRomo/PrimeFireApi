import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlmodel import Session

from bd.connection import engine as main_engine


class ConnectionManager:
    _engines = {}
    _main_engine = main_engine

    @classmethod
    def get_engine(cls, tenant_key: str | None = None):
        """
        Get database engine.
        If tenant_key is None or 'main', returns the main DB engine.
        Otherwise, looks for a connection string in environment variables
        formatted as DB_CONNECTION_{TENANT_KEY}.
        """
        if not tenant_key or tenant_key.lower() == "main":
            return cls._main_engine

        if tenant_key in cls._engines:
            return cls._engines[tenant_key]

        # Build connection string dynamically
        # Format: DB_CONNECTION_CLIENTA="mssql+pyodbc://..."
        env_var_name = f"DB_CONNECTION_{tenant_key.upper()}"
        connection_url = os.getenv(env_var_name)

        if not connection_url:
            # Fallback: try to construct it from standard params if they exist with suffix
            # e.g. DB_SERVER_CLIENTA
            server = os.getenv(f"DB_SERVER_{tenant_key.upper()}")
            database = os.getenv(f"DB_DATABASE_{tenant_key.upper()}")

            if server and database:
                # Construct URL similar to main connection (simplified for brevity)
                username = os.getenv(f"DB_USERNAME_{tenant_key.upper()}", os.getenv("DB_USERNAME"))
                password = os.getenv(f"DB_PASSWORD_{tenant_key.upper()}", os.getenv("DB_PASSWORD"))
                driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

                quoted_driver = quote_plus(driver)
                quoted_server = quote_plus(server)
                quoted_password = quote_plus(password)
                quoted_username = quote_plus(username)

                connection_url = (
                    f"mssql+pyodbc://{quoted_username}:{quoted_password}@{quoted_server}/{database}?"
                    f"driver={quoted_driver}&trusted_connection=no&Connection Timeout=30"
                )
            else:
                raise ValueError(f"No configuration found for tenant key: {tenant_key}")

        echo = os.getenv("DB_ECHO", "False").lower() == "true"
        new_engine = create_engine(connection_url, echo=echo)
        cls._engines[tenant_key] = new_engine
        return new_engine

    @classmethod
    def get_session(cls, tenant_key: str | None = None) -> Session:
        engine = cls.get_engine(tenant_key)
        return Session(engine)
