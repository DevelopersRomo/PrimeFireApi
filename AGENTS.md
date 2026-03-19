# PrimeFireApi - Agenda de Proyecto y Documentación Técnica

## 1. Resumen Ejecutivo

**PrimeFireApi** es el backend de la solución empresarial PrimeFire, desarrollado en Python con el framework FastAPI. Proporciona una API RESTful completa para la gestión de recursos empresariales incluyendo empleados, clientes, tickets de soporte, licencias, productos, cotizaciones, empleos, inventario de hardware, gestión de tiempo libre, hojas de tiempo y notificaciones.

### Características Principales
- **API RESTful** con documentación automática via Swagger/OpenAPI
- **Autenticación Multiesquema**: Azure AD PKCE, Password Grant, JWT Bearer, Token de contacto
- **Base de Datos**: Microsoft SQL Server en Azure
- **Integración**: Microsoft 365, Azure AD, Microsoft Graph, Teams
- **Notificaciones**: Email, Teams, Webhooks
- **Background Tasks**: Sincronización automática de empleados

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Arquitectura

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PRIMEFIRE API                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   Clients    │    │   Frontend   │    │   External APIs      │  │
│  │  (Angular)  │    │  (PrimeFire) │    │  (Azure AD, Graph)   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘  │
│         │                   │                       │               │
│         └───────────────────┼───────────────────────┘               │
│                             │ HTTPS                                   │
│                     ┌──────▼──────┐                                 │
│                     │   FASTAPI   │                                 │
│                     │   Server    │                                 │
│                     │  (Uvicorn)  │                                 │
│                     └──────┬──────┘                                 │
│                            │                                         │
│         ┌──────────────────┼──────────────────┐                    │
│         │                  │                  │                    │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐            │
│  │   Routers   │    │   Services  │    │   Background│            │
│  │   (API)     │    │  (Notif)    │    │   Tasks     │            │
│  └──────┬──────┘    └─────────────┘    └─────────────┘            │
│         │                                                         │
│  ┌──────▼──────┐                                                  │
│  │   Models    │  ◄── SQLModel (ORM)                              │
│  │  (Entities) │                                                  │
│  └──────┬──────┘                                                  │
│         │                                                         │
│  ┌──────▼──────┐    ┌─────────────────────────────────────────┐  │
│  │  Schemas    │    │           SQL Server                    │  │
│  │  (DTOs)     │    │      (Azure SQL Database)              │  │
│  └─────────────┘    └─────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.2 Capas de la Aplicación

| Capa | Descripción | Directorio |
|------|-------------|------------|
| **Routers** | Endpoints HTTP, validación de requests | `api/` |
| **Models** | Entidades de base de datos (SQLModel) | `models/` |
| **Schemas** | DTOs, validación de datos (Pydantic) | `schemas/` |
| **Services** | Lógica de negocio, notificaciones | `services/` |
| **Core** | Configuración, utilitários | `core/` |
| **Background** | Tareas programadas, sincronización | `core/background_tasks.py` |

---

## 3. Tecnologías y Dependencias

### 3.1 Dependencias Principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `fastapi` | 0.135.1 | Framework web asíncrono |
| `uvicorn[standard]` | 0.41.0 | Servidor ASGI |
| `sqlmodel` | 0.0.37 | ORM para SQL |
| `pydantic` | 2.12.5 | Validación de datos |
| `pydantic-settings` | 2.13.1 | Configuración |
| `python-jose[cryptography]` | 3.5.0 | Tokens JWT |
| `PyJWT` | 2.11.0 | Manejo de JWT |
| `fastapi-azure-auth` | 5.2.0 | Azure AD Auth |
| `passlib[bcrypt]` | 1.7.4 | Hash de contraseñas |
| `pyodbc` | 5.3.0 | SQL Server driver |
| `httpx` | 0.28.1 | Cliente HTTP async |
| `python-multipart` | 0.0.22 | Form-data |
| `python-dotenv` | 1.2.2 | Variables de entorno |
| `openpyxl` | - | Excel processing |
| `schedule` | - | Task scheduling |
| `pytest` | 9.0.2 | Testing |
| `pytest-asyncio` | 1.3.0 | Async testing |

