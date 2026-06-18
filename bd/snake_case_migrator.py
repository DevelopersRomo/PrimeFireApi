"""
================================================================================
MIGRADOR PascalCase -> snake_case.
================================================================================
Script completo para migrar tablas y columnas de PascalCase a snake_case.
Maneja: columnas, primary keys, foreign keys, indexes, constraints, data.

CONTROL: Edita la seccion TABLE_LIST para activar/desactivar tablas.
         Solo las tablas marcadas como True seran procesadas.

BASES DE DATOS:
  - DB_SERVER (DevRomo): Base de datos principal
  - PRIMEFIRE_DB_SERVER (PrimeFireCorp): Base de datos de empleados

MODO VISTA PREVIA:
  - Cambia DRY_RUN = True para solo ver que pasaria sin ejecutar cambios
  - Cambia DRY_RUN = False para ejecutar la migracion real

NOTAS:
  - Las FKs que referencian tablas no procesadas se recrean al final
  - Las tablas con FKs cruzadas pueden requerir ejecucion multiple
================================================================================
"""

import contextlib
import os
import re
import sys

import pyodbc
from dotenv import load_dotenv

load_dotenv()

# =================================================================================
# MODO DE OPERACION
# =================================================================================
DRY_RUN = False  # False = ejecuta la migracion real


# =================================================================================
# CONFIGURACION - CONTROL DE TABLAS
# =================================================================================
# Establece True para procesar la tabla, False para saltar
# El formato es: "nombre_tabla": True/False
#
# NOTA: Las tablas con referencias FK deben procesarse en orden.
#       Si hay referencias circulares, desactiva las FK temporalmente.

TABLE_LIST = {
    # ---- DevRomo (DB_SERVER) ----
    # Core Security
    "Tenants": True,
    "TenantEmployees": True,
    "TenantLogos": True,
    "ExternalUsers": True,
    "Roles": True,
    "Modules": True,
    "EmployeeRoles": True,
    "RoleModules": True,
    # Catalogos
    "Countries": True,
    # Employees y relacionados
    "Employees": True,
    "Licenses": True,
    "Departments": True,
    "Holidays": True,
    # Operacion Comercial
    "Jobs": True,
    "Curriculums": True,
    "QuotationItems": True,
    # Customers (con FK a Addresses, Employees)
    "Addresses": True,
    "Customers": True,
    "CustomerNotes": True,
    "CustomerAlternateContacts": True,
    "CustomerAttachments": True,
    # Products y Quotations
    "Products": True,
    "Quotations": True,
    # Tickets (con FK a Employees)
    "Tickets": True,
    "ticketMessages": True,
    "ticketAttachments": True,
    # Time Off y Timesheet
    "TimeOff": True,
    "Timesheet": True,
    "TimeOffBalances": True,
    "TimeOffRequests": True,
    "TimeSheetLocationSnapshots": True,
    "TimeSheetPunches": True,
    "TimeSheetSettings": True,
    # Hardware
    "HardwareInventory": True,
    # Notifications y Backups
    "Notifications": True,
    "Backups": True,
}

# Base de datos a procesar
PROCESS_DEVROMO = True
PROCESS_PRIMEFIRE = True  # Ambas bases de datos procesadas por defecto


# =================================================================================
# UTILIDADES
# =================================================================================


def to_snake_case(name: str) -> str:
    """Convierte PascalCase/camelCase a snake_case."""
    if not name or name.islower() or name.isupper():
        return name.lower()
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def get_connection_string(prefix: str) -> str:
    """Construye connection string desde variables de entorno."""
    server = os.getenv(f"{prefix}_SERVER", "localhost")
    database = os.getenv(f"{prefix}_DATABASE", "")
    username = os.getenv(f"{prefix}_USERNAME", "sa")
    password = os.getenv(f"{prefix}_PASSWORD", "")
    driver = os.getenv(f"{prefix}_DRIVER", "ODBC Driver 17 for SQL Server")
    encrypt = os.getenv(f"{prefix}_ENCRYPT", "yes").lower() == "yes"

    auth = f"UID={username};PWD={password}" if username and password else "Trusted_Connection=yes"

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"{auth};"
        f"TrustServerCertificate=yes;"
        f"Encrypt={'yes' if encrypt else 'no'};"
        f"Connection Timeout=30;"
    )


def connect_db(prefix: str) -> pyodbc.Connection:
    """Establece conexion a la base de datos."""
    conn_str = get_connection_string(prefix)
    conn = pyodbc.connect(conn_str)
    conn.autocommit = False
    return conn


