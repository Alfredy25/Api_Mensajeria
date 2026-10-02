# [AGENTS.md](http://AGENTS.md)

## Objetivo del Proyecto

Sistema interno de mensajería y logística.

La plataforma permite:

- Crear guías de envío.
- Generar cotizaciones.
- Consultar coberturas.
- Administrar destinatarios.
- Consultar rastreo de envíos.
- Gestionar usuarios y permisos.
- Integrarse con múltiples paqueterías.

---

## Contexto de Negocio

Actualmente el sistema se utiliza para gestionar envíos asociados principalmente a la Auditoría Superior de la Federación (ASF), así como documentación que viene en sobres con la etiqueta dirigida a dependencias gubernamentales y organizaciones publicas y privadas ubicadas en toda la República Mexicana.
 
El sistema busca centralizar la operación relacionada con:
 

- Administración de destinatarios.
- Administración de clientes.
- Consulta de coberturas.
- Generación de cotizaciones.
- Creación de guías.
- Consulta de rastreo.
- Seguimiento de envíos.
- Integración con múltiples paqueterías.

 
Los envíos metropolitanos son atendidos por mensajeros propios.
 
Los envíos nacionales son procesados mediante proveedores externos:
 

- FedEx
- UPS
- DHL
- Paquetexpress.

 
La prioridad actual del proyecto es soportar correctamente la operación de clientes gubernamentales.
 
Los destinatarios pueden pertenecer a:
 

- Dependencias gubernamentales.
- Servidores públicos.
- Empresas privadas.

---



## Aprendizaje

La IA debe priorizar el aprendizaje del desarrollador.

Siempre que proponga una decisión técnica relevante debe explicar:

- Qué problema resuelve.
- Por qué se eligió esa solución.
- Qué alternativas existen.
- Cuándo convendría elegir otra alternativa.

La IA debe actuar como mentor técnico y no solamente como generador de código.

---



## Stack Tecnológico

- Python 3.14
- FastAPI
- SQLAlchemy 2.0 Typed ORM
- Alembic
- MySQL (InnoDB)
- Pydantic
- JWT Authentication

---



## Arquitectura

Mantener la arquitectura existente basada en módulos funcionales y separación por capas.

Cada módulo puede contener:

- router.py
- schemas.py
- service.py
- repository.py

Separando claramente:

- API Layer
- Service Layer
- Data Access Layer

---



## Estructura

