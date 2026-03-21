-- =============================================
-- RENAMING ALL COLUMNS TO SNAKE_CASE
-- Run this on your existing database
-- =============================================

-- addresses table
EXEC sp_rename 'dbo.addresses.AddressId', 'address_id', 'COLUMN';
EXEC sp_rename 'dbo.addresses.Address1', 'address_1', 'COLUMN';
EXEC sp_rename 'dbo.addresses.Address2', 'address_2', 'COLUMN';
EXEC sp_rename 'dbo.addresses.City', 'city', 'COLUMN';
EXEC sp_rename 'dbo.addresses.State', 'state', 'COLUMN';
EXEC sp_rename 'dbo.addresses.ZipCode', 'zip_code', 'COLUMN';
EXEC sp_rename 'dbo.addresses.CountryId', 'country_id', 'COLUMN';
EXEC sp_rename 'dbo.addresses.GooglePlaceId', 'google_place_id', 'COLUMN';
EXEC sp_rename 'dbo.addresses.IsValidated', 'is_validated', 'COLUMN';
EXEC sp_rename 'dbo.addresses.ValidatedAt', 'validated_at', 'COLUMN';
EXEC sp_rename 'dbo.addresses.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.addresses.UpdatedAt', 'updated_at', 'COLUMN';

-- countries table
EXEC sp_rename 'dbo.countries.CountryId', 'country_id', 'COLUMN';

-- curriculums table
EXEC sp_rename 'dbo.curriculums.CurriculumId', 'curriculum_id', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.JobId', 'job_id', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.Email', 'email', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.Phone', 'phone', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.CurriculumPath', 'curriculum_path', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.CoverLetter', 'cover_letter', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.SubmittedAt', 'submitted_at', 'COLUMN';
EXEC sp_rename 'dbo.curriculums.EmployeeId', 'employee_id', 'COLUMN';

-- customer_alternate_contacts table
EXEC sp_rename 'dbo.customer_alternate_contacts.CustomerAlternateContactId', 'customer_alternate_contact_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.Email', 'email', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.Phone', 'phone', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.customer_alternate_contacts.UpdatedAt', 'updated_at', 'COLUMN';

-- customer_attachments table
EXEC sp_rename 'dbo.customer_attachments.CustomerAttachmentId', 'customer_attachment_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.FileName', 'file_name', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.FileType', 'file_type', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.FilePath', 'file_path', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.customer_attachments.CreatedBy', 'created_by', 'COLUMN';

-- customer_notes table
EXEC sp_rename 'dbo.customer_notes.CustomerNoteId', 'customer_note_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_notes.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.customer_notes.NoteText', 'note_text', 'COLUMN';
EXEC sp_rename 'dbo.customer_notes.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.customer_notes.UpdatedAt', 'updated_at', 'COLUMN';
EXEC sp_rename 'dbo.customer_notes.CreatedBy', 'created_by', 'COLUMN';

-- customers table
EXEC sp_rename 'dbo.customers.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.customers.CustomerType', 'customer_type', 'COLUMN';
EXEC sp_rename 'dbo.customers.CompanyName', 'company_name', 'COLUMN';
EXEC sp_rename 'dbo.customers.FirstName', 'first_name', 'COLUMN';
EXEC sp_rename 'dbo.customers.LastName', 'last_name', 'COLUMN';
EXEC sp_rename 'dbo.customers.AdditionalName', 'additional_name', 'COLUMN';
EXEC sp_rename 'dbo.customers.Market', 'market', 'COLUMN';
EXEC sp_rename 'dbo.customers.DtdPotential', 'dtd_potential', 'COLUMN';
EXEC sp_rename 'dbo.customers.PrimaryEmail', 'primary_email', 'COLUMN';
EXEC sp_rename 'dbo.customers.PrimaryPhone', 'primary_phone', 'COLUMN';
EXEC sp_rename 'dbo.customers.PrimaryAddressId', 'primary_address_id', 'COLUMN';
EXEC sp_rename 'dbo.customers.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.customers.UpdatedAt', 'updated_at', 'COLUMN';
EXEC sp_rename 'dbo.customers.CreatedBy', 'created_by', 'COLUMN';