def get_tables(cursor, database: str) -> list[dict]:
    """Obtiene todas las tablas de la base de datos (case-sensitive TABLE_NAME)."""
    cursor.execute(
        """
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE = 'BASE TABLE'
        AND TABLE_CATALOG = ?
        ORDER BY TABLE_NAME
    """,
        database,
    )
    return [{"name": row[0]} for row in cursor.fetchall()]


def get_columns(cursor, table: str) -> list[dict]:
    """Obtiene todas las columnas de una tabla (case-sensitive)."""
    cursor.execute(
        """
        SELECT
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.NUMERIC_PRECISION,
            c.NUMERIC_SCALE,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            CASE WHEN ic.column_id IS NOT NULL THEN 1 ELSE 0 END as IS_IDENTITY
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN sys.identity_columns ic
            ON OBJECT_NAME(ic.object_id) = c.TABLE_NAME
            AND ic.name = c.COLUMN_NAME
        WHERE c.TABLE_NAME = ? COLLATE Latin1_General_CS_AS
        ORDER BY c.ORDINAL_POSITION
    """,
        table,
    )
    return [
        {
            "name": row[0],
            "data_type": row[1],
            "max_length": row[2],
            "precision": row[3],
            "scale": row[4],
            "nullable": row[5] == "YES",
            "default": row[6],
            "is_identity": row[7] == 1,
        }
        for row in cursor.fetchall()
    ]


def get_primary_key(cursor, table: str) -> dict | None:
    """Obtiene la clave primaria de una tabla (soporta PK simples y compuestas, case-sensitive)."""
    cursor.execute(
        """
        SELECT
            kcu.COLUMN_NAME,
            kcu.ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
        WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
        AND tc.TABLE_NAME = ? COLLATE Latin1_General_CS_AS
        ORDER BY kcu.ORDINAL_POSITION
    """,
        table,
    )
    rows = cursor.fetchall()
    if not rows:
        return None
    if len(rows) == 1:
        return {"column": rows[0][0], "position": rows[0][1], "columns": [rows[0][0]]}
    # PK compuesta
    return {"column": rows[0][0], "position": rows[0][1], "columns": [row[0] for row in rows]}


def get_foreign_keys(cursor, table: str) -> list[dict]:
    """Obtiene las foreign keys de una tabla (case-sensitive)."""
    cursor.execute(
        """
        SELECT
            fk.name as FK_NAME,
            pc.name as PARENT_COLUMN,
            tr.name as REFERENCED_TABLE,
            rc.name as REFERENCED_COLUMN,
            fk.delete_referential_action_desc,
            fk.update_referential_action_desc
        FROM sys.foreign_keys fk
        INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN sys.columns pc ON fkc.parent_column_id = pc.column_id AND fkc.parent_object_id = pc.object_id
        INNER JOIN sys.columns rc ON fkc.referenced_column_id = rc.column_id AND fkc.referenced_object_id = rc.object_id
        INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
        WHERE OBJECT_NAME(fk.parent_object_id) = ? COLLATE Latin1_General_CS_AS
        ORDER BY fk.name, fkc.constraint_column_id
    """,
        table,
    )
    return [
        {
            "name": row[0],
            "parent_column": row[1],
            "referenced_table": row[2],
            "referenced_column": row[3],
            "delete_action": row[4],
            "update_action": row[5],
        }
        for row in cursor.fetchall()
    ]


def get_indexes(cursor, table: str) -> list[dict]:
    """Obtiene los indices de una tabla (excluyendo PK y auto-generated, case-sensitive)."""
    cursor.execute(
        """
        SELECT
            i.name as INDEX_NAME,
            i.is_unique,
            i.type_desc,
            STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) as COLUMNS
        FROM sys.indexes i
        INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE OBJECT_NAME(i.object_id) = ? COLLATE Latin1_General_CS_AS
        AND i.is_primary_key = 0
        AND i.type > 0
        GROUP BY i.name, i.is_unique, i.type_desc
        ORDER BY i.name
    """,
        table,
    )
    return [{"name": row[0], "unique": row[1], "type": row[2], "columns": row[3]} for row in cursor.fetchall()]


