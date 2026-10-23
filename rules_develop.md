## Reglas Generales de Desarrollo

Aplicar clean code haciendo el código fácil de leer, entender y modificar.

crear nueva funcionalidad y luego pulirla siguiendo estas recomendaciones que se presentan a continuación

### Programa en inglés

Es el idioma universal ya que los lenguajes de programación están en inglés.
La mayoria del código escrito está en inglés.
Usar el inglés sin vocabulario complicado haciendo que cualquier desarrollador lo entienda

### Nombres significativos
aplica para todo lo que se llegue a nombrar:

- Variables, funciones, argumentos, clases, métodos .
- Clases, paquetes
- Ficheros y directorios.
- Ficheros de despliegue

ahora te proporciono ejemplos:\
    - Variables: Nombres que revelen intención ejemplo:
        ```python
        # correcto
        day_of_birth: int
        month_of_birth: int
        year_of_birth: int

        # no correcto
        d # Day
        m # Month
        y # Year
        ```
    existe un caso en el que si se pueden declarar variables de una sola letra que es en los bucles como i, j y k normales al realizar un bucle

    - Evitar desinformación ejemplo:
        ```python
        # ¿Encuentras la diferencia?

        """
        clase demasiado larga sin aportar valor
        aportando confusion es:
            1) complicado buscar estas clases
            2) conplicado identificar las clases que se llaman de esta forma
        """
        class ServiceForEfficientUpdateMysqlDatabase:
            pass

        class ServiceForEfficientBackupMysqlDatabase:
            pass

        """
        ¿ cuál es la diferencia entre data e info?
        """
        class ProductData:
            pass

        class ProductInfo:
            pass
        ```
        - Usar nombres pronunciables: Los nombres deben ser fáciles de buscar ejemplo:
        ```python

        # Incorrecto
        class InfRcrd:
            def __init__(self, nm, snm):
                self._nm = nm
                self._snm = snm

        # Correcto
        class Employee:
            def __init__(self, name: str, surname: str):
                self._name = name
                self._surname = surname

        # Es mucho mejor elegir un nombre muy largo a uno que no deja claro su significado

        lst_used_name = "Espancho"
        least_used_name = "Patrotlo"

        ```

    - Nombres de clases y métodos
        - Los nombres de las clases deben ser un nombre o un conjunto de nombres, no deberían ser verbos.
        - Los nombres de los métodos deberían ser verbos,
        indicando una acción.
        - No llamar a una clase CreateEmployee, ni a un método EmployeeName(), por ejemplo:
        ```python
        from datetime import date

        class DateParser:

            def parse(date: date):
                pass

        ```
    - Añadir contexto que aporte significado
        - Variables first_name, last_name, street, house_number, city, state, zip_code.
        - Estando juntas, es obvio que se trata de una dirección.
        - Añadir prefijo addr para aportar información.
        - user.get_first_name() vs user.get_addr_first_name()

### Funciones

- Pequeñas. Muy pequeñas.
- Hacen una sola cosa. ejemplo:
    ```python
    # Incorrecto
    def read_numbers_from_file_and_calculate_total(file_url: str) -> int:
        with open(file_url, mode='r') as file:
            numbers = file.readlines()

        total = 0
        for number_string in numbers:
            total += int(number_string.strip())

        return total

    # Correcto
    MONTHLY_SALES_FILE_PATH = "monthly_sales.txt"

    def get_monthly_sales() -> int:
        sales = read_numbers_from_file(MONTHLY_SALES_FILE_PATH)
        return calculate_summatory(sales)

    def read_numbers_from_file(file_path: str) -> list[str]:
        with open(file_path, mode="r", encoding="utf-8") as file:
            return file.readlines()

    def calculate_summatory(values: list[str]) -> int:
        return sum(int(value.strip()) for value in values)

    ```
    La función get_monthly_sales() se encuentra en un nivel de abstracción superior a las otras dos que su nivel de abstracción más bajo por que realizan acciones de más bajo nivel es necesario que asi como se van llamando las funciones se vayan acomodando para su fácil lectura, por ejemplo al ejecutar la función read_numbers_from_file() esta se encuentra inmediatamente abajo para su fácil encuentro y lectura.

