# Avances de la API de destinatarios

## Última actualización

6 de octubre de 2026.

## Punto actual

Se está trabajando en el paso 1 del diseño:

> Alinear y validar los schemas de destinatarios.

El siguiente trabajo será crear las pruebas unitarias de `ReceiverCreate`.
Todavía no se debe avanzar al router, repository o service hasta verificar el
contrato de entrada y corregir los pendientes indicados en este documento.

## Trabajo realizado

### Diseño

Se actualizó `DISENO_API_DESTINATARIOS.md` para definir:

- Puesto opcional para destinatarios `PERSONA`.
- Cargo genérico `SIN CARGO` cuando existe organización, pero no cargo.
- Ausencia de puesto cuando una persona no tiene cargo ni organización.
- Puesto obligatorio para destinatarios `GOBIERNO` y `PRIVADA`.
- Filtros opcionales, ordenamiento y paginación.
- Normalización para búsquedas y detección de duplicados.
- Endpoints posteriores para direcciones, contactos, volantes y cambio de
  puesto.

### Schemas

Se realizaron los siguientes cambios iniciales:

- `ReceiverCreate.title` utiliza `TitleCreate` en lugar de `TitleDto`.
- Los campos opcionales de `ReceiverCreate` tienen `default=None`.
- `ReceiverCreate` tiene un `model_validator` con reglas por tipo de
  destinatario.
- Una `PERSONA` requiere `full_name` no vacío y `title`.
- `GOBIERNO` y `PRIVADA` rechazan `full_name` y `title`.
- `GOBIERNO` y `PRIVADA` requieren `position`.
- `PositionCreate.job_role` es opcional.
- `PositionCreate.organization` continúa siendo obligatorio.
- Las colecciones de `ReceiverDto` utilizan listas vacías como valor
  predeterminado en lugar de `null`.
- Se agregaron restricciones iniciales de longitud a schemas auxiliares.

### Modelo

- El límite de `ReceiverORM.email` cambió de 70 a 80 caracteres para coincidir
  con `ReceiverCreate.email`.

Este cambio de longitud todavía requiere una migración de Alembic antes de
considerarse completo.

## Pendientes antes de las pruebas

Revisar estos puntos en `app/api/v1/receiver/schemas.py`:

1. `ReceiverCreate.title` no debe declarar `min_length` ni `max_length`, porque
   es un objeto `TitleCreate`, no una cadena. Esas restricciones pertenecen a
   los campos internos de `TitleCreate`.
2. Revisar `full_name` con `min_length=5`. Este límite rechaza nombres válidos
   como `Ana`; la recomendación actual es `min_length=1` y conservar la
   comprobación con `strip()` para rechazar cadenas de espacios.
3. Puede eliminarse el `else` posterior al retorno del caso `PERSONA` para
   reducir indentación, aunque no es un error funcional.
4. Se puede utilizar `Self` como tipo de retorno del validator en lugar de la
   referencia de cadena `"ReceiverCreate"`.
5. Eliminar imports que todavía no se utilizan, por ejemplo `AddressUpdate`.

También debe verificarse que las longitudes declaradas en `AddressCreate`,
`JobCreate`, `OrganizationCreate`, `TitleCreate` y `ContactCreate` coincidan
con las columnas ORM o sean restricciones de negocio intencionales.

## Siguiente paso: pruebas unitarias de `ReceiverCreate`

Crear un archivo de pruebas para los schemas de destinatarios, por ejemplo:

```text
tests/unit/api/v1/receiver/test_schemas.py
```

Casos mínimos:

1. `PERSONA` con nombre, título y dirección, sin puesto: válido.
2. `PERSONA` con organización y sin cargo: válido.
3. `PERSONA` con organización y cargo: válido.
4. `PERSONA` con `full_name` vacío: inválido.
5. `PERSONA` con `full_name` compuesto solamente por espacios: inválido.
6. `PERSONA` sin título: inválido.
7. `GOBIERNO` con organización y sin cargo: válido.
8. `PRIVADA` con organización y cargo: válido.
9. `GOBIERNO` o `PRIVADA` sin puesto: inválido.
10. `GOBIERNO` o `PRIVADA` con nombre: inválido.
11. `GOBIERNO` o `PRIVADA` con título: inválido.
12. Campos opcionales omitidos: válido.

