### Test
Caracteristicas
- Fáciles de escribir
- Fáciles de leer
- Rápidas
- Flexibles

Utilizar tecnica triple A
1. Arrange -> Arreglar 
    - Importaciones
    - Inicializaciones
2. Act -> Actuar
    - Aplicar estímulos
    - Llamar métodos
    - Simular clicks
3. Assert -> Afirmar
    - Qué debe de haber sucedido de acuerdo al estimulo anterior
    - Qué no debe de suceder 

Coverage -  Cobertura
- Cobertura de líneas: Porcentaje de líneas ejecutadas
- Cobertura de ramas: Porcentaje de ramas de decisión probadas
- Cobertura de funciones: Porcentaje de funciones/métodos invocados
- Cobertura de condiciones: Porcentaje de condiciones evaluadas en ambos sentidos

#### Filosofía TDD (Test Driven Development)
TDD es una metodología donde las pruebas guían el desarrollo del software.
```text
RED
↓
Crear un test que falle

GREEN
↓
Implementar la funcionalidad mínima para que el test pase

REFACTOR
↓
Mejorar la implementación sin romper los tests
```
Ejemplo:

```python
# Paso 1: Crear el test

def test_given_negative_number_when_abs_called_then_returns_positive():
    assert abs_value(-5) == 5
```
La función aún no existe y el test falla.

```python
# Paso 2: Implementar la funcionalidad mínima

def abs_value(number):
    return -number
```
Ahora el test pasa.

```python
# Paso 3: Mejorar la implementación

def abs_value(number):
    if number >= 0:
        return number

    return -number
```
#### Nombrado de tests

Los nombres deben describir claramente:
- Estado inicial
- Acción ejecutada
- Resultado esperado

Seguir el patrón:
```python
# test_given_<estado>_when_<accion>_then_<resultado>()
```
Ejemplo:
```python
def test_given_empty_flight_controller_when_flight_added_then_flight_can_be_found():
    ...
```

Evitar nombres genéricos.

````python
# Incorrecto
def test_flight():
    ...


# Incorrecto
def test_add():
    ...


# Correcto
def test_given_empty_flight_controller_when_flight_added_then_flight_can_be_found():
    ...
````
Estructura Given / When / Then

Cada test debe estar dividido visualmente en tres secciones:
- Given: preparación
- When: acción
- Then: validación

Ejemplo:
```python
def test_given_valid_user_when_created_then_user_is_stored():

    # Given
    repository = UserRepository()
    service = UserService(repository)

    # When
    service.create_user("alfredo@test.com")

    # Then
    stored_user = repository.get_by_email(
        "alfredo@test.com"
    )

    assert stored_user is not None
```

Un comportamiento por test

Cada test debe validar un único comportamiento.
Incorrecto:
```python
def test_create_user():

    user = service.create_user(
        "alfredo@test.com"
    )

    assert user.email == "alfredo@test.com"
    assert user.id == 1
    assert user.is_active is True
    assert user.role == "admin"
```
Correcto:
```python
def test_given_valid_user_when_created_then_email_is_assigned():
    ...

def test_given_valid_user_when_created_then_id_is_generated():
    ...

def test_given_valid_user_when_created_then_user_is_active():
    ...
```

#### Usar AAA (Arrange, Act, Assert)

Given / When / Then es equivalente a:
```text
Given   = Arrange
When    = Act
Then    = Assert
```
Ejemplo:

```python
def test_given_valid_user_when_created_then_id_is_generated():

    # Arrange
    repository = Mock()
    service = UserService(repository)

    # Act
    user = service.create_user(
        "alfredo@test.com"
    )

    # Assert
    assert user.email == "alfredo@test.com"
```

#### Test Unitarios
Los tests unitarios validan una única unidad de código de forma aislada.
Deben:

- Utilizar mocks para dependencias externas.
- No usar FastAPI.
- No usar bases de datos.
- No hacer llamadas HTTP.
- Ejecutarse rápidamente.

Ejemplo:
```python
from unittest.mock import Mock


def test_given_existing_email_when_creating_user_then_error_is_raised():

    # Given
    repository = Mock()

    repository.get_by_email.return_value = User(
        email="alfredo@test.com"
    )

    service = UserService(repository)

    # When / Then
    with pytest.raises(UserAlreadyExistsError):
        service.create_user(
            "alfredo@test.com"
        )
```

Uso de mocks

Utilizar mocks cuando una dependencia no forma parte de la unidad bajo prueba.

Ejemplo:
```python
# Correcto

repository = Mock()

service = UserService(
    repository
)
```
Evitar:

```python
# Incorrecto para un test unitario

repository = UserRepository(
    real_database
)
```
El objetivo es probar únicamente la lógica del servicio.

Verificación de excepciones

Cuando se espera un error se debe usar:
```python
pytest.raises()
```

Ejemplo:
```python
def test_given_zero_divisor_when_dividing_then_exception_is_raised():

    calculator = Calculator()

    with pytest.raises(
        DivisionByZeroError
    ):
        calculator.divide(10, 0)
```

Tests parametrizados

Cuando el mismo comportamiento debe probarse con múltiples entradas, utilizar:
```python
@pytest.mark.parametrize()
```
Ejemplo:
```python
@pytest.mark.parametrize(
    "value,expected",
    [
        (-10, 10),
        (-5, 5),
        (0, 0),
        (10, 10),
    ]
)
def test_given_number_when_abs_called_then_returns_positive_value(
    value,
    expected,
):
    assert abs(value) == expected
```
Evitar:
```python
def test_abs_1():
    ...


def test_abs_2():
    ...


def test_abs_3():
    ...
```
#### Tests de integración
Los tests de integración verifican que varios componentes colaboran correctamente.

Pueden utilizar:

- FastAPI TestClient
- SQLite de prueba
- PostgreSQL de prueba
- Dependency Overrides
Ejemplo:
```python
def test_given_valid_user_when_request_is_sent_then_user_is_created(
    client,
):
    response = client.post(
        "/users",
        json={
            "email": "alfredo@test.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 201
```
Estos tests validan:
```text
FastAPI
↓
Service
↓
Repository
↓
Database
```

#### Tests E2E
Los tests End-To-End validan flujos completos del sistema.

Deben evitar mocks de negocio.

Ejemplo:
```python
def test_given_registered_user_when_login_and_create_order_then_order_is_stored():

    token = login_user()

    response = client.post(
        "/orders",
        json={
            "product_id": 1,
        },
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 201
```
Estos tests validan:
```text
Autenticación
↓
Endpoints
↓
Servicios
↓
Repositorios
↓
Base de datos
```
Happy Path y Error Path

Todo comportamiento importante debe tener:

- Camino exitoso.
- Camino de error.