### 3.2 Herramientas de Calidad

| Herramienta | Propósito |
|-------------|-----------|
| `ruff` | Linting de Python |
| `mypy` | Type checking |
| `codespell` | Spell checking |

---

## 4. Estructura de Directorios

```
PrimeFireApi/
├── api/                          # Endpoints/Routers
│   ├── __init__.py
│   ├── auth.py                   # Autenticación
│   ├── backups.py                 # Backups
│   ├── catalogs.py               # Catálogos
│   ├── countries.py              # Países
│   ├── curriculums.py            # Currículums
│   ├── customer_attachments.py   # Archivos clientes
│   ├── customer_contacts.py      # Contactos clientes
│   ├── customer_notes.py         # Notas clientes
│   ├── customers.py              # Clientes
│   ├── dependencies.py           # Dependencias auth
│   ├── employees.py             # Empleados
│   ├── hardware_inventory.py     # Inventario hardware
│   ├── jobs.py                  # Empleos
│   ├── licenses.py              # Licencias
│   ├── modules.py               # Módulos sistema
│   ├── notifications.py         # Notificaciones
│   ├── permissions.py           # Permisos
│   ├── products.py              # Productos
│   ├── quotations.py           # Cotizaciones
│   ├── roles.py                # Roles
│   ├── tenants.py              # Inquilinos
│   ├── ticket_attachments.py    # Archivos tickets
│   ├── ticket_messages.py      # Mensajes tickets
│   ├── tickets.py              # Tickets soporte
│   ├── time_off.py             # Tiempo libre
│   └── timesheet.py            # Hojas tiempo
│
├── models/                       # Modelos DB (SQLModel)
│   ├── __init__.py
│   ├── addresses.py
│   ├── countries.py
│   ├── curriculums.py
│   ├── customers.py
│   ├── employees.py
│   ├── hardware_inventory.py
│   ├── jobs.py
│   ├── licenses.py
│   ├── modules.py
│   ├── products.py
│   ├── quotations.py
│   ├── tenants.py
│   ├── ticket_messages.py
│   ├── tickets.py
│   ├── time_off.py
│   └── timesheet.py
│
├── schemas/                      # DTOs (Pydantic)
│   ├── __init__.py
│   ├── base.py
│   ├── catalogs.py
│   ├── curriculums.py
│   ├── hardware_inventory.py
│   ├── jobs.py
│   ├── licenses.py
│   ├── notifications.py
│   ├── products.py
│   ├── quotations.py
│   ├── tickets.py
│   ├── ticket_messages.py
│   ├── time_off.py
│   └── timesheet.py
│
├── services/                     # Servicios internos
│   ├── __init__.py
│   └── notifications/          # Módulo notificaciones
│       ├── __init__.py
│       ├── auth.py
│       ├── contact_primefire.py
│       ├── email_functions.py
│       ├── forms.py
│       ├── notifications.py
│       ├── schemas.py
│       └── teams_functions.py
│
├── core/                         # Configuración central
│   ├── __init__.py
│   ├── config.py               # Settings
│   ├── microsoft_graph.py      # Graph API client
│   └── background_tasks.py     # Tareas background
│
├── bd/                           # Base de datos
│   ├── connection.py           # Conexión DB
│   └── sql/                    # Scripts SQL
│       ├── ADD_MODULES_PERMISSIONS_TABLES.sql
│       └── employees.sql
│
├── scripts/                      # Scripts utilitarios
│   ├── __init__.py
│   ├── generate_complete_backup.py
│   └── generate_partial_backup.py
│
├── helpers/                      # Helpers
│   ├── __init__.py
│   └── date_helpers.py
│
├── tests/                        # Pruebas
│   ├── __init__.py
│   ├── test_jobs.py
│   └── test_licenses.py
│
├── uploads/                      # Archivos subidos
│   └── curriculums/
│
├── main.py                       # Punto de entrada
├── requirements.txt              # Dependencias
└── venv/                         # Entorno virtual
```

