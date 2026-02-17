# TimeSheet - Reglas de negocio y alcance

> La imagen provista es solo referencia de layout.

## Objetivo
Controlar el tiempo trabajado por empleado mediante punches (clock in/out), con relación obligatoria a Customer, cálculo de horas regulares y overtime, integración con Time Off y soporte de aprobaciones admin.

## Entidades principales
- **TimeSheetPunch**: registro de entrada/salida con timestamps exactos.
- **TimeSheetSettings**: catálogo para reglas de overtime.
- **TimeSheetLocationSnapshot**: captura de geolocalización (IP/GPS) bajo demanda.

## Reglas clave
1. **Un punch abierto por usuario**: no puede existir más de un `open`.
2. **Customer obligatorio**: cada punch requiere `CustomerId`.
3. **Hora exacta**: se guarda `ClockInAt` y `ClockOutAt` (UTC string `YYYY-MM-DD HH:MM:SS`).
4. **Horas calculadas**: `WorkedMinutes` se calcula al cerrar (ClockOut - ClockIn).
5. **Overtime**: se separa de Regular usando `OvertimeDailyHours` (y opcionalmente `OvertimeWeeklyHours` si se activa).
6. **Time Off integrado**: `Vacation/Sick/Holiday` provienen de `time_off` (solo aprobados).
7. **Notas**: `Note` opcional por punch.
8. **Admin**: puede listar, editar punch, aprobar/rechazar.
9. **Ubicación**: se guarda IP geolocation y GPS si el front lo envía.

## Estados de punch
- `open`: clock in activo.
- `closed`: clock out realizado.
- `approved`: aprobado por admin.
- `rejected`: rechazado por admin.

## Cálculo de horas
- **Regular**: `min(WorkedHours, OvertimeDailyHours)`.
- **Overtime**: `max(WorkedHours - OvertimeDailyHours, 0)`.
- **Totales**: Regular + Overtime + TimeOff (vacation/holiday/sick) por periodo.

## Integración con Time Off
Se agregan horas de:
- `Vacation`: `AbsenceType = vacation`
- `Sick`: `AbsenceType = sick`
- `Holiday`: desde tabla `Holidays`

Solo se consideran **aprobados**. Si el request es por días, se asignan `8.00` horas por día; si es por horas, se prorratea por día.

## Paginado y vistas
El resumen soporta:
- **view=day**: total por día
- **view=week**: total por semana
- **view=month**: total por mes

Paginado con `skip/limit`. Filtros por `customer_id`.

## Exportación
Exporta el mismo resumen visible (filtros/rango aplicados).
Formato actual: CSV (compatible con Excel).

## Permisos (admin)
Se requiere `AdminActions` en módulo `timesheet` para:
- listar global (`/timesheet/admin`)
- editar punch
- aprobar/rechazar
- export por empleado

## Riesgos / supuestos
- IP geolocation no es GPS; es aproximado.
- Si el punch queda abierto, no cuenta en resumen hasta que cierre.
- Overtime semanal solo se aplica si se decide activar la regla.
