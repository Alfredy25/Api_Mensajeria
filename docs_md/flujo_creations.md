# Flujos de creación — destinatarios y entidades relacionadas

Documento de referencia con diagramas Mermaid. Combina el comportamiento **actual** del código (`ReceiverService`, `ensure_*`) y las reglas del diseño en `DISENO_API_DESTINATARIOS.md` (verificación de dirección y contacto **por destinatario**, aún no implementada en servicios).

## Modelo de datos (lectura de los diagramas)

| Entidad | ¿Catálogo reutilizable? | Relación con destinatario |
|--------|-------------------------|---------------------------|
| Título, cargo, organización, puesto, volante | Sí (buscar o crear) | Puesto en `receiver.position_id`; volante **N:N** (`receiver_volante`) |
| Dirección, contacto | No tienen sentido “sueltos” en negocio | **FK obligatorio** a `receivers`; hoy siempre se crea fila nueva al alta |
| Dirección “compartida” entre destinatarios | Mismo texto en **filas distintas** | OK entre destinatarios; **409** si el **mismo** destinatario repite domicilio equivalente (diseño) |
| Contacto | Igual | **409** si mismo `phone` + misma `ext` (normalizados) en el **mismo** destinatario; otra `ext` sí es válida (diseño) |

---

## 1. Creación compuesta — `POST /receivers`

```mermaid
flowchart TD
    A([POST /receivers<br/>ReceiverCreate]) --> B{Validar Pydantic<br/>según type_entity}
    B -->|inválido| Z1([422 Validation Error])
    B -->|válido| C[Normalizar full_name UPPER<br/>email lower trim]

    C --> D{Resolver título y puesto<br/>_resolve_title_and_position}

    D --> E{_check_duplicate<br/>identidad lógica destinatario}
    E -->|existe| Z2([409 Conflict<br/>receiver_id existente])
    E -->|no existe| F[Crear ReceiverORM<br/>flush]

    F --> G[Crear AddressORM<br/>create_address_with_receiver]
    G --> H{¿contact en payload?}
    H -->|sí| I[Crear ContactORM<br/>create_contact_with_receiver]
    H -->|no| J{¿volante en payload?}
    I --> J
    J -->|sí| K[ensure_volante<br/>reutilizar o crear]
    J -->|no| L[append relaciones]
    K --> L

    L --> M[db.commit]
    M --> N([201 ReceiverDto])

    B -.->|error SQL| R[rollback]
    E -.-> R
    F -.-> R
    G -.-> R
    I -.-> R
    K -.-> R
    R --> Z3([500 / error propagado])
```

### Identidad duplicado destinatario (repositorio)

```mermaid
flowchart TD
    A{type_entity} -->|PERSONA| P[full_name normalizado + position_id<br/>NULL o id concreto]
    A -->|GOBIERNO / PRIVADA| I[type_entity + position_id]

    P --> D{¿find_duplicate<br/>devuelve fila?}
    I --> D
    D -->|sí| E([409])
    D -->|no| OK([continuar alta])

    note1[Diseño doc: PERSONA también incluye title_id;<br/>BD: uq full_name + title_id + position_id]
    P -.-> note1
```

---

## 2. Resolución de título y puesto (alta compuesta)

```mermaid
flowchart TD
    START([payload.type_entity]) --> T{type_entity}

    T -->|PERSONA| P1[ensure_title<br/>por abbreviation]
    P1 --> P2{¿position en payload?}
    P2 -->|no| P3([title_orm, position_id = None])
    P2 -->|sí| P4{¿job_role en position?}
    P4 -->|no| P5[job = SIN CARGO]
    P4 -->|sí| P6[job = payload.job_role]
    P5 --> POS[_ensure_position_from_parts]
    P6 --> POS
    POS --> P7([title_orm, position_orm])

    T -->|GOBIERNO| G1{¿job_role en payload?}
    T -->|PRIVADA| G1
    G1 -->|sí| G2[usar job_role recibido]
    G1 -->|no + GOBIERNO| G3[INSTITUCIONAL GOBIERNO]
    G1 -->|no + PRIVADA| G4[INSTITUCIONAL PRIVADO]
    G2 --> POS2[_ensure_position_from_parts]
    G3 --> POS2
    G4 --> POS2
    POS2 --> G5([None, position_orm])
```

