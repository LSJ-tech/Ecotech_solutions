# Validacion de cambios apoyados por IA

## Cambio 1 - Criterio 2.1.1 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** traducir el modelo UML inicial a clases Python.

### Implementacion

Se crearon las clases `Departamento`, `Empleado`, `Proyecto`, `Usuario` y `RegistroTiempo` mediante `dataclass`. Se representaron las relaciones del modelo con referencias entre objetos y listas de empleados, proyectos y registros de tiempo.

También se agregaron las operaciones `asignar_empleado_a_departamento()`, `asignar_empleado_a_proyecto()` y `registrar_tiempo()` para mantener las relaciones bidireccionales del modelo.

### Revisión técnica

La estructura fue revisada contra `uml.png`. Se utilizó IA como apoyo para proponer la estructura, pero se eligieron manualmente los atributos, las relaciones y la forma de evitar duplicados en las listas.

### Validación pendiente

La compilación se ejecutó correctamente con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`. El editor tampoco reportó errores en el archivo.

La prueba de instanciación y asociación se ejecutó correctamente y mostró `Prueba 2.1.1 OK`. Se verificó que el empleado quedara relacionado con su departamento y proyecto, que el proyecto quedara en la lista del empleado y que el registro de tiempo quedara asociado al empleado y al proyecto.

El primer intento de prueba produjo un error del cargador dinámico porque el módulo no había sido registrado en `sys.modules`; se corrigió el arnés de prueba y se repitió con resultado exitoso. No fue necesario modificar el modelo por ese error.

## Cambio 2 - Documentación inicial del proyecto

**Fecha:** 2026-09-12
**Archivo creado:** `README.md`
**Objetivo:** documentar el trabajo de la Unidad 2 para facilitar su revisión académica.

### Implementación

Se creó un README con el objetivo del proyecto, el estado actual del criterio 2.1.1, la correspondencia entre las clases y el UML, la estructura de archivos, los requisitos de ejecución, las validaciones realizadas y las próximas etapas de la Unidad 2.

### Revisión técnica

El documento fue redactado a partir de la guía de aprendizaje, la rúbrica, `uml.png` y el código vigente de `main.py`. Se evitó presentar como terminadas las funcionalidades que todavía no han sido implementadas, como la base de datos, el CRUD y el manejo avanzado de errores.

### Validación

Se verificará que el README sea visible desde la carpeta del proyecto, que sus comandos correspondan al estado actual del código y que los criterios pendientes estén diferenciados del criterio 2.1.1 ya validado.

## Cambio 3 - Criterio 2.1.2 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** aplicar encapsulamiento, abstracción, herencia, polimorfismo y reutilización de código.

### Implementación

La clase `Usuario` ahora mantiene la contraseña en `_contrasena` y ofrece la propiedad `contrasena` junto con `actualizar_contrasena()`. La actualización rechaza contraseñas vacías mediante `ValueError`.

También se creó la abstracción `IExportador` con el método `exportar()`. `ExportadorPDF` y `ExportadorExcel` heredan de ella y generan formatos diferentes. `ServicioReportes` recibe cualquier `IExportador`, demostrando polimorfismo y evitando duplicar la lógica de generación.

### Revisión técnica

La implementación se contrastó con el UML y con el criterio 2.1.2 de la rúbrica. Se utilizó IA como apoyo para proponer alternativas de abstracción, pero se conservaron únicamente las estructuras compatibles con las responsabilidades del modelo.

### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.2 OK`.
- Verificación de contraseña privada, actualización controlada y rechazo de valores vacíos.
- Verificación de `ServicioReportes` con `ExportadorPDF` y `ExportadorExcel`.

## Cambio 4 - Criterio 2.1.3 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** integrar una base de datos SQLite y operaciones CRUD coherentes con el UML.

### Implementación

Se incorporó `sqlite3`, sin dependencias externas, con una ruta predeterminada en `ecotech_solutions.db`. `SCHEMA_SQL` crea las tablas de departamentos, empleados, proyectos, usuarios, registros de tiempo y la tabla intermedia `empleado_proyecto`.