-- departments table
EXEC sp_rename 'dbo.departments.DepartmentId', 'department_id', 'COLUMN';
EXEC sp_rename 'dbo.departments.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.departments.Code', 'code', 'COLUMN';

-- employee_roles table
EXEC sp_rename 'dbo.employee_roles.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.employee_roles.RoleId', 'role_id', 'COLUMN';

-- employees table
EXEC sp_rename 'dbo.employees.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.employees.FirstName', 'first_name', 'COLUMN';
EXEC sp_rename 'dbo.employees.LastName', 'last_name', 'COLUMN';
EXEC sp_rename 'dbo.employees.DisplayName', 'display_name', 'COLUMN';
EXEC sp_rename 'dbo.employees.Title', 'title', 'COLUMN';
EXEC sp_rename 'dbo.employees.Department', 'department', 'COLUMN';
EXEC sp_rename 'dbo.employees.Office', 'office', 'COLUMN';
EXEC sp_rename 'dbo.employees.Email', 'email', 'COLUMN';
EXEC sp_rename 'dbo.employees.Phone', 'phone', 'COLUMN';
EXEC sp_rename 'dbo.employees.MobilePhone', 'mobile_phone', 'COLUMN';
EXEC sp_rename 'dbo.employees.OfficePhone', 'office_phone', 'COLUMN';
EXEC sp_rename 'dbo.employees.StreetAddress', 'street_address', 'COLUMN';
EXEC sp_rename 'dbo.employees.City', 'city', 'COLUMN';
EXEC sp_rename 'dbo.employees.State', 'state', 'COLUMN';
EXEC sp_rename 'dbo.employees.PostalCode', 'postal_code', 'COLUMN';
EXEC sp_rename 'dbo.employees.CountryId', 'country_id', 'COLUMN';
EXEC sp_rename 'dbo.employees.AzureOid', 'azure_oid', 'COLUMN';
EXEC sp_rename 'dbo.employees.AzureUpn', 'azure_upn', 'COLUMN';
EXEC sp_rename 'dbo.employees.LastSyncedAt', 'last_synced_at', 'COLUMN';
EXEC sp_rename 'dbo.employees.Anydesk', 'anydesk', 'COLUMN';
EXEC sp_rename 'dbo.employees.PasswordHash', 'password_hash', 'COLUMN';
EXEC sp_rename 'dbo.employees.Manager', 'manager', 'COLUMN';
EXEC sp_rename 'dbo.employees.ManagerEmail', 'manager_email', 'COLUMN';
EXEC sp_rename 'dbo.employees.ManagerEmployeeId', 'manager_employee_id', 'COLUMN';

-- external_users table
EXEC sp_rename 'dbo.external_users.ExternalUserId', 'external_user_id', 'COLUMN';
EXEC sp_rename 'dbo.external_users.Email', 'email', 'COLUMN';
EXEC sp_rename 'dbo.external_users.PasswordHash', 'password_hash', 'COLUMN';
EXEC sp_rename 'dbo.external_users.TenantId', 'tenant_id', 'COLUMN';
EXEC sp_rename 'dbo.external_users.CreatedAt', 'created_at', 'COLUMN';

-- hardware_inventory table
EXEC sp_rename 'dbo.hardware_inventory.HardwareID', 'hardware_id', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.SerialNumber', 'serial_number', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Brand', 'brand', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Model', 'model', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.DeviceType', 'device_type', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Processor', 'processor', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.RAM_GB', 'ram_gb', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.StorageType', 'storage_type', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.StorageSize_GB', 'storage_size_gb', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.GPU', 'gpu', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.OperatingSystem', 'operating_system', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.WarrantyStartDate', 'warranty_start_date', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.WarrantyEndDate', 'warranty_end_date', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.PurchaseDate', 'purchase_date', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Location', 'location', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.Notes', 'notes', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.hardware_inventory.UpdatedAt', 'updated_at', 'COLUMN';

