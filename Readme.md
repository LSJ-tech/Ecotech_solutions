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
- Seguridad: PBKDF2 para contraseñas y entrada enmascarada con asteriscos para datos sensibles.
- Roles: `admin`, `rrhh` y `empleado`, con menús y permisos diferenciados. Los empleados solo ven y registran sus propias horas; crear proyectos y asignar personas es exclusivo de `admin` y `rrhh`.
- Calidad: correcciones aplicadas para duplicidad, literales repetidos, código sin uso y complejidad cognitiva; sin avisos de mantenibilidad SonarQube en la interfaz.
- Unidad 3: en desarrollo. Paso 1: configuración segura mediante `.env` y `requirements.txt`. Paso 2: consumo de la API de clima (OpenWeatherMap) con `requests`, validación de entradas, manejo de errores HTTP y de red, y ciudad asociada a cada proyecto. Pendiente: indicadores económicos, cálculo de pagos y caché local.

## Requisitos

- Python 3.10 o superior.
- Dependencias declaradas en `requirements.txt`: `requests` (consumo de APIs) y `python-dotenv` (carga de `.env`).
- SQLite se utiliza mediante la librería estándar `sqlite3`.

## Estructura del proyecto

```text
Ecotech_solutions/
├── main.py
├── servicios_externos.py
├── interfaz.py
├── requirements.txt
├── .env.example
├── Readme.md
├── VALIDACION_IA.md
├── Rubrica.pdf
├── TI3V21_U2_U3_ES02_GUÍA.docx
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

El diagrama original se encuentra en `uml.png`.

## Estado de los criterios

### Criterio 2.1.1: implementación del modelo UML

**Estado: completado.**

El archivo `main.py` contiene las siguientes clases:

- `Departamento`: identifica un departamento y mantiene sus empleados.
- `Empleado`: representa a un trabajador, su departamento, proyectos y registros de tiempo.
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

## Ejecución

Desde la carpeta del proyecto, la primera vez:

```powershell
py -3 -m pip install -r requirements.txt
copy .env.example .env
```

Luego editar `.env` y definir `ECOTECH_CODIGO_ADMIN` y `ECOTECH_CODIGO_RRHH` (códigos exigidos para registrar cuentas `admin` y `rrhh`). Para ejecutar:

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
- Crear automáticamente la ficha del empleado para los roles `empleado` y `rrhh`.
- Permitir que `admin` y `rrhh` gestionen departamentos, usuarios y reportes.
- Permitir que solo un administrador cambie roles o elimine otras cuentas.
- Generar reportes en formato de texto tipo PDF o CSV tipo Excel.
- Consultar el clima actual de la ciudad de un proyecto (opción 15, disponible para todos los roles).

Para cerrar el programa se selecciona la opción `0`. La base de datos se guarda localmente y no se sube a GitHub porque está incluida en `.gitignore`.

En el primer inicio se debe registrar el primer usuario. Para seleccionar el rol `admin` o `rrhh` se solicita el código secreto definido en `.env`; si la variable no está configurada, el sistema lo informa sin revelar ningún valor. Los usuarios nuevos se guardan con hash PBKDF2; las credenciales antiguas almacenadas en texto plano se rechazan y deben restablecerse de forma segura.

Las contraseñas y códigos secretos se muestran como asteriscos mientras se escriben. Las contraseñas se almacenan mediante PBKDF2 y no en texto plano.

La interfaz centraliza mensajes y consultas reutilizadas, y separa el flujo de inicio de sesión en funciones auxiliares para mantener una complejidad cognitiva baja.

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

`.env` está en `.gitignore`; `.env.example` documenta las variables sin valores. Para la entrega comprimida se debe incluir un `.env` con los códigos acordados por el equipo.

## Consumo de servicios externos (Unidad 3)

`servicios_externos.py` concentra el acceso a APIs y no depende de la interfaz.

- `ClienteHTTP` envuelve `requests.Session` con HTTPS obligatorio, `timeout` explícito, un reintento ante timeout o errores 5xx, y traducción de cada código HTTP (401/403, 404, 429, 5xx) y de los errores de red a `ErrorServicioExterno`, cuyo mensaje es apto para el usuario y nunca incluye la URL, los parámetros ni la llave.
- `IServicioExterno` es la abstracción común; `ServicioClima` la implementa consultando OpenWeatherMap (`/weather`, unidades métricas, idioma español). La llave se lee de `OPENWEATHER_API_KEY` al construir el servicio y se envía solo como parámetro de la petición.
- La respuesta se valida antes de usarse: se exigen `main.temp`, `main.humidity` y `weather[0].description` con tipos correctos y rangos plausibles; cualquier desviación se rechaza con un mensaje genérico.
- `validar_ciudad()` acepta únicamente letras, espacios y guiones (2 a 60 caracteres); la entrada se envía mediante `params=` de `requests`, nunca concatenada en la URL.
- Los detalles técnicos se registran con `logging` en `ecotech.log` (excluido del repositorio); la consola solo muestra el mensaje sanitizado.

Cada proyecto puede tener una ciudad (`proyectos.ciudad`, agregada mediante migración automática en `inicializar_bd()`). La opción `Consultar clima de un proyecto` muestra temperatura, humedad y descripción para apoyar la planificación.

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