Se implementaron `conectar_bd()`, `inicializar_bd()`, `guardar_departamento()`, `guardar_empleado()`, `listar_empleados()`, `actualizar_empleado()`, `eliminar_empleado()`, `guardar_proyecto()`, `asignar_empleado_proyecto_bd()` y `guardar_registro_tiempo()`.

Las operaciones utilizan consultas parametrizadas, claves foráneas y confirmación explícita mediante `commit()`. Las pruebas pueden usar `:memory:` para evitar generar archivos temporales.

### Revisión técnica

La estructura de tablas y relaciones se contrastó con `uml.png` y con el requisito 2.1.3 de la rúbrica. Se utilizó IA como apoyo para proponer el esquema inicial, pero se revisaron manualmente las claves primarias, las claves foráneas, la tabla intermedia y los parámetros de las consultas.

### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.3 SQLite OK`.
- Verificación de creación del esquema SQLite en memoria.
- Verificación del CRUD de empleados.
- Verificación de proyecto, asignación empleado-proyecto y registro de horas.

## Cambio 5 - Cierre del criterio 2.1.3 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** completar el CRUD requerido por la rúbrica para las entidades persistentes del sistema.

### Implementación

Se agregaron operaciones de consulta, actualización y eliminación para departamentos, proyectos, usuarios y registros de tiempo. El CRUD de empleados ya existente se mantuvo y se amplió con las operaciones para todas las entidades principales.

Además, `guardar_proyecto()` ahora actualiza `proyecto.id_proyecto` con el identificador generado por SQLite. Esto garantiza que los registros de tiempo utilicen el ID real de la base de datos y no un valor inicial del objeto.

Las consultas de usuarios no devuelven la columna de contraseña. Las relaciones entre empleado y proyecto se mantienen mediante la tabla intermedia `empleado_proyecto`.

### Revisión técnica

Se revisó que cada operación use consultas parametrizadas y que las operaciones devuelvan un resultado booleano o identificador que permita saber si se ejecutaron sobre una entidad existente. La prueba usa una base SQLite en memoria para no mezclar datos de validación con la base local del proyecto.

### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.3 CRUD completo OK`.
- CRUD verificado para departamentos, empleados, proyectos, usuarios y registros de tiempo.
- Verificación de propagación del ID generado por SQLite en `Proyecto`.
- Verificación de que las consultas de usuarios no expongan contraseñas.

## Cambio 6 - Criterio 2.1.4 de la Unidad 2

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** validar los datos de entrada y rechazar estados inválidos del modelo.

### Implementación

Se agregó validación de campos obligatorios, identificadores, correos, fechas, horas trabajadas y credenciales. Las entidades lanzan `ValueError` con mensajes descriptivos cuando reciben datos inválidos.

### Revisión técnica

Las validaciones se incorporaron en `__post_init__()` para que se ejecuten al crear las entidades. Se mantuvieron las relaciones del modelo, el CRUD existente y la abstracción de los exportadores.

### Validación

- Se creó correctamente un empleado, un proyecto y un registro válido.
- Se rechazó un RUT vacío.
- Se rechazó un correo sin formato básico válido.
- Se rechazó una fecha de fin anterior a la fecha de inicio.
- Se rechazaron horas fuera del rango permitido de 0 a 24.
- La prueba final mostró `Validaciones 2.1.4 OK`.

## Cambio 7 - Criterio 2.1.5 de la Unidad 2

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** revisar críticamente el código apoyado por IA y corregir riesgos verificables.

### Hallazgo y corrección

La revisión comprobó que `actualizar_empleado()` y `actualizar_registro_tiempo()` podían guardar datos inválidos directamente en SQLite, aunque las entidades rechazaban esos datos al crearse. Se agregaron validaciones reutilizables para textos, fechas y horas en las operaciones CRUD de actualización.

### Riesgo residual

La contraseña de `Usuario` todavía se almacena en texto plano y puede leerse mediante la propiedad `contrasena`. Esto mantiene la compatibilidad con la implementación académica actual, pero no es adecuado para producción. La mejora recomendada es almacenar un hash seguro y agregar una operación de verificación, antes de implementar autenticación real.

### Validación

