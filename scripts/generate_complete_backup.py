import argparse
import os
import pathlib
import sys
from datetime import datetime

project_root = pathlib.Path(pathlib.Path(__file__).parent).parent
sys.path.insert(0, str(project_root / "bd"))
sys.path.insert(0, str(project_root))

# Crear carpeta de backups si no existe
backup_dir = os.path.join(project_root, "bd", "sql", "backups")  # noqa: PTH118
pathlib.Path(backup_dir).mkdir(exist_ok=True, parents=True)

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session

from connection import create_engine_from_env


def get_session_local(db_prefix="DB"):
    """Create a session maker for the specified database prefix."""
    engine = create_engine_from_env(db_prefix)
    return sessionmaker(bind=engine, class_=Session)


def get_all_tables(session):
    """Get all user tables in the database."""
    query = """
    SELECT TABLE_NAME
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    AND TABLE_SCHEMA = 'dbo'
    ORDER BY TABLE_NAME
    """
    result = session.exec(text(query))
    return [row[0] for row in result.fetchall()]


def get_foreign_keys(session, table_name):
    """Get foreign key constraints for a table."""
    query = f"""
    SELECT
        fk.name AS FK_Name,
        tp.name AS Parent_Table,
        cp.name AS Parent_Column,
        tr.name AS Referenced_Table,
        cr.name AS Referenced_Column,
        fk.delete_referential_action_desc AS Delete_Action,
        fk.update_referential_action_desc AS Update_Action
    FROM sys.foreign_keys fk
    INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
    INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
    INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
    INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
    INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
    WHERE tp.name = '{table_name}'
    """
    result = session.exec(text(query))
    return result.fetchall()


def get_primary_key(session, table_name):
    """Get primary key constraint for a table."""
    query = f"""
    SELECT
        kc.name AS PK_Name,
        STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS PK_Columns
    FROM sys.key_constraints kc
    INNER JOIN sys.index_columns ic ON kc.parent_object_id = ic.object_id AND kc.unique_index_id = ic.index_id
    INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    WHERE kc.type = 'PK' AND OBJECT_NAME(kc.parent_object_id) = '{table_name}'
    GROUP BY kc.name
    """
    result = session.exec(text(query))
    pk = result.fetchone()
    return pk or None


def get_table_data(session, table_name):
    """Get all data from a table."""
    try:
        result = session.exec(text(f"SELECT * FROM [{table_name}]"))
        columns = result.keys()
        rows = result.fetchall()
        return columns, rows
    except Exception:
        return None, []


def format_value(value):
    """Format a value for SQL INSERT."""
    if value is None:
        return "NULL"
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"N'{escaped}'"
    if isinstance(value, (int, float, bool)):
        return str(int(value) if isinstance(value, bool) else value)
    if isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    return f"'{value!s}'"


def get_table_dependencies(session):
    """Get table dependencies to determine insert order."""
    query = """
    SELECT
        OBJECT_NAME(fkc.parent_object_id) AS DependentTable,
        OBJECT_NAME(fkc.referenced_object_id) AS ReferencedTable
    FROM sys.foreign_key_columns fkc
    GROUP BY fkc.parent_object_id, fkc.referenced_object_id
    ORDER BY OBJECT_NAME(fkc.referenced_object_id)
    """
    result = session.exec(text(query))
    return result.fetchall()


def topological_sort_tables(tables, dependencies):
    """Sort tables in dependency order for data insertion."""
    dep_map = {}
    for table in tables:
        dep_map[table] = []

    for dep_table, ref_table in dependencies:
        if dep_table in dep_map and ref_table in dep_map and dep_table != ref_table:
            dep_map[dep_table].append(ref_table)

    sorted_tables = []
    visited = set()

    def visit(table) -> None:
        if table in visited:
            return
        visited.add(table)
        for dep in dep_map.get(table, []):
            visit(dep)
        sorted_tables.append(table)

    for table in tables:
        visit(table)

    return sorted_tables