Las pruebas deben instanciar directamente `ReceiverCreate` y comprobar
`ValidationError` en los casos inválidos. Estas son pruebas unitarias de
Pydantic y no requieren base de datos.

## Pendientes del paso 1

Después de aprobar las pruebas de `ReceiverCreate`:

1. Revisar `ReceiverDto`.
2. Definir el mapeo entre `ReceiverORM.titulo` y `ReceiverDto.title`.
3. Corregir la diferencia entre `AddressORM.id` y `AddressDto.address_id`.
4. Definir el mapeo de `JobRoleORM.abreviatura/significado` hacia
   `JobDto.abbreviation/meaning`.
5. Decidir si el service construirá los DTO explícitamente. Esta es la opción
   recomendada por el diseño para evitar acoplar los schemas a los nombres ORM.
6. Revisar `ReceiverUpdate`; en Pydantic v2 sus campos `Optional` siguen siendo
   obligatorios mientras no tengan `default=None`.
7. Definir si `type_entity` podrá modificarse.
8. Mantener el cambio de puesto fuera de `ReceiverUpdate`, mediante los
   endpoints específicos definidos en el diseño.
9. Crear el schema de respuesta paginada para el listado.
10. Crear los schemas de filtros y ordenamiento si se decide representarlos
    mediante modelos Pydantic.

## Pasos posteriores de implementación

### Paso 2. Revisar schemas auxiliares

- Títulos.
- Cargos.
- Organizaciones.
- Puestos.
- Direcciones.
- Contactos.
- Volantes.
- Contratos para agregar relaciones después del alta.

### Paso 3. Repository de destinatarios

- Consulta por identificador.
- Búsqueda general.
- Filtros opcionales.
- Ordenamiento mediante lista de campos permitidos.
- Paginación y total.
- Búsqueda de duplicados con y sin puesto.
- Consultas sin reglas HTTP y sin `commit`.

### Paso 4. Services auxiliares

- `TitleService.ensure_title`.
- `PositionService.ensure_job_role`.
- `PositionService.ensure_organization`.
- `PositionService.ensure_position`.
- Cargo genérico e institucional.
- `VolanteService.ensure_volante`.
- Operaciones de direcciones y contactos.

### Paso 5. `ReceiverService`

- Normalización.
- Validaciones de negocio.
- Detección de duplicados.
- Orquestación del alta compuesta.
- Una sola transacción.
- `flush` en services auxiliares.
- `commit` y `rollback` en el coordinador.
- Conversión explícita a DTO.

### Paso 6. Inyección de dependencias

- Construir repositories y services mediante dependencias de FastAPI.
- Evitar su creación manual dentro del router.

### Paso 7. Router

- Delegar la lógica al service.
- Implementar códigos HTTP y schemas de respuesta.
- Eliminar la coordinación directa de repositories.

### Paso 8. Pruebas completas

- Pruebas unitarias de services.
- Pruebas de repository con base de datos.
- Pruebas de endpoints.
- Casos de concurrencia y unicidad.
- Casos `PERSONA`, `GOBIERNO` y `PRIVADA`.

## Pendientes de base de datos

- Crear una migración para ampliar `receivers.email` a 80 caracteres.
- Diseñar la restricción de unicidad para personas con `position_id = null`.
- Agregar columnas o claves normalizadas cuando se implemente la estrategia de
  búsqueda.
- Agregar el `CHECK` para abreviaturas de cargos en mayúsculas.
- Revisar restricciones únicas de direcciones, contactos y relaciones con
  volantes.

## Mensaje de commit sugerido

No se ha creado el commit. Un ejemplo para los cambios actuales es:

```text
feat(receivers): valida contratos iniciales de destinatarios

- valida campos según el tipo de destinatario
- permite personas sin puesto y cargos opcionales
- agrega restricciones a schemas relacionados
- alinea la longitud del email del destinatario
- documenta las reglas y próximos pasos de implementación
```