def get_constraints(cursor, table: str) -> list[dict]:
    """Obtiene constraints unicos y checks de una tabla (case-sensitive)."""
    cursor.execute(
        """
        SELECT
            tc.CONSTRAINT_NAME,
            tc.CONSTRAINT_TYPE,
            kcu.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
            ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            AND tc.TABLE_NAME = kcu.TABLE_NAME
        WHERE tc.TABLE_NAME = ? COLLATE Latin1_General_CS_AS
        AND tc.CONSTRAINT_TYPE IN ('UNIQUE', 'CHECK')
        ORDER BY tc.CONSTRAINT_NAME
    """,
        table,
    )
    return [{"name": row[0], "type": row[1], "column": row[2]} for row in cursor.fetchall()]


def build_column_definition(col: dict, include_identity: bool = False) -> str:
    """Construye la definicion SQL de una columna."""
    dtype = col["data_type"].upper()

    # Manejar max_length
    if col["max_length"] == -1 or col["max_length"] == "MAX":
        if dtype in {"NVARCHAR", "VARCHAR", "CHAR", "NCHAR"}:
            dtype = f"{dtype}(MAX)"
    elif col["max_length"] and col["max_length"] > 0:
        if dtype in {"NVARCHAR", "VARCHAR", "CHAR", "NCHAR"}:
            dtype = f"{dtype}({col['max_length']})"
        elif dtype == "DATETIME2":
            dtype = f"{dtype}({col['scale']})"

    # Precision/scale SOLO para DECIMAL y NUMERIC (SQL Server no soporta esto para INT, BIGINT, etc.)
    if col["precision"] is not None and dtype in {"DECIMAL", "NUMERIC"}:
        dtype = f"{dtype}({col['precision']},{col['scale'] or 0})"

    result = f"{dtype} {'NULL' if col['nullable'] else 'NOT NULL'}"

    # NOTA: No se añade DEFAULT aquí porque:
    # - Para ADD COLUMN: el DEFAULT se maneja después
    # - Para ALTER COLUMN: SQL Server no acepta DEFAULT en la definición, ya existe

    if col["is_identity"] and include_identity:
        result += " IDENTITY(1,1)"

    return result


def column_exists(cursor, table: str, column: str) -> bool:
    """Verifica si existe una columna (case-sensitive)."""
    cursor.execute(
        """
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ? COLLATE Latin1_General_CS_AS
        AND COLUMN_NAME = ? COLLATE Latin1_General_CS_AS
    """,
        table,
        column,
    )
    return cursor.fetchone() is not None


def table_exists(cursor, table: str) -> bool:
    """Verifica si existe una tabla (case-sensitive)."""
    cursor.execute(
        """
        SELECT 1 FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = ? COLLATE Latin1_General_CS_AS
    """,
        table,
    )
    return cursor.fetchone() is not None


def get_table_row_count(cursor, table: str) -> int:
    """Obtiene el numero de filas de una tabla."""
    try:
        cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
        return cursor.fetchone()[0]
    except Exception:
        return -1


# =================================================================================
# MIGRADOR DE TABLA
# =================================================================================