---

## 5. Módulos de la API (Routers)

### 5.1 Lista Completa de Routers

| # | Router | Prefijo | Descripción | Estado |
|---|--------|---------|-------------|--------|
| 1 | `licenses_router` | `/licenses` | Gestión de licencias de software | ✅ |
| 2 | `employees_router` | `/employees` | Gestión de empleados | ✅ |
| 3 | `jobs_router` | `/jobs` | Bolsa de trabajo/empleos | ✅ |
| 4 | `curriculums_router` | `/curriculums` | Currículums/postulaciones | ✅ |
| 5 | `roles_router` | `/roles` | Roles de usuario | ✅ |
| 6 | `countries_router` | `/countries` | Catálogo países | ✅ |
| 7 | `modules_router` | `/modules` | Módulos del sistema | ✅ |
| 8 | `permissions_router` | `/permissions` | Permisos | ✅ |
| 9 | `tickets_router` | `/tickets` | Tickets de soporte | ✅ |
| 10 | `ticket_messages_router` | - | Mensajes de tickets | ✅ |
| 11 | `ticket_attachments_router` | - | Archivos de tickets | ✅ |
| 12 | `hardware_inventory_router` | `/hardware` | Inventario hardware | ✅ |
| 13 | `time_off_router` | - | Solicitudes tiempo libre | ✅ |
| 14 | `timesheet_router` | - | Hojas de tiempo | ✅ |
| 15 | `catalogs_router` | - | Catálogos genéricos | ✅ |
| 16 | `notifications_router` | `/notifications` | Notificaciones | ✅ |
| 17 | `tenants_router` | `/tenants` | Multi-tenancy | ✅ |
| 18 | `auth_router` | `/auth` | Autenticación | ✅ |
| 19 | `customers_router` | `/customers` | Clientes | ✅ |
| 20 | `customer_notes_router` | - | Notas de clientes | ✅ |
| 21 | `customer_contacts_router` | - | Contactos de clientes | ✅ |
| 22 | `customer_attachments_router` | - | Archivos de clientes | ✅ |
| 23 | `products_router` | `/products` | Productos | ✅ |
| 24 | `quotations_router` | - | Cotizaciones | ✅ |
| 25 | `backups_router` | `/backups` | Backups | ✅ |

### 5.2 Endpoints Especiales

| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/` | GET | Redirige a `/docs` | ❌ |
| `/health` | GET | Health check | ❌ |
| `/debug-auth` | GET | Debug autenticación Azure | ✅ Azure |
| `/debug-token` | GET | Debug validación token | ✅ Bearer |

---

## 6. Modelos de Datos (Entities)

### 6.1 Entidades Principales

| Entidad | Descripción | Archivos relacionados |
|---------|-------------|----------------------|
| `Employees` | Empleados del sistema | `employees.py` |
| `Customers` | Clientes empresariales | `customers.py` |
| `CustomerContacts` | Contactos de clientes | `customer_contacts.py` |
| `CustomerNotes` | Notas de clientes | `customer_notes.py` |
| `CustomerAttachments` | Archivos de clientes | `customer_attachments.py` |
| `Addresses` | Direcciones | `addresses.py` |
| `Countries` | Países | `countries.py` |
| `Products` | Productos | `products.py` |
| `Quotations` | Cotizaciones | `quotations.py` |
| `Tickets` | Tickets de soporte | `tickets.py` |
| `TicketMessages` | Mensajes en tickets | `ticket_messages.py` |
| `TicketAttachments` | Archivos de tickets | `ticket_attachments.py` |
| `Licenses` | Licencias de software | `licenses.py` |
| `Jobs` | Empleos/posiciones | `jobs.py` |
| `Curriculums` | Currículums/postulaciones | `curriculums.py` |
| `HardwareInventory` | Inventario hardware | `hardware_inventory.py` |
| `TimeOff` | Solicitudes tiempo libre | `time_off.py` |
| `Timesheet` | Hojas de tiempo | `timesheet.py` |
| `Modules` | Módulos del sistema | `modules.py` |
| `Tenants` | Inquilinos/multi-tenancy | `tenants.py` |

---

## 7. Autenticación y Seguridad

### 7.1 Esquemas de Autenticación

La API soporta múltiples esquemas de autenticación simultáneos:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY SCHEMES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ Azure AD PKCE   │    │  Local Password │                   │
│  │ (OAuth2)        │    │  (OAuth2)        │                   │
│  │                 │    │                  │                   │
│  │ - Authorization │    │ - Username      │                   │
│  │   Code Flow     │    │ - Password      │                   │
│  │ - PKCE          │    │ - Grant Type    │                   │
│  │ - Scopes        │    │   password      │                   │
│  └────────┬────────┘    └────────┬────────┘                   │
│           │                      │                             │
│           └──────────┬───────────┘                             │
│                      ▼                                         │
│           ┌────────────────────────┐                           │
│           │   JWT Bearer Token    │                           │
│           │   (Token Validation)  │                           │
│           └────────────────────────┘                           │
│                                                                  │
│   ┌─────────────────────────────────────────┐                  │
│   │      Contact Token (Public)             │                  │
│   │  Header: x-contact-token               │                  │
│   └─────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Variables de Autenticación

```bash
# Azure AD
TENANT_ID              # Azure AD Tenant ID
BACKEND_CLIENT_ID      # Client ID backend
BACKEND_CLIENT_SECRET  # Secret backend
FRONTEND_CLIENT_ID     # Client ID frontend

# Microsoft Graph (Service-to-Service)
MICROSOFT_TENANT_ID
MICROSOFT_CLIENT_ID
MICROSOFT_CLIENT_SECRET

# Token público para contacto
CONTACT_PRIMEFIRE_API_TOKEN=7dd8430e-2c2b-4239-9ddf-b299dea05bc4
```

### 7.3 Configuración de Seguridad (main.py)

```python
security_schemes = {
    "AzureAD_PKCE_single_tenant": {
        "type": "oauth2",
        "flows": {"authorizationCode": {...}}
    },
    "LocalPasswordAuth": {
        "type": "oauth2",
        "flows": {"password": {"tokenUrl": "/auth/token"}}
    },
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    },
    "ContactTokenAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "x-contact-token"
    }
}
```

---

## 8. Servicios de Notificaciones

### 8.1 Arquitectura de Notificaciones

```
┌─────────────────────────────────────────────────────────────────┐
│                   SERVICIOS DE NOTIFICACIONES                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                           │
│  │ notifications.py │  ◄── Orquestador principal               │
│  └────────┬────────┘                                           │
│           │                                                    │
│     ┌─────┴─────┬──────────────────┐                          │
│     ▼           ▼                  ▼                          │
│  ┌──────┐  ┌──────────┐  ┌────────────┐                       │
│  │Email │  │  Teams   │  │ Webhook    │                       │
│  │ Func │  │  Func    │  │  (Future)  │                       │
│  └──┬───┘  └────┬─────┘  └────────────┘                       │
│     │           │                                               │
│     └─────┬─────┘                                               │
│           ▼                                                     │
│    ┌──────────────┐                                            │
│    │  SMTP/Teams  │                                            │
│    │     API      │                                            │
│    └──────────────┘                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Módulos de Notificaciones

| Módulo | Funcionalidad |
|--------|---------------|
| `email_functions.py` | Envío de emails via SMTP |
| `teams_functions.py` | Mensajes a Microsoft Teams |
| `forms.py` | Generación de formularios HTML |
| `contact_primefire.py` | Endpoint de contacto público |
| `auth.py` | Autenticación para notificaciones |
| `notifications.py` | Orquestador de notificaciones |
| `schemas.py` | Esquemas de validación |

