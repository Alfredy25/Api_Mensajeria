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
- `address`

Serán opcionales:

- `position`
  - Cargo.
  - Organización.
- `email`
- `contact`
- `volante`

El puesto de una persona se resolverá de acuerdo con los datos recibidos:

| Cargo | Organización | Regla |
|---|---|---|
| Sí | Sí | Buscar o crear el puesto normalmente. |
| No | Sí | Utilizar el cargo genérico `SIN CARGO` con la organización recibida. |
| No | No | No crear un puesto y conservar `position_id` como `null`. |
| Sí | No | Rechazar la solicitud con `422 Unprocessable Entity`. |

No se creará una organización genérica para una persona sin cargo ni
organización, porque produciría información artificial en el catálogo y en las
búsquedas.



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

El cargo genérico se registrará con abreviatura `SIN CARGO` y significado
`Sin cargo especificado`. Se reutilizará para las personas que tengan una
organización conocida, pero cuyo cargo no haya sido proporcionado. La
combinación de ese cargo con cada organización producirá un puesto diferente.

Una persona sin cargo ni organización no tendrá puesto. Los destinatarios
`GOBIERNO` y `PRIVADA` siempre deberán tener organización y puesto.

## Búsqueda de destinatarios



### Endpoint previsto

```http
GET /receivers?search=juanito
```

`search` será una búsqueda general y consultará coincidencias parciales en:

- `ReceiverORM.full_name`
- `OrganizationORM.name`, mediante la relación con `PositionORM`

También se admitirán filtros opcionales:

```http
GET /receivers?type_entity=PERSONA&name=JUAN&address_state=JALISCO&sort_by=full_name&sort_order=asc&page=1&page_size=50
```

- `type_entity`: tipo de destinatario.
- `name`: coincidencia parcial del nombre normalizado.
- `organization_name`: coincidencia parcial del nombre de la organización.
- `organization_state`: estado al que pertenece la organización.
- `address_state`: estado de alguna dirección asociada al destinatario.
- `sort_by`: campo de ordenamiento permitido.
- `sort_order`: `asc` o `desc`.
- `page`: número de página.
- `page_size`: cantidad de resultados por página; será `50` por defecto y
  tendrá un máximo de `100`.

Solamente se aplicarán los filtros enviados y todos se combinarán mediante
`AND`. Los filtros de dirección se implementarán mediante `EXISTS`, o una
estrategia equivalente, para no duplicar destinatarios que tengan varias
direcciones coincidentes.

`sort_by` utilizará una lista cerrada de campos para evitar construir consultas
con nombres de columna arbitrarios. Inicialmente se permitirán:

- `id`
- `full_name`
- `type_entity`
- `created_at`

El orden predeterminado será `created_at desc`. Todo ordenamiento agregará `id`
como segundo criterio para obtener resultados estables entre páginas.



### Respuestas

- Si existen coincidencias: `200 OK` con una respuesta paginada.
- Si no existen coincidencias: `200 OK` con `items` vacío.
- `404 Not Found` se reservará para operaciones sobre un recurso individual
  inexistente, como consultar o actualizar un destinatario mediante su ID.