def generate_complete_backup(target_table=None, db_prefix="DB", backup_dir=None) -> None:
    """Generate complete backup of entire database with ALL data.

    Args:
        target_table: Optional single table to backup
        db_prefix: Database prefix for environment variables (e.g., 'DB', 'PRIMEFIRE_DB')
        backup_dir: Custom backup directory (optional)
    """
    SessionLocal = get_session_local(db_prefix)
    database_name = os.getenv(f"{db_prefix}_DATABASE", "unknown")
    server_name = os.getenv(f"{db_prefix}_SERVER", "unknown")

    # Usar directorio por defecto si no se especifica
    if backup_dir is None:
        backup_dir = os.path.join(pathlib.Path(pathlib.Path(__file__).parent).parent, "bd", "sql", "backups")  # noqa: PTH118

    pathlib.Path(backup_dir).mkdir(exist_ok=True, parents=True)
    output_file = os.path.join(  # noqa: PTH118
        backup_dir,
        f"complete_backup_{database_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",  # noqa: DTZ005
    )

    with pathlib.Path(output_file).open("w", encoding="utf-8") as f:
        f.write(f"USE [{database_name}]\n")
        f.write("GO\n\n")
        f.write("/****** COMPLETE DATABASE BACKUP WITH ALL DATA ******/\n")
        f.write(f"/****** Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ******/\n")  # noqa: DTZ005
        f.write(f"/****** Database: {database_name} on {server_name} ******/\n")
        f.write("/****** This script contains ALL table structures and ALL data ******/\n\n")

        with SessionLocal() as session:
            # Get all tables or a single table
            all_tables = get_all_tables(session)
            if target_table:
                if target_table not in all_tables:
                    raise ValueError(f"Table '{target_table}' not found in database")
                tables = [target_table]
            else:
                tables = all_tables

            # Get dependencies for proper insert order
            dependencies = get_table_dependencies(session)
            sorted_tables = topological_sort_tables(tables, dependencies)

            # First pass: Drop all tables
            f.write("-- =============================================\n")
            f.write("-- DROP ALL TABLES\n")
            f.write("-- =============================================\n\n")

            # Drop tables in reverse order to handle FK dependencies
            for table in reversed(tables):
                f.write(f"IF OBJECT_ID('dbo.{table}', 'U') IS NOT NULL\n")
                f.write(f"    DROP TABLE dbo.{table};\n")
                f.write("GO\n\n")

            # Second pass: Create all tables
            f.write("\n-- =============================================\n")
            f.write("-- CREATE ALL TABLES\n")
            f.write("-- =============================================\n\n")

            for table in tables:
                f.write("-- =============================================\n")
                f.write(f"-- Table: {table}\n")
                f.write("-- =============================================\n\n")

                # Get columns info
                columns_query = f"""
                SELECT
                    c.COLUMN_NAME,
                    c.DATA_TYPE,
                    c.CHARACTER_MAXIMUM_LENGTH,
                    c.NUMERIC_PRECISION,
                    c.NUMERIC_SCALE,
                    c.IS_NULLABLE,
                    c.COLUMN_DEFAULT,
                    COLUMNPROPERTY(OBJECT_ID('{table}'), c.COLUMN_NAME, 'IsIdentity') AS IS_IDENTITY
                FROM INFORMATION_SCHEMA.COLUMNS c
                WHERE c.TABLE_NAME = '{table}'
                ORDER BY c.ORDINAL_POSITION
                """

                cols_result = session.exec(text(columns_query))
                columns = cols_result.fetchall()

                # Build CREATE TABLE statement
                f.write(f"CREATE TABLE [dbo].[{table}](\n")

                col_definitions = []
                for col in columns:
                    col_name, data_type, max_length, precision, scale, is_nullable, default, is_identity = col

                    col_def = f"    [{col_name}] [{data_type}]"

                    if data_type in {"varchar", "char", "nvarchar", "nchar"}:
                        size = "MAX" if max_length == -1 else str(max_length)
                        col_def += f"({size})"
                    elif data_type in {"decimal", "numeric"}:
                        col_def += f"({precision},{scale})"

                    if is_identity:
                        col_def += " IDENTITY(1,1)"

                    col_def += " NOT NULL" if is_nullable == "NO" else " NULL"

                    if default:
                        col_def += f" DEFAULT {default}"

                    col_definitions.append(col_def)

                # Add primary key to CREATE TABLE
                pk = get_primary_key(session, table)
                if pk:
                    pk_name, pk_cols = pk
                    pk_cols_formatted = ",".join([f"[{c.strip()}] ASC" for c in pk_cols.split(",")])
                    col_definitions.append(
                        f" CONSTRAINT [{pk_name}] PRIMARY KEY CLUSTERED\n(\n    {pk_cols_formatted}\n)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]"
                    )

                f.write(",\n".join(col_definitions))
                f.write("\n) ON [PRIMARY]\n")
                f.write("GO\n\n")

            # Third pass: Insert data for ALL tables in dependency order
            f.write("\n-- =============================================\n")
            f.write("-- INSERT DATA FOR ALL TABLES\n")
            f.write("-- =============================================\n\n")

            total_records = 0
            tables_with_data = []

            for table in sorted_tables:
                if table not in tables:
                    continue

                columns, rows = get_table_data(session, table)

                if rows:
                    tables_with_data.append((table, len(rows)))
                    total_records += len(rows)

                    f.write(f"\n-- Data for {table} ({len(rows)} records)\n")

                    # Check if table has identity column
                    has_identity_query = f"""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table}'
                    AND COLUMNPROPERTY(OBJECT_ID('{table}'), COLUMN_NAME, 'IsIdentity') = 1
                    """
                    has_identity_result = session.exec(text(has_identity_query))
                    has_identity = has_identity_result.fetchone()[0] > 0

                    if has_identity:
                        f.write(f"SET IDENTITY_INSERT [dbo].[{table}] ON\n")
                        f.write("GO\n\n")

                    for row in rows:
                        col_names = ", ".join([f"[{col}]" for col in columns])
                        values = ", ".join([format_value(val) for val in row])
                        f.write(f"INSERT [dbo].[{table}] ({col_names}) VALUES ({values})\n")

                    if has_identity:
                        f.write(f"\nSET IDENTITY_INSERT [dbo].[{table}] OFF\n")

                    f.write("GO\n\n")
                else:
                    f.write(f"\n-- {table}: No data to insert\n\n")

            # Fourth pass: Add foreign keys
            f.write("\n-- =============================================\n")
            f.write("-- FOREIGN KEYS\n")
            f.write("-- =============================================\n\n")

            tables_set = set(tables)
            for table in tables:
                fks = get_foreign_keys(session, table)
                for fk in fks:
                    fk_name, parent_table, parent_col, ref_table, ref_col, delete_action, update_action = fk
                    if parent_table not in tables_set or ref_table not in tables_set:
                        continue

                    f.write(f"ALTER TABLE [dbo].[{parent_table}] WITH CHECK ADD CONSTRAINT [{fk_name}]\n")
                    f.write(f"FOREIGN KEY([{parent_col}])\n")
                    f.write(f"REFERENCES [dbo].[{ref_table}] ([{ref_col}])\n")

                    if delete_action != "NO_ACTION":
                        f.write(f"ON DELETE {delete_action.replace('_', ' ')}\n")
                    if update_action != "NO_ACTION":
                        f.write(f"ON UPDATE {update_action.replace('_', ' ')}\n")

                    f.write("GO\n")
                    f.write(f"ALTER TABLE [dbo].[{parent_table}] CHECK CONSTRAINT [{fk_name}]\n")
                    f.write("GO\n\n")

            # Summary
            f.write("\n-- =============================================\n")
            f.write("-- BACKUP SUMMARY\n")
            f.write("-- =============================================\n")
            f.write(f"-- Total Tables: {len(tables)}\n")
            f.write(f"-- Total Records: {total_records}\n")
            f.write("-- \n")
            f.write("-- Data per table:\n")

            for table, count in tables_with_data:
                f.write(f"--   {table}: {count} records\n")

            f.write("-- =============================================\n")
            f.write("\nPRINT 'Complete backup restored successfully!'\n")
            f.write(f"PRINT 'Total records inserted: {total_records}'\n")
            f.write("GO\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate complete database backup")
    parser.add_argument("--table", help="Backup a single table only")
    parser.add_argument(
        "--db", default="DB", help="Database prefix for environment variables (e.g., DB, PRIMEFIRE_DB). Default: DB"
    )
    parser.add_argument("--backup-dir", default=None, help="Custom backup directory (optional)")
    args = parser.parse_args()
    generate_complete_backup(target_table=args.table, db_prefix=args.db, backup_dir=args.backup_dir)