- Se reprodujo el defecto: una actualización aceptaba un nombre vacío, un correo inválido y horas superiores a 24.
- Se verificó que las mismas actualizaciones ahora lanzan `ValueError`.
- La prueba mostró `Revisión 2.1.5: validaciones CRUD OK`.
- `main.py` compiló correctamente con `py -3 -m py_compile main.py`.

## Cambio 8 - Menú conectado a SQLite

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** permitir ejecutar el sistema mediante un menú funcional y persistir los datos en SQLite.

### Implementación

Se agregó un menú de consola que abre `ecotech_solutions.db`, inicializa las tablas y permite crear y consultar departamentos, empleados y proyectos, asignar empleados, registrar horas y generar reportes.

### Validación

- Al ejecutar `py -3 main.py` se creó correctamente `ecotech_solutions.db`.
- Se probó la salida mediante la opción `0`.
- Se completó un flujo con departamento, empleado, proyecto, asignación y registro de 4 horas.
- Se generó correctamente un reporte CSV desde los registros almacenados.
- La base local permanece excluida del control de versiones mediante `.gitignore`.
- Se creó y listó un usuario asociado a un empleado sin mostrar su contraseña.

## Cambio 9 - Autenticación y roles

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** proteger el acceso al sistema y separar las funciones administrativas.

### Implementación

Se agregó un acceso inicial con login y registro. El primer usuario puede registrarse como `admin` o `empleado`; el rol `admin` requiere el código temporal `1234`. La tabla `usuarios` incorpora la columna `rol` mediante una migración compatible con bases existentes.

Las contraseñas nuevas se almacenan usando PBKDF2-SHA256 con sal. Las contraseñas antiguas se aceptan durante la migración y se convierten a hash después de un login correcto. Los usuarios inactivos no pueden iniciar sesión.

La gestión de usuarios y la opción de cambiar roles están restringidas al rol `admin`. Los usuarios empleados pueden utilizar las funciones operativas, pero no administrar cuentas.

### Validación

- Se verificó la creación de usuarios con hash, sin guardar la contraseña original.
- Se verificó login correcto y rechazo de contraseña incorrecta.
- Se verificó la migración automática de un usuario antiguo en texto plano a PBKDF2.
- Se verificó la incorporación de la columna `rol` en la base SQLite existente.
- No se realizó `commit` ni `push`; los cambios permanecen locales.

### Observación de seguridad

El código `1234` es temporal y débil, tal como se solicitó para esta etapa. Debe reemplazarse por una variable de entorno o un mecanismo de configuración segura antes de usar el sistema en producción.

## Cambio 10 - Revisión crítica 2.1.5: protección de credenciales

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** corregir el riesgo detectado en la revisión de seguridad del criterio 2.1.5.

### Hallazgo

La propiedad pública `contrasena` de la clase `Usuario` devolvía el texto original de la contraseña, lo que permitía exponer credenciales sensibles al leer el objeto directamente. Aunque el sistema usaba hash al guardar en la base de datos, la lectura del atributo público era un riesgo verificable y no compatible con principios de seguridad básicos.

### Implementación

Se modificó la clase `Usuario` para que:

- la propiedad `contrasena` devuelva un valor enmascarado (`********`) y no el secreto real;
- la contraseña real permanezca en un atributo privado (`_contrasena`), usado únicamente en validaciones internas y persistencia;
- se agreguen los métodos `obtener_contrasena_interna()` y `verificar_contrasena()` para controlar el acceso a la contraseña sin exponerla;
- la persistencia use `usuario.obtener_contrasena_interna()` antes de generar el hash.

### Revisión técnica

La corrección se validó con una prueba directa en Python: al instanciar un usuario y consultar `usuario.contrasena`, el valor devuelto ya no es la contraseña real. La comprobación se realizó con una instancia de prueba y se confirmó que la validación del login se mantiene usando `verificar_contrasena()`.

### Validación

- Prueba de reproducciòn: `Usuario(1, 'ana', 'supersecreta').contrasena` devolvía la contraseña real antes del cambio.
- Verificación posterior: retorna `********` y no el valor original.
- Compilación correcta con `py -3 -m py_compile main.py`.
- Resultado de la revisión: `Criterio 2.1.5 reforzado con corrección de fuga de credenciales.`
