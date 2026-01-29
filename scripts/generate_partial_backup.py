import argparse
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from bd.connection import SessionLocal
from sqlalchemy import text

def get_all_tables(session):
    """Get all user tables in the database"""
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
    """Get foreign key constraints for a table"""
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
    """Get primary key constraint for a table"""
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
    return pk if pk else None

def get_table_data(session, table_name):
    """Get all data from a table"""
    try:
        result = session.exec(text(f"SELECT * FROM [{table_name}]"))
        columns = result.keys()
        rows = result.fetchall()
        return columns, rows
    except Exception as e:
        print(f"Error getting data from {table_name}: {e}")
        return None, []

def format_value(value):
    """Format a value for SQL INSERT"""
    if value is None:
        return 'NULL'
    elif isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"N'{escaped}'"
    elif isinstance(value, (int, float, bool)):
        return str(int(value) if isinstance(value, bool) else value)
    elif isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    else:
        return f"'{str(value)}'"

def generate_partial_backup(tables_with_data=None, target_table=None):
    """
    Generate partial backup: ALL table structures, but data only for specified tables
    
    Args:
        tables_with_data: List of table names to include data. 
                         Default: ['Countries', 'Roles', 'Modules', 'RoleModules']
    """
    
    if tables_with_data is None:
        tables_with_data = ['Countries', 'Roles', 'Modules', 'RoleModules']
    
    output_file = f"bd/sql/partial_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("USE [primefirebd]\n")
        f.write("GO\n\n")
        f.write("/****** PARTIAL DATABASE BACKUP ******/\n")
        f.write(f"/****** Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ******/\n")
        f.write(f"/****** This script contains ALL table structures and data for: {', '.join(tables_with_data)} ******/\n\n")
        
        with SessionLocal() as session:
            # Get all tables or a single table
            all_tables = get_all_tables(session)
            if target_table:
                if target_table not in all_tables:
                    raise ValueError(f"Table '{target_table}' not found in database")
                tables = [target_table]
                tables_with_data = [target_table]
            else:
                tables = all_tables
            print(f"Found {len(tables)} tables")
            
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
                print(f"Creating table: {table}")
                
                f.write(f"-- =============================================\n")
                f.write(f"-- Table: {table}\n")
                f.write(f"-- =============================================\n\n")
                
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
                    
                    if data_type in ('varchar', 'char', 'nvarchar', 'nchar'):
                        size = 'MAX' if max_length == -1 else str(max_length)
                        col_def += f"({size})"
                    elif data_type in ('decimal', 'numeric'):
                        col_def += f"({precision},{scale})"
                    
                    if is_identity:
                        col_def += " IDENTITY(1,1)"
                    
                    col_def += " NOT NULL" if is_nullable == 'NO' else " NULL"
                    
                    if default:
                        col_def += f" DEFAULT {default}"
                    
                    col_definitions.append(col_def)
                
                # Add primary key to CREATE TABLE
                pk = get_primary_key(session, table)
                if pk:
                    pk_name, pk_cols = pk
                    pk_cols_formatted = ','.join([f"[{c.strip()}] ASC" for c in pk_cols.split(',')])
                    col_definitions.append(f" CONSTRAINT [{pk_name}] PRIMARY KEY CLUSTERED\n(\n    {pk_cols_formatted}\n)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]")
                
                f.write(',\n'.join(col_definitions))
                f.write("\n) ON [PRIMARY]\n")
                f.write("GO\n\n")
            
            # Third pass: Insert data for specific tables only
            f.write("\n-- =============================================\n")
            f.write("-- INSERT DATA FOR SPECIFIC TABLES\n")
            f.write("-- =============================================\n\n")
            
            total_records = 0
            
            for table in tables_with_data:
                if table not in tables:
                    print(f"Warning: Table '{table}' not found in database")
                    continue
                
                print(f"Inserting data for: {table}")
                    
                columns, rows = get_table_data(session, table)
                
                if rows:
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
                        col_names = ', '.join([f"[{col}]" for col in columns])
                        values = ', '.join([format_value(val) for val in row])
                        f.write(f"INSERT [dbo].[{table}] ({col_names}) VALUES ({values})\n")
                    
                    if has_identity:
                        f.write(f"\nSET IDENTITY_INSERT [dbo].[{table}] OFF\n")
                    
                    f.write("GO\n\n")
            
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
                    
                    if delete_action != 'NO_ACTION':
                        f.write(f"ON DELETE {delete_action.replace('_', ' ')}\n")
                    if update_action != 'NO_ACTION':
                        f.write(f"ON UPDATE {update_action.replace('_', ' ')}\n")
                    
                    f.write("GO\n")
                    f.write(f"ALTER TABLE [dbo].[{parent_table}] CHECK CONSTRAINT [{fk_name}]\n")
                    f.write("GO\n\n")
            
            # Summary
            f.write("\n-- =============================================\n")
            f.write("-- BACKUP SUMMARY\n")
            f.write("-- =============================================\n")
            f.write(f"-- Total Tables: {len(tables)}\n")
            f.write(f"-- Tables with data: {', '.join(tables_with_data)}\n")
            
            for table in tables_with_data:
                if table in tables:
                    _, rows = get_table_data(session, table)
                    f.write(f"--   {table}: {len(rows)} records\n")
            
            f.write(f"-- Total Records: {total_records}\n")
            f.write("-- =============================================\n")
            f.write("\nPRINT 'Partial backup restored successfully!'\n")
            f.write(f"PRINT 'Total records inserted: {total_records}'\n")
            f.write("GO\n")
    
    print(f"\n[OK] Partial backup generated: {output_file}")
    print(f"   - {len(tables)} tables created")
    print(f"   - Data included for: {', '.join(tables_with_data)}")
    print(f"   - {total_records} total records")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate partial database backup")
    parser.add_argument("--table", help="Backup a single table only")
    args = parser.parse_args()
    generate_partial_backup(target_table=args.table)