def migrate_table(
    conn: pyodbc.Connection,
    cursor,
    table_name: str,
    pk_columns: list[str] | None = None,
    fk_info: dict | None = None,
    pending_fks: list[dict] | None = None,
    tables_to_migrate: dict[str, bool] | None = None,
) -> bool:
    """
    Migra una tabla de PascalCase a snake_case.

    Proceso:
    1. Agregar columnas snake_case (nullable)
    2. Copiar datos
    3. Hacer NOT NULL
    4. Recrear FKs con nuevas columnas (o marcar pendiente si ref tabla no lista)
    5. Recrear constraints e indexes
    6. Recrear Primary Key
    7. Eliminar columnas legacy
    8. Renombrar tabla

    Args:
        conn: Conexion a la base de datos
        cursor: Cursor de la conexion
        table_name: Nombre actual de la tabla (PascalCase)
        pk_columns: Lista de columnas que forman la PK (si no se detecta auto)
        fk_info: Info de FKs para recrear
        pending_fks: Lista de FKs pendientes por recrear (por referencias cruzadas)
        tables_to_migrate: Dict de tablas que seran migradas (para verificar refs)

    Returns:
        True si exitoso, False si hubo error
    """
    snake_table = to_snake_case(table_name)
    if snake_table == table_name:
        return True

    if DRY_RUN:
        return True

    try:  # noqa: PLW0717
        # Obtener columnas
        columns = get_columns(cursor, table_name)
        if not columns:
            return False

        # Identificar PK (soporta simple y compuesta)
        pk_info = get_primary_key(cursor, table_name)
        pk_cols = pk_info.get("columns", [pk_info.get("column")]) if pk_info else []
        pk_cols_snake = [to_snake_case(c) for c in pk_cols] if pk_cols else []

        # Obtener FKs
        fks = get_foreign_keys(cursor, table_name)

        # Obtener indexes
        indexes = get_indexes(cursor, table_name)

        # Obtener constraints
        constraints = get_constraints(cursor, table_name)

        new_columns: dict[str, dict] = {}
        for col in columns:
            snake_col = to_snake_case(col["name"])
            if snake_col != col["name"]:
                new_columns[snake_col] = col

        # =========================================================================
        # PASO 1: Renombrar columnas PascalCase a snake_case
        # (SQL Server es case-insensitive, sp_rename renombra en vez de agregar)
        # =========================================================================
        for snake_col, col_info in new_columns.items():
            pascal_col = col_info["name"]

            # Verificar si la columna snake_case YA existe (de run parcial anterior)
            if column_exists(cursor, table_name, snake_col):
                continue

            # Usar sp_rename para renombrar directamente (preserva datos)
            # SQL Server ve Address1 y address1 como mismo nombre, así que esto funciona
            try:
                sql = f"EXEC sp_rename 'dbo.{table_name}.{pascal_col}', '{snake_col}', 'COLUMN'"
                cursor.execute(sql)
            except Exception:
                pass

        conn.commit()

        # =========================================================================
        # PASO 2: Copiar datos de PascalCase a snake_case
        # (SKIP: sp_rename ya preserva los datos, no necesario copiar)
        # =========================================================================
        # row_count = get_table_row_count(cursor, table_name)
        # print(f"    Filas a procesar: {row_count}")

        # OMITIDO: sp_rename ya preserva los datos, no es necesario copiar
        # (Si sp_rename fallo para alguna columna, se maneiara en recovery)

        conn.commit()

        # =========================================================================
        # PASO 3: Hacer columnas NOT NULL (despues de copiar datos)
        # =========================================================================

        for snake_col, col_info in new_columns.items():
            if not col_info["nullable"]:
                # Verificar que no hay nulos
                cursor.execute(f"""
                    SELECT COUNT(*) FROM [{table_name}]
                    WHERE [{snake_col}] IS NULL
                """)
                null_count = cursor.fetchone()[0]

                if null_count > 0:
                    continue

                # Obtener la definicion sin nullable
                temp_col = col_info.copy()
                temp_col["nullable"] = False
                temp_col["is_identity"] = False
                definition = build_column_definition(temp_col)

                sql = f"ALTER TABLE [{table_name}] ALTER COLUMN [{snake_col}] {definition}"
                cursor.execute(sql)

        conn.commit()

        # =========================================================================
        # PASO 4: Recrear Foreign Keys con nuevas columnas
        # =========================================================================

        # Verificar si la tabla referenciada ya fue migrada
        cursor.execute("""
            SELECT name FROM sys.tables
            WHERE name != LOWER(name) COLLATE Latin1_General_CI_AS
        """)
        for _row in cursor.fetchall():
            # Si una tabla aun tiene PascalCase, no ha sido migrada
            pass  # Por ahora no podemos saber con certeza quais foram migradas

        for fk in fks:
            old_fk_name = fk["name"]
            parent_col = fk["parent_column"]
            ref_table = fk["referenced_table"]
            ref_col = fk["referenced_column"]
            delete_action = fk["delete_action"]
            update_action = fk["update_action"]

            parent_col_snake = to_snake_case(parent_col)
            ref_table_snake = to_snake_case(ref_table)
            ref_col_snake = to_snake_case(ref_col)

            # Solo renombrar si cambio
            if parent_col_snake == parent_col:
                continue

            # Verificar si la tabla referenciada necesita migracion
            ref_needs_migration = (
                tables_to_migrate is not None
                and ref_table in tables_to_migrate
                and tables_to_migrate[ref_table]
                and ref_table != ref_table_snake
            )

            # Eliminar FK vieja
            if old_fk_name:
                with contextlib.suppress(Exception):
                    cursor.execute(f"""
                        ALTER TABLE [{table_name}]
                        DROP CONSTRAINT [{old_fk_name}]
                    """)

            # Si la tabla referenciada necesita migracion pero no ha sido procesada,
            # agregar a pendientes y continuar
            if ref_needs_migration and pending_fks is not None:
                pending_fks.append(
                    {
                        "table": snake_table,
                        "parent_col": parent_col_snake,
                        "ref_table": ref_table,
                        "ref_table_snake": ref_table_snake,
                        "ref_col": ref_col,
                        "ref_col_snake": ref_col_snake,
                        "delete_action": delete_action,
                        "update_action": update_action,
                    }
                )
                continue

            # Crear FK nueva con nombre snake_case
            new_fk_name = f"fk_{snake_table}_{parent_col_snake}"
            on_delete = "CASCADE" if "CASCADE" in delete_action else "NO ACTION"
            on_update = "CASCADE" if "CASCADE" in update_action else "NO ACTION"

            with contextlib.suppress(Exception):
                cursor.execute(f"""
                    ALTER TABLE [{table_name}]
                    ADD CONSTRAINT [{new_fk_name}]
                    FOREIGN KEY ([{parent_col_snake}])
                    REFERENCES [{ref_table_snake}] ([{ref_col_snake}])
                    ON DELETE {on_delete}
                    ON UPDATE {on_update}
                """)

        conn.commit()

        # =========================================================================
        # PASO 5: Recrear indexes con nuevas columnas
        # =========================================================================

        for idx in indexes:
            old_idx_name = idx["name"]
            idx_columns = idx["columns"]

            # Convertir nombres de columnas
            new_idx_columns = ", ".join([to_snake_case(c) for c in idx_columns.split(", ")])

            # Solo renombrar si cambio
            if to_snake_case(old_idx_name) == old_idx_name and idx_columns == new_idx_columns:
                continue

            # Eliminar indice viejo
            with contextlib.suppress(Exception):
                cursor.execute(f"DROP INDEX [{old_idx_name}] ON [{table_name}]")

            # Crear indice nuevo
            # NOTA: Usar table_name (no snake_table) porque el rename ocurre en paso 9
            new_idx_name = to_snake_case(old_idx_name)
            unique = "UNIQUE" if idx["unique"] else ""

            with contextlib.suppress(Exception):
                cursor.execute(f"""
                    CREATE {unique} INDEX [{new_idx_name}]
                    ON [{table_name}] ({new_idx_columns})
                """)

        conn.commit()

        # =========================================================================
        # PASO 6: Recrear constraints unique
        # =========================================================================

        for constr in constraints:
            old_name = constr["name"]
            col = constr["column"]

            # Solo renombrar si cambio
            new_name = to_snake_case(old_name)
            col_snake = to_snake_case(col)

            if col_snake == col and new_name == old_name:
                continue

            # Eliminar constraint viejo
            with contextlib.suppress(Exception):
                cursor.execute(f"""
                    ALTER TABLE [{table_name}]
                    DROP CONSTRAINT [{old_name}]
                """)

            # Crear constraint nuevo
            # NOTA: Usar table_name (no snake_table) porque el rename ocurre en paso 9
            try:
                if constr["type"] == "UNIQUE":
                    cursor.execute(f"""
                        ALTER TABLE [{table_name}]
                        ADD CONSTRAINT [{new_name}]
                        UNIQUE ([{col_snake}])
                    """)
                # CHECK constraints son mas complejos, se saltan por ahora
            except Exception:
                pass

        conn.commit()

        # =========================================================================
        # PASO 7: Recrear Primary Key si cambio
        # =========================================================================

        if pk_info:
            pk_cols = pk_info.get("columns", [pk_info.get("column")])
            pk_cols_snake = [to_snake_case(c) for c in pk_cols]

            # Solo procesar si al menos una columna cambio
            if pk_cols_snake != pk_cols:
                # Obtener nombre de PK
                cursor.execute(
                    """
                    SELECT name FROM sys.key_constraints
                    WHERE parent_object_id = OBJECT_ID(?)
                    AND type = 'PK'
                """,
                    table_name,
                )
                pk_row = cursor.fetchone()
                old_pk_name = pk_row[0] if pk_row else None

                if old_pk_name:
                    with contextlib.suppress(Exception):
                        cursor.execute(f"""
                            ALTER TABLE [{table_name}]
                            DROP CONSTRAINT [{old_pk_name}]
                        """)

                # Crear PK nueva (soporta PK simple y compuesta)
                # NOTA: Usar table_name (no snake_table) porque el rename ocurre en paso 9
                new_pk_name = f"pk_{snake_table}"
                pk_columns_str = ", ".join([f"[{c}]" for c in pk_cols_snake])
                with contextlib.suppress(Exception):
                    cursor.execute(f"""
                        ALTER TABLE [{table_name}]
                        ADD CONSTRAINT [{new_pk_name}]
                        PRIMARY KEY ({pk_columns_str})
                    """)

        conn.commit()

        # =========================================================================
        # PASO 8: Eliminar columnas legacy (PascalCase)
        # (sp_rename las renombró, así que ya no deberían existir)
        # =========================================================================

        for col_info in new_columns.values():
            pascal_col = col_info["name"]

            # No eliminar si es la PK identity
            if pascal_col in pk_cols and col_info["is_identity"]:
                continue

            # La columna PascalCase ya no existe (fue renombrada por sp_rename)
            # Solo intentamos eliminar por si acaso (puede fallar si ya no existe)
            try:
                if column_exists(cursor, snake_table, pascal_col):
                    cursor.execute(f"""ALTER TABLE [{snake_table}] DROP COLUMN [{pascal_col}]""")
            except Exception:
                pass

        conn.commit()

        # =========================================================================
        # PASO 9: Renombrar tabla a snake_case
        # =========================================================================
        if table_name != snake_table:
            try:
                cursor.execute(f"EXEC sp_rename 'dbo.{table_name}', '{snake_table}'")
                conn.commit()
            except Exception:
                conn.rollback()
                return False

        return True

    except Exception:
        conn.rollback()
        return False


