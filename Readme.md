# EcoTechSolutions — Sistema de Gestión Interna

Aplicación de consola en **Python 3** con **SQLite** que gestiona empleados, departamentos, proyectos y registros de tiempo de EcoTech Solutions, con autenticación por roles, cifrado de datos personales, informes exportables y consumo de servicios externos (clima e indicadores económicos).

Proyecto de la asignatura **TI3V21 Programación Orientada a Objeto Seguro** (INACAP). Autores: **Logan Silva** y **Maximiliano Montoya**.

| | |
|---|---|
| Lenguaje / BD | Python 3.10+ · `sqlite3` (librería estándar) |
| Dependencias | `requests`, `python-dotenv`, `cryptography` |
| Pruebas | **111 automatizadas** (`tests/test_nucleo.py` 71 · `tests/test_servicios_externos.py` 36 · `tests/test_documentacion.py` 4), sin red, en verde |
| Modelo | `docs/uml.mmd` / `docs/uml.png` — el código coincide con el diagrama |
| Trazabilidad | `VALIDACION_IA.md`: 60 cambios documentados, mapa por criterio de la rúbrica e inventario de fragmentos apoyados por IA |

## Índice

1. [Resumen para la evaluación](#1-resumen-para-la-evaluación)
2. [Inicio rápido](#2-inicio-rápido)
3. [Funcionalidades y menú](#3-funcionalidades-y-menú)
4. [Arquitectura y correspondencia con el UML](#4-arquitectura-y-correspondencia-con-el-uml)
5. [Cumplimiento por unidad](#5-cumplimiento-por-unidad)
6. [Seguridad](#6-seguridad)
7. [Servicios externos](#7-servicios-externos)
8. [Pruebas automatizadas](#8-pruebas-automatizadas)
9. [Decisiones técnicas destacadas](#9-decisiones-técnicas-destacadas)
10. [Uso de IA y registro de cambios](#10-uso-de-ia-y-registro-de-cambios)
11. [Anexo: verificaciones realizadas](#11-anexo-verificaciones-realizadas)

---

## 1. Resumen para la evaluación

| Unidad | Qué se evalúa | Estado | Dónde verlo |
|---|---|---|---|
| **1** | Requisitos del sistema (registro de empleados, departamentos, proyectos, tiempo, informes, seguridad) | ✅ 11/11 requisitos | [§5.1](#51-unidad-1-requisitos-del-sistema) |
| **2** | 2.1.1 UML→código · 2.1.2 POO · 2.1.3 BD y CRUD · 2.1.4 errores · 2.1.5 validación de IA | ✅ 5/5 criterios | [§5.2](#52-unidad-2-implementación-orientada-a-objetos) |
| **3** | 3.1.1 APIs · 3.1.2 autenticación y validación · 3.1.3 errores en servicios · 3.1.4 ajuste con IA | ✅ 4/4 criterios | [§5.3](#53-unidad-3-servicios-externos-y-seguridad) |

En una frase por unidad:

- **U1**: las cuatro entidades tienen CRUD completo desde el menú, con gerente de departamento, descripción de tareas, asignación/desasignación a proyectos, informes de las cuatro entidades a archivo, cifrado de datos personales y contraseñas con política.
- **U2**: `main.py` implementa el UML con `dataclass`, abstracción (`IExportador`, `IServicioExterno`), herencia y polimorfismo; SQLite con claves foráneas, consultas parametrizadas y rollback; toda entrada validada y todo error capturado sin interrumpir el programa.
- **U3**: `servicios_externos.py` consume OpenWeatherMap y mindicador.cl con `requests`, valida entradas y respuestas, traduce cada fallo HTTP o de red a mensajes sin datos sensibles, mantiene un respaldo local y calcula pagos en moneda extranjera.

## 2. Inicio rápido

> **¿Viene a evaluar el proyecto?** `docs/CREDENCIALES_PRUEBA.md` trae la configuración lista, seis cuentas con sus contraseñas, una base de datos con datos ficticios ya cargados y un recorrido de prueba por cada criterio de la rúbrica.

**Para probar el sistema con los datos ya cargados** (lo que necesita quien evalúa):

```powershell
py -3 -m pip install -r requirements.txt
copy .env.demo .env
py -3 main.py
```

`.env.demo` trae los códigos de rol, la base de demostración del repositorio y su clave de cifrado. Las cuentas están en `docs/CREDENCIALES_PRUEBA.md`.

**Para partir de una base vacía y propia:**

```powershell
py -3 -m pip install -r requirements.txt
copy .env.example .env
py -3 -c "import main; print(main.generar_clave_cifrado())"   # pegar el resultado en ECOTECH_CLAVE_CIFRADO
py -3 main.py
```

`.env` necesita cuatro valores (ver [§6.1](#61-configuración-segura-env)): `ECOTECH_CODIGO_ADMIN`, `ECOTECH_CODIGO_RRHH`, `OPENWEATHER_API_KEY` y `ECOTECH_CLAVE_CIFRADO`. La entrega comprimida incluye el `.env` del equipo.

**Primer inicio.** El programa crea `ecotech_solutions.db` con sus tablas y ofrece `2. Registrar administrador inicial`: el primer usuario es siempre `admin` (exige `ECOTECH_CODIGO_ADMIN`) y su contraseña debe tener al menos 8 caracteres con letras y números. Como toda cuenta pertenece a una persona de la empresa, también se pide su ficha de empleado (RUT, cargo, dirección, teléfono, fecha de contrato y salario); el correo institucional se genera a partir del nombre de usuario. El nombre de usuario se genera con la inicial del nombre y el primer apellido (por ejemplo `lsilva`). Desde entonces las cuentas se crean únicamente dentro del sistema por `admin` o `rrhh` (opción 14). La opción `0` cierra el programa.

**Pruebas.**

```powershell
py -3 -m unittest discover -s tests -t .
```

## 3. Funcionalidades y menú

Tres roles: `admin`, `rrhh` (requiere código y ficha de empleado; gestiona todo salvo roles y eliminación de cuentas) y `empleado` (solo sus propias horas e informes). Las verificaciones de permiso se aplican al construir el menú **y** al ejecutar la opción: escribir un número oculto responde `Opcion no valida.` sin ejecutar nada.

| N.º | Opción | Roles |
|---|---|---|
| 1 | Gestionar departamentos: crear, editar nombre, eliminar, asignar o cambiar gerente, asignar o cambiar el departamento de un empleado | admin, rrhh |
| 2 | Listar o buscar departamentos por nombre (Enter lista todos) | todos |
| 3 | Gestionar empleados: editar ficha (Enter conserva cada valor; el correo institucional se informa y no se edita), eliminar | admin, rrhh |
| 4 | Listar o buscar empleados: `admin` y `rrhh` buscan por RUT, nombre o apellido y ven la ficha personal; un `empleado` busca por nombre o apellido y ve enmascarado el RUT de los demás | todos |
| 5 | Gestionar proyectos: crear, editar, eliminar, asignar y desasignar empleados | admin, rrhh |
| 6 | Listar proyectos | todos |
| 7 | Registrar horas trabajadas con descripción de la tarea (los empleados, solo las propias) | todos |
| 8 | Ver registros de tiempo (los empleados, solo los propios) | todos |
| 9 | Editar o eliminar registros de tiempo (los empleados, solo los propios) | todos |
| 10 | Generar informe de horas, empleados, departamentos o proyectos, en texto o CSV, guardado en `informes/` (los empleados, solo el de sus horas) | todos |
| 11 | Consultar clima de la ciudad de un proyecto (OpenWeatherMap si hay llave; si no, Open-Meteo, que no la exige) | todos |
| 12 | Consultar indicador económico: dólar, euro o UF (mindicador.cl) | todos |
| 13 | Calcular pago de un empleado en moneda extranjera | admin, rrhh |
| 14 | Crear usuario con su ficha de empleado (RUT, cargo, dirección, teléfono, contrato y salario), cualquiera sea el rol; el usuario y el correo institucional se generan solos | admin, rrhh |
| 15 | Listar usuarios | admin, rrhh |
| 16 | Cambiar rol de usuario | admin |
| 17 | Eliminar usuario | admin |
| 0 | Salir | todos |

Comportamientos que conviene conocer al probar:

- **Usuario y correo automáticos**: el nombre de usuario se forma con la inicial del nombre y el primer apellido (`Logan Silva` → `lsilva`) y el correo se deriva de él (`lsilva@ecotech.cl`). Ninguno se escribe a mano, y ambos se normalizan sin tildes ni ñ para que se puedan escribir en cualquier teclado; al terminar, el registro muestra usuario, correo y RUT de la ficha. El correo tampoco se edita después: es una regla de la empresa, y al editar la ficha se informa como dato fijo.
- **RUT**: se pide con el formato `12345678-5` (cuerpo, guion y dígito verificador); el sistema normaliza puntos y espacios y rechaza un dígito verificador incorrecto. En el listado, un `empleado` ve el RUT de sus compañeros como `****5678-5` y el suyo completo.
- **Pausa antes de volver**: tras cada opción el sistema espera un Enter (`Presione Enter para volver al menu...`), de modo que el listado, el informe o el mensaje de error se puedan leer antes de que el menú se redibuje.
- **Los submenús se repiten**: dentro de `Gestionar …`, `Editar o eliminar registros` o `Generar informe` se pueden encadenar varias operaciones, incluso si una falla, y se vuelve al menú principal con `0. Volver`.
- **Edición campo por campo**: cada campo muestra su valor actual `[así]`; Enter lo conserva; un valor inválido repite solo ese campo, nunca el formulario completo.
- **Eliminaciones confirmadas** (`s/n`) e informadas: eliminar un proyecto borra sus asignaciones y horas; eliminar un empleado borra también su cuenta; un departamento con empleados no se puede eliminar; desasignar de un proyecto **conserva** las horas ya registradas.
- **Búsqueda** parcial sin distinguir mayúsculas; `%` y `_` se tratan como texto.
- **Informes** en pantalla y en `informes/informe_de_<entidad>_<fecha>_<hora>.txt|csv`. El de empleados omite dirección, teléfono y salario (ver [§9](#9-decisiones-técnicas-destacadas)).
- **Datos externos**: si la API falla, el sistema muestra el último dato guardado con un aviso y su fecha.

## 4. Arquitectura y correspondencia con el UML

```text
Ecotech_solutions/
├── Readme.md                       esta guía: qué es, cómo se ejecuta y dónde está cada evidencia
├── VALIDACION_IA.md                registro técnico de los 60 cambios y del uso de IA
├── datos_ejemplo.py                genera una base de demostración con datos ficticios
├── main.py                         núcleo: modelo de dominio, validaciones, cifrado, SQLite, informes
├── servicios_externos.py           cliente HTTP, servicios de clima e indicadores, respaldo local
├── interfaz.py                     consola: menús, lectura validada de entradas, permisos por rol
├── requirements.txt · .env.example configuración
├── .env.demo                       configuración lista para la base de demostración
├── tests/
│   ├── test_nucleo.py              71 pruebas del núcleo y de los flujos de menú
│   ├── test_servicios_externos.py  36 pruebas de los servicios externos (sin red)
│   └── test_documentacion.py        4 pruebas que contrastan esta guía con el proyecto
├── docs/
│   ├── CREDENCIALES_PRUEBA.md      cuentas, configuración y recorrido para evaluar
│   ├── demo/ecotech_demo.db        base con datos ficticios, lista para usar
│   ├── uml.mmd · uml.png           modelo vigente: diagrama de clases (Mermaid y su render)
│   ├── uml_original_unidad1.png    modelo inicial entregado en la Unidad 1
│   └── evaluacion/                 rúbrica y guías de las unidades 1, 2 y 3
└── informes/                       generado en ejecución, no versionado
```

Los tres módulos de código quedan en la raíz para que el sistema se ejecute con `py -3 main.py` sin configurar rutas; las pruebas y la documentación se agrupan en `tests/` y `docs/`.

`main.py` expone su API pública mediante `__all__` y no conoce la consola; `interfaz.py` solo orquesta entradas y salidas; `servicios_externos.py` no depende de la interfaz. Las tres capas se prueban por separado.

**Modelo.** `docs/uml.mmd` integra el diagrama de la Unidad 1 (con los atributos que exigen sus requisitos) y las clases de la Unidad 3; `docs/uml.png` es su render en mermaid.live, y `docs/uml_original_unidad1.png` conserva el modelo inicial entregado en la Unidad 1, para contrastar ambos. Relaciones implementadas con `dataclass` y anotaciones de tipo:

- Un empleado pertenece a un departamento (0..1); un departamento tiene un empleado como gerente (0..1) y agrupa empleados.
- Empleado ↔ proyecto es muchos a muchos (tabla `empleado_proyecto`), con asignación y desasignación.
- Un registro de tiempo pertenece a un empleado y a un proyecto (composición).
- Un usuario puede estar asociado a un empleado; un proyecto puede tener una ciudad para consultar el clima.
- `Informe` toma datos de las cuatro entidades y `ServicioReportes` lo exporta con cualquier `IExportador`.
- `ServicioClima` y `ServicioIndicadores` implementan `IServicioExterno` sobre `ClienteHTTP`; producen `Clima` e `Indicador`, envueltos en `ResultadoConsulta` cuando provienen del respaldo.

Del diagrama se omiten a propósito detalles de implementación (`IExportador.codificacion`, `Informe.nombre_archivo`, las funciones `construir_informe_*`).

## 5. Cumplimiento por unidad

### 5.1 Unidad 1: requisitos del sistema

| Requisito de la guía | Implementación |
|---|---|
| Registro de empleados por RR.HH. con nombre, dirección, teléfono, correo, fecha de contrato, salario e ID automático | Opción 14; toda cuenta (también `admin`) se crea con su ficha; `empleados.id_empleado AUTOINCREMENT`; datos personales cifrados |
| Departamentos: crear, editar, buscar, eliminar; nombre y gerente | Submenú 1 y opción 2; `rut_gerente` es clave foránea a `empleados` con `ON DELETE SET NULL` |
| Un solo departamento por empleado; asignación y reasignación | Columna única `id_departamento`; submenú 1 → 5 |
| Registro de tiempo con fecha, horas y descripción, ligado a empleado y proyecto | Opción 7; `descripcion_tarea` (hasta 200 caracteres); exige asignación previa al proyecto |
| Proyectos: crear, editar, eliminar (nombre, descripción, fecha de inicio) | Submenú 5 |
| Asignar y desasignar empleados de proyectos | Submenú 5 → 4 y 5; `desasignar_empleado_de_proyecto()` |
| Informes de empleados, proyectos, departamentos y registros, exportables a PDF o Excel | Opción 10: `Informe` + `ExportadorPDF` (texto alineado, `.txt`) y `ExportadorExcel` (CSV con BOM) guardados en `informes/` |
| Autenticación robusta con contraseñas seguras y autorización por módulo | PBKDF2-SHA256 con sal; política de 8+ caracteres con letras y números; menú y ejecución verificados por rol |
| Datos personales cifrados | `CifradorDatos` (Fernet) sobre dirección, teléfono y salario |
| Validación rigurosa de entradas | Validadores por campo, RUT con dígito verificador, SQL parametrizado, comodines escapados |
| POO, clases para las cuatro entidades, herencia y polimorfismo, base de datos, interfaz | `main.py`, `IExportador` / `IServicioExterno`, SQLite, consola |

### 5.2 Unidad 2: implementación orientada a objetos

| Criterio | Evidencia |
|---|---|
| **2.1.1** Estructura de clases desde el UML validado | `Departamento`, `Empleado`, `Proyecto`, `RegistroTiempo`, `Usuario`, `Informe`, `Pago`, exportadores y servicios en `main.py`/`servicios_externos.py`; operaciones de dominio `asignar_*`, `desasignar_*`, `registrar_tiempo()`, `calcular_pago()`. El código coincide con `uml.mmd`. |
| **2.1.2** Principios POO | Encapsulamiento: `Usuario._contrasena` con propiedad que no expone el valor y `actualizar_contrasena()` validada. Abstracción y herencia: `IExportador` → `ExportadorPDF`/`ExportadorExcel`; `IServicioExterno` → `ServicioClima`/`ServicioIndicadores`. Polimorfismo: `ServicioReportes` y `consultar_con_respaldo()` trabajan con cualquier implementación. Reutilización: `ejecutar_submenu()`, `leer_o_conservar()`, validadores compartidos entre alta y edición. |
| **2.1.3** Librería oficial y CRUD | `sqlite3` con `PRAGMA foreign_keys = ON`, filas por nombre, migraciones automáticas en `inicializar_bd()`. Registro, consulta, actualización y eliminación de las cinco entidades, todas accesibles desde el menú; consultas parametrizadas; decorador `@revertir_si_falla` con rollback. |
| **2.1.4** Errores y validaciones | `try/except` en la conexión inicial, en cada opción del menú y en el acceso; `ValueError` con mensajes claros para texto vacío, correo, RUT, teléfono, montos, fechas, horas (0-24], descripción y contraseña; `EOFError`/`KeyboardInterrupt` cierran la sesión sin traceback. |
| **2.1.5** Validación crítica del código de IA | `VALIDACION_IA.md`: 60 cambios con decisión adoptar/modificar/descartar y su justificación, más un **inventario por fragmento** al inicio del archivo. Hallazgos propios de la revisión: actualizaciones que eludían las validaciones, propiedad que exponía la contraseña, `serie[-1]` que tomaba el dato más antiguo, borrado accidental de `__all__`. |

### 5.3 Unidad 3: servicios externos y seguridad

| Criterio | Evidencia |
|---|---|
| **3.1.1** Consumo de APIs con librerías oficiales | `requests.Session` en `ClienteHTTP`; OpenWeatherMap (`/weather`, métrico, español), Open-Meteo (geocodificación más pronóstico, sin llave) y mindicador.cl (`/api/{codigo}`); JSON validado en tipo y rango (temperatura, humedad, descripción; valor, fecha, moneda); datos usados en las opciones 11, 12 y 13. |
| **3.1.2** Autenticación y validación de entradas | Login PBKDF2 con rechazo de credenciales vacías; política de contraseñas; RUT ajeno enmascarado para el rol `empleado`; `validar_ciudad()` (letras, espacios y guiones) y lista blanca `INDICADORES_PERMITIDOS`; llaves y códigos solo en `.env`; `hmac.compare_digest`; solo usuarios autenticados llegan al menú. |
| **3.1.3** Manejo de errores en servicios externos | 401/403, 404, 429, 5xx, otros códigos, timeout, sin conexión, cuerpo no JSON y respuestas > 1 MB → `ErrorServicioExterno` con mensaje genérico (sin URL ni llave); un reintento ante 5xx/timeout; respaldo local con aviso; el menú captura y continúa. Registro técnico en `ecotech.log` sin secretos. |
| **3.1.4** Ajuste de seguridad con apoyo de IA | Cambios 27-34: se descartaron valores por defecto para secretos, `except Exception` genérico, `str(error)` al usuario, peticiones sin `timeout`, caché con expiración; se agregaron límite de tamaño, HTTPS obligatorio y logging sin llave (verificado por prueba). |

## 6. Seguridad

### 6.1 Configuración segura (`.env`)

`main.py` carga `.env` con `python-dotenv` sin sobrescribir variables del sistema. `.env` está en `.gitignore`; `.env.example` documenta las variables sin valores.

| Variable | Uso |
|---|---|
| `ECOTECH_CODIGO_ADMIN` | Código exigido para registrar una cuenta `admin`. |
| `ECOTECH_CODIGO_RRHH` | Código exigido para registrar una cuenta `rrhh`. |
| `OPENWEATHER_API_KEY` | Llave de OpenWeatherMap para el servicio de clima. |
| `ECOTECH_CLAVE_CIFRADO` | Clave Fernet para dirección, teléfono y salario. Si se pierde, esos datos no se recuperan. |
| `ECOTECH_DB_PATH` | Opcional: ruta de la base SQLite. |

Si falta un código de rol, el sistema lo informa sin revelar ningún valor. La comparación de códigos usa `hmac.compare_digest`.

### 6.2 Autenticación y autorización

- Contraseñas con **PBKDF2-SHA256, sal aleatoria y 120 000 iteraciones**; nunca en texto plano. La entrada se enmascara con asteriscos.
- **Política**: mínimo 8 caracteres con letras y números, aplicada en `generar_hash_contrasena()` (único punto por el que pasa toda contraseña persistida), en `Usuario.actualizar_contrasena()` y en el formulario. Los códigos de rol no están sujetos a ella porque son secretos de configuración.
- El **primer usuario** es siempre `admin`; después no existe autoregistro: crear cuentas es función de RR.HH. dentro del sistema.
- Cada opción del menú tiene un permiso en una sola tabla (`construir_opciones_menu()`), de la que se derivan tanto el listado como la ejecución.

### 6.3 Cifrado de datos personales

`CifradorDatos` envuelve `cryptography.fernet.Fernet` (AES-128-CBC + HMAC-SHA256, IV aleatorio por valor). Dirección, teléfono y salario se cifran antes de cada `INSERT`/`UPDATE` y se descifran al leer; en la base solo existen tokens `gAAAAA…`. RUT, nombre y correo permanecen en claro porque son identificadores y se usan en búsquedas. Una clave incorrecta produce un mensaje claro sin exponer datos; valores heredados en texto plano se cifran automáticamente al iniciar. Los datos personales solo se muestran a `admin` y `rrhh`.

### 6.4 Enmascarado del RUT

`enmascarar_rut()` oculta el **cuerpo** del RUT y deja a la vista sus últimos cuatro dígitos y el verificador (`12345678-5` → `****5678-5`). Se enmascara el cuerpo y no el dígito verificador porque este se calcula desde el cuerpo con el algoritmo módulo 11: ocultarlo no protegería nada, mientras que el cuerpo es lo que identifica a la persona. Los últimos dígitos quedan visibles para que cada quien reconozca su propia ficha.

Se aplica solo a quien no tiene permisos de gestión: `admin` y `rrhh` ven los RUT completos porque los escriben para asignar departamentos, registrar horas o calcular pagos. Además, un `empleado` solo puede buscar por nombre o apellido (`listar_empleados(..., buscar_por_rut=False)`): si pudiera buscar por RUT, bastaría escribir uno para confirmarlo y el enmascarado sería solo visual. El enmascarado es de presentación; la base guarda el RUT completo, que sigue siendo clave foránea de asignaciones y registros.

### 6.5 Validación de entradas

RUT chileno con dígito verificador; nombres solo con letras; correo con formato básico; teléfono con patrón; montos y horas positivos (horas ≤ 24); fechas ISO y fecha de fin no anterior al inicio; descripción de tarea ≤ 200 caracteres; ciudad e indicador validados antes de salir a la red. Toda consulta SQL es parametrizada y las búsquedas escapan los comodines de `LIKE`.

## 7. Servicios externos

- **`ClienteHTTP`**: `requests.Session`, HTTPS obligatorio, `timeout` de 8 s (20 s para mindicador.cl, que responde entre 5 y 8 s), un reintento ante timeout o 5xx, límite de 1 MB por respuesta, traducción de códigos HTTP y errores de red a `ErrorServicioExterno`. Los mensajes al usuario nunca incluyen URL, parámetros ni llave; el detalle técnico va a `ecotech.log` (los errores de `requests` se registran solo por tipo, porque su texto incluye la URL completa con la llave).
- **`ServicioClima`** (OpenWeatherMap): temperatura, humedad y descripción de la ciudad del proyecto, con rangos plausibles verificados. Necesita `OPENWEATHER_API_KEY`.
- **`ServicioClimaPublico`** (Open-Meteo, sin llave ni registro): la misma información para quien no tenga credencial. Resuelve el nombre de la ciudad a coordenadas con la API de geocodificación del proveedor y traduce el código WMO del estado del tiempo a texto (`describir_tiempo()`). `obtener_servicio_clima()` elige uno u otro según haya llave configurada, de modo que el sistema funciona recién clonado sin publicar ninguna credencial.
- **`ServicioIndicadores`** (mindicador.cl, sin llave): último valor de la serie (`serie[0]`, orden descendente) para `dolar`, `euro` o `uf`; otros códigos se rechazan antes de la red porque la API responde 500 y se confundiría con una caída.
- **Cálculo de pago**: `sumar_horas_empleado()` × `calcular_tarifa_hora()` (fórmula de la Dirección del Trabajo: sueldo / 30 × 7 / 44 h) → CLP → moneda del indicador. Resultado inmutable `Pago` con ambos montos y el tipo de cambio usado.
- **Respaldo local**: cada consulta exitosa se guarda en `consultas_clima` / `indicadores`; ante un fallo, `consultar_con_respaldo()` devuelve el último dato con aviso y fecha; solo sin respaldo se propaga el error.

## 8. Pruebas automatizadas

```powershell
py -3 -m unittest discover -s tests -t .          # las 85
py -3 -m unittest -v tests.test_nucleo            # una suite, con detalle
```

| Suite | Pruebas | Cubre |
|---|---|---|
| `tests/test_nucleo.py` | 71 | Migraciones sobre bases antiguas (empleados, gerente, descripción), ficha del empleado y valor hora, cifrado en reposo (solo tokens en la base, clave incorrecta, valores heredados), acceso (admin inicial, autoregistro cerrado, credenciales vacías), CRUD completo desde el menú (edición con Enter, eliminaciones confirmadas, desasignación, registros propios), informes (validación, exportadores, archivo, exclusión de datos cifrados), política de contraseñas y búsquedas. |
| `tests/test_documentacion.py` | 4 | Contrasta esta guía con el proyecto: que cada cambio de `VALIDACION_IA.md` esté en su índice y en orden, que las cifras de cambios y de pruebas citadas aquí sean las reales y que los archivos mencionados existan. |
| `tests/test_servicios_externos.py` | 36 | Sesión HTTP simulada con `unittest.mock`: 200, 401, 404, 429, 500 con reintento, timeout, sin conexión, JSON inválido o fuera de rango, respuesta demasiado grande, validación de entradas, cálculo de pago y respaldo local. Para el servicio sin llave: geocodificación, traducción de códigos WMO, ciudad inexistente y elección automática de servicio. Dos pruebas verifican que la llave no aparece ni en mensajes ni en el registro técnico. |

Los flujos de menú se prueban con `input()` simulado y salida capturada; las bases son SQLite en memoria; la clave de cifrado de pruebas es independiente del `.env`.

## 9. Decisiones técnicas destacadas

Cada una está justificada en el cambio indicado de `VALIDACION_IA.md`.

| Decisión | Por qué | Cambio |
|---|---|---|
| Gerente como clave foránea a `empleados` (`ON DELETE SET NULL`) y no texto libre | Evita duplicar nombres y define qué pasa si el gerente se elimina | 39 |
| Cifrar dirección, teléfono y salario, pero no RUT, nombre ni correo | Los identificadores se usan en `UNIQUE` y búsquedas; Fernet con IV aleatorio los haría inutilizables | 37 |
| Clave Fernet en `.env`, no derivada de la contraseña del admin | Cambiar la contraseña dejaría ilegible la base; hay varios administradores | 37 |
| Desasignar de un proyecto conserva las horas | Son trabajo realizado, necesario para informes y pagos; solo se impide registrar horas nuevas | 40 |
| El informe de empleados omite los datos cifrados | Un archivo en `informes/` queda fuera del cifrado en reposo | 41 |
| Lista blanca de indicadores | mindicador.cl responde 500 a códigos desconocidos, indistinguible de una caída | 29 |
| Segundo servicio de clima sin llave en vez de publicar la credencial | El sistema funciona recién clonado y ninguna credencial queda expuesta en el repositorio | 60 |
| Respaldo solo ante fallo, sin caché con expiración | El usuario debe saber cuándo el dato no es en tiempo real | 30 |
| Valor hora con la fórmula de la Dirección del Trabajo (44 h) | Convención legal vigente en Chile, en lugar de dividir por 180 | 36 |
| Primer usuario forzado a `admin`; sin autoregistro posterior | La guía asigna el registro a RR.HH.; sin un admin nadie podría crear cuentas | 38 |
| Política de contraseñas aplicada al persistir, no en el constructor | `Usuario` también representa la sesión y filas con hash | 42 |
| Enmascarar el **cuerpo** del RUT y no el dígito verificador | El verificador se recalcula desde el cuerpo con módulo 11: ocultarlo no protegería nada | 50 |
| Un `empleado` no puede buscar por RUT | Si pudiera, bastaría escribir uno para confirmarlo y el enmascarado sería solo visual | 50 |
| Timeout por servicio (20 s para indicadores, 8 s para clima) | Medidos: mindicador.cl responde entre 5 y 8 s y OpenWeatherMap en 0,7 s | 53 |
| Correo derivado del nombre de usuario y no editable | Son el mismo identificador en dos formatos; editar uno los desalinearía | 54, 55 |
| Clave de cifrado publicada solo para la base de demostración | Sus datos son ficticios; la clave de trabajo del equipo sigue fuera del repositorio | 56 |

## 10. Uso de IA y registro de cambios

El desarrollo fue incremental: cada cambio se implementó, se probó y se documentó en `VALIDACION_IA.md` con objetivo, implementación, revisión técnica y validación. El apoyo de IA (asistente de programación operado desde el editor) se usó para proponer borradores que el equipo ejecutó, probó y luego **adoptó, modificó o descartó** con criterio técnico; ningún fragmento se incorporó sin ejecutarse. La sección **"Inventario de fragmentos apoyados por IA"** al inicio de ese archivo identifica, fragmento por fragmento, el origen, la decisión y el criterio aplicado (indicador 2.1.5).

`defensa_oral.py` es material local de apoyo para la defensa; está excluido del repositorio mediante `.git/info/exclude`.

## 11. Anexo: verificaciones realizadas

Además de las suites automatizadas, durante el desarrollo se verificó manualmente:

- Compilación (`py -3 -m py_compile`) y `ruff --select F` sin nombres indefinidos en cada cambio; análisis de SonarCloud sin incidencias abiertas (literales centralizados, complejidad cognitiva bajo el umbral, `datetime` con zona horaria, reglas S1192, S3776, S5778, S5906, S8572).
- Migraciones y cifrado probados sobre copias de la base real del equipo, sin pérdida de filas ni claves foráneas inválidas.
- Consulta real a OpenWeatherMap con la llave activa (`Santiago: 16.98 °C, humedad 63%, nubes`) y a mindicador.cl.
- Recorrido completo del menú sobre una base nueva: registro del administrador, creación y edición de departamento, empleado y proyecto, registro y edición de horas, desasignación, informes y eliminaciones con confirmación hasta dejar las tablas vacías.
- Menús diferenciados y numeración consecutiva para `admin` (1-17), `rrhh` (1-15) y `empleado`; un número oculto para el rol no ejecuta nada.
- Generación automática de nombres de usuario con uso del segundo apellido ante duplicidad; vinculación obligatoria de `empleado` y `rrhh` a una ficha.
- La base de datos no se versiona: cada integrante la genera en el primer inicio; el equipo debe compartir la misma `ECOTECH_CLAVE_CIFRADO` si comparte una base.
