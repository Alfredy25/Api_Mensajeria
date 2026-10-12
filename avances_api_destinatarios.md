# Avances de la API de destinatarios

## Última actualización

12 de octubre de 2026.

## Punto actual

Se completó la creación de destinatarios (`POST /receivers`). El endpoint está
funcional y probado manualmente para los tres tipos de entidad: `PERSONA`,
`GOBIERNO` y `PRIVADA`.

El siguiente trabajo será implementar la búsqueda de destinatarios
(`GET /receivers`) con filtros, ordenamiento y paginación. Después de la
búsqueda se crearán las pruebas unitarias y de integración.

## Trabajo completado

### Diseño

Se actualizó `DISENO_API_DESTINATARIOS.md` para definir:

- Puesto opcional para destinatarios `PERSONA`.
- Cargo genérico `SIN CARGO` cuando existe organización, pero no cargo.
- Ausencia de puesto cuando una persona no tiene cargo ni organización.
- Puesto obligatorio para destinatarios `GOBIERNO` y `PRIVADA`.
- Cargos institucionales `INSTITUCIONAL GOBIERNO` e `INSTITUCIONAL PRIVADO`.
- Filtros opcionales, ordenamiento y paginación.
- Normalización para búsquedas y detección de duplicados.
- Endpoints posteriores para direcciones, contactos, volantes y cambio de
  puesto.
- Sección de cambio de collation a `utf8mb4_0900_ai_ci` para producción.

### Schemas (paso 1)

- `ReceiverCreate.position` utiliza `PositionCreateWithReceiver` donde
  `job_role` es opcional.
- `ReceiverCreate.title` utiliza `TitleCreate`.
- Los campos opcionales tienen `default=None`.
- `model_validator` valida reglas por tipo de destinatario.
- `PERSONA` requiere `full_name` (min 5 caracteres) y `title`.
- `GOBIERNO` y `PRIVADA` rechazan `full_name` y `title`, requieren `position`.
- `ReceiverDto` incluye listas vacías por defecto para colecciones.
- `AddressDto` incluye `municipality`.

### Services auxiliares (paso 2)

Todos los métodos `ensure_*` están implementados y verificados:

- `TitleService.ensure_title(title: TitleCreate) -> TitleORM`
- `JobService.ensure_job_role(job: JobCreate) -> JobRoleORM`
- `OrganizationService.ensure_organization(org_create: OrganizationCreate) -> OrganizationORM`
- `PositionService.ensure_position(job: JobRoleORM, organization: OrganizationORM) -> PositionORM`
- `VolanteService.ensure_volante(volante: VolanteCreate) -> VolanteORM`
- `AddressService.create_address_with_receiver(address_create: AddressCreate) -> AddressORM`
- `ContactService.create_contact_with_receiver(contact: ContactCreate) -> ContactORM`

Ninguno hace `commit`; usan `flush` o delegan al repositorio.

### Repository de destinatarios (paso 3)

- `create(...)` acepta `full_name`, `title` y `position` opcionales.
- `find_duplicate(...)` detecta duplicados según la identidad lógica:
  - `PERSONA`: `type_entity + full_name(upper) + position_id`.
  - `GOBIERNO` / `PRIVADA`: `type_entity + position_id`.
- `find_by_id(...)` y `find_by_name(...)` implementados.
- `update(...)` implementado.

### ReceiverService (paso 4)

- Cargos genéricos definidos como constantes `JobCreate` a nivel de módulo.
- `_resolve_persona`: título obligatorio; puesto opcional; `SIN CARGO` cuando
  hay organización sin cargo.
- `_resolve_institution`: cargo institucional por tipo cuando no se proporciona.
- `_check_duplicate`: responde `409 Conflict` con `receiver_id` en header.
- Normalización de `full_name` (upper) y `email` (lower).
- Un solo `commit` al final; `rollback` ante cualquier error.
- Dirección obligatoria; contacto y volante opcionales.

### Inyección de dependencias (paso 5)

- Funciones factory en `app/core/dependencies.py` para los 8 repositorios y
  8 services.
- `get_receiver_service` inyecta todos los services auxiliares.
- Todos comparten la misma sesión `db`.

### Router (paso 6)

- `POST /receivers` delega a `ReceiverService.create_receiver`.
- Responde `201 Created` con `ReceiverDto`.
- Sin lógica de negocio ni creación manual de repositorios.

### Migración

- Primera migración de Alembic creada con todos los modelos de destinatarios.
- Tablas: `receivers`, `addresses`, `contacts`, `titles`, `job_roles`,
  `organizations`, `positions`, `volantes`, `receiver_volante`.
- Corrección de `server_default=func.now()` en `ReceiverORM.created_at`
  (se eliminó `timezone.utc` como argumento que causaba error de compilación).

### Modelo

- `ReceiverORM.email` con límite de 80 caracteres.
- `ReceiverORM.full_name` nullable.
- `AddressORM` incluye campo `municipality`.
- `server_default=func.now()` corregido en `created_at`.

## Siguiente paso: búsqueda de destinatarios (pasos 7 y 8)

### Paso 7. Repository + Service

- Búsqueda general por texto en `full_name` y `organization.name`.
- Filtros opcionales: `type_entity`, `organization_name`, `organization_state`,
  `address_state`.
- Ordenamiento mediante lista cerrada de campos permitidos.
- Paginación con `page` y `page_size` (máximo 100, defecto 50).
- Respuesta paginada con `items`, `total`, `page` y `page_size`.
- Responder `200 OK` con lista vacía si no hay coincidencias.

### Paso 8. Router

- `GET /receivers` con búsqueda, filtros y paginación como query params.
- `GET /receivers/{receiver_id}` para consulta individual.
- Router delgado que delega al service.

## Pasos posteriores

### Paso 9. Pruebas

- Pruebas unitarias de schemas (`ReceiverCreate` validaciones por tipo).
- Pruebas unitarias de services (lógica de negocio, cargos genéricos,
  duplicados).
- Pruebas de integración de repository con base de datos.
- Pruebas de endpoints (`POST`, `GET`).
- Casos para `PERSONA`, `GOBIERNO` y `PRIVADA`.
- Casos de concurrencia y unicidad.

### Extensiones posteriores

- Endpoints para direcciones, contactos, volantes y cambio de puesto.
- `ReceiverUpdate` y `PATCH /receivers/{receiver_id}`.
- Auditoría, soft delete, usuarios, roles, permisos, JWT.

## Pendientes de base de datos

- Migrar producción a `utf8mb4_0900_ai_ci` (documentado en
  `DISENO_API_DESTINATARIOS.md`).
- Diseñar la restricción de unicidad para personas con `position_id = null`.
- Agregar el `CHECK` para abreviaturas de cargos en mayúsculas.
- Revisar restricciones únicas de direcciones, contactos y relaciones con
  volantes.
