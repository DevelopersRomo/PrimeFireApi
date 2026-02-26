# TimeSheet - Guía para Frontend

> La imagen provista es solo referencia de layout.

## Layout (según tu navbar actual)
- **Navbar lateral**: TimeSheet vive dentro de Workforce Management.
- **Grid principal (2 columnas)**:
  - **Columna izquierda** (stack vertical):
    - **Card User** (arriba): nombre, email, timezone.
    - **Card Time and buttons** (abajo): reloj actual, estado, botones.
  - **Columna derecha**:
    - **Card Filters and config** (arriba): filtros y configuración.
    - **Card Table** (abajo): tabla de resumen.

## Elementos por card
- **Card User**:
  - DisplayName
  - Email
  - Timezone actual
- **Card Time and buttons**:
  - Hora actual (reloj)
  - Estado: `Clocked in at HH:MM` o `Not clocked in`
  - `Time worked` (si hay punch abierto)
  - Botones **Clock In** / **Clock Out**
  - Aviso: “Select a customer to enable Clock In”
- **Card Filters and config**:
  - Selector de **Customer** (obligatorio)
  - Selector de **Vista**: day/week/month
  - Rango fechas (si aplica)
  - Botón **Show export** (si existe) y **Export to Excel**
- **Card Table**:
  - Columnas: Day, Regular Hrs, Overtime, Vacation, Holiday, Sick, Total Hrs
  - Paginado (Previous/Next)

## Pantallas y componentes
- **Header user**: nombre, email, timezone.
- **Selector de Customer**: obligatorio antes de clock in.
- **Clock in/out**: botones y estado del punch abierto.
- **Resumen**: tabla por día/semana/mes.
- **Export**: botón para export actual (filtros/rango).

## Flujo recomendado
1. **Al cargar**:
   - `GET /api/v1/timesheet/open` para saber si hay punch abierto.
   - `GET /api/v1/timesheet?view=month` para resumen inicial.
2. **Clock In**:
   - Validar `CustomerId`.
   - Pedir GPS (si user acepta).
   - `POST /api/v1/timesheet/clock-in`.
3. **Clock Out**:
   - Pedir GPS (si user acepta).
   - `POST /api/v1/timesheet/clock-out`.
4. **Refresh**: volver a pedir `open` y `timesheet`.

## Endpoints y payloads

### Clock In
`POST /api/v1/timesheet/clock-in`
```json
{
  "CustomerId": 123,
  "Note": "Arrived to site",
  "UseLocation": true,
  "Latitude": "25.6789",
  "Longitude": "-100.1234",
  "GpsAccuracy": "15"
}
```

### Clock Out
`POST /api/v1/timesheet/clock-out`
```json
{
  "Note": "Finished task",
  "UseLocation": true,
  "Latitude": "25.6789",
  "Longitude": "-100.1234",
  "GpsAccuracy": "12"
}
```

### Punch abierto
`GET /api/v1/timesheet/open`
```json
{
  "Punch": {
    "PunchId": 10,
    "EmployeeId": 5,
    "CustomerId": 123,
    "ClockInAt": "2026-02-07 18:25:00",
    "ClockOutAt": null,
    "WorkedMinutes": 0,
    "Status": "open",
    "Note": "Arrived to site",
    "Timezone": "America/Monterrey",
    "IpAddress": "187.1.2.3",
    "Latitude": "25.6789",
    "Longitude": "-100.1234",
    "GpsAccuracy": "15",
    "City": "Monterrey",
    "Region": "Nuevo Leon",
    "Country": "Mexico",
    "ApprovedBy": null,
    "ApprovedAt": null,
    "CreatedAt": "2026-02-07 18:25:00",
    "UpdatedAt": "2026-02-07 18:25:00"
  },
  "ElapsedMinutes": 12,
  "ElapsedHours": 0.2
}
```