```text
api_mensajeria/
│
├── alembic.ini                         -> Archivo principal de configuración de Alembic.
├── pyproject.toml                      -> Dependencias y configuración general del proyecto.
├── .env                                -> Variables de entorno locales. No debe subirse al repositorio.
├── .env.example                        -> Ejemplo de las variables necesarias para ejecutar el proyecto.
├── .gitignore                          -> Archivos y carpetas que Git debe ignorar.
├── README.md                           -> Documentación principal del proyecto.
│
├── app/                                -> Paquete principal del backend.
│   │
│   ├── __init__.py                     -> Indica que app es un paquete de Python.
│   ├── main.py                         -> Punto de entrada donde se crea la aplicación FastAPI.
│   │
│   ├── core/                           -> Elementos transversales utilizados por toda la aplicación.
│   │   ├── __init__.py
│   │   ├── config.py                   -> Variables de entorno y configuración con Pydantic Settings.
│   │   ├── database.py                 -> Engine, sesiones y configuración de SQLAlchemy.
│   │   ├── dependencies.py             -> Dependencias globales de FastAPI.
│   │   ├── exceptions.py               -> Excepciones personalizadas y manejadores globales.
│   │   ├── logging.py                  -> Configuración general de logs.
│   │   ├── security.py                 -> JWT, contraseñas, autenticación y autorización.
│   │   └── lifespan.py                 -> Procesos ejecutados al iniciar y cerrar la aplicación.
│   │
│   ├── models/                         -> Modelos ORM que representan las tablas de la base de datos.
│   │   ├── __init__.py                 -> Exporta los modelos para facilitar su importación.
│   │   ├── user.py                     -> Usuarios del sistema.
│   │   ├── role.py                     -> Roles y permisos.
│   │   ├── customer.py                 -> Clientes que realizan envíos.
│   │   ├── address.py                  -> Direcciones destinatarios.
|   |   ├── contact.py                  -> Contactos de los destinatarios
|   |   ├── coverage_px.py              -> Coberturas de px (nos las pasan en lo que consumimos su api para poder validar la cobertura)
|   |   ├── organization.py             -> Dependencia de gobierno o privada
|   |   ├── job_role.py                 -> Cargo del destinatario
|   |   ├── position.py                 -> Puesto que ocupa el destinatario combinando el cargo que tiene y en que dependencia
|   |   ├── receiver.py                 -> Destinatarios
|   |   ├── register.py                 -> Registros son los datos que se obtienen actualmente con la ia desde el cliente de aplicación de escritorio
|   |   ├── titulo.py                   -> Titulo que tiene el destinatario
|   |   ├── volante.py                  -> No de volante es propio de nuestro cliente de gobierno en un volante puede haber uno o muchos destinatarios 
|   |   ├── shipment_px.py              -> son envios de paquete express actualmente se registran para poder descargarse posteriormente en un excel que genera el cliente y poder subirlos a la plataforma de PaqueteXpress
│   │   ├── quote.py                    -> Cotizaciones obtenidas de las paqueterías.
│   │   ├── shipment.py                 -> Envíos y guías generadas.
│   │   ├── tracking_event.py           -> Historial de estados de un envío.
│   │   ├── payment.py                  -> Pagos realizados por los clientes.
│   │   ├── whatsapp_message.py         -> Mensajes entrantes y salientes de WhatsApp.
│   │   └── webhook_event.py            -> Registro de eventos recibidos mediante webhooks.
│   │
│   ├── api/                            -> Endpoints HTTP expuestos por el backend.
│   │   ├── __init__.py
│   │   │
│   │   └── v1/                         -> Primera versión pública de la API.
│   │       ├── __init__.py
│   │       ├── router.py               -> Une todos los routers pertenecientes a la versión 1.
│   │       │
│   │       ├── auth/                   -> Inicio de sesión, tokens y autenticación.
│   │       │   ├── __init__.py
│   │       │   ├── router.py           -> Endpoints de autenticación.
│   │       │   ├── schemas.py          -> Datos de entrada y salida de autenticación.
│   │       │   ├── repository.py       -> Consultas relacionadas con usuarios y autenticación.
│   │       │   └── service.py          -> Reglas para iniciar sesión y generar tokens.
│   │       │
│   │       ├── users/                  -> Administración de usuarios, operadores y administradores.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── customers/              -> Administración de clientes.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── addresses/              -> Direcciones de remitentes y destinatarios.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── quotes/                 -> Cotizaciones de servicios de mensajería.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── shipments/              -> Creación y administración de envíos y guías.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── tracking/               -> Consulta del rastreo e historial de los envíos.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── payments/               -> Creación, consulta y validación de pagos.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   ├── repository.py
│   │       │   └── service.py
│   │       │
│   │       ├── documents/              -> Recepción y procesamiento de imágenes o documentos.
│   │       │   ├── __init__.py
│   │       │   ├── router.py
│   │       │   ├── schemas.py
│   │       │   └── service.py
│   │       │
│   │       ├── webhooks/               -> Endpoints que reciben eventos de sistemas externos.
│   │       │   ├── __init__.py
│   │       │   ├── whatsapp.py         -> Eventos enviados por Meta WhatsApp.
│   │       │   ├── ups.py              -> Eventos de rastreo enviados por UPS.
│   │       │   ├── fedex.py            -> Eventos de rastreo enviados por FedEx.
│   │       │   └── payments.py          -> Confirmaciones enviadas por el proveedor de pagos.
│   │       │
│   │       ├── sockets/                -> Conexiones WebSocket para comunicación en tiempo real.
│   │       │   ├── __init__.py
│   │       │   ├── manager.py          -> Administra conexiones WebSocket activas.
│   │       │   ├── tracking.py         -> Envía actualizaciones de rastreo.
│   │       │   └── notifications.py    -> Envía notificaciones generales.
│   │       │
│   │       └── health/                 -> Verificación del estado de la aplicación.
│   │           ├── __init__.py
│   │           └── router.py           -> Endpoint health check para VPS, Docker o proxy.
│   │
│   ├── integrations/                   -> Clientes utilizados para consumir APIs externas.
│   │   ├── __init__.py
│   │   │
│   │   ├── carriers/                   -> Integraciones con empresas de mensajería.
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 -> Interfaz común que deben implementar las paqueterías.
│   │   │   │
│   │   │   ├── ups/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py           -> Realiza solicitudes a la API de UPS.
│   │   │   │   ├── schemas.py          -> Modelos de datos propios de las respuestas de UPS.
│   │   │   │   ├── mapper.py           -> Convierte respuestas de UPS al formato interno.
│   │   │   │   └── exceptions.py       -> Errores específicos de la integración con UPS.
│   │   │   │
│   │   │   └── fedex/
│   │   │       ├── __init__.py
│   │   │       ├── client.py           -> Realiza solicitudes a la API de FedEx.
│   │   │       ├── schemas.py          -> Modelos de datos propios de FedEx.
│   │   │       ├── mapper.py           -> Convierte respuestas de FedEx al formato interno.
│   │   │       └── exceptions.py       -> Errores específicos de FedEx.
│   │   │
│   │   ├── ai/                         -> Integraciones con servicios de inteligencia artificial.
│   │   │   ├── __init__.py
│   │   │   └── openai/
│   │   │       ├── __init__.py
│   │   │       ├── client.py           -> Envía imágenes o instrucciones a OpenAI.
│   │   │       ├── schemas.py          -> Representa las respuestas esperadas.
│   │   │       ├── prompts.py          -> Instrucciones utilizadas para analizar documentos.
│   │   │       └── mapper.py           -> Normaliza los datos devueltos por la IA.
│   │   │
│   │   ├── messaging/                  -> Integraciones con plataformas de mensajería.
│   │   │   ├── __init__.py
│   │   │   └── whatsapp/
│   │   │       ├── __init__.py
│   │   │       ├── client.py           -> Envía mensajes utilizando la API de Meta.
│   │   │       ├── schemas.py          -> Modelos de mensajes enviados y recibidos.
│   │   │       ├── mapper.py           -> Convierte eventos de Meta al formato interno.
│   │   │       └── exceptions.py       -> Errores específicos de WhatsApp.
│   │   │
│   │   └── payments/                   -> Integraciones con proveedores de pagos.
│   │       ├── __init__.py
│   │       └── provider/
│   │           ├── __init__.py
│   │           ├── client.py           -> Crea cobros y consulta pagos.
│   │           ├── schemas.py          -> Modelos de solicitudes y respuestas del proveedor.
│   │           ├── mapper.py           -> Normaliza las respuestas del proveedor.
│   │           └── exceptions.py       -> Errores asociados con los pagos.
│   │
│   ├── jobs/                           -> Tareas programadas o procesos ejecutados en segundo plano.
│   │   ├── __init__.py
│   │   ├── tracking_sync.py            -> Consulta periódicamente el estado de envíos.
│   │   ├── webhook_retry.py            -> Reintenta el procesamiento de webhooks fallidos.
│   │   └── notification_sender.py      -> Envía notificaciones pendientes.
│   │
│   └── utils/                          -> Funciones pequeñas y genéricas sin reglas de negocio.
│       ├── __init__.py
│       ├── dates.py                    -> Funciones auxiliares para trabajar con fechas UTC.
│       ├── files.py                    -> Validación de archivos, extensiones y tamaños.
│       └── identifiers.py              -> Generación o validación de identificadores.
│
├── migrations/                         -> Migraciones de la base de datos administradas por Alembic.
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/                              -> Pruebas automatizadas.
│   ├── __init__.py
│   ├── conftest.py                     -> Fixtures y configuración compartida de pytest.
│   ├── unit/                           -> Pruebas aisladas de servicios y funciones.
│   ├── integration/                    -> Pruebas con BD o servicios simulados.
│   └── api/                            -> Pruebas de endpoints de FastAPI.
│
└── logs/                               -> Archivos de log generados por la aplicación.
```



