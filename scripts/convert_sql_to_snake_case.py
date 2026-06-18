"""
Script to convert SQL Server backup files from PascalCase to snake_case.
Converts table names, column names, constraint names, and FK references.
"""

import os
import pathlib
import re

# Table name mappings (PascalCase -> snake_case)
TABLE_RENAMES = {
    "Addresses": "addresses",
    "Countries": "countries",
    "Curriculums": "curriculums",
    "CustomerAlternateContacts": "customer_alternate_contacts",
    "CustomerAttachments": "customer_attachments",
    "CustomerNotes": "customer_notes",
    "Customers": "customers",
    "Departments": "departments",
    "EmployeeRoles": "employee_roles",
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
    "RoleModules": "role_modules",
    "Roles": "roles",
    "TenantEmployees": "tenant_employees",
    "TenantLogos": "tenant_logos",
    "Tenants": "tenants",
    "Tickets": "tickets",
    "ticketAttachments": "ticket_attachments",
    "ticketMessages": "ticket_messages",
    "TimeOffBalances": "time_off_balances",
    "TimeOffRequests": "time_off_requests",
    "TimeSheetLocationSnapshots": "time_sheet_location_snapshots",
    "TimeSheetPunches": "time_sheet_punches",
    "TimeSheetSettings": "time_sheet_settings",
}