### Resumen (tabla)
`GET /api/v1/timesheet?view=day&start_date=2026-02-01&end_date=2026-02-28&customer_id=123&skip=0&limit=50`
```json
{
  "Items": [
    {
      "PeriodStart": "2026-02-01",
      "PeriodEnd": "2026-02-01",
      "RegularHours": 6.0,
      "OvertimeHours": 2.0,
      "VacationHours": 0,
      "HolidayHours": 0,
      "SickHours": 0,
      "TotalHours": 8.0
    }
  ],
  "Totals": {
    "RegularHours": 6.0,
    "OvertimeHours": 2.0,
    "VacationHours": 0,
    "HolidayHours": 0,
    "SickHours": 0,
    "TotalHours": 8.0
  },
  "Skip": 0,
  "Limit": 50,
  "Total": 1
}
```

### Export
`GET /api/v1/timesheet/export?view=month&start_date=2026-02-01&end_date=2026-02-28&customer_id=123`
Devuelve CSV con headers:
```
period_start,period_end,regular_hours,overtime_hours,vacation_hours,holiday_hours,sick_hours,total_hours
```

### Ubicación (on-demand)
`GET /api/v1/timesheet/location?customer_id=123`

## UX / Estados
- **Clock In** deshabilitado si no hay Customer.
- **Clock Out** deshabilitado si no hay punch abierto.
- Mostrar `ElapsedMinutes/Hours` si existe punch abierto.
- Si user niega GPS, enviar `UseLocation=true` para IP.

## Errores comunes
- `409 There is already an open punch` → ya hay clock-in activo.
- `404 Open punch not found` → no hay punch abierto para clock-out.
- `404 Customer not found` → customer inválido.

## Configuración
Para IP geolocation se requiere `IPGEOLOCATION_API_KEY` en backend.

## Catalogs (TimeSheet settings)
El front debe leer el catálogo para configurar overtime:

- `GET /api/v1/catalogs/timesheet`
  - Devuelve `OvertimeDailyHours`, `OvertimeWeeklyHours`, `RoundToMinutes`, `IsActive`.
- El valor **OvertimeDailyHours** define cuándo empieza overtime en el cálculo.
- (Admin) `PUT /api/v1/catalogs/timesheet` actualiza las reglas.

Ejemplo response:
```json
{
  "SettingId": 1,
  "OvertimeDailyHours": "8.00",
  "OvertimeWeeklyHours": "40.00",
  "RoundToMinutes": null,
  "IsActive": true,
  "CreatedAt": "2026-02-08 16:58:58",
  "UpdatedAt": "2026-02-08 16:58:58"
}
```

## Admin (vista y acciones)
Objetivo: permitir a admin revisar punches de todos los empleados y tomar acciones.

### Listado global
`GET /api/v1/timesheet/admin`
- Filtros:
  - `employee_id`: puede enviarse n veces (`employee_id=1&employee_id=2`)
  - `customer_id`: puede enviarse n veces (`customer_id=2&customer_id=3`)
  - `status`: `open|closed|approved|rejected`
  - `start_date`, `end_date` (YYYY-MM-DD)
  - `skip`, `limit`
- Respuesta: lista de punches con `ClockInAt`, `ClockOutAt`, `WorkedMinutes`, `Note`, `CustomerId`, `Status`.
- UX: tabla con columnas Employee, Customer, ClockIn, ClockOut, Status, Note, Actions.

### Edición
`PATCH /api/v1/timesheet/{punch_id}`
- Permite corregir:
  - `ClockInAt`, `ClockOutAt` (recalcula `WorkedMinutes`)
  - `CustomerId`
  - `Note`
  - `Status`
- UX: modal de edición con validación de timestamps.

### Aprobación / Rechazo
`POST /api/v1/timesheet/{punch_id}/approve`
`POST /api/v1/timesheet/{punch_id}/reject`
- Cambia `Status` y guarda `ApprovedBy/ApprovedAt`.
- UX: botones rápidos en la tabla.

### Export admin
`GET /api/v1/timesheet/admin/export`
- Filtros: `employee_id` y `customer_id` admiten n valores, `status`, `start_date`, `end_date`
- Descarga `.xlsx` con columnas:
  - `employee_id`, `employee_name`
  - `day`, `clock_in_at`, `clock_out_at`
  - `worked_minutes`, `worked_hours`
  - `customer_id`, `customer_name`
  - `status`, `note`

### Permisos
Requiere `AdminActions` en módulo `timesheet`.