### 8.3 Canales de Entrega

1. **Email (SMTP)**: Notificaciones por correo electrónico
2. **Microsoft Teams**: Mensajes a canales o usuarios
3. **Webhook**: Notificaciones HTTP (futuro)

---

## 9. Background Tasks

### 9.1 Sincronización de Empleados

El sistema implementa sincronización automática de empleados desde Microsoft 365:

```
┌─────────────────────────────────────────────────────────────────┐
│              BACKGROUND TASKS - SYNC EMPLOYEES                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STARTUP                          SHUTDOWN                       │
│    │                                │                           │
│    ▼                                │                           │
│  ┌──────────────────┐               │                           │
│  │ sync_on_startup  │               │                           │
│  │  (One-time)      │               │                           │
│  └────────┬─────────┘               │                           │
│           │                        │                           │
│           ▼                        │                           │
│  ┌──────────────────┐   periodic  │                           │
│  │ periodic_sync    │◄────────────┤                           │
│  │  (Every 24h)     │   (config)  │                           │
│  └──────────────────┘            │                           │
│                                   ▼                           │
│                          ┌──────────────────┐                 │
│                          │ stop_periodic    │                 │
│                          │     _sync()       │                 │
│                          └──────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Configuración de Sync

| Variable | Default | Descripción |
|----------|---------|-------------|
| `SYNC_EMPLOYEES_PRIMEFIRE` | `true` | Habilitar sync inicial |
| `ENABLE_AUTO_SYNC` | `true` | Sync automático |
| `SYNC_INTERVAL_HOURS` | `24` | Intervalo en horas |

---

## 10. Scripts Disponibles

| Script | Descripción |
|--------|-------------|
| `generate_complete_backup.py` | Genera backup completo de la DB |
| `generate_partial_backup.py` | Genera backup parcial |

---

## 11. Configuración de Variables de Entorno

### 11.1 Archivo .env

```bash
# Entorno
ENVIRONMENT=local

# Azure AD
TENANT_ID=
BACKEND_CLIENT_ID=
BACKEND_CLIENT_SECRET=
FRONTEND_CLIENT_ID=

# Microsoft Graph
MICROSOFT_TENANT_ID=
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# Sync
SYNC_EMPLOYEES_PRIMEFIRE=true
ENABLE_AUTO_SYNC=true
SYNC_INTERVAL_HOURS=24

# Notificaciones
BOT_EMAIL=
SUPPORT_EMAIL=info@primefire.us
APP_URL=https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net
CONTACT_PRIMEFIRE_API_TOKEN=7dd8430e-2c2b-4239-9ddf-b299dea05bc4

# Archivos
UPLOAD_DIR=uploads

# Geolocation
IPGEOLOCATION_API_KEY=
```

---

## 12. Comandos de Desarrollo

### 12.1 Comandos Principales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor desarrollo
uvicorn main:app --reload

# Ejecución con puerto específico
uvicorn main:app --host 0.0.0.0 --port 8000

# Ejecutar tests
pytest

# Ejecutar tests con coverage
pytest --cov

# Linting con ruff
ruff check .

# Type checking con mypy
mypy .

# Spell checking
codespell
```

---

## 13. URLs y Endpoints

### 13.1 Entornos

| Entorno | URL API | URL Frontend |
|---------|---------|---------------|
| Local | http://localhost:8000 | http://localhost:4200 |
| Dev | https://primefireapi-dev.azurewebsites.net | - |
| Prod | https://primefireapi.azurewebsites.net | https://app.primefire.us |

### 13.2 Documentación

| Entorno | Swagger URL |
|---------|-------------|
| Local | http://localhost:8000/docs |
| Prod | https://primefireapi.azurewebsites.net/docs |

### 13.3 CORS Origins

```python
origins = [
    "https://primefireapp-cgh0c9ace5haapcc.mexicocentral-01.azurewebsites.net",
    "https://app.devromo.com",
    "https://app.primefire.us",
    "http://localhost:4200",
    "http://localhost:4201",
]
```

