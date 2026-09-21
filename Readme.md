# EcoTechSolutions

Sistema de gestión de empleados para EcoTechSolutions, desarrollado en Python a partir del modelo UML definido para el proyecto de la Unidad 2.

La solución aborda la programación orientada a objetos, la integración con una base de datos, las operaciones CRUD, la validación de datos y el manejo de errores.

## Objetivo

Representar y gestionar los siguientes elementos:

- Departamentos.
- Empleados.
- Proyectos.
- Usuarios del sistema.
- Registros de tiempo trabajado.

El desarrollo se realiza de forma incremental. Cada avance se revisa técnicamente y se documenta en `VALIDACION_IA.md`.

## Estado actual

- Unidad 2: criterios 2.1.1 a 2.1.5 implementados y validados.
- Arquitectura: núcleo de dominio y persistencia en `main.py`; servicios externos en `servicios_externos.py`; interfaz de consola en `interfaz.py`.
- Seguridad: PBKDF2 para contraseñas, cifrado Fernet en reposo para dirección, teléfono y salario, y entrada enmascarada con asteriscos para datos sensibles.
- Roles: `admin`, `rrhh` y `empleado`, con menús y permisos diferenciados. Los empleados solo ven y registran sus propias horas; crear proyectos y asignar personas es exclusivo de `admin` y `rrhh`.
- Calidad: correcciones aplicadas para duplicidad, literales repetidos, código sin uso, complejidad cognitiva y fechas con zona horaria; sin avisos de mantenibilidad SonarQube en los módulos ni en las pruebas.
- Unidad 3: criterios 3.1.1 a 3.1.4 implementados y validados. Consumo de OpenWeatherMap (clima por proyecto) y mindicador.cl (dólar, euro, UF) con `requests`; secretos en `.env`; validación de entradas y de respuestas; manejo de errores HTTP y de red con mensajes sin datos sensibles; respaldo local en SQLite; cálculo de pagos en moneda extranjera; 28 pruebas automatizadas sin red en `test_servicios_externos.py`.

## Requisitos

- Python 3.10 o superior.
- Dependencias declaradas en `requirements.txt`: `requests` (consumo de APIs), `python-dotenv` (carga de `.env`) y `cryptography` (cifrado de datos personales).
- SQLite se utiliza mediante la librería estándar `sqlite3`.

## Estructura del proyecto

```text
Ecotech_solutions/
├── main.py
├── servicios_externos.py
├── interfaz.py
├── test_nucleo.py
├── test_servicios_externos.py
├── requirements.txt
├── .env.example
├── Readme.md
├── VALIDACION_IA.md
├── Rubrica.pdf
├── TI3V21_U1_ES_GUÍA primera parte.pdf
├── TI3V21_U2_U3_ES02_GUÍA.docx
├── uml.mmd
└── uml.png
```

## Correspondencia con el UML

La implementación utiliza `dataclass` para representar las entidades del diagrama y anotaciones de tipo para expresar sus relaciones:

- Un empleado puede pertenecer a un departamento.
- Un empleado puede participar en varios proyectos.
- Un proyecto puede tener varios empleados asignados.
- Un registro de tiempo pertenece a un empleado y a un proyecto.
- Un usuario puede estar asociado a un empleado.
- Un proyecto puede tener una ciudad asociada (Unidad 3), usada para consultar el clima.
- Las consultas de clima e indicadores se guardan localmente (`consultas_clima`, `indicadores`) como respaldo.

El diagrama original de la Unidad 1 se encuentra en `uml.png`. El modelo vigente, que integra los requisitos de la guía de la Unidad 1 (dirección, teléfono, fecha de inicio de contrato y salario del empleado; gerente del departamento; descripción de tarea en el registro de tiempo; desasignación de proyectos; informes exportables; cifrado de datos personales) con las clases de la Unidad 3, está en `uml.mmd` (Mermaid) y se renderiza en https://mermaid.live.