-- holidays table
EXEC sp_rename 'dbo.holidays.HolidayId', 'holiday_id', 'COLUMN';
EXEC sp_rename 'dbo.holidays.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.holidays.Date', 'date', 'COLUMN';
EXEC sp_rename 'dbo.holidays.Year', 'year', 'COLUMN';

-- jobs table
EXEC sp_rename 'dbo.jobs.JobId', 'job_id', 'COLUMN';
EXEC sp_rename 'dbo.jobs.Title', 'title', 'COLUMN';
EXEC sp_rename 'dbo.jobs.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.jobs.Requirements', 'requirements', 'COLUMN';
EXEC sp_rename 'dbo.jobs.Location', 'location', 'COLUMN';
EXEC sp_rename 'dbo.jobs.SalaryMin', 'salary_min', 'COLUMN';
EXEC sp_rename 'dbo.jobs.SalaryMax', 'salary_max', 'COLUMN';
EXEC sp_rename 'dbo.jobs.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.jobs.PostedAt', 'posted_at', 'COLUMN';
EXEC sp_rename 'dbo.jobs.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.jobs.CountryId', 'country_id', 'COLUMN';

-- licenses table
EXEC sp_rename 'dbo.licenses.LicenseId', 'license_id', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Software', 'software', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Version', 'version', 'COLUMN';
EXEC sp_rename 'dbo.licenses.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.licenses.ExpiryDate', 'expiry_date', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Key', 'key', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Account', 'account', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Password', 'password', 'COLUMN';
EXEC sp_rename 'dbo.licenses.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.licenses.Notes', 'notes', 'COLUMN';

-- modules table
EXEC sp_rename 'dbo.modules.ModuleId', 'module_id', 'COLUMN';
EXEC sp_rename 'dbo.modules.ModuleName', 'module_name', 'COLUMN';
EXEC sp_rename 'dbo.modules.ModuleKey', 'module_key', 'COLUMN';
EXEC sp_rename 'dbo.modules.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.modules.Icon', 'icon', 'COLUMN';
EXEC sp_rename 'dbo.modules.RouteUrl', 'route_url', 'COLUMN';
EXEC sp_rename 'dbo.modules.DisplayOrder', 'display_order', 'COLUMN';
EXEC sp_rename 'dbo.modules.IsActive', 'is_active', 'COLUMN';
EXEC sp_rename 'dbo.modules.ParentModuleId', 'parent_module_id', 'COLUMN';
EXEC sp_rename 'dbo.modules.CreatedAt', 'created_at', 'COLUMN';

-- products table
EXEC sp_rename 'dbo.products.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.products.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.products.Type', 'type', 'COLUMN';
EXEC sp_rename 'dbo.products.SKU', 'sku', 'COLUMN';
EXEC sp_rename 'dbo.products.UnitPrice', 'unit_price', 'COLUMN';
EXEC sp_rename 'dbo.products.Cost', 'cost', 'COLUMN';
EXEC sp_rename 'dbo.products.TaxRate', 'tax_rate', 'COLUMN';
EXEC sp_rename 'dbo.products.Unit', 'unit', 'COLUMN';
EXEC sp_rename 'dbo.products.StockQuantity', 'stock_quantity', 'COLUMN';
EXEC sp_rename 'dbo.products.IsActive', 'is_active', 'COLUMN';
EXEC sp_rename 'dbo.products.CreatedAt', 'created_at', 'COLUMN';