```mermaid
flowchart LR
    subgraph ensure_position["_ensure_position_from_parts"]
        J[ensure_job_role<br/>abbreviation] --> O[ensure_organization<br/>name + state]
        O --> POS[ensure_position<br/>job_id + organization_id]
    end
```

---

## 3. Patrón **ensure** (reutilización en alta compuesta)

En el alta compuesta **no hay commit** en estos servicios; usan `flush` donde hace falta el id.

```mermaid
flowchart TD
    subgraph TITULO["TitleService.ensure_title"]
        T1[Buscar por abbreviation] --> T2{¿existe?}
        T2 -->|sí| T3[Retornar TitleORM]
        T2 -->|no| T4[Crear + flush]
    end

    subgraph CARGO["JobService.ensure_job_role"]
        J1[Buscar por abbreviation] --> J2{¿existe?}
        J2 -->|sí| J3[Retornar JobRoleORM]
        J2 -->|no| J4[Crear sin commit]
    end

    subgraph ORG["OrganizationService.ensure_organization"]
        O1[Buscar name + state] --> O2{¿existe?}
        O2 -->|sí| O3[Retornar OrganizationORM]
        O2 -->|no| O4[Crear sin commit]
    end

    subgraph PUESTO["PositionService.ensure_position"]
        P1[Buscar job_id + organization_id] --> P2{¿existe?}
        P2 -->|sí| P3[Retornar PositionORM]
        P2 -->|no| P4[Crear sin commit]
    end

    subgraph VOL["VolanteService.ensure_volante"]
        V1[Buscar por name] --> V2{¿existe?}
        V2 -->|sí| V3[Retornar VolanteORM]
        V2 -->|no| V4[Crear + flush]
    end
```

---

## 4. Creación **explícita** por catálogo (endpoints separados)

Comportamiento **distinto** de `ensure`: si ya existe, **error** (no reutilizar silenciosamente).

```mermaid
flowchart TD
    subgraph POST_TITLE["POST /titles — implementado"]
        PT1[Buscar abbreviation] --> PT2{¿existe?}
        PT2 -->|sí| PT409([409 El título ya existe])
        PT2 -->|no| PT201([201 TitleDto + commit])
    end

    subgraph POST_JOB["POST /job_roles — implementado en service"]
        PJ1[Buscar abbreviation] --> PJ2{¿existe?}
        PJ2 -->|sí| PJ400([400 already exists])
        PJ2 -->|no| PJ201([201 JobDto + commit])
    end

    subgraph POST_ORG["POST /organizations — implementado"]
        PO1[find name + state] --> PO2{¿existe?}
        PO2 -->|sí| PO400([400 Organization already exists])
        PO2 -->|no| PO201([201 OrganizationDto + commit])
    end

    subgraph POST_POS["POST /positions — implementado"]
        PP1[¿existen job y org?] --> PP2{404 si falta alguno}
        PP2 --> PP3[find_position job+org]
        PP3 --> PP4{¿puesto existe?}
        PP4 -->|sí| PP409([409 Position already exists])
        PP4 -->|no| PP201([201 PositionDto + commit])
    end

    subgraph POST_VOL["POST /volantes — implementado"]
        PV1[get_by_name] --> PV2{¿existe?}
        PV2 -->|sí| PV409([409 Volante ya existe])
        PV2 -->|no| PV201([201 VolanteDto + commit])
    end
```

**Cuándo usar qué:**

- **Alta masiva / formulario destinatario** → `ensure_*` dentro de `POST /receivers`.
- **Catálogo curado por operador** → `POST` explícito; luego en destinatarios solo referencias (p. ej. `create_position` exige cargo y org ya creados).

---

## 5. Direcciones — flujo objetivo (diseño) vs hoy

**Hoy:** `create_address_with_receiver` siempre instancia `AddressORM` sin comparar duplicados en el mismo destinatario. `POST /addresses` crea fila sin asignar destinatario en el flujo compuesto; el modelo exige `receiver_id`.

