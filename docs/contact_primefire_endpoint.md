# Contact PrimeFire Endpoint

Guia rapida del endpoint para enviar correos de contacto con plantilla HTML.

## Endpoint

- Metodo: `POST`
- Ruta: `https://primefireapi-dfe5fac8h6ajcxee.canadacentral-01.azurewebsites.net/notifications/send/contact-primefire`
- Content-Type: `application/json`

## ejemplo
curl -X 'POST' \
  'https://primefireapi-dfe5fac8h6ajcxee.canadacentral-01.azurewebsites.net/notifications/send/contact-primefire' \
  -H 'accept: application/json' \
  -H 'x-contact-token: 7dd8430e-2c2b-4239-9ddf-b299dea05bc4' \
  -H 'Content-Type: application/json' \
  -d '{
  "to_email": "jcarlos.villa.rivera@gmail.com",
  "cc_email": "javiermendozar73@gmail.com",
  "logo_url": "https://primefire.do/assets/images/logoRDF.png",
  "title": "New Contact Received - PrimeFire",
  "subtitle": "A new contact request was received. Details:",
  "name": "John Doe",
  "company": "Acme Corp",
  "email": "john@acme.com",
  "phone": "+1 (829) 961-4866",
  "industry": "Manufacturing",
  "service": "Alarm System",
  "note": "I need a maintenance visit.",
  "fields": [
    { "key": "budget", "label": "Estimated Budget", "type": "number", "value": "5000" },
    { "key": "website", "label": "Website", "type": "url", "value": "https://acme.com" },
    { "key": "alt_email", "label": "Alternative Email", "type": "email", "value": "ops@acme.com" }
  ]
}'

## Body (JSON)

### Campos principales

- `to_email` (string, requerido): correo destino principal.
- `cc_email` (string, opcional): uno o varios correos en copia.
  - Soporta multiples separados por `;` o `,`.
- `logo_url` (string URL, opcional): logo para encabezado de la plantilla.
- `title` (string, requerido): titulo del correo.
- `subtitle` (string, opcional): subtitulo.
- `name` (string, requerido): nombre del contacto.
- `company` (string, opcional): empresa.
- `email` (string email, requerido): email del contacto.
- `phone` (string, requerido): telefono del contacto.
- `industry` (string, opcional): industria.
- `service` (string, requerido): servicio solicitado.
- `note` (string, opcional): nota libre.
- `fields` (array, opcional): campos dinamicos extra.

### Campos dinamicos (`fields[]`)

Cada elemento debe tener:

- `key` (string, requerido)
- `label` (string, requerido)
- `type` (string, requerido)
- `value` (string, requerido)

Tipos permitidos en `type`:

- `text`
- `email`
- `phone`
- `url`
- `number`
- `textarea`

Validaciones por tipo:

- `email`: formato de correo valido.
- `phone`: formato de telefono valido.
- `url`: debe iniciar con `http://` o `https://`.

## Ejemplo de payload 2

```json
{
  "to_email": "jcarlos.villa.rivera@gmail.com",
  "cc_email": "javiermendozar73@gmail.com;otro1@gmail.com",
  "logo_url": "https://primefire.do/assets/images/logoRDF.png",
  "title": "New Contact Received - PrimeFire",
  "subtitle": "A new contact request was received. Details:",
  "name": "John Doe",
  "company": "Acme Corp",
  "email": "john@acme.com",
  "phone": "+1 (829) 961-4866",
  "industry": "Manufacturing",
  "service": "Alarm System",
  "note": "I need a maintenance visit.",
  "fields": [
    {
      "key": "budget",
      "label": "Estimated Budget",
      "type": "number",
      "value": "5000"
    },
    {
      "key": "website",
      "label": "Website",
      "type": "url",
      "value": "https://acme.com"
    },
    {
      "key": "alt_email",
      "label": "Alternative Email",
      "type": "email",
      "value": "ops@acme.com"
    }
  ]
}
```

## Respuestas comunes

- `200 OK`: correo enviado correctamente.
- `401 Unauthorized`: token faltante o invalido.
- `422 Unprocessable Entity`: payload invalido (por ejemplo email/telefono/url).
- `503 Service Unavailable`: fallo al enviar correo (Graph/API de correo).
