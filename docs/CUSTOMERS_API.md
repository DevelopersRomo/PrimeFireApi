# Customers API Documentation

## Base URL
Todos los endpoints están bajo `/customers` o sub-rutas relacionadas.

## Enumeraciones

### CustomerType
- `residential` - Cliente residencial
- `commercial` - Cliente comercial

### Market (Solo para Commercial)
- `commercial`
- `individual`
- `environmental`
- `engineering`

### DtdPotential (Solo para Commercial)
- `very_high`
- `high`
- `medium`
- `low`
- `very_low`
- `one_off`
- `prospect`

---

## Customers

### GET /customers
Lista todos los clientes con filtros opcionales.

**Query Parameters:**
- `customer_type` (opcional): `CustomerType`
- `market` (opcional): `Market`
- `dtd_potential` (opcional): `DtdPotential`
- `search` (opcional): `string` - Busca en nombre, compañía, email
- `skip` (opcional): `number` - Default: 0
- `limit` (opcional): `number` - Default: 50, Max: 100

**Response:** `Customer[]`

---

### GET /customers/{customer_id}
Obtiene un cliente por ID.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `Customer`

---

### GET /customers/{customer_id}/merged
Obtiene un cliente con notes, contacts y attachments en un solo response.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `CustomerMerged`

---

### POST /customers
Crea un nuevo cliente.

**Request Body:** `CustomerCreate`

**Campos CustomerCreate:**
- `CustomerType`: `CustomerType` (requerido)
- `CompanyName`: `string` (opcional, requerido si CustomerType = commercial)
- `FirstName`: `string` (opcional, requerido si CustomerType = residential)
- `LastName`: `string` (opcional, requerido si CustomerType = residential)
- `AdditionalName`: `string` (opcional)
- `Market`: `Market` (opcional, solo para commercial)
- `DtdPotential`: `DtdPotential` (opcional, solo para commercial)
- `PrimaryEmail`: `string` (opcional, pero al menos Email o Phone requerido)
- `PrimaryPhone`: `string` (opcional, pero al menos Email o Phone requerido)
- `PrimaryAddress`: `AddressCreate` (opcional)
- `PrimaryAddressId`: `number` (opcional)

**Campos AddressCreate:**
- `Address1`: `string` (requerido)
- `Address2`: `string` (opcional)
- `City`: `string` (requerido)
- `State`: `string` (requerido)
- `ZipCode`: `string` (requerido)
- `CountryId`: `number` (requerido)
- `GooglePlaceId`: `string` (opcional)

**Response:** `Customer`

**Validaciones:**
- Residential: FirstName y LastName requeridos, CompanyName/Market/DtdPotential no permitidos
- Commercial: CompanyName requerido
- Al menos PrimaryEmail o PrimaryPhone debe existir

---

### PATCH /customers/{customer_id}
Actualiza un cliente existente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Request Body:** `CustomerUpdate` (todos los campos opcionales)

**Campos CustomerUpdate:**
- `CustomerType`: `CustomerType` (opcional)
- `CompanyName`: `string` (opcional)
- `FirstName`: `string` (opcional)
- `LastName`: `string` (opcional)
- `AdditionalName`: `string` (opcional)
- `Market`: `Market` (opcional)
- `DtdPotential`: `DtdPotential` (opcional)
- `PrimaryEmail`: `string` (opcional)
- `PrimaryPhone`: `string` (opcional)
- `PrimaryAddress`: `AddressUpdate` (opcional)
- `PrimaryAddressId`: `number` (opcional)

**Campos AddressUpdate:**
- `Address1`: `string` (opcional)
- `Address2`: `string` (opcional)
- `City`: `string` (opcional)
- `State`: `string` (opcional)
- `ZipCode`: `string` (opcional)
- `CountryId`: `number` (opcional)
- `GooglePlaceId`: `string` (opcional)

**Response:** `Customer`

---

### DELETE /customers/{customer_id}
Elimina un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `{ success: boolean, message: string }`

---

## Customer Notes

### GET /customers/{customer_id}/notes
Lista todas las notas de un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `CustomerNote[]`

---

### POST /customers/{customer_id}/notes
Crea una nueva nota para un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Request Body:** `CustomerNoteCreate`
- `NoteText`: `string` (requerido)

**Response:** `CustomerNote`

---

### PATCH /customers/{customer_id}/notes/{note_id}
Actualiza una nota existente.

**Path Parameters:**
- `customer_id`: `number` (requerido)
- `note_id`: `number` (requerido)

**Request Body:** `CustomerNoteUpdate`
- `NoteText`: `string` (opcional)

**Response:** `CustomerNote`

---

### DELETE /customers/{customer_id}/notes/{note_id}
Elimina una nota.

**Path Parameters:**
- `customer_id`: `number` (requerido)
- `note_id`: `number` (requerido)