# Column name mappings (PascalCase -> snake_case)
COLUMN_RENAMES = {
    # Generic column names used across multiple tables
    "Name": "name",
    "Email": "email",
    "Phone": "phone",
    "Code": "code",
    "Date": "date",
    "Year": "year",
    "City": "city",
    "Region": "region",
    "Country": "country",
    "Title": "title",
    "Status": "status",
    "Location": "location",
    "Description": "description",
    "Notes": "notes",
    "Model": "model",
    "Brand": "brand",
    "Type": "type",
    "Version": "version",
    "Key": "key",
    "Account": "account",
    "Cost": "cost",
    "Total": "total",
    "Tax": "tax",
    "Unit": "unit",
    "Icon": "icon",
    "Url": "url",
    "Path": "path",
    # Addresses
    "AddressId": "address_id",
    "Address1": "address_1",
    "Address2": "address_2",
    "ZipCode": "zip_code",
    "CountryId": "country_id",
    "GooglePlaceId": "google_place_id",
    "IsValidated": "is_validated",
    "ValidatedAt": "validated_at",
    "CreatedAt": "created_at",
    "UpdatedAt": "updated_at",
    "State": "state",
    # Curriculums
    "CurriculumId": "curriculum_id",
    "JobId": "job_id",
    "CurriculumPath": "curriculum_path",
    "CoverLetter": "cover_letter",
    "SubmittedAt": "submitted_at",
    "EmployeeId": "employee_id",
    # CustomerAlternateContacts
    "CustomerAlternateContactId": "customer_alternate_contact_id",
    "CustomerId": "customer_id",
    # CustomerAttachments
    "CustomerAttachmentId": "customer_attachment_id",
    "FileName": "file_name",
    "FileType": "file_type",
    "FilePath": "file_path",
    "CreatedBy": "created_by",
    # CustomerNotes
    "CustomerNoteId": "customer_note_id",
    "NoteText": "note_text",
    # Customers
    "CustomerType": "customer_type",
    "CompanyName": "company_name",
    "FirstName": "first_name",
    "LastName": "last_name",
    "AdditionalName": "additional_name",
    "Market": "market",
    "DtdPotential": "dtd_potential",
    "PrimaryEmail": "primary_email",
    "PrimaryPhone": "primary_phone",
    "PrimaryAddressId": "primary_address_id",
    # Departments
    "DepartmentId": "department_id",
    "DisplayName": "display_name",
    "Department": "department",
    "Office": "office",
    "MobilePhone": "mobile_phone",
    "OfficePhone": "office_phone",
    "StreetAddress": "street_address",
    "PostalCode": "postal_code",
    "AzureOid": "azure_oid",
    "AzureUpn": "azure_upn",
    "LastSyncedAt": "last_synced_at",
    "Anydesk": "anydesk",
    "PasswordHash": "password_hash",
    "Manager": "manager",
    "ManagerEmail": "manager_email",
    "ManagerEmployeeId": "manager_employee_id",
    # ExternalUsers
    "ExternalUserId": "external_user_id",
    "TenantId": "tenant_id",
    # HardwareInventory
    "HardwareID": "hardware_id",
    "SerialNumber": "serial_number",
    "DeviceType": "device_type",
    "Processor": "processor",
    "RAM_GB": "ram_gb",
    "StorageType": "storage_type",
    "StorageSize_GB": "storage_size_gb",
    "GPU": "gpu",
    "OperatingSystem": "operating_system",
    "WarrantyStartDate": "warranty_start_date",
    "WarrantyEndDate": "warranty_end_date",
    "PurchaseDate": "purchase_date",
    # Holidays
    "HolidayId": "holiday_id",
    "Requirements": "requirements",
    "SalaryMin": "salary_min",
    "SalaryMax": "salary_max",
    "PostedAt": "posted_at",
    # Licenses
    "LicenseId": "license_id",
    "Software": "software",
    "ExpiryDate": "expiry_date",
    # Modules
    "ModuleId": "module_id",
    "ModuleName": "module_name",
    "ModuleKey": "module_key",
    "RouteUrl": "route_url",
    "DisplayOrder": "display_order",
    "IsActive": "is_active",
    "ParentModuleId": "parent_module_id",
    # Products
    "Id": "id",
    "SKU": "sku",
    "UnitPrice": "unit_price",
    "TaxRate": "tax_rate",
    "StockQuantity": "stock_quantity",
    # QuotationItems
    "QuotationId": "quotation_id",
    "ProductId": "product_id",
    "Quantity": "quantity",
    "Discount": "discount",
    # Quotations
    "QuoteDate": "quote_date",
    "ExpirationDate": "expiration_date",
    "Subtotal": "subtotal",
    # Roles
    "RoleId": "role_id",
    "RoleName": "role_name",
    # Tenants
    "DbConnectionKey": "db_connection_key",
    # TenantEmployees
    # TenantLogos
    "LogoId": "logo_id",
    "PathBackground": "path_background",
    "PrimaryColor": "primary_color",
    "SecondaryColor": "secondary_color",
    "TertiaryColor": "tertiary_color",
    "FavIcon": "fav_icon",
    # Tickets
    "TicketId": "ticket_id",
    "Priority": "priority",
    "SLA": "sla",
    "AssignedTo": "assigned_to",
    # ticketAttachments
    "TicketAttachmentId": "ticket_attachment_id",
    "TicketMessageId": "ticket_message_id",
    "UserId": "user_id",
    "MessageTxt": "message_txt",
    "EditedAt": "edited_at",
    # TimeOffBalances
    "BalanceId": "balance_id",
    "AbsenceType": "absence_type",
    "EntitledDays": "entitled_days",
    "UsedDays": "used_days",
    "PendingDays": "pending_days",
    "CarryoverDays": "carryover_days",
    # TimeOffRequests
    "RequestId": "request_id",
    "TimeUnit": "time_unit",
    "StartDate": "start_date",
    "EndDate": "end_date",
    "StartTime": "start_time",
    "EndTime": "end_time",
    "TotalHours": "total_hours",
    "TotalDays": "total_days",
    "Reason": "reason",
    "ReviewedBy": "reviewed_by",
    "ReviewedAt": "reviewed_at",
    "ReviewNotes": "review_notes",
    # TimeSheetLocationSnapshots
    "SnapshotId": "snapshot_id",
    "IpAddress": "ip_address",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "GpsAccuracy": "gps_accuracy",
    "Timezone": "timezone",
    "LocationRaw": "location_raw",
    "CapturedAt": "captured_at",
    # TimeSheetPunches
    "PunchId": "punch_id",
    "ClockInAt": "clock_in_at",
    "ClockOutAt": "clock_out_at",
    "WorkedMinutes": "worked_minutes",
    "ApprovedBy": "approved_by",
    "ApprovedAt": "approved_at",
    # TimeSheetSettings
    "SettingId": "setting_id",
    "OvertimeDailyHours": "overtime_daily_hours",
    "OvertimeWeeklyHours": "overtime_weekly_hours",
    "RoundToMinutes": "round_to_minutes",
    "MaxOvertimeDailyHours": "max_overtime_daily_hours",
}


def to_snake_case(name):
    """Convert PascalCase to snake_case."""
    result = []
    for i, char in enumerate(name):
        if char.isupper():
            if i > 0 and (
                name[i - 1].islower()
                or (i > 1 and name[i - 2].islower())
                or (i < len(name) - 1 and name[i + 1].islower())
            ):
                result.append("_")
            result.append(char.lower())
        else:
            result.append(char)
    return "".join(result).strip("_")