Al contrastar el código con la guía de la Unidad 1 se detectaron requisitos aún no implementados; `uml.mmd` es el modelo objetivo y el código se alinea con él en los cambios siguientes. Hasta completar esa alineación, las diferencias vigentes son: `Departamento` sin `gerente`; `RegistroTiempo` sin `descripcion_tarea`; sin `Informe`, `ServicioReportes.guardar()` ni `desasignar_empleado_de_proyecto()`; y el autoregistro de cuentas `empleado` todavía abierto. La ficha completa de `Empleado` y `CifradorDatos` ya están implementados.

## Estado de los criterios

### Criterio 2.1.1: implementación del modelo UML

**Estado: completado.**

El archivo `main.py` contiene las siguientes clases:

- `Departamento`: identifica un departamento y mantiene sus empleados.
- `Empleado`: representa a un trabajador con su ficha personal (dirección, teléfono, fecha de inicio de contrato y salario), un ID único automático, su departamento, proyectos y registros de tiempo.
- `Proyecto`: representa un proyecto, sus empleados asignados y sus registros de tiempo.
- `Usuario`: representa las credenciales y el estado de acceso de un empleado.
- `RegistroTiempo`: relaciona una fecha y una cantidad de horas con un empleado y un proyecto.

También se implementaron las operaciones:

- `asignar_empleado_a_departamento()`.
- `asignar_empleado_a_proyecto()`.
- `registrar_tiempo()`.

Estas operaciones mantienen las relaciones entre objetos y evitan registrar duplicados en las listas asociadas.

### Criterio 2.1.2: principios de orientación a objetos

**Estado: completado.**

Se incorporaron los siguientes elementos:

- Encapsulamiento de la contraseña de `Usuario` mediante `_contrasena`, una propiedad de lectura y `actualizar_contrasena()`.
- Abstracción mediante la clase `IExportador` y su método abstracto `exportar()`.
- Herencia en `ExportadorPDF` y `ExportadorExcel`.
- Polimorfismo en `ServicioReportes`, que trabaja con cualquier implementación de `IExportador`.
- Reutilización de la lógica común del servicio sin duplicar el proceso de generación de informes.

### Criterio 2.1.3: integración con base de datos

**Estado: completado.**

Se seleccionó **SQLite** por ser una base de datos relacional integrada en Python mediante la librería estándar `sqlite3`. La base se guarda en `ecotech_solutions.db` cuando se utiliza la ruta predeterminada.

La implementación incluye:

- Creación de tablas para departamentos, empleados, proyectos, usuarios y registros de tiempo.
- Claves foráneas para mantener las relaciones del UML.
- Tabla intermedia `empleado_proyecto` para la relación muchos a muchos.
- Operaciones CRUD para departamentos, empleados, proyectos, usuarios y registros de tiempo.
- Persistencia de proyectos, asignaciones y registros de horas.
- Al eliminar un usuario asociado, también se elimina su empleado y su asignación, pero el proyecto se conserva para asignarlo a otra persona.
- Validación de la asignación empleado-proyecto antes de guardar horas.
- Consultas parametrizadas para separar los datos de las instrucciones SQL.

### Criterio 2.1.4: validaciones y manejo de excepciones

**Estado: completado.**

Las entidades rechazan datos inválidos mediante `ValueError`, incluyendo:

- Campos de texto obligatorios vacíos.
- Correos sin un formato básico válido.
- Identificadores negativos.
- Fechas de fin anteriores a la fecha de inicio.
- Registros de tiempo con horas menores o iguales a cero o mayores que 24.
- Usuarios con nombre o contraseña vacíos.
- Rollback automático y manejo de errores SQLite durante las operaciones.
- Cierre controlado ante interrupciones del usuario o fin de entrada.

### Criterio 2.1.5: revisión crítica del código apoyado por IA

**Estado: completado.**

La revisión detectó que algunas operaciones de actualización SQLite podían saltarse las validaciones aplicadas al crear entidades. Se corrigió el problema reutilizando las validaciones de texto, fechas y horas en las operaciones CRUD.