---

## 14. Skills de Claude Code Disponibles

### 14.1 Skills Globales

| Skill | Descripción | Aplicado |
|-------|-------------|----------|
| `update-config` | Configurar Claude Code via settings.json | ✅ |
| `simplify` | Revisar código para reutilización | ✅ |
| `loop` | Ejecutar comandos en intervalos | ✅ |
| `claude-api` | Construir apps con API de Claude | ✅ |
| `architecture-guardrails` | Reglas arquitectura Engram | ❌ |
| `branch-pr` | Workflow de branch y PR | ❌ |
| `business-rules` | Reglas de negocio | ❌ |
| `commit-hygiene` | Estándares de commit | ❌ |
| `cultural-norms` | Normas culturales | ❌ |
| `dashboard-htmx` | Reglas HTMX | ❌ |
| `docs-alignment` | Alineación documentación | ❌ |
| `gentleman-bubbletea` | Patrones TUI | ❌ |
| `memory-protocol` | Memoria persistente | ❌ |
| `mypy` | Type checking Python | ✅ |
| `plugin-thin` | Adaptadores de plugins | ❌ |
| `pr-review-deep` | Revisión técnica | ❌ |
| `project-structure` | Estructura repositorio | ❌ |
| `ruff-linting` | Linting Python | ✅ |
| `sdd-flow` | Spec-Driven Development | ❌ |
| `server-api` | Guardrails API | ❌ |
| `testing-coverage` | Estándares TDD | ✅ |
| `tui-quality` | Calidad TUI | ❌ |
| `ui-elements` | Elementos UI | ❌ |
| `visual-language` | Lenguaje visual | ❌ |

### 14.2 Skills del Proyecto

| Skill | Descripción | Estado |
|-------|-------------|--------|
| `fastapi-templates` | Crear proyectos FastAPI production-ready | ✅ |
| `find-skills` | Descubrir e instalar skills | ✅ |
| `mcp-builder` | Crear servidores MCP | ✅ |
| `memory-merger` | Mergear memorias | ✅ |
| `obsidian-markdown` | Markdown de Obsidian | ✅ |
| `python-testing-patterns` | Testing con pytest | ✅ |
| `self-improving-agent` | Agente auto-mejorable | ✅ |
| `skill-creator` | Crear nuevos skills | ✅ |
| `skill-creator-prowler` | Crear skills AI agent | ✅ |
| `skill-sync-prowler` | Sincronizar metadata skills | ✅ |

---

## 15. Mejores Prácticas de Desarrollo

### 15.1 Estándares de Código

1. **Type Hints**: Usar type hints en todas las funciones
2. **Docstrings**: Documentar funciones públicas
3. **Nomenclatura**: snake_case para funciones, PascalCase para clases
4. **Imports**: Ordenar imports (stdlib, third-party, local)

### 15.2 Testing

1. **pytest**: Framework de testing
2. **Fixtures**: Usar fixtures para setup/teardown
3. **Async**: Usar pytest-asyncio para tests async

### 15.3 Seguridad

1. **Secrets**: Nunca commitear secrets
2. **Auth**: Validar tokens en cada request
3. **CORS**: Configurar orígenes permitidos

---

## 16. Roadmap y Mejoras Futuras

### 16.1 Pendientes

- [ ] Implementar cache con Redis
- [ ] Más unit tests (cobertura > 80%)
- [ ] Pipeline CI/CD
- [ ] Monitoreo y logging centralizado
- [ ] Rate limiting
- [ ] API versioning
- [ ] Documentación completa OpenAPI

---

## 17. Contacto y Recursos

| Recurso | URL |
|---------|-----|
| Swagger UI | `/docs` |
| ReDoc | `/redoc` |
| Health Check | `/health` |
| Support Email | info@primefire.us |

---

*Documento generado: 2026-03-18*
*Proyecto: PrimeFireApi*
*Versión API: 1.0.0*
*Framework: FastAPI 0.135.1*
*Python: 3.13+*