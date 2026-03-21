"""
MIGRACION COMPLETA: PascalCase -> snake_case (TODO EN UNA SOLA VUELLA)

Estrategia correcta:
1. Renombrar tablas
2. Agregar columnas snake_case
3. Copiar datos
4. Hacer NOT NULL las snake_case (si tienen datos)
5. Eliminar TODAS las constraints (PK, FK, DEFAULT) de columnas PascalCase
6. Eliminar columnas PascalCase
7. Recrear PKs en snake_case
8. Recrear FKs en snake_case
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pyodbc
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    "DevRomo": {
        "server": os.getenv("DB_SERVER", "localhost"),
        "database": os.getenv("DB_DATABASE", "DevRomo"),
        "driver": os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}"),
    },
    "PrimeFireCorp": {
        "server": os.getenv("PRIMEFIRE_DB_SERVER", "localhost"),
        "database": os.getenv("PRIMEFIRE_DB_DATABASE", "PrimeFireCorp"),
        "driver": os.getenv("PRIMEFIRE_DB_DRIVER", "{ODBC Driver 17 for SQL Server}"),
    },
}

ACTIVE_DB = None


def get_conn():
    db_config = DATABASES[ACTIVE_DB]
    return pyodbc.connect(
        f"DRIVER={db_config['driver']};SERVER={db_config['server']};DATABASE={db_config['database']};Trusted_Connection=yes;TrustServerCertificate=yes"
    )


def table_exists(name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{name}' AND TABLE_SCHEMA = 'dbo'")
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return exists


def col_exists(table, col):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' AND COLUMN_NAME = '{col}' AND TABLE_SCHEMA = 'dbo'")
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    conn.close()
    return exists


def exec_sql(sql, desc="", quiet=False):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        if not quiet:
            print(f"    [OK] {desc}")
        return True, None
    except Exception as e:
        cursor.close()
        conn.close()
        if not quiet:
            print(f"    [ERROR] {desc}: {e}")
        return False, str(e)


def drop_all_constraints():
    """Drop ALL constraints in the database - PKs, FKs, DEFAULTs"""
    conn = get_conn()
    cursor = conn.cursor()

    # Drop all DEFAULT constraints
    try:
        cursor.execute("""
            SELECT 'ALTER TABLE [' + OBJECT_SCHEMA_NAME(dc.parent_object_id) + '].[' + OBJECT_NAME(dc.parent_object_id) +
                          '] DROP CONSTRAINT [' + dc.name + ']'
            FROM sys.default_constraints dc
        """)
        for row in cursor.fetchall():
            sql = row[0]
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"    [OK] DEFAULT constraint dropped")
            except:
                pass
    except Exception as e:
        print(f"    [WARN] Error dropping defaults: {e}")

    # Drop all FK constraints
    try:
        cursor.execute("""
            SELECT 'ALTER TABLE [' + OBJECT_SCHEMA_NAME(fk.parent_object_id) + '].[' + OBJECT_NAME(fk.parent_object_id) +
                          '] DROP CONSTRAINT [' + fk.name + ']'
            FROM sys.foreign_keys fk
        """)
        for row in cursor.fetchall():
            sql = row[0]
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"    [OK] FK dropped")
            except:
                pass
    except Exception as e:
        print(f"    [WARN] Error dropping FKs: {e}")

    # Drop all PK constraints (will fail if referenced by FKs, but we already tried to drop FKs)
    try:
        cursor.execute("""
            SELECT 'ALTER TABLE [' + OBJECT_SCHEMA_NAME(i.object_id) + '].[' + OBJECT_NAME(i.object_id) +
                          '] DROP CONSTRAINT [' + i.name + ']'
            FROM sys.indexes i
            WHERE i.is_primary_key = 1
        """)
        for row in cursor.fetchall():
            sql = row[0]
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"    [OK] PK dropped")
            except:
                pass
    except Exception as e:
        print(f"    [WARN] Error dropping PKs: {e}")

    cursor.close()
    conn.close()


def col_has_data(table, col):
    """Check if column has any non-NULL data"""
    reserved = {"key", "order", "group", "user", "password", "date", "time", "text"}
    col_q = f"[{col}]" if col.lower() in reserved else col
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM dbo.{table} WHERE {col_q} IS NOT NULL")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return count > 0
    except:
        cursor.close()
        conn.close()
        return False


# Tablas a renombrar
TABLE_RENAMES = {
    "Addresses": "addresses",
    "Countries": "countries",
    "Curriculums": "curriculums",
    "Departments": "departments",
    "Employees": "employees",
    "ExternalUsers": "external_users",
    "HardwareInventory": "hardware_inventory",
    "Holidays": "holidays",
    "Jobs": "jobs",
    "Licenses": "licenses",
    "Modules": "modules",
    "Products": "products",
    "QuotationItems": "quotation_items",
    "Quotations": "quotations",
    "Roles": "roles",
    "Tenants": "tenants",
    "Tickets": "tickets",
    "TicketAttachments": "ticket_attachments",
    "TicketMessages": "ticket_messages",
    "TimeOffBalances": "time_off_balances",
    "TimeOffRequests": "time_off_requests",
    "TimesheetLocationSnapshots": "timesheet_location_snapshots",
    "TimesheetPunches": "timesheet_punches",
    "TimesheetSettings": "timesheet_settings",
}

# Columnas a agregar (snake_case) con su tipo de datos
COLUMNS_TO_ADD = {
    "addresses": [
        ("address_id", "INT"),
        ("address_1", "NVARCHAR(200)"),
        ("address_2", "NVARCHAR(200)"),
        ("city", "NVARCHAR(100)"),
        ("state", "NVARCHAR(100)"),
        ("zip_code", "NVARCHAR(20)"),
        ("country_id", "INT"),
        ("google_place_id", "NVARCHAR(255)"),
        ("is_validated", "BIT"),
        ("validated_at", "DATETIME"),
        ("created_at", "DATETIME"),
    ],
    "countries": [
        ("country_id", "INT"),
    ],
    "curriculums": [
        ("curriculum_id", "INT"),
        ("job_id", "INT"),
        ("curriculum_path", "NVARCHAR(255)"),
        ("cover_letter", "NVARCHAR(1000)"),
        ("submitted_at", "DATETIME"),
        ("employee_id", "INT"),
    ],
    "customer_alternate_contacts": [
        ("customer_alternate_contact_id", "INT"),
        ("customer_id", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ],
    "customer_attachments": [
        ("customer_attachment_id", "INT"),
        ("customer_id", "INT"),
        ("created_at", "DATETIME"),
        ("created_by", "INT"),
    ],
    "customer_notes": [
        ("customer_note_id", "INT"),
        ("customer_id", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("created_by", "INT"),
    ],
    "customers": [
        ("customer_id", "INT"),
        ("customer_type", "NVARCHAR(20)"),
        ("dtd_potential", "NVARCHAR(20)"),
        ("primary_address_id", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("created_by", "INT"),
        ("company_name", "NVARCHAR(200)"),
        ("first_name", "NVARCHAR(100)"),
        ("last_name", "NVARCHAR(100)"),
        ("additional_name", "NVARCHAR(100)"),
        ("primary_email", "NVARCHAR(255)"),
        ("primary_phone", "NVARCHAR(20)"),
    ],
    "departments": [
        ("department_id", "INT"),
    ],
    "employee_roles": [
        ("employee_id", "INT"),
        ("role_id", "INT"),
    ],
    "employees": [
        ("first_name", "NVARCHAR(50)"),
        ("last_name", "NVARCHAR(50)"),
        ("display_name", "NVARCHAR(100)"),
        ("mobile_phone", "NVARCHAR(20)"),
        ("office_phone", "NVARCHAR(20)"),
        ("manager_email", "NVARCHAR(100)"),
        ("street_address", "NVARCHAR(100)"),
        ("postal_code", "NVARCHAR(20)"),
        ("azure_oid", "NVARCHAR(100)"),
        ("azure_upn", "NVARCHAR(100)"),
        ("password_hash", "NVARCHAR(255)"),
        ("last_synced_at", "DATETIME"),
        ("country_id", "INT"),
        ("manager_employee_id", "INT"),
    ],
    "external_users": [
        ("external_user_id", "INT"),
        ("password_hash", "NVARCHAR(255)"),
        ("tenant_id", "INT"),
        ("created_at", "DATETIME"),
    ],
    "hardware_inventory": [
        ("hardware_id", "INT"),
        ("serial_number", "NVARCHAR(50)"),
        ("device_type", "NVARCHAR(20)"),
        ("storage_type", "NVARCHAR(20)"),
        ("storage_size_gb", "INT"),
        ("operating_system", "NVARCHAR(100)"),
        ("warranty_start_date", "DATE"),
        ("warranty_end_date", "DATE"),
        ("purchase_date", "DATE"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("employee_id", "INT"),
    ],
    "holidays": [
        ("holiday_id", "INT"),
    ],
    "jobs": [
        ("job_id", "INT"),
        ("salary_min", "DECIMAL(18,2)"),
        ("salary_max", "DECIMAL(18,2)"),
        ("posted_at", "DATETIME"),
        ("employee_id", "INT"),
        ("country_id", "INT"),
    ],
    "licenses": [
        ("license_id", "INT"),
        ("created_at", "DATE"),
        ("expiry_date", "DATE"),
        ("employee_id", "INT"),
    ],
    "modules": [
        ("module_id", "INT"),
        ("module_name", "NVARCHAR(50)"),
        ("module_key", "NVARCHAR(50)"),
        ("route_url", "NVARCHAR(100)"),
        ("display_order", "INT"),
        ("is_active", "BIT"),
        ("parent_module_id", "INT"),
    ],
    "products": [
        ("id", "INT"),
        ("unit_price", "DECIMAL(18,2)"),
        ("cost", "DECIMAL(18,2)"),
        ("tax_rate", "DECIMAL(5,2)"),
        ("stock_quantity", "INT"),
        ("is_active", "BIT"),
        ("created_at", "DATETIME"),
    ],
    "quotation_items": [
        ("id", "INT"),
        ("quotation_id", "INT"),
        ("product_id", "INT"),
        ("unit_price", "DECIMAL(18,2)"),
    ],
    "quotations": [
        ("id", "INT"),
        ("customer_id", "INT"),
        ("quote_date", "DATETIME"),
        ("expiration_date", "DATETIME"),
        ("created_at", "DATETIME"),
    ],
    "role_modules": [
        ("role_id", "INT"),
        ("module_id", "INT"),
        ("can_view", "BIT"),
        ("can_create", "BIT"),
        ("can_edit", "BIT"),
        ("can_delete", "BIT"),
        ("can_export", "BIT"),
        ("admin_actions", "BIT"),
        ("other_actions", "BIT"),
        ("assigned_at", "DATETIME"),
    ],
    "roles": [
        ("role_id", "INT"),
        ("role_name", "NVARCHAR(50)"),
    ],
    "tenant_employees": [
        ("id", "INT"),
        ("tenant_id", "INT"),
        ("password_hash", "NVARCHAR(255)"),
        ("created_at", "DATETIME"),
    ],
    "tenant_logos": [
        ("logo_id", "INT"),
        ("tenant_id", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("path_background", "NVARCHAR(500)"),
        ("primary_color", "NVARCHAR(50)"),
        ("secondary_color", "NVARCHAR(50)"),
        ("tertiary_color", "NVARCHAR(50)"),
        ("fav_icon", "NVARCHAR(500)"),
    ],
    "tenants": [
        ("tenant_id", "INT"),
        ("created_at", "DATETIME"),
        ("is_active", "BIT"),
        ("db_connection_key", "NVARCHAR(50)"),
    ],
    "ticket_attachments": [
        ("ticket_attachment_id", "INT"),
        ("ticket_id", "INT"),
        ("ticket_message_id", "INT"),
        ("created_at", "DATETIME"),
    ],
    "ticket_messages": [
        ("ticket_message_id", "INT"),
        ("ticket_id", "INT"),
        ("user_id", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
        ("edited_at", "DATETIME"),
    ],
    "tickets": [
        ("ticket_id", "INT"),
        ("created_by", "INT"),
        ("assigned_to", "INT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ],
    "time_off_balances": [
        ("balance_id", "INT"),
        ("employee_id", "INT"),
        ("entitled_days", "DECIMAL(10,2)"),
        ("used_days", "DECIMAL(10,2)"),
        ("pending_days", "DECIMAL(10,2)"),
        ("carryover_days", "DECIMAL(10,2)"),
        ("absence_type", "NVARCHAR(20)"),
    ],
    "time_off_requests": [
        ("request_id", "INT"),
        ("employee_id", "INT"),
        ("absence_type", "NVARCHAR(20)"),
        ("time_unit", "NVARCHAR(20)"),
        ("start_date", "DATE"),
        ("end_date", "DATE"),
        ("start_time", "NVARCHAR(8)"),
        ("end_time", "NVARCHAR(8)"),
        ("total_hours", "DECIMAL(10,2)"),
        ("total_days", "DECIMAL(10,2)"),
        ("reviewed_by", "INT"),
        ("reviewed_at", "DATETIME"),
        ("review_notes", "NVARCHAR(MAX)"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ],
    "timesheet_location_snapshots": [
        ("snapshot_id", "INT"),
        ("employee_id", "INT"),
        ("customer_id", "INT"),
        ("ip_address", "NVARCHAR(45)"),
        ("gps_accuracy", "NVARCHAR(20)"),
        ("location_raw", "NVARCHAR(MAX)"),
        ("captured_at", "DATETIME"),
    ],
    "timesheet_punches": [
        ("punch_id", "INT"),
        ("employee_id", "INT"),
        ("customer_id", "INT"),
        ("clock_in_at", "DATETIME"),
        ("clock_out_at", "DATETIME"),
        ("ip_address", "NVARCHAR(45)"),
        ("gps_accuracy", "NVARCHAR(20)"),
        ("location_raw", "NVARCHAR(MAX)"),
        ("worked_minutes", "INT"),
        ("approved_by", "INT"),
        ("approved_at", "DATETIME"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ],
    "timesheet_settings": [
        ("setting_id", "INT"),
        ("overtime_daily_hours", "DECIMAL(10,2)"),
        ("overtime_weekly_hours", "DECIMAL(10,2)"),
        ("max_overtime_daily_hours", "DECIMAL(10,2)"),
        ("round_to_minutes", "INT"),
        ("is_active", "BIT"),
        ("created_at", "DATETIME"),
        ("updated_at", "DATETIME"),
    ],
}

# Mapeo de columnas PascalCase -> snake_case
COLUMN_MAP = {
    "addresses": [
        ("AddressId", "address_id"), ("Address1", "address_1"), ("Address2", "address_2"),
        ("City", "city"), ("State", "state"), ("ZipCode", "zip_code"), ("CountryId", "country_id"),
        ("GooglePlaceId", "google_place_id"), ("IsValidated", "is_validated"),
        ("ValidatedAt", "validated_at"), ("CreatedAt", "created_at"),
    ],
    "countries": [("CountryId", "country_id")],
    "curriculums": [
        ("CurriculumId", "curriculum_id"), ("JobId", "job_id"), ("CurriculumPath", "curriculum_path"),
        ("CoverLetter", "cover_letter"), ("SubmittedAt", "submitted_at"), ("EmployeeId", "employee_id"),
    ],
    "customer_alternate_contacts": [
        ("CustomerAlternateContactId", "customer_alternate_contact_id"), ("CustomerId", "customer_id"),
        ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"),
    ],
    "customer_attachments": [
        ("CustomerAttachmentId", "customer_attachment_id"), ("CustomerId", "customer_id"),
        ("CreatedAt", "created_at"), ("CreatedBy", "created_by"),
    ],
    "customer_notes": [
        ("CustomerNoteId", "customer_note_id"), ("CustomerId", "customer_id"),
        ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"), ("CreatedBy", "created_by"),
    ],
    "customers": [
        ("CustomerId", "customer_id"), ("CustomerType", "customer_type"), ("DtdPotential", "dtd_potential"),
        ("PrimaryAddressId", "primary_address_id"), ("CreatedAt", "created_at"),
        ("UpdatedAt", "updated_at"), ("CreatedBy", "created_by"), ("CompanyName", "company_name"),
        ("FirstName", "first_name"), ("LastName", "last_name"), ("AdditionalName", "additional_name"),
        ("PrimaryEmail", "primary_email"), ("PrimaryPhone", "primary_phone"),
    ],
    "departments": [("DepartmentId", "department_id")],
    "employee_roles": [("EmployeeId", "employee_id"), ("RoleId", "role_id")],
    "employees": [
        ("EmployeeId", "employee_id"), ("CountryId", "country_id"), ("ManagerEmployeeId", "manager_employee_id"),
        ("FirstName", "first_name"), ("LastName", "last_name"), ("DisplayName", "display_name"),
        ("MobilePhone", "mobile_phone"), ("OfficePhone", "office_phone"), ("ManagerEmail", "manager_email"),
        ("StreetAddress", "street_address"), ("PostalCode", "postal_code"), ("AzureOid", "azure_oid"),
        ("AzureUpn", "azure_upn"), ("PasswordHash", "password_hash"), ("LastSyncedAt", "last_synced_at"),
    ],
    "external_users": [
        ("ExternalUserId", "external_user_id"), ("TenantId", "tenant_id"),
        ("PasswordHash", "password_hash"), ("CreatedAt", "created_at"),
    ],
    "hardware_inventory": [
        ("HardwareID", "hardware_id"), ("EmployeeId", "employee_id"), ("SerialNumber", "serial_number"),
        ("DeviceType", "device_type"), ("StorageType", "storage_type"), ("StorageSize_GB", "storage_size_gb"),
        ("OperatingSystem", "operating_system"), ("WarrantyStartDate", "warranty_start_date"),
        ("WarrantyEndDate", "warranty_end_date"), ("PurchaseDate", "purchase_date"),
        ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"),
    ],
    "holidays": [("HolidayId", "holiday_id")],
    "jobs": [
        ("JobId", "job_id"), ("CountryId", "country_id"), ("SalaryMin", "salary_min"),
        ("SalaryMax", "salary_max"), ("PostedAt", "posted_at"), ("EmployeeId", "employee_id"),
    ],
    "licenses": [
        ("LicenseId", "license_id"), ("CreatedAt", "created_at"), ("ExpiryDate", "expiry_date"),
        ("EmployeeId", "employee_id"),
    ],
    "modules": [
        ("ModuleId", "module_id"), ("ModuleName", "module_name"), ("ModuleKey", "module_key"),
        ("ParentModuleId", "parent_module_id"), ("CreatedAt", "created_at"), ("RouteUrl", "route_url"),
        ("DisplayOrder", "display_order"), ("IsActive", "is_active"),
    ],
    "products": [
        ("Id", "id"), ("UnitPrice", "unit_price"), ("Cost", "cost"), ("TaxRate", "tax_rate"),
        ("StockQuantity", "stock_quantity"), ("IsActive", "is_active"), ("CreatedAt", "created_at"),
    ],
    "quotation_items": [
        ("Id", "id"), ("QuotationId", "quotation_id"), ("ProductId", "product_id"),
        ("UnitPrice", "unit_price"),
    ],
    "quotations": [
        ("Id", "id"), ("CustomerId", "customer_id"), ("QuoteDate", "quote_date"),
        ("ExpirationDate", "expiration_date"), ("CreatedAt", "created_at"),
    ],
    "role_modules": [
        ("RoleId", "role_id"), ("ModuleId", "module_id"), ("CanView", "can_view"),
        ("CanCreate", "can_create"), ("CanEdit", "can_edit"), ("CanDelete", "can_delete"),
        ("CanExport", "can_export"), ("AdminActions", "admin_actions"), ("OtherActions", "other_actions"),
        ("AssignedAt", "assigned_at"),
    ],
    "roles": [("RoleId", "role_id"), ("RoleName", "role_name")],
    "tenant_employees": [
        ("Id", "id"), ("TenantId", "tenant_id"), ("PasswordHash", "password_hash"),
        ("CreatedAt", "created_at"),
    ],
    "tenant_logos": [
        ("LogoId", "logo_id"), ("TenantId", "tenant_id"), ("CreatedAt", "created_at"),
        ("UpdatedAt", "updated_at"), ("PathBackground", "path_background"),
        ("PrimaryColor", "primary_color"), ("SecondaryColor", "secondary_color"),
        ("TertiaryColor", "tertiary_color"), ("FavIcon", "fav_icon"),
    ],
    "tenants": [
        ("TenantId", "tenant_id"), ("CreatedAt", "created_at"), ("IsActive", "is_active"),
        ("DbConnectionKey", "db_connection_key"),
    ],
    "ticket_attachments": [
        ("TicketAttachmentId", "ticket_attachment_id"), ("TicketId", "ticket_id"),
        ("TicketMessageId", "ticket_message_id"), ("CreatedAt", "created_at"),
    ],
    "ticket_messages": [
        ("TicketMessageId", "ticket_message_id"), ("TicketId", "ticket_id"), ("UserId", "user_id"),
        ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"), ("EditedAt", "edited_at"),
    ],
    "tickets": [
        ("TicketId", "ticket_id"), ("CreatedBy", "created_by"), ("AssignedTo", "assigned_to"),
        ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"),
    ],
    "time_off_balances": [
        ("BalanceId", "balance_id"), ("EmployeeId", "employee_id"), ("EntitledDays", "entitled_days"),
        ("UsedDays", "used_days"), ("PendingDays", "pending_days"), ("CarryoverDays", "carryover_days"),
        ("AbsenceType", "absence_type"),
    ],
    "time_off_requests": [
        ("RequestId", "request_id"), ("EmployeeId", "employee_id"), ("AbsenceType", "absence_type"),
        ("TimeUnit", "time_unit"), ("StartDate", "start_date"), ("EndDate", "end_date"),
        ("StartTime", "start_time"), ("EndTime", "end_time"), ("TotalHours", "total_hours"),
        ("TotalDays", "total_days"), ("ReviewedBy", "reviewed_by"), ("ReviewedAt", "reviewed_at"),
        ("ReviewNotes", "review_notes"), ("CreatedAt", "created_at"), ("UpdatedAt", "updated_at"),
    ],
    "timesheet_location_snapshots": [
        ("SnapshotId", "snapshot_id"), ("EmployeeId", "employee_id"), ("CustomerId", "customer_id"),
        ("IpAddress", "ip_address"), ("GpsAccuracy", "gps_accuracy"), ("LocationRaw", "location_raw"),
        ("CapturedAt", "captured_at"),
    ],
    "timesheet_punches": [
        ("PunchId", "punch_id"), ("EmployeeId", "employee_id"), ("CustomerId", "customer_id"),
        ("ClockInAt", "clock_in_at"), ("ClockOutAt", "clock_out_at"), ("IpAddress", "ip_address"),
        ("GpsAccuracy", "gps_accuracy"), ("LocationRaw", "location_raw"), ("WorkedMinutes", "worked_minutes"),
        ("ApprovedBy", "approved_by"), ("ApprovedAt", "approved_at"), ("CreatedAt", "created_at"),
        ("UpdatedAt", "updated_at"),
    ],
    "timesheet_settings": [
        ("SettingId", "setting_id"), ("OvertimeDailyHours", "overtime_daily_hours"),
        ("OvertimeWeeklyHours", "overtime_weekly_hours"), ("MaxOvertimeDailyHours", "max_overtime_daily_hours"),
        ("RoundToMinutes", "round_to_minutes"), ("IsActive", "is_active"), ("CreatedAt", "created_at"),
        ("UpdatedAt", "updated_at"),
    ],
}


def main():
    global ACTIVE_DB

    print("=" * 60)
    print("MIGRACION COMPLETA: PascalCase -> snake_case")
    print("=" * 60)

    # ============================================================
    # PASO 1: Renombrar tablas
    # ============================================================
    print("\n[1/8] Renombrando tablas PascalCase -> snake_case...")
    for old_name, new_name in TABLE_RENAMES.items():
        if table_exists(old_name) and not table_exists(new_name):
            print(f"    {old_name} -> {new_name}...")
            success, _ = exec_sql(f"EXEC sp_rename 'dbo.{old_name}', '{new_name}'", f"rename {old_name}")
            if success:
                print(f"    [OK] {old_name} -> {new_name}")
        elif table_exists(new_name):
            print(f"    [SKIP] {new_name} (ya existe)")
        elif table_exists(old_name):
            print(f"    [SKIP] {old_name} (no existe)")

    # ============================================================
    # PASO 2: Agregar columnas snake_case
    # ============================================================
    print("\n[2/8] Agregando columnas snake_case...")
    for table, cols in COLUMNS_TO_ADD.items():
        if not table_exists(table):
            continue
        for col_name, col_type in cols:
            if not col_exists(table, col_name):
                success, _ = exec_sql(f"ALTER TABLE dbo.{table} ADD {col_name} {col_type}", f"{table}.{col_name}")
            else:
                print(f"    [SKIP] {table}.{col_name} (ya existe)")

    # ============================================================
    # PASO 3: Copiar datos PascalCase -> snake_case
    # ============================================================
    print("\n[3/8] Copiando datos a columnas snake_case...")
    for table, mappings in COLUMN_MAP.items():
        if not table_exists(table):
            continue
        for pascal_col, snake_col in mappings:
            if col_exists(table, snake_col) and col_exists(table, pascal_col):
                if not col_has_data(table, snake_col) and col_has_data(table, pascal_col):
                    reserved = {"key", "order", "group", "user", "password", "date", "time", "text"}
                    snake_q = f"[{snake_col}]" if snake_col.lower() in reserved else snake_col
                    pascal_q = f"[{pascal_col}]" if pascal_col.lower() in reserved else pascal_col
                    success, _ = exec_sql(
                        f"UPDATE dbo.{table} SET {snake_q} = {pascal_q} WHERE {snake_q} IS NULL",
                        f"{table}.{snake_col}"
                    )

    # ============================================================
    # PASO 4: Hacer NOT NULL las columnas snake_case (solo si ya tiene datos)
    # ============================================================
    print("\n[4/8] Haciendo NOT NULL las columnas snake_case...")
    not_null_types = {
        "INT": "INT",
        "NVARCHAR": "NVARCHAR(MAX)",
        "DECIMAL": "DECIMAL(18,2)",
        "DATE": "DATE",
        "DATETIME": "DATETIME",
        "BIT": "BIT",
    }
    for table, cols in COLUMNS_TO_ADD.items():
        if not table_exists(table):
            continue
        for col_name, col_type in cols:
            if col_exists(table, col_name) and col_has_data(table, col_name):
                base_type = col_type.split("(")[0] if "(" in col_type else col_type
                alter_type = not_null_types.get(base_type, col_type)
                success, _ = exec_sql(
                    f"ALTER TABLE dbo.{table} ALTER COLUMN {col_name} {alter_type} NOT NULL",
                    f"{table}.{col_name} NOT NULL"
                )

    # ============================================================
    # PASO 5: Eliminar TODAS las constraints (PK, FK, DEFAULT)
    # ============================================================
    print("\n[5/8] Eliminando TODAS las constraints (PK, FK, DEFAULT)...")
    drop_all_constraints()

    # ============================================================
    # PASO 6: Eliminar columnas PascalCase
    # ============================================================
    print("\n[6/8] Eliminando columnas PascalCase...")
    for table, mappings in COLUMN_MAP.items():
        if not table_exists(table):
            continue
        for pascal_col, snake_col in mappings:
            if col_exists(table, pascal_col):
                reserved = {"key", "order", "group", "user", "password", "date", "time", "text"}
                col_q = f"[{pascal_col}]" if pascal_col.lower() in reserved else pascal_col
                success, _ = exec_sql(f"ALTER TABLE dbo.{table} DROP COLUMN {col_q}", f"{table}.{pascal_col}")

    # ============================================================
    # PASO 7: Recrear PKs en columnas snake_case
    # ============================================================
    print("\n[7/8] Recreando PKs en columnas snake_case...")
    pk_columns = {
        "addresses": "address_id",
        "countries": "country_id",
        "curriculums": "curriculum_id",
        "customer_alternate_contacts": "customer_alternate_contact_id",
        "customer_attachments": "customer_attachment_id",
        "customer_notes": "customer_note_id",
        "customers": "customer_id",
        "departments": "department_id",
        "employees": "employee_id",
        "external_users": "external_user_id",
        "hardware_inventory": "hardware_id",
        "holidays": "holiday_id",
        "jobs": "job_id",
        "licenses": "license_id",
        "modules": "module_id",
        "products": "id",
        "quotation_items": "id",
        "quotations": "id",
        "roles": "role_id",
        "tenant_employees": "id",
        "tenant_logos": "logo_id",
        "tenants": "tenant_id",
        "ticket_attachments": "ticket_attachment_id",
        "ticket_messages": "ticket_message_id",
        "tickets": "ticket_id",
        "time_off_balances": "balance_id",
        "time_off_requests": "request_id",
        "timesheet_location_snapshots": "snapshot_id",
        "timesheet_punches": "punch_id",
        "timesheet_settings": "setting_id",
    }

    for table, pk_col in pk_columns.items():
        if not table_exists(table) or not pk_col:
            continue
        if col_exists(table, pk_col):
            success, _ = exec_sql(
                f"ALTER TABLE dbo.{table} ADD PRIMARY KEY ({pk_col})",
                f"PK {table}.{pk_col}"
            )

    # ============================================================
    # PASO 8: Recrear FKs en columnas snake_case
    # ============================================================
    print("\n[8/8] Recreando FKs en columnas snake_case...")
    fk_definitions = [
        ("customer_notes", "fk_customer_notes_customers", "customer_id", "customers", "customer_id"),
        ("customer_attachments", "fk_customer_attachments_customers", "customer_id", "customers", "customer_id"),
        ("customer_attachments", "fk_customer_attachments_employees", "created_by", "employees", "employee_id"),
        ("customer_alternate_contacts", "fk_customer_alternate_contacts_customers", "customer_id", "customers", "customer_id"),
        ("customers", "fk_customers_addresses", "primary_address_id", "addresses", "address_id"),
        ("customers", "fk_customers_employees", "created_by", "employees", "employee_id"),
        ("addresses", "fk_addresses_countries", "country_id", "countries", "country_id"),
        ("employees", "fk_employees_countries", "country_id", "countries", "country_id"),
        ("employees", "fk_employees_employees", "manager_employee_id", "employees", "employee_id"),
        ("jobs", "fk_jobs_countries", "country_id", "countries", "country_id"),
        ("jobs", "fk_jobs_employees", "employee_id", "employees", "employee_id"),
        ("curriculums", "fk_curriculums_jobs", "job_id", "jobs", "job_id"),
        ("curriculums", "fk_curriculums_employees", "employee_id", "employees", "employee_id"),
        ("employee_roles", "fk_employee_roles_employees", "employee_id", "employees", "employee_id"),
        ("employee_roles", "fk_employee_roles_roles", "role_id", "roles", "role_id"),
        ("role_modules", "fk_role_modules_roles", "role_id", "roles", "role_id"),
        ("role_modules", "fk_role_modules_modules", "module_id", "modules", "module_id"),
        ("modules", "fk_modules_modules", "parent_module_id", "modules", "module_id"),
        ("licenses", "fk_licenses_employees", "employee_id", "employees", "employee_id"),
        ("hardware_inventory", "fk_hardware_inventory_employees", "employee_id", "employees", "employee_id"),
        ("products", "fk_quotation_items_products", "id", "products", "id"),
        ("quotation_items", "fk_quotation_items_quotations", "quotation_id", "quotations", "id"),
        ("quotation_items", "fk_quotation_items_products", "product_id", "products", "id"),
        ("quotations", "fk_quotations_customers", "customer_id", "customers", "customer_id"),
        ("external_users", "fk_external_users_tenants", "tenant_id", "tenants", "tenant_id"),
        ("tenant_employees", "fk_tenant_employees_tenants", "tenant_id", "tenants", "tenant_id"),
        ("tenant_logos", "fk_tenant_logos_tenants", "tenant_id", "tenants", "tenant_id"),
        ("tickets", "fk_tickets_employees_created", "created_by", "employees", "employee_id"),
        ("tickets", "fk_tickets_employees_assigned", "assigned_to", "employees", "employee_id"),
        ("ticket_messages", "fk_ticket_messages_tickets", "ticket_id", "tickets", "ticket_id"),
        ("ticket_messages", "fk_ticket_messages_employees", "user_id", "employees", "employee_id"),
        ("ticket_attachments", "fk_ticket_attachments_tickets", "ticket_id", "tickets", "ticket_id"),
        ("ticket_attachments", "fk_ticket_attachments_messages", "ticket_message_id", "ticket_messages", "ticket_message_id"),
        ("time_off_balances", "fk_time_off_balances_employees", "employee_id", "employees", "employee_id"),
        ("time_off_requests", "fk_time_off_requests_employees", "employee_id", "employees", "employee_id"),
        ("time_off_requests", "fk_time_off_requests_employees_reviewed", "reviewed_by", "employees", "employee_id"),
        ("timesheet_punches", "fk_timesheet_punches_employees", "employee_id", "employees", "employee_id"),
        ("timesheet_punches", "fk_timesheet_punches_customers", "customer_id", "customers", "customer_id"),
        ("timesheet_punches", "fk_timesheet_punches_employees_approved", "approved_by", "employees", "employee_id"),
        ("timesheet_location_snapshots", "fk_timesheet_location_snapshots_employees", "employee_id", "employees", "employee_id"),
        ("timesheet_location_snapshots", "fk_timesheet_location_snapshots_customers", "customer_id", "customers", "customer_id"),
    ]

    for child_table, fk_name, child_col, parent_table, parent_col in fk_definitions:
        if not table_exists(child_table) or not table_exists(parent_table):
            continue
        if col_exists(child_table, child_col) and col_exists(parent_table, parent_col):
            success, _ = exec_sql(
                f"ALTER TABLE dbo.[{child_table}] ADD CONSTRAINT [{fk_name}] FOREIGN KEY ([{child_col}]) REFERENCES dbo.[{parent_table}]([{parent_col}])",
                f"FK {child_table}.{child_col} -> {parent_table}.{parent_col}"
            )

    print("\n" + "=" * 60)
    print("MIGRACION COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target not in DATABASES:
            print(f"Base de datos '{target}' no encontrada.")
            sys.exit(1)
        databases_to_run = [target]
    else:
        databases_to_run = list(DATABASES.keys())

    print(f"Bases de datos a migrar: {', '.join(databases_to_run)}")
    print("PRESIONA Enter PARA CONTINUAR o Ctrl+C para cancelar...")
    input()

    for db_name in databases_to_run:
        ACTIVE_DB = db_name
        print(f"\n{'=' * 60}")
        print(f"MIGRANDO: {db_name}")
        print(f"{'=' * 60}")
        main()