Además, se reforzó la seguridad del modelo de usuario: la propiedad `contrasena` ya no expone el valor real en texto plano, y el acceso interno se controla mediante `obtener_contrasena_interna()` y `verificar_contrasena()`. Esto evita fugas de credenciales por lectura directa del objeto y mantiene el flujo de autenticación y persistencia bajo validación explícita.

La revisión crítica se documenta en `VALIDACION_IA.md`, donde se describen los hallazgos, las decisiones técnicas y la validación de cada mejora.

## Estado de los criterios de la Unidad 3

| Criterio | Evidencia |
|---|---|
| 3.1.1 Consumo de servicios externos con librerías oficiales | `ServicioClima` (OpenWeatherMap) y `ServicioIndicadores` (mindicador.cl) sobre `requests.Session`; respuestas JSON procesadas y validadas; datos usados en el menú (opciones 10, 11 y 12). |
| 3.1.2 Autenticación y validación de entradas | Login con PBKDF2 y roles; códigos de rol y llave de API en `.env`; `validar_ciudad()`, lista blanca de indicadores, `validar_monto()`; opciones filtradas por rol y verificadas al ejecutar. |
| 3.1.3 Manejo de errores en servicios externos | `ClienteHTTP` traduce 401/403, 404, 429, 5xx, timeout, sin conexión, cuerpo no JSON y respuestas de más de 1 MB a `ErrorServicioExterno` con mensajes sin URL ni llave; reintento ante 5xx/timeout; respaldo local con aviso; el menú nunca se interrumpe. |
| 3.1.4 Ajuste de seguridad con apoyo de IA | Cambios 27 a 32 de `VALIDACION_IA.md`: propuestas de IA evaluadas, modificadas o descartadas con justificación (exposición de la llave en mensajes, falta de timeout, uso sin validar de la respuesta, orden de la serie, caché con expiración, tamaño de respuesta). |

## Pruebas automatizadas

```powershell
py -3 -m unittest -v test_nucleo test_servicios_externos
```

`test_nucleo.py` (19 pruebas) cubre el núcleo de la Unidad 2: migración de una base antigua a la nueva tabla `empleados` conservando filas y claves foráneas, validaciones de la ficha del empleado, valor hora, persistencia y actualización con los nuevos campos, cifrado en reposo (la base solo contiene tokens, clave incorrecta o ausente informada con claridad, cifrado de valores heredados), registro desde el menú, listado con y sin datos personales, y cálculo de pago desde el salario.

`test_servicios_externos.py` (28 pruebas) se ejecuta sin red: simulan la sesión HTTP con `unittest.mock` para cubrir respuestas correctas, cada código de error, timeout, sin conexión, JSON inválido o fuera de rango, respuestas demasiado grandes, la validación de entradas, el cálculo de pagos y el respaldo local en SQLite en memoria. Una de ellas verifica que ningún mensaje de error contenga la llave de la API y otra que tampoco aparezca en el registro técnico, incluso cuando se guarda el traceback.

## Ejecución

Desde la carpeta del proyecto, la primera vez:

```powershell
py -3 -m pip install -r requirements.txt
copy .env.example .env
```

Luego editar `.env` y definir `ECOTECH_CODIGO_ADMIN` y `ECOTECH_CODIGO_RRHH` (códigos exigidos para registrar cuentas `admin` y `rrhh`), `OPENWEATHER_API_KEY` y `ECOTECH_CLAVE_CIFRADO`. La clave de cifrado se genera una sola vez con:

```powershell
py -3 -c "import main; print(main.generar_clave_cifrado())"
```

Para ejecutar:

```powershell
py -3 interfaz.py
```

La interfaz de consola se encuentra separada exclusivamente en `interfaz.py`. El archivo `main.py` expone una API pública de dominio y persistencia mediante `__all__`, y mantiene únicamente un lanzador compatible para no romper la ejecución anterior con `py -3 main.py`.