- Nivel de abstracción único ejemplo:
    ```python
    # Incorrecto
    class Person:
        def drive(self, car: Car):
            car.open_door()
            car.set_driver(self)
            car.get_battery().connect()
            car.get_engine().start()

    # Correcto
    class Car:
        def __init__(battery: Battery, engine: Engine):
            self.battery = battery
            self.engine = engine

        def start(self):
            self.battery.connect()
            self.engine.start()

    class Person:
        def drive(self, car: Car):
            car.open_door()
            car.set_driver(self)
            car.start()


    ```
- Reciben pocos argumentos. ejemplo:
    - Se deben evitar funciones con más de 3 argumentos.
    - Un gran número de argumentos suele indicar una mala encapsulación.
    ```python
    # Incorrecto
    def create_user(user_name: str, password: str, first_name: str,
                    last_name: str, address: str):
        pass

    def createCircle(x: float, y: float, radius: float):
        pass

    # Correcto
    def create_user(user_form_data: UserFormData):
        pass

    def create_circle(center: Point, radius: float):
        pass

    ```

- No tienen efectos secundarios.
- Devuelven excepciones en lugar de códigos de error
    - las buenas funciones devuelven exepciones en lugar de códigos de error
    - Si devuelves códigos de error, debes tratarlo al momento, con exepciones no.\
ejemplo incorrecto:
    ```python
    def restore_last_database_backup() -> None:
        if backup_current_data() == "OK":
            backup = get_last_backup()
            if backup.restore() == "OK":
                logger.log("Backup restored")
            else:
                logger.log("Error restoring backup")
        else:
            logger.log(
                "Could not backup current data. Restore backup canceled"
            )


    ```
    - Utilizar excepciones te permite tener el camino de ejecución correcto separado del camino de errores.\
    ejemplo correcto:

    ```python
    def safely_restore_last_database_baskup() -> None:
        try:
            backup_current_data()
            backup = get_last_backup()
            backup.restore()
            logger.info("Backup restored")

        except CreateBackupException as exc:
            logger.error(
                f"Could not backup current data. Restore backup canceled. Error: {exc}"
            )

        except RestoreBackupException as exc:
            logger.error(
                f"Error restoring backup. Error: {exc}"
            )

    # Todavía mejor
    def safely_restore_last_database_backup() -> None:
    try:
        restore_last_database_backup()

    except CreateBackupError:
        logger.error(
            "Could not backup current data. Restore backup canceled."
        )

    except RestoreBackupError:
        logger.error(
            "Error restoring backup"
        )

    def restore_last_database_backup() -> None:
        backup_current_data()
        backup = get_last_backup()
        backup.restore()

    ```

### Comentarios
El buen código no necesita comentarios
 - Añadir comentarios solo cuando sea estrictamente necesario.
 - Son muy complicados de mantener. El código cambia muy rápido, y los comentarios quedan desactualizados rápidamente.
 - Si el código tiene muchos comentarios, puede ser por dos razones:
    1. El código no se entiende => Refactorización.
    2. Los comentarios son obvios => Eliminar comentarios (no aportan nada)
Ejemplos de malos comentarios:
    ```python

    # check if password is secure
    if (password != None and password.length > 9 and password.contains(username)):
        pass

    if (is_secure(password)):
        pass

    ```
    En el ejemplo la condición dentro del if hay que analizarla para entenderla y se elimina encapsulando en una función con is_secure()
    Mas ejemplos:
        ```python

        from datetime import date

        # clase incorrecta
        class Event:
            def __init__(self) -> None:
                self.date: str = "" # The date as string

        # clase incorrecta se desactualizo el comentario
        class Event:
            def __init__(self) -> None:
                self.date: date = date.today() # The date as string

        ```
    Escribir comentarios lleva tiempo y es tiempo que podemos invertir en cosas más productivas como mejorar el código en otras partes, ademas si el código esta lleno de comentarios hay comentarios importantes que se pierden en la jungla de comentarios obvios. Último ejemplo:
        ```python

        def calculate_total_price(products: list[float]) -> float:
            total = sum(products)

            # total = 0
            # for product in products:
            #     total += product

            return total

        ```
    Nunca dejes comentado código que ya no se está utilizando.. ¡ Para algo tenemos el software de control de versiones!

    Buenos comentarios

    ```python
    """En el caso de regex o expresiones regulares si es buena práctica realizar un comentario por que si no el programador tendria que descifrar cada grupo"""
    import re

    # Matches dates in format 17-01-2021 18:03:45
    is_valid = bool(
        re.fullmatch(
            r"(\d{2})-(\d{2})-(\d{4}) (\d{2}):(\d{2}):(\d{2})",
            date,
        )
    )

    # TODO: Expect this method to change when the client changes auth API
    def login(user: User) -> None:
        pass

    # TODO: Replace mock service with real implementation.

    # TODO: Remove this workaround after API v2 migration.

    # FIXME: Raises an error when the user has no permissions.

    # HACK: Temporary solution until Redis cache is implemented.
    ```
