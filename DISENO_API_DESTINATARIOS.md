# Diseño de la API de destinatarios

## Objetivo

Definir las reglas de negocio y el diseño inicial de la API de destinatarios
antes de implementar sus capas.

El destinatario es el agregado principal y puede relacionarse con:

- Título.
- Cargo.
- Organización.
- Puesto.
- Direcciones.
- Contactos.
- Volantes.

Los módulos relacionados tendrán sus propios schemas, repositories, services y
endpoints. `ReceiverService` será responsable de coordinar estos módulos durante
el alta compuesta de un destinatario.

## Tipos de destinatario

Se utilizará `EntidadesEnum`:

- `PERSONA`
- `GOBIERNO`
- `PRIVADA`

### Persona

Para un destinatario de tipo `PERSONA` serán obligatorios:

- `type_entity`
- `full_name`
- `title`
- `position`
  - Cargo.
  - Organización.
- `address`

Serán opcionales:

- `email`
- `contact`
- `volante`

### Gobierno y privada

Para destinatarios de tipo `GOBIERNO` o `PRIVADA`:

- `full_name` será `null`.
- `title` será `null`.
- `position` será obligatorio.
- `address` será obligatorio.
- `contact` será opcional.
- `volante` será opcional.

Cuando el registro no incluya un cargo, se utilizará uno institucional:

- `GOBIERNO`: `INSTITUCIONAL GOBIERNO`
- `PRIVADA`: `INSTITUCIONAL PRIVADO`

Si el registro sí incluye un cargo, se conservará. El cargo institucional
solamente funcionará como valor predeterminado cuando no exista uno.

## Puesto

Un puesto representa la combinación única de:

- Cargo.
- Organización.

Antes de crear un puesto se buscarán ambos catálogos:

1. Buscar o crear el cargo.
2. Buscar o crear la organización.
3. Buscar o crear el puesto mediante ambos identificadores.

Los cargos institucionales permiten representar organizaciones sin una persona
específica y sin cambiar inicialmente el modelo de puestos.

## Búsqueda de destinatarios

### Endpoint previsto

```http
GET /receivers?search=juanito
```

Una sola búsqueda consultará coincidencias parciales en:

- `ReceiverORM.full_name`
- `OrganizationORM.name`, mediante la relación con `PositionORM`

### Respuestas

- Si existen coincidencias: `200 OK` con una lista de `ReceiverDto`.
- Si no existen coincidencias: `200 OK` con una lista vacía.
- `404 Not Found` se reservará para operaciones sobre un recurso individual
  inexistente, como consultar o actualizar un destinatario mediante su ID.

## Alta compuesta

### Endpoint previsto

```http
POST /receivers
```

El alta puede recibir:

- Datos del destinatario.
- Título, cuando corresponda.
- Puesto con cargo y organización.
- Una dirección obligatoria.
- Un contacto opcional.
- Un volante opcional.

Después del alta podrán existir endpoints independientes para agregar nuevas
direcciones, contactos, puestos o volantes.

## Flujo de creación

`ReceiverService` coordinará el alta completa dentro de una sola transacción:

1. Validar el payload según `type_entity`.
2. Normalizar los textos utilizados para búsquedas y comparaciones.
3. Para `PERSONA`, buscar o crear el título.
4. Buscar o crear el cargo.
5. Buscar o crear la organización.
6. Buscar o crear el puesto.
7. Buscar un destinatario existente mediante su identidad lógica.
8. Si existe, responder con `409 Conflict` y su identificador.
9. Si se recibió un volante, buscarlo o crearlo.
10. Crear el destinatario.
11. Crear y asociar la dirección.
12. Crear y asociar el contacto, si fue proporcionado.
13. Asociar el volante, si fue proporcionado.
14. Confirmar toda la operación mediante un único `commit`.
15. Ejecutar `rollback` ante cualquier error.

Los services auxiliares utilizados por este flujo no harán `commit`. Podrán
utilizar `flush` para obtener identificadores sin cerrar la transacción.

## Normalización

Los valores utilizados para buscar y detectar duplicados se normalizarán:

- Eliminar espacios al inicio y al final.
- Convertir a mayúsculas.
- Eliminar acentos.

También deberá definirse cómo tratar espacios internos repetidos. La regla
recomendada es reducir cualquier secuencia de espacios a un único espacio.

La implementación deberá verificar la collation de MySQL. Si es insensible a
mayúsculas y acentos puede ayudar en las búsquedas, pero la normalización de
entrada seguirá siendo necesaria para mantener datos consistentes.

## Reglas de unicidad

### Persona

Un destinatario `PERSONA` se considerará duplicado cuando coincidan:

```text
type_entity + full_name normalizado + title_id + position_id
```

### Gobierno o privada

Un destinatario `GOBIERNO` o `PRIVADA` sin persona se considerará duplicado
cuando coincidan:

```text
type_entity + position_id
```

Como el puesto contiene cargo y organización, esta combinación diferencia una
organización gubernamental de una privada y también permite conservar cargos
reales cuando estén disponibles.

