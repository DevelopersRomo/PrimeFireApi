# Sistema Multi-Tenant - PrimeFire API

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Arquitectura](#arquitectura)
3. [Configuración Inicial](#configuración-inicial)
4. [Endpoints](#endpoints)
5. [Flujos de Uso](#flujos-de-uso)
6. [Estructura de Base de Datos](#estructura-de-base-de-datos)
7. [Ejemplos](#ejemplos)

---

## Introducción

El sistema multi-tenant permite que múltiples clientes externos tengan sus propias bases de datos independientes, mientras que PrimeFire mantiene una base de datos principal para gestión centralizada.

### Características Principales

- **Separación de Datos**: Cada tenant tiene su propia base de datos
- **Autenticación Dual**: 
  - Usuarios internos (PrimeFire): Login con Microsoft Azure AD
  - Usuarios externos: Login con email/password tradicional
- **Gestión Centralizada**: La BD principal (`PrimeFireCorp`) gestiona tenants y referencias de usuarios externos
- **Aprobación Manual**: Los usuarios externos requieren aprobación de admin para asignarles un tenant

---

## Arquitectura

### Bases de Datos

```
┌─────────────────────────────────┐
│   BD Principal (PrimeFireCorp)  │
│   - Tenants                     │
│   - ExternalUsers               │
│   - Employees (internos)        │
│   - TenantEmployees             │
└─────────────────────────────────┘
              │
              │ Referencias
              │
    ┌─────────┴─────────┬──────────────┐
    │                   │              │
┌───▼────┐      ┌──────▼─────┐  ┌─────▼─────┐
│ Tenant │      │  Tenant    │  │  Tenant   │
│   A    │      │     B      │  │     C     │
│        │      │            │  │           │
│ BD     │      │ BD         │  │ BD        │
│ Externa│      │ Externa    │  │ Externa   │
└────────┘      └────────────┘  └───────────┘
```

### Componentes Clave

1. **BD Principal**: Gestiona tenants, usuarios externos (referencias ligeras), y empleados internos
2. **BDs Externas**: Cada tenant tiene su propia BD con estructura completa (Employees, Jobs, Tickets, etc.)
3. **ConnectionManager**: Gestiona conexiones dinámicas a múltiples BDs según el tenant
4. **ExternalUsers**: Tabla ligera en BD principal que solo guarda email, password hash y referencia al tenant

---

## Configuración Inicial

### Paso 1: Migrar Base de Datos Principal

Ejecuta estos scripts en tu BD principal (`PrimeFireCorp`):

```sql
-- 1. Crear tablas de gestión de tenants
-- Ejecutar: bd/sql/tenants_migration.sql

-- 2. Crear tabla de usuarios externos
-- Ejecutar: bd/sql/add_external_users_table.sql

-- 3. Agregar PasswordHash a Employees (si no existe)
ALTER TABLE [dbo].[Employees] ADD [PasswordHash] [nvarchar](255) NULL;
GO

-- 4. Agregar CountryId a Jobs (si no existe)
-- Ejecutar: bd/sql/add_country_to_jobs.sql
```

### Paso 2: Crear Base de Datos Externa

Para cada cliente externo:

1. **Crear nueva BD** en SQL Server (ej: `PrimeFire_ClienteA`)

2. **Ejecutar script de inicialización**:
   ```sql
   -- Ejecutar: bd/sql/create_external_db.sql
   -- Este script crea todas las tablas necesarias
   ```

3. **Configurar conexión en `.env`**:
   ```ini
   # Formato: DB_CONNECTION_{TENANT_KEY}
   DB_CONNECTION_CLIENTE_A="mssql+pyodbc://@localhost\SQLEXPRESS/PrimeFire_ClienteA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
   ```

   **Nota**: Si usas autenticación de Windows (`Trusted_Connection=True`), el formato es:
   ```ini
   DB_CONNECTION_CLIENTE_A="mssql+pyodbc://@localhost\SQLEXPRESS/PrimeFire_ClienteA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
   ```

### Paso 3: Registrar Tenant en BD Principal

```sql
INSERT INTO Tenants (Name, DbConnectionKey, Description, IsActive)
VALUES ('Empresa Cliente A', 'CLIENTE_A', 'Entorno para Cliente A', 1);
```

**Importante**: El `DbConnectionKey` debe coincidir exactamente con el sufijo usado en `.env` (sin `DB_CONNECTION_`).

---

## Endpoints

### Autenticación

#### `POST /auth/register`

Registra un nuevo usuario externo.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Villa",
  "tenant_key": "CLIENTE_A"  // Opcional
}
```

**Comportamiento**:
- Si `tenant_key` está presente: Crea usuario en BD del tenant inmediatamente
- Si `tenant_key` es `null`: Guarda referencia en BD principal con tenant "PENDING" (requiere aprobación)

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### `POST /auth/token`

Login de usuario (interno o externo).

**Request** (form-data):
```
username: user@example.com
password: password123
```

**Response**:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Nota**: El token incluye `tenant_key` si es usuario externo, permitiendo acceso automático a su BD.

---

### Gestión de Tenants

#### `GET /tenants/list-all`

Lista todos los tenants registrados en la BD principal.

**Response**:
```json
[
  {
    "TenantId": 1,
    "Name": "Empresa Cliente A",
    "Description": "Entorno para Cliente A",
    "IsActive": true,
    "CreatedAt": "2025-01-15T10:00:00"
  }
]
```

#### `GET /tenants/my-tenants`

Lista los tenants a los que el usuario actual tiene acceso.

**Requiere**: Autenticación

**Response**: Lista de `TenantRead`

#### `GET /tenants/pending-users`

Lista usuarios externos pendientes de aprobación (Admin).

**Requiere**: Autenticación

**Response**:
```json
[
  {
    "ExternalUserId": 1,
    "Email": "user@example.com",
    "TenantId": null,
    "TenantName": "Pending Approval",
    "CreatedAt": "2025-01-15T10:00:00"
  }
]
```

#### `POST /tenants/approve-user`

Aprueba un usuario externo y le asigna un tenant.

**Request Body**:
```json
{
  "ExternalUserId": 1,
  "TenantId": 2,
  "Status": "Active"
}
```

**Comportamiento**:
1. Actualiza `ExternalUsers` para apuntar al tenant asignado
2. Crea el usuario completo en la BD del tenant correspondiente
3. El usuario puede hacer login y acceder a su BD

**Response**:
```json
{
  "message": "User approved and assigned to tenant",
  "external_user_id": 1,
  "tenant_id": 2,
  "tenant_name": "Empresa Cliente A",
  "status": "Active"
}
```

---

## Flujos de Uso

### Flujo 1: Registro con Tenant Key (Auto-aprobado)

```
1. Usuario → POST /auth/register { tenant_key: "CLIENTE_A" }
2. Sistema verifica tenant existe y está activo
3. Guarda en ExternalUsers (BD Principal)
4. Crea usuario en BD del Tenant
5. Retorna token con tenant_key
6. Usuario puede usar API inmediatamente
```

### Flujo 2: Registro sin Tenant Key (Requiere Aprobación)

```
1. Usuario → POST /auth/register { sin tenant_key }
2. Sistema guarda en ExternalUsers con tenant "PENDING"
3. Retorna token SIN tenant_key
4. Usuario NO puede acceder a endpoints que requieren tenant
5. Admin → GET /tenants/pending-users (ve usuarios pendientes)
6. Admin → POST /tenants/approve-user { ExternalUserId, TenantId }
7. Sistema crea usuario en BD del tenant
8. Usuario puede hacer login y acceder
```

### Flujo 3: Uso de API con Tenant

```
1. Usuario hace login → Recibe token con tenant_key
2. Usuario hace request → GET /employees
3. Sistema lee tenant_key del token JWT
4. ConnectionManager conecta a BD del tenant
5. Query se ejecuta en BD del tenant
6. Retorna datos del tenant
```

**Alternativa**: Usuario puede enviar header `X-Tenant-ID: CLIENTE_A` en lugar de depender del token.

---

## Estructura de Base de Datos

### BD Principal (`PrimeFireCorp`)

#### Tabla: `Tenants`
```sql
TenantId (PK)
Name
DbConnectionKey  -- Clave para buscar en .env (ej: "CLIENTE_A")
Description
IsActive
CreatedAt
```

#### Tabla: `ExternalUsers`
```sql
ExternalUserId (PK)
Email (UNIQUE)
PasswordHash
TenantId (FK → Tenants)
CreatedAt
```

**Nota**: Esta tabla solo guarda referencias ligeras. Los datos completos están en la BD del tenant.

#### Tabla: `TenantEmployees`
```sql
Id (PK)
TenantId (FK → Tenants)
EmployeeId (FK → Employees)  -- Solo para empleados internos
Status
IsDefault
CreatedAt
```

### BD Externa (Cada Tenant)

Estructura completa con todas las tablas:
- `Employees` (con `PasswordHash`)
- `Jobs` (con `CountryId`)
- `Tickets`, `TicketMessages`, `TicketAttachments`
- `Licences` (nota: tabla se llama "Licences" con 'c')
- `Curriculums`
- `HardwareInventory`
- `Modules`, `RoleModules`
- `TimeOffRequests`, `TimeOffBalances`, `Holidays`
- `Countries`, `Roles`, `Departments`

---

## Ejemplos

### Ejemplo 1: Registrar Usuario Externo (Sin Aprobación)

```bash
# 1. Registrar usuario
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "juan@cliente.com",
    "password": "pass123",
    "first_name": "Juan",
    "last_name": "Villa",
    "tenant_key": "CLIENTE_A"
  }'

# Response:
# {
#   "access_token": "eyJ...",
#   "token_type": "bearer"
# }

# 2. Usar token para acceder a endpoints
curl -X GET "http://localhost:8000/employees" \
  -H "Authorization: Bearer eyJ..."
  # El sistema detecta tenant_key del token y conecta a BD de CLIENTE_A
```

### Ejemplo 2: Flujo Completo con Aprobación

```bash
# 1. Usuario se registra sin tenant_key
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@empresa.com",
    "password": "pass123",
    "first_name": "Maria",
    "last_name": "Garcia"
  }'

# 2. Admin ve usuarios pendientes
curl -X GET "http://localhost:8000/tenants/pending-users" \
  -H "Authorization: Bearer <admin_token>"

# Response:
# [
#   {
#     "ExternalUserId": 1,
#     "Email": "maria@empresa.com",
#     "TenantId": 1,  // PENDING tenant
#     "TenantName": "Pending Approval"
#   }
# ]

# 3. Admin aprueba y asigna tenant
curl -X POST "http://localhost:8000/tenants/approve-user" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "ExternalUserId": 1,
    "TenantId": 2,  // ID del tenant "CLIENTE_A"
    "Status": "Active"
  }'

# 4. Usuario puede hacer login y acceder
curl -X POST "http://localhost:8000/auth/token" \
  -d "username=maria@empresa.com&password=pass123"

# El token ahora incluye tenant_key y puede acceder a su BD
```

### Ejemplo 3: Listar Tenants Disponibles

```bash
curl -X GET "http://localhost:8000/tenants/list-all"

# Response:
# [
#   {
#     "TenantId": 1,
#     "Name": "Pending Approval",
#     "IsActive": false
#   },
#   {
#     "TenantId": 2,
#     "Name": "Empresa Cliente A",
#     "DbConnectionKey": "CLIENTE_A",
#     "IsActive": true
#   }
# ]
```

---

## Variables de Entorno

### Formato de Conexión para Tenants

```ini
# BD Principal (ya existente)
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=PrimeFireCorp
DB_USERNAME=sa
DB_PASSWORD=tu_password

# BD Externa - Tenant A
DB_CONNECTION_CLIENTE_A="mssql+pyodbc://@localhost\SQLEXPRESS/PrimeFire_ClienteA?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"

# BD Externa - Tenant B
DB_CONNECTION_CLIENTE_B="mssql+pyodbc://sa:pass@server/PrimeFire_ClienteB?driver=ODBC+Driver+17+for+SQL+Server"
```

**Reglas**:
- El nombre después de `DB_CONNECTION_` debe coincidir con `DbConnectionKey` en la tabla `Tenants`
- Si usas autenticación Windows, usa `trusted_connection=yes` y deja usuario/password vacíos
- Si usas SQL Auth, incluye usuario y password en la URL

---

## Notas Importantes

1. **Separación de Datos**: Los usuarios externos NO se guardan en la BD principal (solo referencias). Sus datos completos viven en su BD del tenant.

2. **Token JWT**: Los tokens de usuarios externos incluyen `tenant_key`, permitiendo acceso automático a su BD sin necesidad de header `X-Tenant-ID`.

3. **Header Alternativo**: Si prefieres, puedes enviar `X-Tenant-ID: CLIENTE_A` en cada request en lugar de depender del token.

4. **Tabla Licences**: La tabla se llama `Licences` (con 'c'), no `Licenses`. El modelo Python ya está corregido.

5. **Migraciones**: Si creaste una BD externa antes de agregar `CountryId` a `Jobs`, ejecuta `bd/sql/add_countryid_to_jobs.sql` en esa BD.

6. **Tenant PENDING**: Existe un tenant especial "PENDING" para usuarios sin asignar. No debe tener conexión configurada en `.env`.

---

## Troubleshooting

### Error: "Invalid Tenant ID: X"

**Causa**: El tenant no existe en la tabla `Tenants` o no tiene conexión configurada en `.env`.

**Solución**:
1. Verifica que el tenant existe: `GET /tenants/list-all`
2. Verifica que `DbConnectionKey` coincide con la variable en `.env`
3. Verifica que la variable `DB_CONNECTION_{KEY}` está en `.env`

### Error: "Invalid object name 'dbo.Licenses'"

**Causa**: La tabla se llama `Licences` (con 'c'), no `Licenses`.

**Solución**: El modelo ya está corregido. Si persiste, verifica que la BD tenga la tabla `Licences`.

### Error: "Invalid column name 'CountryId'" en Jobs

**Causa**: La BD externa fue creada antes de agregar `CountryId` a `Jobs`.

**Solución**: Ejecuta `bd/sql/add_countryid_to_jobs.sql` en la BD externa.

### `/tenants/list-all` retorna vacío

**Causa**: No hay tenants registrados o hay problema de conexión.

**Solución**: 
1. Verifica que ejecutaste `tenants_migration.sql` en la BD principal
2. Inserta un tenant manualmente:
   ```sql
   INSERT INTO Tenants (Name, DbConnectionKey, IsActive)
   VALUES ('Test Tenant', 'TEST', 1);
   ```

---

## Resumen de Scripts SQL

| Script | BD | Descripción |
|--------|----|-------------|
| `tenants_migration.sql` | Principal | Crea tablas `Tenants` y `TenantEmployees` |
| `add_external_users_table.sql` | Principal | Crea tabla `ExternalUsers` |
| `create_external_db.sql` | Externa | Crea estructura completa para nuevo tenant |
| `add_country_to_jobs.sql` | Principal | Agrega `CountryId` a `Jobs` |
| `add_countryid_to_jobs.sql` | Externa | Agrega `CountryId` a `Jobs` en BD externa |