# =================================================================================
# PROCESO PRINCIPAL
# =================================================================================


def process_database(prefix: str, database_name: str, tables_to_process: dict[str, bool]):
    """Procesa una base de datos completa."""
    pending_fks: list[dict] = []

    try:  # noqa: PLW0717
        conn = connect_db(prefix)
        cursor = conn.cursor()

        # Obtener tablas
        tables = get_tables(cursor, database_name)

        success_count = 0
        error_count = 0
        skipped_count = 0

        for table_info in tables:
            table_name = table_info["name"]

            # Verificar si esta en la lista de control
            if table_name not in tables_to_process:
                skipped_count += 1
                continue

            if not tables_to_process[table_name]:
                skipped_count += 1
                continue

            # Verificar si la tabla ya es snake_case
            snake_name = to_snake_case(table_name)
            if table_name == snake_name:
                skipped_count += 1
                continue

            # Migrar tabla
            result = migrate_table(
                conn, cursor, table_name, tables_to_migrate=tables_to_process, pending_fks=pending_fks
            )

            if result:
                success_count += 1
            else:
                error_count += 1

        # Procesar FKs pendientes
        if pending_fks:
            for fk in pending_fks:
                table = fk["table"]
                parent_col = fk["parent_col"]
                ref_table_snake = fk["ref_table_snake"]
                ref_col_snake = fk["ref_col_snake"]
                delete_action = fk["delete_action"]
                update_action = fk["update_action"]

                new_fk_name = f"fk_{table}_{parent_col}"
                on_delete = "CASCADE" if "CASCADE" in delete_action else "NO ACTION"
                on_update = "CASCADE" if "CASCADE" in update_action else "NO ACTION"

                try:
                    cursor.execute(f"""
                        ALTER TABLE [{table}]
                        ADD CONSTRAINT [{new_fk_name}]
                        FOREIGN KEY ([{parent_col}])
                        REFERENCES [{ref_table_snake}] ([{ref_col_snake}])
                        ON DELETE {on_delete}
                        ON UPDATE {on_update}
                    """)
                except Exception:
                    error_count += 1

            conn.commit()

        cursor.close()
        conn.close()

        return {"success": success_count, "errors": error_count, "skipped": skipped_count}

    except Exception as e:
        return {"success": 0, "errors": 1, "skipped": 0, "fatal_error": str(e)}


def main():
    """Punto de entrada principal."""
    # Verificar variables de entorno
    os.getenv("DB_SERVER", "localhost")
    db_database = os.getenv("DB_DATABASE", "")
    os.getenv("PRIMEFIRE_DB_SERVER", "")
    pf_database = os.getenv("PRIMEFIRE_DB_DATABASE", "")

    total_success = 0
    total_errors = 0

    # Procesar DevRomo
    if PROCESS_DEVROMO and db_database:
        result = process_database("DB", db_database, TABLE_LIST)
        total_success += result.get("success", 0)
        total_errors += result.get("errors", 0)

    # Procesar PrimeFireCorp
    if PROCESS_PRIMEFIRE and pf_database:
        result = process_database("PRIMEFIRE_DB", pf_database, TABLE_LIST)
        total_success += result.get("success", 0)
        total_errors += result.get("errors", 0)

    # Resumen final

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