### Formato del código

- Formato vertical. Densidad, distancia y orden
  - densidad vertical baja (uso de líneas en blanco para separar conceptos relacionados)
  ```python
  # Incorrecto
  class Car:
    def __init__(self, battery, engine):
        self.battery = battery
        self.engine = engine
    def start(self):
        self.battery.connect()
        self.engine.start()
    def stop(self):
        self.engine.stop()
        self.battery.disconnect()
    def check_battery(self):
        self.battery.check_battery_life()
    def check_engine(self):
        self.engine.check()

  # Correcto
  # - Correcto baja densidad visual
  class Car:
    def __init__(self, battery, engine):
        self.battery = battery
        self.engine = engine

    def start(self):
        self.battery.connect()
        self.engine.start()

    def stop(self):
        self.engine.stop()
        self.battery.disconnect()

    def check_battery(self):
        self.battery.check_battery_life()

    def check_engine(self):
        self.engine.check()
  ```
  Observa cómo:
    - Los atributos están agrupados en __init__.
    - Cada método está separado por una línea en blanco.
    - Es fácil distinguir dónde termina un concepto y comienza otro.
  - Formato orden vertical
  ```python
  # Incorrecto: orden vertical desorganizado
  class UserService:
    def _send_welcome_email(self, data):
        print("Enviando correo de bienvenida")

    def _validate_data(self, data):
        if not data["email"]:
            raise ValueError("Email requerido")

    def create_user(self, data):
        self._validate_data(data)
        self._save_user(data)
        self._send_welcome_email(data)

    def _save_user(self, data):
        print("Guardando usuario en la base de datos")

  # Correcto: lectura de arriba hacia abajo
  class UserService:
    def create_user(self, data):
        self._validate_data(data)
        self._save_user(data)
        self._send_welcome_email(data)

    def _validate_data(self, data):
        if not data["email"]:
            raise ValueError("Email requerido")

    def _save_user(self, data):
        print("Guardando usuario en la base de datos")

    def _send_welcome_email(self, data):
        print("Enviando correo de bienvenida")
  ```
  Al leer el archivo:
    - Primero entiendes el flujo general (create_user).
    - Después encuentras cómo se valida.
    - Luego cómo se guarda.\
  Finalmente cómo se envía el correo.
  La explicación va descendiendo en nivel de detalle.
    - Formato vertical - Distancia
      - La idea es que las líneas en blanco no se usan al azar, sino para separar bloques de código que representan diferentes etapas de un proceso.
      ```python
      # Correcto: bloques bien agrupados
      def calculate_discounted_price(product_id: int) -> float:
      product = get_product(product_id)
      customer = get_current_customer()

      final_price = product.price

      if customer.is_premium:
          final_price *= 0.9

      return final_price
      ```
      Se divide en:
      - Obtención de datos
      - Procesamiento
      - Resultado o retorno
    Incorrecto sin separacion de conceptos
      ```python
      def calculate_discounted_price(product_id: int) -> float:
        product = get_product(product_id)
        customer = get_current_customer()
        final_price = product.price
        if customer.is_premium:
            final_price *= 0.9
        return final_price
      ```
- Formato horizontal. Densidad e identación
    - Densidad -> se refiere a cuánto espacio existe entre los elementos de una misma línea. Cuando todo está pegado, el código se vuelve más difícil de leer visualmente. Los espacios ayudan a distinguir parámetros, operadores y expresiones.
    ```python
    # Incorrecto: alta densidad horizontal
    def calculate_total(price,tax,discount):
        if price is None or tax is None or discount is None:
            return None

        return price+tax-discount

    # Correcto: baja densidad horizontal
    def calculate_total(price, tax, discount):
        if price is None or tax is None or discount is None:
            return None

        return price + tax - discount
    ```
    Los espacios permiten identificar rápidamente:
        - Los parámetros.
        - Los operadores.
        - Las partes de la expresión.
    - Identacion Horizontal -> a idea es evitar líneas demasiado largas y mantener una indentación consistente.
    ```python
    # Incorrecto: línea demasiado larga
    def create_user(name, email, phone, address, city, state, postal_code, country, is_active):
        return User(name=name, email=email, phone=phone, address=address, city=city, state=state, postal_code=postal_code, country=country, is_active=is_active)

    # Correcto: división vertical de la línea
    def create_user(
        name,
        email,
        phone,
        address,
        city,
        state,
        postal_code,
        country,
        is_active,
    ):
        return User(
            name=name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_active=is_active,
        )
    ```

    Las reglas son las siguientes:
        - 4 espacios por nivel de indentación.
        - Evitar líneas demasiado largas (79-88 caracteres).
        - Dividir llamadas y definiciones largas en varias líneas.
        - Priorizar la legibilidad sobre ahorrar líneas