**Response:** `{ success: boolean, message: string }`

---

## Customer Alternate Contacts

### GET /customers/{customer_id}/contacts
Lista todos los contactos alternativos de un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `CustomerAlternateContact[]`

---

### POST /customers/{customer_id}/contacts
Crea un nuevo contacto alternativo.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Request Body:** `CustomerAlternateContactCreate`
- `Name`: `string` (requerido)
- `Email`: `string` (opcional, pero al menos Email o Phone requerido)
- `Phone`: `string` (opcional, pero al menos Email o Phone requerido)

**Response:** `CustomerAlternateContact`

**Validaciones:**
- Al menos Email o Phone debe existir

---

### PATCH /customers/{customer_id}/contacts/{contact_id}
Actualiza un contacto alternativo.

**Path Parameters:**
- `customer_id`: `number` (requerido)
- `contact_id`: `number` (requerido)

**Request Body:** `CustomerAlternateContactUpdate`
- `Name`: `string` (opcional)
- `Email`: `string` (opcional)
- `Phone`: `string` (opcional)

**Response:** `CustomerAlternateContact`

**Validaciones:**
- Si se actualiza, al menos Email o Phone debe existir

---

### DELETE /customers/{customer_id}/contacts/{contact_id}
Elimina un contacto alternativo.

**Path Parameters:**
- `customer_id`: `number` (requerido)
- `contact_id`: `number` (requerido)

**Response:** `{ success: boolean, message: string }`

---

## Customer Attachments

### GET /customers/{customer_id}/attachments
Lista todos los adjuntos de un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Response:** `CustomerAttachment[]`

---

### GET /attachments/{attachment_id}
Obtiene metadata de un adjunto o descarga el archivo.

**Path Parameters:**
- `attachment_id`: `number` (requerido)

**Response:** 
- Si existe archivo: Descarga del archivo
- Si no existe archivo: `CustomerAttachment` (metadata)

---

### POST /customers/{customer_id}/attachments
Sube un nuevo adjunto para un cliente.

**Path Parameters:**
- `customer_id`: `number` (requerido)

**Request Body:** `multipart/form-data`
- `file`: `File` (opcional, archivo a subir)
- `file_name`: `string` (opcional, nombre del archivo)
- `file_type`: `string` (opcional, tipo MIME)
- `file_path`: `string` (opcional, ruta si no se sube archivo)

**Response:** `CustomerAttachment`

**Nota:** Si se proporciona `file`, se guarda en `uploads/customers/{customer_id}/` con nombre único.

---

### DELETE /attachments/{attachment_id}
Elimina un adjunto.

**Path Parameters:**
- `attachment_id`: `number` (requerido)

**Response:** `{ success: boolean, message: string }`

---

## Schemas de Respuesta

### Customer
```typescript
{
  CustomerId?: number;
  CustomerType: CustomerType;
  CompanyName?: string;
  FirstName?: string;
  LastName?: string;
  AdditionalName?: string;
  Market?: Market;
  DtdPotential?: DtdPotential;
  PrimaryEmail?: string;
  PrimaryPhone?: string;
  PrimaryAddressId?: number;
  PrimaryAddress?: Address;
  CreatedAt: datetime;
  UpdatedAt?: datetime;
  CreatedBy: number;
  creator?: CustomerEmployee;
}
```

### Address
```typescript
{
  AddressId?: number;
  Address1: string;
  Address2?: string;
  City: string;
  State: string;
  ZipCode: string;
  CountryId: number;
  GooglePlaceId?: string;
  IsValidated: boolean;
  ValidatedAt?: datetime;
  CreatedAt: datetime;
}
```

### CustomerNote
```typescript
{
  CustomerNoteId?: number;
  CustomerId: number;
  NoteText: string;
  CreatedAt: datetime;
  UpdatedAt?: datetime;
  CreatedBy: number;
  creator?: CustomerEmployee;
}
```

### CustomerAlternateContact
```typescript
{
  CustomerAlternateContactId?: number;
  CustomerId: number;
  Name: string;
  Email?: string;
  Phone?: string;
  CreatedAt: datetime;
  UpdatedAt?: datetime;
}
```

### CustomerAttachment
```typescript
{
  CustomerAttachmentId?: number;
  CustomerId: number;
  FileName: string;
  FileType?: string;
  FilePath?: string;
  CreatedAt: datetime;
  CreatedBy: number;
  creator?: CustomerEmployee;
}
```

### CustomerMerged
```typescript
{
  Customer: Customer;
  Notes: CustomerNote[];
  Contacts: CustomerAlternateContact[];
  Attachments: CustomerAttachment[];
}
```

### CustomerEmployee
```typescript
{
  EmployeeId: number;
  DisplayName?: string;
  Email?: string;
  Title?: string;
}
```