```mermaid
flowchart TD
    A([Alta dirección]) --> B{¿Contexto?}

    B -->|POST /receivers| C[Destinatario nuevo]
    B -->|POST /receivers/id/addresses| D[Destinatario existente]

    C --> E[Normalizar campos identidad<br/>calle, num, colonia, CP, ciudad, estado, país<br/>sin address_reference]
    D --> F[404 si receiver no existe]
    F --> E

    E --> G{¿Este receiver ya tiene<br/>dirección equivalente?}
    G -->|sí| H([409 Conflict<br/>mismo destinatario])
    G -->|no| I[Crear nueva fila AddressORM<br/>receiver_id = id]

    I --> J{¿Otro destinatario<br/>misma dirección lógica?}
    J -->|sí| K[OK: otra fila, otro receiver_id]
    J -->|no| K

    K --> L([201 AddressDto])

    note[Hoy en código: salta G → siempre I]
    G -.-> note
```

---

## 6. Contactos — flujo objetivo (diseño) vs hoy

**Hoy:** siempre crea `ContactORM` nuevo; no hay chequeo `phone + ext` por destinatario.

```mermaid
flowchart TD
    A([Alta contacto]) --> B{¿Contexto?}

    B -->|POST /receivers + contact| C[En misma transacción<br/>después de crear receiver]
    B -->|POST /receivers/id/contacts| D[Receiver existente]

    D --> E[404 si no existe receiver]
    C --> F[Normalizar phone y ext<br/>ext vacía = NULL consistente]
    E --> F

    F --> G{¿Mismo receiver_id + phone + ext?}
    G -->|sí| H([409 Conflict])
    G -->|no| I[Crear ContactORM]

    I --> J{¿Mismo phone+ext<br/>en otro destinatario?}
    J -->|sí| K([201 OK — permitido])
    J -->|no| K

    note2[Hoy: no ejecuta G]
    G -.-> note2
```

---

## 7. Volantes — catálogo + asociación

```mermaid
flowchart TD
    subgraph CATALOGO["Catálogo volante"]
        V1([POST /volantes]) --> V2{¿name único?}
        V2 -->|no| V409([409])
        V2 -->|sí| V201([201 VolanteDto])
    end

    subgraph EN_ALTA["Dentro POST /receivers"]
        E1[ensure_volante] --> E2[receiver.volantes.append]
        E2 --> E3{¿Par receiver_id + volante_id<br/>ya en receiver_volante?}
        E3 -->|sí| E409([409 asociación duplicada])
        E3 -->|no| EOK([OK])
    end

    subgraph ASOC["POST /receivers/id/volantes — diseño"]
        A1[404 receiver] --> A2[ensure_volante]
        A2 --> A3[Insert en receiver_volante]
        A3 --> A4{UniqueConstraint<br/>receiver_id + volante_id}
        A4 -->|violación| A409([409])
        A4 -->|ok| A201([201])
    end
```

---

## 8. Vista de capas

```mermaid
flowchart TB
    subgraph API
        R[ReceiverRouter]
        T[TitleRouter]
        Others[Organizations / Jobs / Positions / Volantes / Addresses / Contacts]
    end

    subgraph Orquestación
        RS[ReceiverService<br/>1 transacción, commit único]
    end

    subgraph Catálogo_reutilizable
        TS[TitleService]
        JS[JobService]
        OS[OrganizationService]
        PS[PositionService]
        VS[VolanteService]
    end

    subgraph Dependientes_de_receiver
        AS[AddressService]
        CS[ContactService]
    end

    R --> RS
    RS --> TS
    RS --> JS
    RS --> OS
    RS --> PS
    RS --> VS
    RS --> AS
    RS --> CS

    T --> TS
    Others -.-> JS
    Others -.-> OS
    Others -.-> PS
    Others -.-> VS
    Others -.-> AS
    Others -.-> CS
```

---

## Backlog resumido

1. **Ya orquestado:** título, cargo, org, puesto, volante (`ensure`), destinatario, dirección y contacto en una transacción.
2. **Pendiente (diseño):** `find_duplicate_address_for_receiver`, `find_duplicate_contact_for_receiver`; endpoints `POST /receivers/{id}/addresses|contacts|volantes`.
3. **Alinear:** duplicado PERSONA con `title_id` en repositorio (diseño y `uq_receiver_name_position` en BD).
4. **Volante en alta:** se resuelve después de crear el receiver; equivalente funcional si todo va en la misma transacción.