-- quotation_items table
EXEC sp_rename 'dbo.quotation_items.QuotationId', 'quotation_id', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.ProductId', 'product_id', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.Quantity', 'quantity', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.UnitPrice', 'unit_price', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.Discount', 'discount', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.Tax', 'tax', 'COLUMN';
EXEC sp_rename 'dbo.quotation_items.Total', 'total', 'COLUMN';

-- quotations table
EXEC sp_rename 'dbo.quotations.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.quotations.QuoteDate', 'quote_date', 'COLUMN';
EXEC sp_rename 'dbo.quotations.ExpirationDate', 'expiration_date', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Subtotal', 'subtotal', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Tax', 'tax', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Discount', 'discount', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Total', 'total', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.quotations.Notes', 'notes', 'COLUMN';
EXEC sp_rename 'dbo.quotations.CreatedAt', 'created_at', 'COLUMN';

-- roles table
EXEC sp_rename 'dbo.roles.RoleId', 'role_id', 'COLUMN';
EXEC sp_rename 'dbo.roles.RoleName', 'role_name', 'COLUMN';
EXEC sp_rename 'dbo.roles.Description', 'description', 'COLUMN';

-- role_modules table
EXEC sp_rename 'dbo.role_modules.RoleId', 'role_id', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.ModuleId', 'module_id', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.CanView', 'can_view', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.CanCreate', 'can_create', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.CanEdit', 'can_edit', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.CanDelete', 'can_delete', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.CanExport', 'can_export', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.AdminActions', 'admin_actions', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.OtherActions', 'other_actions', 'COLUMN';
EXEC sp_rename 'dbo.role_modules.AssignedAt', 'assigned_at', 'COLUMN';

-- tenant_employees table
EXEC sp_rename 'dbo.tenant_employees.TenantId', 'tenant_id', 'COLUMN';
EXEC sp_rename 'dbo.tenant_employees.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.tenant_employees.Email', 'email', 'COLUMN';
EXEC sp_rename 'dbo.tenant_employees.PasswordHash', 'password_hash', 'COLUMN';

-- tenant_logos table
EXEC sp_rename 'dbo.tenant_logos.LogoId', 'logo_id', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.TenantId', 'tenant_id', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.Title', 'title', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.Path', 'path', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.PathBackground', 'path_background', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.PrimaryColor', 'primary_color', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.SecondaryColor', 'secondary_color', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.TertiaryColor', 'tertiary_color', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.UpdatedAt', 'updated_at', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.Url', 'url', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.FavIcon', 'fav_icon', 'COLUMN';
EXEC sp_rename 'dbo.tenant_logos.Email', 'email', 'COLUMN';

-- tenants table
EXEC sp_rename 'dbo.tenants.TenantId', 'tenant_id', 'COLUMN';
EXEC sp_rename 'dbo.tenants.Name', 'name', 'COLUMN';
EXEC sp_rename 'dbo.tenants.DbConnectionKey', 'db_connection_key', 'COLUMN';
EXEC sp_rename 'dbo.tenants.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.tenants.IsActive', 'is_active', 'COLUMN';
EXEC sp_rename 'dbo.tenants.CreatedAt', 'created_at', 'COLUMN';

-- tickets table
EXEC sp_rename 'dbo.tickets.TicketId', 'ticket_id', 'COLUMN';
EXEC sp_rename 'dbo.tickets.Title', 'title', 'COLUMN';
EXEC sp_rename 'dbo.tickets.Description', 'description', 'COLUMN';
EXEC sp_rename 'dbo.tickets.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.tickets.Priority', 'priority', 'COLUMN';
EXEC sp_rename 'dbo.tickets.SLA', 'sla', 'COLUMN';
EXEC sp_rename 'dbo.tickets.CreatedBy', 'created_by', 'COLUMN';
EXEC sp_rename 'dbo.tickets.AssignedTo', 'assigned_to', 'COLUMN';
EXEC sp_rename 'dbo.tickets.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.tickets.UpdatedAt', 'updated_at', 'COLUMN';