- Seguir styleguide de Google -> [syleguide de python](https://google.github.io/styleguide/pyguide.html)

### Gestión de errores
- El código debe ser limpio pero también robusto
- La gestión de errores puede ensuciar mucho el código, por lo que hay que prestarle especial atención.
    - Excepciones en lugar de códigos de error -> Lo que Robert C. Martin intenta enseñar en ese ejemplo no es que nunca debas usar try/except dentro de una función, sino que la lógica de negocio y el manejo de errores deberían estar separados.
    ```python
    def shutdown_device():
        try:
            handle = get_handle("DEV1")

            record = retrieve_device_record(handle)

            pause_device(handle)
            clear_device_work_queue(handle)
            close_device(handle)

        except DeviceShutdownError as error:
            logger.error(error)

    # Correcto
    def shutdown_device():
        try:
            try_shutdown_device()
        except DeviceShutdownError as error:
            logger.error(error)

    def try_shutdown_device():
        handle = get_handle("DEV1")

        record = retrieve_device_record(handle)

        pause_device(handle)
        clear_device_work_queue(handle)
        close_device(handle)
    ```
- Devolver excepciones en lugar de códigos de error
    - En Python normalmente usamos raise
    - Python ya favorece este estilo naturalmente. Ejemplo:

    ```python
    def get_user(user_id: int):
        user = db.find_user(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    ```
    - La función:
        - Hace su trabajo.
        - Detecta que no puede continuar.
        - Lanza una excepción
    - Después alguien más decide:
    ```python
    try:
        user = get_user(10)
    except UserNotFoundError:
        print("Usuario no encontrado")
    ```

- Usar excepciones unchecked
    - Se pueden tratar co try catch, pero no es estrictamente necesario. ejemplo
    ```python
    # errors.py
    class UserNotFoundError(Exception):
        pass

    # repository.py
    def get_by_id(user_id: int):
        user = db.query(UserORM).get(user_id)

        if user is None:
            raise UserNotFoundError(user_id)

        return user

    # service.py
    def get_user(user_id: int):
        return repository.get_by_id(user_id)

    # endpoint.py
    @router.get("/{user_id}")
    def get_user(user_id: int):
    try:
        return service.get_user(user_id)

    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    # O en fastaApi tiene el Exception Handlers
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": "Usuario no encontrado"},
        )
    ```
- No devolver ni pasar null
    - No obligues a todos los consumidores a estar verificando constantemente if x is not None. Si puedes devolver un objeto vacío válido, hazlo. Y reserva las excepciones para situaciones verdaderamente excepcionales.

    ```python
    # Incorrecto
    def get_active_users() -> list[User] | None:
        users = repository.find_active_users()

        if not users:
            return None

        return users


    users = get_active_users()

    if users is not None:
        for user in users:
            process_user(user)

    # Correcto
    # Regla: Si una colección está vacía, devuelve una colección vacía (`[]`), no `None`.
    def get_active_users() -> list[User]:
        users = repository.find_active_users()

        return users or []


    for user in get_active_users():
        process_user(user)

    # Caso "Se esperaba que existiera algo"
    # Incorrecto
    def get_user(user_id: int) -> User | None:
        user = repository.get_by_id(user_id)

        if user is None:
            return None

        return user


    user = get_user(1)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    # Correcto
    # Regla: Si el objeto debería existir y no existe, lanza una excepción específica en lugar de devolver `None`.
    class UserNotFoundError(Exception):
        pass


    def get_user(user_id: int) -> User:
        user = repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError(
                f"Usuario {user_id} no encontrado"
            )

        return user

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)}
        )

    ```