def convert_sql_file(input_path, output_path=None):
    """Convert a SQL backup file from PascalCase to snake_case."""
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_snake_case{ext}"

    content = pathlib.Path(input_path).read_text(encoding="utf-8")

    # Build sorted table renames (longest first to handle overlaps)
    sorted_tables = sorted(TABLE_RENAMES.items(), key=lambda x: len(x[0]), reverse=True)

    # 1. Convert table names in brackets [dbo].[TableName]
    for pascal, snake in sorted_tables:
        # [dbo].[Addresses] -> [dbo].[addresses]
        content = re.sub(r"\[dbo\]\.\[" + re.escape(pascal) + r"\]", f"[dbo].[{snake}]", content)
        # dbo].[Addresses] -> dbo].[addresses] (edge case)
        content = re.sub(r"dbo\]\.\[" + re.escape(pascal) + r"\]", f"dbo].[{snake}]", content)

    # 2. Convert table names in non-bracketed contexts like DROP TABLE dbo.TableName
    for pascal, snake in sorted_tables:
        # 'dbo.TableName' -> 'dbo.tablename'
        content = re.sub(r"'dbo\." + re.escape(pascal) + r"'", f"'dbo.{snake}'", content)
        # DROP TABLE dbo.TableName; -> DROP TABLE dbo.tablename;
        content = re.sub(r" DROP TABLE dbo\." + re.escape(pascal) + r";", f" DROP TABLE dbo.{snake};", content)
        # DROP TABLE dbo.TableName] -> DROP TABLE dbo.tablename]
        content = re.sub(r" DROP TABLE dbo\." + re.escape(pascal) + r"\]", f" DROP TABLE dbo.{snake}]", content)

    # 3. Convert column names in brackets [ColumnName]
    for pascal, snake in sorted(COLUMN_RENAMES.items(), key=lambda x: len(x[0]), reverse=True):
        # Only match whole column names in brackets
        content = re.sub(r"\[" + re.escape(pascal) + r"\]", f"[{snake}]", content)

    # 4. Convert FK constraint names
    fk_patterns = [
        (r"FK_Addresses_Countries", "fk_addresses_countries"),
        (r"FK_CustomerAlternateContacts_CustomerId_Customers", "fk_customer_alternate_contacts_customer_id_customers"),
        (r"FK_CustomerAttachments_CustomerId_Customers", "fk_customer_attachments_customer_id_customers"),
        (r"FK_CustomerAttachments_CreatedBy_Employees", "fk_customer_attachments_created_by_employees"),
        (r"FK_CustomerNotes_CustomerId_Customers", "fk_customer_notes_customer_id_customers"),
        (r"FK_CustomerNotes_CreatedBy_Employees", "fk_customer_notes_created_by_employees"),
        (r"FK_Customers_PrimaryAddressId_Addresses", "fk_customers_primary_address_id_addresses"),
        (r"FK_Customers_CreatedBy_Employees", "fk_customers_created_by_employees"),
        (r"FK_Employees_ManagerEmployee", "fk_employees_manager_employee"),
        (r"FK_Jobs_Countries", "fk_jobs_countries"),
        (r"FK_QuotationItems_Product", "fk_quotation_items_product"),
        (r"FK_QuotationItems_Quotation", "fk_quotation_items_quotation"),
        (r"FK_Quotations_Customers", "fk_quotations_customers"),
        (r"FK_RoleModules_ModuleId_Modules", "fk_role_modules_module_id_modules"),
        (r"FK_RoleModules_RoleId_Roles", "fk_role_modules_role_id_roles"),
        (
            r"FK_ticketAttachments_TicketMessageId_ticketMessages",
            "fk_ticket_attachments_ticket_message_id_ticket_messages",
        ),
        (r"FK_ticketAttachments_TicketId_Tickets", "fk_ticket_attachments_ticket_id_tickets"),
        (r"FK_ticketMessages_UserId_Employees", "fk_ticket_messages_user_id_employees"),
        (r"FK_ticketMessages_TicketId_Tickets", "fk_ticket_messages_ticket_id_tickets"),
        (r"FK_Tickets_CreatedBy_Employees", "fk_tickets_created_by_employees"),
        (r"FK_Tickets_AssignedTo_Employees", "fk_tickets_assigned_to_employees"),
        (r"FK_TimeOffBalances_Employee", "fk_time_off_balances_employee"),
        (r"FK_TimeOffRequests_Employee", "fk_time_off_requests_employee"),
        (r"FK_TimeOffRequests_ReviewedBy", "fk_time_off_requests_reviewed_by"),
        (
            r"FK_TimeSheetLocationSnapshots_CustomerId_Customers",
            "fk_time_sheet_location_snapshots_customer_id_customers",
        ),
        (
            r"FK_TimeSheetLocationSnapshots_EmployeeId_Employees",
            "fk_time_sheet_location_snapshots_employee_id_employees",
        ),
        (r"FK_TimeSheetPunches_CustomerId_Customers", "fk_time_sheet_punches_customer_id_customers"),
        (r"FK_TimeSheetPunches_EmployeeId_Employees", "fk_time_sheet_punches_employee_id_employees"),
        (r"FK_TimeSheetPunches_ApprovedBy_Employees", "fk_time_sheet_punches_approved_by_employees"),
    ]

    for pattern, replacement in fk_patterns:
        content = re.sub(r"\[" + pattern + r"\]", f"[{replacement}]", content)

    # 5. Convert PK constraint names
    pk_patterns = [
        (r"PK_Addresses", "pk_addresses"),
        (r"PK_Countries", "pk_countries"),
        (r"PK_Curriculums", "pk_curriculums"),
        (r"PK_CustomerAlternateContacts", "pk_customer_alternate_contacts"),
        (r"PK_CustomerAttachments", "pk_customer_attachments"),
        (r"PK_CustomerNotes", "pk_customer_notes"),
        (r"PK_Customers", "pk_customers"),
        (r"PK_Departments", "pk_departments"),
        (r"PK_Employees", "pk_employees"),
        (r"PK_ExternalUsers", "pk_external_users"),
        (r"PK_HardwareInventory", "pk_hardware_inventory"),
        (r"PK_Holidays", "pk_holidays"),
        (r"PK_Jobs", "pk_jobs"),
        (r"PK_Licenses", "pk_licenses"),
        (r"PK_Modules", "pk_modules"),
        (r"PK_Products", "pk_products"),
        (r"PK_Roles", "pk_roles"),
        (r"PK_TenantEmployees", "pk_tenant_employees"),
        (r"PK_TenantLogos", "pk_tenant_logos"),
        (r"PK_Tenants", "pk_tenants"),
        (r"PK_Tickets", "pk_tickets"),
        (r"PK_ticketAttachments", "pk_ticket_attachments"),
        (r"PK_ticketMessages", "pk_ticket_messages"),
        (r"PK_TimeOffBalances", "pk_time_off_balances"),
        (r"PK_TimeOffRequests", "pk_time_off_requests"),
        (r"PK_TimeSheetLocationSnapshots", "pk_time_sheet_location_snapshots"),
        (r"PK_TimeSheetPunches", "pk_time_sheet_punches"),
        (r"PK_TimeSheetSettings", "pk_time_sheet_settings"),
    ]

    for pattern, replacement in pk_patterns:
        content = re.sub(r"\[" + pattern + r"\]", f"[{replacement}]", content)

    # 6. Convert auto-generated constraint names (PK__TableName__Hash)
    auto_pk_pattern = r"\[PK__([a-zA-Z]+)__([a-zA-Z0-9]+)\]"

    def replace_auto_pk(match):
        prefix = match.group(1)
        suffix = match.group(2)
        snake_prefix = to_snake_case(prefix)
        return f"[pk_{snake_prefix}_{suffix.lower()}]"

    content = re.sub(auto_pk_pattern, replace_auto_pk, content)

    # 7. Convert auto-generated FK constraint names
    auto_fk_pattern = r"\[FK__([a-zA-Z]+)__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)\]"

    def replace_auto_fk(match):
        table = match.group(1)
        col = match.group(2)
        suffix = match.group(3)
        snake_table = to_snake_case(table)
        snake_col = to_snake_case(col)
        return f"[fk_{snake_table}_{snake_col}_{suffix.lower()}]"

    content = re.sub(auto_fk_pattern, replace_auto_fk, content)

    # 8. Convert comments
    for pascal, snake in sorted_tables:
        content = re.sub(rf"-- Table: {pascal}", f"-- Table: {snake}", content)
        content = re.sub(rf"-- Data for {pascal}", f"-- Data for {snake}", content)
        content = re.sub(rf"{pascal}: No data", f"{snake}: No data", content)

    pathlib.Path(output_path).write_text(content, encoding="utf-8")

    return output_path


if __name__ == "__main__":
    base_path = r"c:\Users\jcarl\OneDrive\Escritorio\PrimeFire\PrimeFireApi\bd\sql\backups"

    # Convert devromo backup
    devromo_input = os.path.join(base_path, "complete_backup_devromo_20260320_221421.sql")
    devromo_output = os.path.join(base_path, "complete_backup_devromo_20260320_221421_snake_case.sql")
    convert_sql_file(devromo_input, devromo_output)

    # Convert primefirebd backup
    primefire_input = os.path.join(base_path, "complete_backup_primefirebd_20260320_221437.sql")
    primefire_output = os.path.join(base_path, "complete_backup_primefirebd_20260320_221437_snake_case.sql")
    convert_sql_file(primefire_input, primefire_output)