Al iniciar, el programa crea `ecotech_solutions.db` si no existe, crea sus tablas y muestra un menú para:

- Crear y listar departamentos, empleados y proyectos.
- Asignar empleados a proyectos (solo `admin` y `rrhh`).
- Registrar horas trabajadas (los empleados solo las propias).
- Consultar registros de tiempo.
- Crear y listar usuarios asociados a empleados.
- Solicitar login antes de entrar al menú principal.
- Registrar usuarios con rol `admin`, `rrhh` o `empleado`.
- Generar automáticamente el nombre de usuario usando la inicial del nombre y el apellido.
- Crear automáticamente la ficha del empleado para los roles `empleado` y `rrhh`, con dirección, teléfono, fecha de inicio de contrato y salario mensual; el sistema asigna un ID único automático.
- Permitir que `admin` y `rrhh` gestionen departamentos, usuarios y reportes.
- Permitir que solo un administrador cambie roles o elimine otras cuentas.
- Generar reportes en formato de texto tipo PDF o CSV tipo Excel.
- Consultar el clima actual de la ciudad de un proyecto (opción 10, disponible para todos los roles).
- Consultar el valor vigente del dólar, el euro o la UF (opción 11, todos los roles).
- Calcular el pago de un empleado en moneda extranjera a partir de sus horas registradas y de su salario mensual (opción 12, solo `admin` y `rrhh`).

Para cerrar el programa se selecciona la opción `0`. La base de datos se guarda localmente y no se sube a GitHub porque está incluida en `.gitignore`.

En el primer inicio se debe registrar el primer usuario. Para seleccionar el rol `admin` o `rrhh` se solicita el código secreto definido en `.env`; si la variable no está configurada, el sistema lo informa sin revelar ningún valor. Los usuarios nuevos se guardan con hash PBKDF2; las credenciales antiguas almacenadas en texto plano se rechazan y deben restablecerse de forma segura.

Las contraseñas y códigos secretos se muestran como asteriscos mientras se escriben. Las contraseñas se almacenan mediante PBKDF2 y no en texto plano.

La interfaz centraliza mensajes y consultas reutilizadas, y separa el flujo de inicio de sesión en funciones auxiliares para mantener una complejidad cognitiva baja. El menú principal se define en una sola tabla (`construir_opciones_menu()`) con número, texto, permiso y acción de cada opción; de ella se derivan tanto el listado en pantalla como la ejecución, por lo que las opciones no visibles para un rol tampoco son ejecutables.

Menú completo (los roles ven solo lo permitido):

| N.º | Opción | Roles |
|---|---|---|
| 1 | Gestionar departamentos | admin, rrhh |
| 2 | Listar departamentos | todos |
| 3 | Listar empleados (admin y rrhh ven además la ficha personal) | todos |
| 4 | Crear proyecto | admin, rrhh |
| 5 | Listar proyectos | todos |
| 6 | Asignar empleado a proyecto | admin, rrhh |
| 7 | Registrar horas trabajadas (los empleados, solo las propias) | todos |
| 8 | Ver registros de tiempo (los empleados, solo los propios) | todos |
| 9 | Generar reporte (los empleados, solo el propio) | todos |
| 10 | Consultar clima de un proyecto | todos |
| 11 | Consultar indicador económico | todos |
| 12 | Calcular pago en moneda extranjera | admin, rrhh |
| 13 | Crear usuario | admin, rrhh |
| 14 | Listar usuarios | admin, rrhh |
| 15 | Cambiar rol de usuario | admin |
| 16 | Eliminar usuario | admin |
| 0 | Salir | todos |

Actualmente los roles disponibles son `admin`, `rrhh` y `empleado`. El rol `rrhh` requiere el código `ECOTECH_CODIGO_RRHH`, tiene permisos de gestión salvo cambiar roles y debe estar asociado a un empleado. El rol `admin` requiere el código `ECOTECH_CODIGO_ADMIN`; cambiar roles y eliminar usuarios son acciones exclusivas de `admin`.