Los domicilios no forman parte de la identidad del destinatario. Una
organización puede tener varias sedes, que se representarán como direcciones
adicionales del mismo destinatario.

## Conflicto por destinatario existente

Si se intenta crear un destinatario que ya existe, la API responderá:

```http
409 Conflict
```

La respuesta deberá incluir el identificador del destinatario existente en un
campo estructurado. Ejemplo conceptual:

```json
{
  "detail": "El destinatario ya existe",
  "receiver_id": 123
}
```

La validación del service permitirá devolver un error comprensible. También se
mantendrán restricciones de unicidad adecuadas en la base de datos para evitar
duplicados cuando existan solicitudes concurrentes.

## Direcciones

- Todo destinatario debe crearse con una dirección.
- Un destinatario puede tener varias direcciones.
- Dos destinatarios diferentes pueden compartir la misma dirección.
- El mismo destinatario no puede tener dos direcciones equivalentes.

La deduplicación de direcciones se realizará dentro del destinatario, no de
manera global.

La identidad lógica de una dirección deberá construirse con sus campos
normalizados, incluyendo al menos:

- Calle.
- Número.
- Colonia.
- Código postal.
- Ciudad.
- Estado.
- País.

Las referencias del domicilio no deberían formar parte de la identidad, porque
pueden cambiar sin representar una dirección diferente.

## Contactos

- El contacto es opcional durante el alta.
- Un destinatario puede tener varios contactos.
- Dos destinatarios pueden compartir el mismo teléfono y extensión.
- El mismo destinatario no puede repetir la combinación de teléfono y
  extensión.

La identidad lógica será:

```text
receiver_id + phone normalizado + ext normalizada
```

## Volantes

Un volante es un folio gubernamental que agrupa uno o varios envíos.

Reglas:

- `name` será único.
- Un volante puede relacionarse con varios destinatarios.
- Un destinatario puede relacionarse con varios volantes.
- La relación es muchos a muchos.
- El volante es opcional durante el alta del destinatario.
- Podrá asociarse posteriormente mediante un endpoint específico.

Durante el alta compuesta se utilizará una operación `ensure_volante`: si el
volante existe se reutiliza; si no existe, se crea.

## Responsabilidades por capa

### Schemas

- Definir los contratos de entrada y salida.
- Validar campos requeridos según `type_entity`.
- Rechazar `full_name` y `title` para `GOBIERNO` y `PRIVADA`.
- Exigir `full_name`, `title` y `position` para `PERSONA`.
- Exigir siempre una dirección.
- Permitir contacto y volante opcionales.

### Repositories

- Ejecutar exclusivamente consultas y operaciones de persistencia.
- Buscar destinatarios por nombre u organización.
- Buscar duplicados según la identidad lógica.
- Crear y actualizar entidades ORM.
- No contener reglas HTTP ni hacer `commit`.
- No coordinar directamente otros repositories.

### Services auxiliares

Cada módulo resolverá su propia lógica:

- `TitleService.ensure_title`
- `PositionService.ensure_job_role`
- `PositionService.ensure_organization`
- `PositionService.ensure_position`
- `VolanteService.ensure_volante`
- Operaciones correspondientes para direcciones y contactos.

Las operaciones `ensure_*` buscarán primero el registro y solamente lo crearán
si no existe. No responderán con `409` cuando sean utilizadas dentro del alta
compuesta.

### ReceiverService

- Coordinar services y repositories.
- Aplicar validaciones de negocio.
- Detectar destinatarios duplicados.
- Administrar la transacción completa.
- Convertir el resultado a DTO.
- Traducir los conflictos de negocio a respuestas HTTP apropiadas.

### Router

- Declarar rutas, parámetros, schemas y códigos HTTP.
- Obtener `ReceiverService` mediante inyección de dependencias.
- Delegar la lógica de negocio al service.
- No construir modelos ORM ni coordinar repositories.

## Endpoints previstos

### Primera etapa

```text
GET    /receivers?search={value}
GET    /receivers/{receiver_id}
POST   /receivers
```

### Extensiones posteriores

```text
PATCH  /receivers/{receiver_id}
POST   /receivers/{receiver_id}/addresses
POST   /receivers/{receiver_id}/contacts
POST   /receivers/{receiver_id}/volantes
```

Los módulos `addresses`, `contacts`, `positions`, `titles` y `volantes` también
podrán exponer sus propios endpoints.

## Orden de implementación

1. Alinear y validar los schemas de destinatarios.
2. Revisar los schemas auxiliares utilizados en el alta.
3. Implementar las consultas del repository de destinatarios.
4. Completar los services auxiliares y sus operaciones `ensure_*`.
5. Implementar la orquestación en `ReceiverService`.
6. Configurar la inyección de dependencias.
7. Simplificar el router para que delegue toda la lógica.
8. Agregar pruebas para `PERSONA`, `GOBIERNO` y `PRIVADA`.

## Fuera del alcance inicial

Se implementarán en etapas posteriores:

- Auditoría completa.
- Soft delete.
- Usuarios.
- Roles y permisos.
- JWT.
- Integración con registros procesados por inteligencia artificial.
- API de envíos.