---



## Reglas Generales de Desarrollo



### Tipado

Todos los métodos y atributos deben utilizar type hints.

Utilizar:

- Mapped[]
- mapped_column()
- Declarative SQLAlchemy 2.0

Evitar patrones antiguos de SQLAlchemy.

---



## Programación Orientada a Objetos

Priorizar diseño orientado a objetos cuando aporte claridad y mantenibilidad.

Aplicar:

- Encapsulamiento.
- Abstracción.
- Composición sobre herencia cuando sea posible.
- Responsabilidad única.

Evitar clases excesivamente grandes o con múltiples responsabilidades.

Favorecer objetos cohesivos y fácilmente testeables.

---



### Docstrings

Usar formato Google Style.

---



### Comentarios

Todos los comentarios deben escribirse en español.

---



### Nomenclatura



#### Tablas

Utilizar nombres en plural.

Ejemplos:

- users
- roles
- shipments
- addresses



#### Campos

Utilizar snake_case.

Ejemplos:

- created_at
- updated_at
- tracking_number

---



## Auditoría

Las entidades principales deben contemplar:

- created_at
- created_by
- updated_at
- updated_by
- deleted_at
- deleted_by

---



## Soft Delete

Se utilizará soft delete.

No eliminar registros físicamente salvo casos excepcionales.