Los empleados solo pueden consultar sus propias horas registradas, registrar horas a su propio nombre y generar su propio reporte. `admin` y `rrhh` pueden crear proyectos, asignar empleados a proyectos, registrar horas de cualquier empleado y consultar los registros generales. Las verificaciones de permiso se aplican tanto al mostrar el menú como al ejecutar la opción, por lo que escribir un número oculto no permite saltarse la restricción.

La opción `Gestionar departamentos` permite crear departamentos y, mediante un submenú, asignar o cambiar el departamento de un empleado. Esta opción está disponible para `admin` y `rrhh`.

La salida inicial esperada es:

```text
Base de datos conectada: ecotech_solutions.db
=== ECOTECH SOLUTIONS ===
```

## Configuración segura (Unidad 3)

Los datos sensibles no se escriben en el código fuente. `main.py` carga el archivo `.env` con `python-dotenv` sin sobrescribir variables ya definidas en el sistema, y expone `obtener_codigo_rol()` y `verificar_codigo_rol()`; esta última compara con `hmac.compare_digest` para evitar fugas por tiempo de respuesta.

| Variable | Uso |
|---|---|
| `ECOTECH_CODIGO_ADMIN` | Código exigido para registrar una cuenta `admin`. |
| `ECOTECH_CODIGO_RRHH` | Código exigido para registrar una cuenta `rrhh`. |
| `ECOTECH_DB_PATH` | Ruta opcional de la base SQLite. |
| `OPENWEATHER_API_KEY` | Llave de OpenWeatherMap para el servicio de clima. |
| `ECOTECH_CLAVE_CIFRADO` | Clave Fernet con la que se cifran dirección, teléfono y salario en la base. Si se pierde, esos datos no se pueden recuperar. |

Los datos personales del empleado (dirección, teléfono, fecha de contrato y salario) solo se muestran a `admin` y `rrhh`; el listado que ven los empleados omite esos campos.

### Cifrado de datos personales

`CifradorDatos` (en `main.py`) envuelve `cryptography.fernet.Fernet` (AES-128-CBC con HMAC-SHA256, IV aleatorio por valor). Dirección, teléfono y salario se cifran antes de cada `INSERT`/`UPDATE` y se descifran al leer (`fila_a_empleado()`, `listar_empleados()`); en `ecotech_solutions.db` solo existen tokens `gAAAAA…`. RUT, nombre y correo se mantienen en claro porque se usan como identificadores y en búsquedas. Si la clave configurada no corresponde a la base, el sistema informa el problema sin exponer datos; si una base anterior contiene valores en texto plano, `inicializar_bd()` los cifra al arrancar.

`.env` está en `.gitignore`; `.env.example` documenta las variables sin valores. Para la entrega comprimida se debe incluir un `.env` con los códigos acordados por el equipo.

## Consumo de servicios externos (Unidad 3)

`servicios_externos.py` concentra el acceso a APIs y no depende de la interfaz.

- `ClienteHTTP` envuelve `requests.Session` con HTTPS obligatorio, `timeout` explícito, un reintento ante timeout o errores 5xx, y traducción de cada código HTTP (401/403, 404, 429, 5xx) y de los errores de red a `ErrorServicioExterno`, cuyo mensaje es apto para el usuario y nunca incluye la URL, los parámetros ni la llave.
- `IServicioExterno` es la abstracción común; `ServicioClima` la implementa consultando OpenWeatherMap (`/weather`, unidades métricas, idioma español). La llave se lee de `OPENWEATHER_API_KEY` al construir el servicio y se envía solo como parámetro de la petición.
- La respuesta se valida antes de usarse: se exigen `main.temp`, `main.humidity` y `weather[0].description` con tipos correctos y rangos plausibles; cualquier desviación se rechaza con un mensaje genérico.
- `validar_ciudad()` acepta únicamente letras, espacios y guiones (2 a 60 caracteres); la entrada se envía mediante `params=` de `requests`, nunca concatenada en la URL.
- Los detalles técnicos se registran con `logging` en `ecotech.log` (excluido del repositorio); la consola solo muestra el mensaje sanitizado. Los errores de interpretación (JSON inválido, campos faltantes) se registran con traceback (`logging.exception`); los errores de `requests` se registran solo por tipo, porque sus mensajes incluyen la URL completa con la llave.