-- ticket_messages table
EXEC sp_rename 'dbo.ticket_messages.TicketMessageId', 'ticket_message_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.TicketId', 'ticket_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.UserId', 'user_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.MessageTxt', 'message_txt', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.UpdatedAt', 'updated_at', 'COLUMN';
EXEC sp_rename 'dbo.ticket_messages.EditedAt', 'edited_at', 'COLUMN';

-- ticket_attachments table
EXEC sp_rename 'dbo.ticket_attachments.TicketAttachmentId', 'ticket_attachment_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.TicketId', 'ticket_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.TicketMessageId', 'ticket_message_id', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.FileName', 'file_name', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.FileType', 'file_type', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.FilePath', 'file_path', 'COLUMN';
EXEC sp_rename 'dbo.ticket_attachments.CreatedAt', 'created_at', 'COLUMN';

-- time_off_balances table
EXEC sp_rename 'dbo.time_off_balances.BalanceId', 'balance_id', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.AbsenceType', 'absence_type', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.Year', 'year', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.EntitledDays', 'entitled_days', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.UsedDays', 'used_days', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.PendingDays', 'pending_days', 'COLUMN';
EXEC sp_rename 'dbo.time_off_balances.CarryoverDays', 'carryover_days', 'COLUMN';

-- time_off_requests table
EXEC sp_rename 'dbo.time_off_requests.RequestId', 'request_id', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.AbsenceType', 'absence_type', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.TimeUnit', 'time_unit', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.StartDate', 'start_date', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.EndDate', 'end_date', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.StartTime', 'start_time', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.EndTime', 'end_time', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.TotalHours', 'total_hours', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.TotalDays', 'total_days', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.Reason', 'reason', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.ReviewedBy', 'reviewed_by', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.ReviewedAt', 'reviewed_at', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.ReviewNotes', 'review_notes', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.time_off_requests.UpdatedAt', 'updated_at', 'COLUMN';

-- time_sheet_settings table
EXEC sp_rename 'dbo.time_sheet_settings.SettingId', 'setting_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.OvertimeDailyHours', 'overtime_daily_hours', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.OvertimeWeeklyHours', 'overtime_weekly_hours', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.RoundToMinutes', 'round_to_minutes', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.IsActive', 'is_active', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.UpdatedAt', 'updated_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_settings.MaxOvertimeDailyHours', 'max_overtime_daily_hours', 'COLUMN';

-- time_sheet_punches table
EXEC sp_rename 'dbo.time_sheet_punches.PunchId', 'punch_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.ClockInAt', 'clock_in_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.ClockOutAt', 'clock_out_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Timezone', 'timezone', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.IpAddress', 'ip_address', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Latitude', 'latitude', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Longitude', 'longitude', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.GpsAccuracy', 'gps_accuracy', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.City', 'city', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Region', 'region', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Country', 'country', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.LocationRaw', 'location_raw', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.WorkedMinutes', 'worked_minutes', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Status', 'status', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.Note', 'note', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.ApprovedBy', 'approved_by', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.ApprovedAt', 'approved_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.CreatedAt', 'created_at', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_punches.UpdatedAt', 'updated_at', 'COLUMN';

-- time_sheet_location_snapshots table
EXEC sp_rename 'dbo.time_sheet_location_snapshots.SnapshotId', 'snapshot_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.EmployeeId', 'employee_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.CustomerId', 'customer_id', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.IpAddress', 'ip_address', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.Latitude', 'latitude', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.Longitude', 'longitude', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.GpsAccuracy', 'gps_accuracy', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.City', 'city', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.Region', 'region', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.Country', 'country', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.Timezone', 'timezone', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.LocationRaw', 'location_raw', 'COLUMN';
EXEC sp_rename 'dbo.time_sheet_location_snapshots.CapturedAt', 'captured_at', 'COLUMN';

PRINT 'All columns renamed to snake_case successfully!'
GO