---



## Seguridad

Implementar:

- JWT Access Token
- Refresh Token
- RBAC

Modelo RBAC esperado:

- users
- roles
- permissions
- role_permissions
- user_roles

Las validaciones de autorización deben realizarse mediante permisos y no únicamente por nombre del rol.

---



## Integraciones

Las paqueterías deben integrarse mediante una interfaz común.

Toda integración debe ser desacoplada mediante adaptadores o mappers.

Proveedores previstos:

- FedEx
- UPS
- DHL
- Paquetexpress

No acoplar la lógica de negocio a una paquetería específica.

---



## Comportamiento Esperado de la IA

Actuar como mentor backend.

Antes de generar código:

1. Explicar el problema.
2. Explicar la solución.
3. Explicar alternativas.
4. Explicar ventajas y desventajas.
5. Justificar decisiones técnicas.

Después generar únicamente el código solicitado.

---



## Restricciones para la IA

- No modificar módulos ajenos a la funcionalidad solicitada.
- Mantener consistencia con la arquitectura existente.
- No generar más código del solicitado.

---



## Calidad de Código

Priorizar:

- Legibilidad.
- Mantenibilidad.
- Escalabilidad.
- Separación de responsabilidades.
- Tipado fuerte.
- Código explícito sobre código mágico.



## Principios SOLID

Las implementaciones deben respetar, cuando sea razonable:

- Single Responsibility Principle (SRP)
- Open/Closed Principle (OCP)
- Liskov Substitution Principle (LSP)
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)

No aplicar SOLID de forma dogmática.

Priorizar simplicidad cuando el problema sea pequeño.

## Patrones de Diseño

 
Utilizar patrones únicamente cuando resuelvan un problema real.
 
No introducir patrones por anticipación o complejidad innecesaria.
 
Justificar siempre:
 

- Qué problema resuelve el patrón.
- Por qué se eligió.
- Qué alternativa más simple existe.

 
Priorizar soluciones simples antes de incorporar patrones avanzados.

## Decisiones Arquitectónicas

Cuando una solución implique:

- Patrones de diseño.
- Refactorización importante.
- Nuevas capas arquitectónicas.
- Cambios estructurales.

La IA debe explicar previamente:

- Beneficios.
- Riesgos.
- Impacto en el proyecto.
- Complejidad agregada.

Antes de proponer la implementación.