Cada proyecto puede tener una ciudad (`proyectos.ciudad`, agregada mediante migración automática en `inicializar_bd()`). La opción `Consultar clima de un proyecto` muestra temperatura, humedad y descripción para apoyar la planificación.

`ServicioIndicadores` implementa la misma abstracción sobre mindicador.cl (API pública sin llave) y devuelve un `Indicador` con el último valor de la serie, su fecha y la moneda que representa. Solo se aceptan los códigos de la lista blanca `INDICADORES_PERMITIDOS` (`dolar`, `euro`, `uf`); cualquier otro texto se rechaza antes de salir a la red, porque la API responde 500 ante códigos desconocidos y eso se confundiría con una caída del servicio.

El cálculo de pagos vive en el núcleo: `sumar_horas_empleado()` totaliza `registros_tiempo`, `calcular_tarifa_hora()` convierte el salario mensual del empleado en valor hora con la fórmula de la Dirección del Trabajo (sueldo / 30 × 7 / 44 horas semanales) y `calcular_pago()` (en `main.py`) convierte horas × valor hora en CLP y luego a la moneda del indicador, validando que horas, tarifa y tipo de cambio sean positivos. Un empleado sin salario registrado no puede tener pago calculado. El resultado es un `Pago` inmutable con ambos montos y el valor de cambio usado, de modo que la conversión sea trazable.

### Persistencia local y continuidad

Cada consulta exitosa se guarda en SQLite (`consultas_clima` e `indicadores`, con `fecha_consulta`). `consultar_con_respaldo()` envuelve a cualquier servicio: si la API responde, persiste el dato y lo devuelve; si lanza `ErrorServicioExterno`, busca el último registro guardado para esa ciudad o indicador y lo devuelve marcado como respaldo, junto con el motivo del fallo. Solo si tampoco existe respaldo se propaga el error. La interfaz muestra un aviso con la fecha del dato guardado, de modo que el usuario sabe que no es información en tiempo real. Así, una caída del servicio externo no interrumpe la planificación ni el cálculo de pagos.

## Validaciones realizadas