Ejemplo conceptual:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 50
}
```



## Alta compuesta



### Endpoint previsto

```http
POST /receivers
```

El alta puede recibir:

- Datos del destinatario.
- Título, cuando corresponda.
- Puesto con cargo y organización, cuando corresponda.
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
4. Resolver si el destinatario requiere puesto según las reglas de su tipo.
5. Cuando corresponda, buscar o crear el cargo.
6. Cuando corresponda, buscar o crear la organización.
7. Cuando corresponda, buscar o crear el puesto.
8. Buscar un destinatario existente mediante su identidad lógica.
9. Si existe, responder con `409 Conflict` y su identificador.
10. Si se recibió un volante, buscarlo o crearlo.
11. Crear el destinatario.
12. Crear y asociar la dirección.
13. Crear y asociar el contacto, si fue proporcionado.
14. Asociar el volante, si fue proporcionado.
15. Confirmar toda la operación mediante un único `commit`.
16. Ejecutar `rollback` ante cualquier error.

Los services auxiliares utilizados por este flujo no harán `commit`. Podrán
utilizar `flush` para obtener identificadores sin cerrar la transacción.

## Normalización

Se distinguirán los valores de presentación de los valores utilizados para
búsquedas y detección de duplicados:

- El valor de presentación conservará los acentos y una capitalización legible.
- El valor normalizado podrá almacenarse en una columna auxiliar o construirse
  de forma consistente antes de consultar.

La normalización para búsquedas y comparaciones seguirá este orden:

1. Aplicar normalización Unicode.
2. Eliminar espacios al inicio y al final.
3. Reducir cualquier secuencia de espacios internos a un único espacio.
4. Convertir a mayúsculas.
5. Eliminar acentos.

No se eliminarán acentos ni se convertirán todos los textos visibles a
mayúsculas, porque eso reduciría la calidad de datos como nombres y
organizaciones. Tampoco se aplicará esta transformación indiscriminadamente a
correos electrónicos, teléfonos, códigos postales o referencias.

Reglas específicas:

- Los correos se guardarán sin espacios exteriores y en minúsculas.
- Los teléfonos y extensiones tendrán su propia normalización.
- La abreviatura de un cargo se guardará en mayúsculas.
- El significado de un cargo conservará mayúsculas y minúsculas para facilitar
  su lectura.

La conversión de la abreviatura se realizará en el service. La base de datos
deberá agregar una restricción `CHECK` que valide que la abreviatura ya se
encuentra en mayúsculas. Un `CHECK` no transforma el dato; solamente rechaza un
valor que incumple la condición.

Si existen otros sistemas que escriben directamente en la tabla, podrá
evaluarse un trigger `BEFORE INSERT` y `BEFORE UPDATE` para realizar la
conversión. Mientras la API sea el único punto de escritura, se preferirá la
normalización en el service y el `CHECK` como protección.

La implementación deberá verificar la collation de MySQL. Si es insensible a
mayúsculas y acentos puede ayudar en las búsquedas, pero no sustituye las claves
normalizadas ni las reglas de persistencia.

## Reglas de unicidad



### Persona

Un destinatario `PERSONA` con puesto se considerará duplicado cuando coincidan:

```text
type_entity + full_name normalizado + title_id + position_id
```

Cuando la persona no tenga puesto, la identidad será:

```text
type_entity + full_name normalizado + title_id + ausencia de position_id
```

MySQL permite varias filas con `NULL` dentro de una restricción `UNIQUE`.
Por ello, la restricción de base de datos no deberá depender directamente de
`position_id` nullable. Durante la implementación se utilizará una columna
generada, una clave de identidad equivalente o una estrategia que represente la
ausencia del puesto mediante un valor estable para garantizar la unicidad ante
solicitudes concurrentes.



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

### Alta de una dirección adicional

```http
POST /receivers/{receiver_id}/addresses
```

- Recibirá un `AddressCreate`.
- Responderá `201 Created` con `AddressDto`.
- Responderá `404 Not Found` si el destinatario no existe.
- Responderá `409 Conflict` si el destinatario ya tiene una dirección
  equivalente.
- Una dirección equivalente perteneciente a otro destinatario no producirá
  conflicto.

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

### Alta de un contacto adicional

```http
POST /receivers/{receiver_id}/contacts
```

- El teléfono será obligatorio y la extensión será opcional.
- Responderá `201 Created` con `ContactDto`.
- Responderá `404 Not Found` si el destinatario no existe.
- Responderá `409 Conflict` si ya existe la misma combinación normalizada de
  teléfono y extensión para ese destinatario.



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

### Asociación de un volante adicional

```http
POST /receivers/{receiver_id}/volantes
```

- Buscará o creará el volante mediante `ensure_volante`.
- Creará la asociación dentro de la misma transacción.
- Responderá `201 Created` con `VolanteDto` cuando se cree la asociación.
- Responderá `404 Not Found` si el destinatario no existe.
- Responderá `409 Conflict` si la asociación ya existe.

## Cambio de puesto

El cambio de puesto reemplazará la asignación actual:

```http
PUT /receivers/{receiver_id}/position
```

El cuerpo contendrá la organización y un cargo opcional. Cuando una `PERSONA`
tenga organización sin cargo se aplicará `SIN CARGO`. Para `GOBIERNO` y
`PRIVADA`, la ausencia del cargo aplicará el cargo institucional
correspondiente. La operación responderá `200 OK` con el `PositionDto`
asignado.

No se modificará un `PositionORM` existente, ya que puede estar compartido por
varios destinatarios. Se buscará o creará la nueva combinación de cargo y
organización y después se reemplazará `receiver.position_id`.

Para retirar el puesto de una persona que ya no tenga cargo ni organización:

```http
DELETE /receivers/{receiver_id}/position
```

Esta operación solamente se permitirá para `PERSONA`. Los destinatarios
`GOBIERNO` y `PRIVADA` siempre deberán conservar un puesto. Cuando se complete
correctamente, responderá `204 No Content`.

Después de cambiar o retirar el puesto se validará nuevamente la identidad
lógica del destinatario. Si el resultado coincide con otro destinatario, se
responderá `409 Conflict` incluyendo el `receiver_id` existente.

Este diseño solamente conserva el puesto actual. Si posteriormente se requiere
historial de puestos, deberá incorporarse una relación histórica con fechas de
inicio y fin en lugar de sobrescribir únicamente `position_id`.

## Responsabilidades por capa



### Schemas

- Definir los contratos de entrada y salida.
- Validar campos requeridos según `type_entity`.
- Rechazar `full_name` y `title` para `GOBIERNO` y `PRIVADA`.
- Exigir `full_name` y `title` para `PERSONA`.
- Permitir que `position` sea opcional únicamente para `PERSONA`.
- Permitir una organización con cargo opcional en los contratos de puesto.
- Rechazar un cargo sin organización.
- Exigir siempre una dirección.
- Permitir contacto y volante opcionales.



### Repositories

- Ejecutar exclusivamente consultas y operaciones de persistencia.
- Buscar destinatarios mediante filtros opcionales.
- Aplicar únicamente campos de ordenamiento permitidos.
- Paginar los resultados y calcular su total.
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
- Resolver los cargos genéricos e institucionales según el tipo de
  destinatario.
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
GET    /receivers
GET    /receivers/{receiver_id}
POST   /receivers
```

El listado `GET /receivers` aceptará `search`, filtros, ordenamiento y
paginación como parámetros opcionales.



### Extensiones posteriores

```text
PATCH  /receivers/{receiver_id}
POST   /receivers/{receiver_id}/addresses
POST   /receivers/{receiver_id}/contacts
POST   /receivers/{receiver_id}/volantes
PUT    /receivers/{receiver_id}/position
DELETE /receivers/{receiver_id}/position
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