- Compilación de `main.py` con `py -3 -m py_compile`.
- Diagnóstico del editor sin errores.
- Instanciación de las entidades principales.
- Verificación de las relaciones entre departamento, empleado, proyecto y registro de tiempo.
- Verificación de que las relaciones no agreguen duplicados.
- Inicialización de un esquema SQLite en una base temporal en memoria.
- Prueba de registro, consulta, actualización y eliminación de empleados.
- Prueba de registro, consulta, actualización y eliminación de departamentos, proyectos, usuarios y registros de tiempo.
- Prueba de persistencia de proyectos, asignaciones y registros de tiempo.
- Prueba del menú conectado a la base de datos local.
- Prueba de registro, login y roles con contraseñas almacenadas mediante PBKDF2.
- Validación del RUT chileno con normalización, cálculo del dígito verificador y rechazo de formatos inválidos.
- Validación interactiva de usuarios: cada campo inválido muestra un mensaje y se repite sin reiniciar el formulario.
- Nombres y apellidos aceptan únicamente letras y espacios, incluidos caracteres acentuados; se rechazan números y símbolos.
- Un error posterior al RUT no obliga a ingresar nuevamente el RUT ya validado.
- Cálculo del dígito verificador expresado con ramas `if/elif/else` para facilitar su revisión.
- Mensaje de validación de departamentos centralizado en una constante para evitar literales duplicados.
- Mensajes de menú y consulta de empleado centralizados en constantes de `interfaz.py`; eliminados el import y la función sin uso.
- Verificación de que los códigos de rol se leen desde `.env`, que un código faltante produce un mensaje claro sin exponer valores y que ningún secreto queda escrito en el código fuente.
- Pruebas del servicio de clima con respuestas simuladas (`unittest.mock`): 200, 401, 404, 429, 500 con reintento, timeout, sin conexión, cuerpo no JSON y JSON con campos faltantes o fuera de rango; ningún mensaje al usuario contiene la llave.
- Verificación de la migración de `proyectos.ciudad` sobre una base antigua, del guardado y actualización de la ciudad, del rechazo de ciudades con números o símbolos y de la opción de menú 15.
- Pruebas del servicio de indicadores con respuestas simuladas (serie vacía, valor no numérico, valor negativo, fecha futura, cuerpo vacío) y con una consulta real a mindicador.cl; validación de la lista blanca de indicadores; cálculo de pago con redondeo a dos decimales y rechazo de horas, tarifas o tipos de cambio no positivos; la opción de cálculo de pago está restringida a `admin` y `rrhh` y bloqueada si el empleado no tiene horas.
- Pruebas del respaldo local: una consulta exitosa se persiste; ante error de conexión, timeout o 5xx se devuelve el último dato guardado (el más reciente si hay varios) con aviso y fecha; sin respaldo el error se propaga con mensaje limpio; el respaldo sobrevive al cierre y reapertura de la base; la lista blanca se aplica también al leer el respaldo; las opciones de clima, indicador y pago muestran el aviso de respaldo.
- Verificación de que el menú se numera de forma consecutiva y ordenada para `admin` (1-16), `rrhh` (1-14) y `empleado`, y de que un número no visible para el rol se responde con `Opcion no valida.` sin ejecutar nada.
- Suites `test_nucleo.py` (19) y `test_servicios_externos.py` (28) en verde; cifrado verificado sobre una copia de la base real (la fila guardada solo contiene tokens y la interfaz la muestra descifrada); migración probada además sobre una copia de la base real (2 empleados, 4 usuarios) sin pérdida de filas ni claves foráneas inválidas; consulta real a OpenWeatherMap con la llave activa (`Santiago: 16.98 °C, humedad 63%, nubes`) y a mindicador.cl.
- Revisión de mantenibilidad SonarQube tras la Unidad 3: literales centralizados, `datetime` con zona horaria, sin parámetros ni `assert` sueltos en los ayudantes de prueba, complejidad cognitiva bajo el umbral, una sola llamada dentro de cada `assertRaises`, `assertAlmostEqual` para montos y `logging.exception` en los `except` donde el traceback no expone secretos.
- Prueba de persistencia completa después de cerrar y reabrir una base SQLite temporal.
- Verificación de que los roles `empleado` y `rrhh` quedan vinculados a una ficha en `empleados`.
- Verificación de filtros de horas y reportes por empleado.
- Verificación de menús diferenciados para `admin`, `rrhh` y `empleado`.
- Verificación de generación automática de usuarios y uso del segundo apellido ante duplicidad.
- Verificación de que eliminar un usuario elimina su empleado y asignación asociada, sin eliminar el proyecto.
- Verificación de que un empleado solo ve sus propios registros en `Ver mis horas registradas` y no puede crear proyectos, asignar personas ni registrar horas a nombre de otro RUT.
- Limpieza de `ecotech_solutions.db`, conservando el esquema y dejando sus tablas vacías.

## Registro de cambios y uso de IA

`VALIDACION_IA.md` registra cada cambio relevante, las decisiones técnicas, el apoyo utilizado de herramientas de IA y las pruebas realizadas. El código generado o sugerido por IA se revisa y ajusta antes de considerarlo parte de la solución final.

## Material privado de defensa

`defensa_oral.py` contiene un guion de apoyo para la defensa de Maximiliano y Logan.
Es material local, está excluido mediante `.git/info/exclude` y no forma parte del
producto que se sube al repositorio.
