# Validación de cambios apoyados por IA

Registro técnico del proyecto EcoTechSolutions (TI3V21, INACAP). Documenta cada cambio relevante del código con la misma estructura: **objetivo**, **implementación**, **revisión técnica** (qué propuso la IA o qué alternativa se evaluó, y por qué se adoptó, modificó o descartó) y **validación** (pruebas ejecutadas y su resultado). Los cambios se numeran en orden cronológico y se agrupan por fase del proyecto.

Cómo usar este documento:

- Para saber **qué parte del código nació de un borrador de IA** y qué se hizo con él: [Inventario de fragmentos apoyados por IA](#inventario-de-fragmentos-apoyados-por-ia).
- Para encontrar **la evidencia de un criterio de la rúbrica**: [Mapa por criterio](#mapa-por-criterio-de-la-rúbrica).
- Para seguir **la historia completa**: el [índice](#índice) enlaza cada cambio, agrupado en cinco fases.

## Índice

- **Fase 1 - Unidad 2: modelo, POO, SQLite y calidad inicial (cambios 1 a 16 y anexos)**
  - [Cambio 1 - Criterio 2.1.1 de la Unidad 2](#cambio-1---criterio-211-de-la-unidad-2)
  - [Cambio 2 - Documentación inicial del proyecto](#cambio-2---documentación-inicial-del-proyecto)
  - [Cambio 3 - Criterio 2.1.2 de la Unidad 2](#cambio-3---criterio-212-de-la-unidad-2)
  - [Cambio 4 - Criterio 2.1.3 de la Unidad 2](#cambio-4---criterio-213-de-la-unidad-2)
  - [Cambio 5 - Cierre del criterio 2.1.3 de la Unidad 2](#cambio-5---cierre-del-criterio-213-de-la-unidad-2)
  - [Cambio 6 - Criterio 2.1.4 de la Unidad 2](#cambio-6---criterio-214-de-la-unidad-2)
  - [Cambio 7 - Criterio 2.1.5 de la Unidad 2](#cambio-7---criterio-215-de-la-unidad-2)
  - [Cambio 8 - Menú conectado a SQLite](#cambio-8---menú-conectado-a-sqlite)
  - [Cambio 9 - Autenticación y roles](#cambio-9---autenticación-y-roles)
  - [Cambio 10 - Separación de la interfaz de consola](#cambio-10---separación-de-la-interfaz-de-consola)
  - [Cambio 11 - API pública del núcleo](#cambio-11---api-pública-del-núcleo)
  - [Material privado - Guion de defensa oral (no versionado)](#material-privado---guion-de-defensa-oral-no-versionado)
  - [Cambio 12 - Eliminación de duplicidad de la interfaz](#cambio-12---eliminación-de-duplicidad-de-la-interfaz)
  - [Cambio 13 - Ajustes de seguridad y complejidad señalados por SonarQube](#cambio-13---ajustes-de-seguridad-y-complejidad-señalados-por-sonarqube)
  - [Cambio 14 - Correcciones de legibilidad detectadas en `main.py`](#cambio-14---correcciones-de-legibilidad-detectadas-en-mainpy)
  - [Cambio 15 - Entrada segura de credenciales en consola](#cambio-15---entrada-segura-de-credenciales-en-consola)
  - [Cambio 16 - Correcciones S1192 y S3776 en la interfaz](#cambio-16---correcciones-s1192-y-s3776-en-la-interfaz)
  - [Anexo histórico A - Integridad de registros de tiempo en SQLite](#anexo-histórico-a---integridad-de-registros-de-tiempo-en-sqlite)
  - [Anexo histórico B - Revisión crítica 2.1.5: protección de credenciales](#anexo-histórico-b---revisión-crítica-215-protección-de-credenciales)
  - [Anexo histórico C - Revisión de validación de RUT](#anexo-histórico-c---revisión-de-validación-de-rut)
  - [Anexo histórico D - Validación completa del RUT chileno](#anexo-histórico-d---validación-completa-del-rut-chileno)
  - [Anexo histórico E - Manejo de errores y excepciones](#anexo-histórico-e---manejo-de-errores-y-excepciones)
  - [Anexo histórico F - Cobertura completa de errores SQLite en el menú](#anexo-histórico-f---cobertura-completa-de-errores-sqlite-en-el-menú)
- **Fase 2 - Roles, permisos y validación interactiva (cambios 17 a 26)**
  - [Cambio 17 - Registro automático de empleado y usuario](#cambio-17---registro-automático-de-empleado-y-usuario)
  - [Cambio 18 - Roles RRHH y permisos por rol](#cambio-18---roles-rrhh-y-permisos-por-rol)
  - [Cambio 19 - Gestión de departamentos](#cambio-19---gestión-de-departamentos)
  - [Cambio 20 - Privacidad de horas y reportes](#cambio-20---privacidad-de-horas-y-reportes)
  - [Cambio 21 - Generación automática de usuarios](#cambio-21---generación-automática-de-usuarios)
  - [Cambio 22 - Limpieza y revisión de SQLite](#cambio-22---limpieza-y-revisión-de-sqlite)
  - [Cambio 23 - Eliminación de usuario y conservación de proyectos](#cambio-23---eliminación-de-usuario-y-conservación-de-proyectos)
  - [Cambio 24 - Validación interactiva de datos de usuario](#cambio-24---validación-interactiva-de-datos-de-usuario)
  - [Cambio 25 - Permisos por rol en proyectos y registros de tiempo](#cambio-25---permisos-por-rol-en-proyectos-y-registros-de-tiempo)
  - [Cambio 26 - Avisos de mantenibilidad SonarQube en la interfaz](#cambio-26---avisos-de-mantenibilidad-sonarqube-en-la-interfaz)
- **Fase 3 - Unidad 3: servicios externos y seguridad (cambios 27 a 34)**
  - [Cambio 27 - Unidad 3, paso 1: configuración segura con variables de entorno](#cambio-27---unidad-3-paso-1-configuración-segura-con-variables-de-entorno)
  - [Cambio 28 - Unidad 3, paso 2: consumo de la API de clima](#cambio-28---unidad-3-paso-2-consumo-de-la-api-de-clima)
  - [Cambio 29 - Unidad 3, paso 3: indicadores económicos y cálculo de pagos](#cambio-29---unidad-3-paso-3-indicadores-económicos-y-cálculo-de-pagos)
  - [Cambio 30 - Unidad 3, paso 4: persistencia local y respaldo ante fallos](#cambio-30---unidad-3-paso-4-persistencia-local-y-respaldo-ante-fallos)
  - [Cambio 31 - Menú principal en una sola tabla y renumeración](#cambio-31---menú-principal-en-una-sola-tabla-y-renumeración)
  - [Cambio 32 - Unidad 3, paso 5: revisión de seguridad final y pruebas automatizadas](#cambio-32---unidad-3-paso-5-revisión-de-seguridad-final-y-pruebas-automatizadas)
  - [Cambio 33 - Avisos de mantenibilidad SonarQube tras la Unidad 3](#cambio-33---avisos-de-mantenibilidad-sonarqube-tras-la-unidad-3)
  - [Cambio 34 - Reglas S5778, S5906 y S8572 de SonarQube](#cambio-34---reglas-s5778-s5906-y-s8572-de-sonarqube)
- **Fase 4 - Alineación con los requisitos de la Unidad 1 (cambios 35 a 43)**
  - [Cambio 35 - Revisión contra la rúbrica y la guía de la Unidad 1; modelo UML unificado](#cambio-35---revisión-contra-la-rúbrica-y-la-guía-de-la-unidad-1-modelo-uml-unificado)
  - [Cambio 36 - Alineación con la Unidad 1, paso 1: ficha completa del empleado](#cambio-36---alineación-con-la-unidad-1-paso-1-ficha-completa-del-empleado)
  - [Cambio 37 - Alineación con la Unidad 1, paso 2: cifrado de datos personales](#cambio-37---alineación-con-la-unidad-1-paso-2-cifrado-de-datos-personales)
  - [Cambio 38 - Alineación con la Unidad 1, paso 3: registro de cuentas restringido](#cambio-38---alineación-con-la-unidad-1-paso-3-registro-de-cuentas-restringido)
  - [Cambio 39 - Alineación con la Unidad 1, paso 4: gerente y descripción de tareas](#cambio-39---alineación-con-la-unidad-1-paso-4-gerente-y-descripción-de-tareas)
  - [Cambio 40 - Alineación con la Unidad 1, paso 5: CRUD completo desde el menú](#cambio-40---alineación-con-la-unidad-1-paso-5-crud-completo-desde-el-menú)
  - [Cambio 41 - Alineación con la Unidad 1, paso 6: informes exportados a archivo](#cambio-41---alineación-con-la-unidad-1-paso-6-informes-exportados-a-archivo)
  - [Cambio 42 - Alineación con la Unidad 1, paso 7: política de contraseñas](#cambio-42---alineación-con-la-unidad-1-paso-7-política-de-contraseñas)
  - [Cambio 43 - Alineación con la Unidad 1, paso 8: búsquedas](#cambio-43---alineación-con-la-unidad-1-paso-8-búsquedas)
- **Fase 5 - Documentación y cierre (cambios 44 a 48)**
  - [Cambio 44 - Inventario de fragmentos apoyados por IA](#cambio-44---inventario-de-fragmentos-apoyados-por-ia)
  - [Cambio 45 - Reorganización del Readme orientada a la evaluación](#cambio-45---reorganización-del-readme-orientada-a-la-evaluación)
  - [Cambio 46 - Reorganización de este registro por fases y por criterio](#cambio-46---reorganización-de-este-registro-por-fases-y-por-criterio)
  - [Cambio 47 - Estructura del repositorio](#cambio-47---estructura-del-repositorio)
  - [Cambio 48 - Ficha de empleado obligatoria para toda cuenta](#cambio-48---ficha-de-empleado-obligatoria-para-toda-cuenta)

## Mapa por criterio de la rúbrica

Para localizar la evidencia de cada criterio sin recorrer el registro completo.

| Criterio | Cambios donde se documenta |
|---|---|
| 2.1.1 Implementación del UML en Python | 1, 35 (modelo unificado `uml.mmd`), 36 a 41 (alineación clase por clase) |
| 2.1.2 Principios de POO | 3, 10, 11, 12 (separación de capas y API pública), 40 (`ejecutar_submenu`, `leer_o_conservar`), 41 (`Informe`, exportadores) |
| 2.1.3 Base de datos y CRUD | 4, 5, 8, 22, 23, 36 (migración `id_empleado`), 39 (migraciones por `ALTER TABLE`), 40 (CRUD completo en el menú), 43 (búsquedas) |
| 2.1.4 Errores y validaciones | 6, Anexos A, C, D, E y F, 24, 25, 42 (política de contraseñas) |
| 2.1.5 Validación crítica del código de IA | 7, Anexo B, 32, 34, 44 (inventario por fragmento) y la sección "Revisión técnica" de cada cambio |
| 3.1.1 Consumo de APIs con librerías oficiales | 28 (clima), 29 (indicadores y pagos) |
| 3.1.2 Autenticación y validación de entradas | 9, 15, 18, 25, 27 (secretos en `.env`), 37 (cifrado), 38 (registro restringido), 42 (contraseñas), 43 (comodines de `LIKE`) |
| 3.1.3 Manejo de errores en servicios externos | 28, 30 (respaldo local), 32 (revisión de seguridad), 33 y 34 (registro técnico sin llave) |
| 3.1.4 Ajuste de seguridad con apoyo de IA | 27 a 34, 37 |

## Inventario de fragmentos apoyados por IA

Esta tabla responde al indicador 2.1.5 ("identificar con transparencia qué fragmentos del código fueron apoyados o generados preliminarmente mediante herramientas de IA"). La herramienta usada en todo el proyecto fue un asistente de programación con IA (Claude, Anthropic) operado desde el editor. El método fue siempre el mismo: el equipo describe el requisito, la IA propone un borrador, el equipo lo ejecuta, lo prueba y decide adoptarlo, modificarlo o descartarlo; la decisión y su justificación quedan en el cambio indicado. Ningún fragmento se incorporó sin ejecutarse y sin pruebas.

Leyenda: **Adoptado** = el borrador se integró con ajustes menores de estilo; **Modificado** = se cambió la lógica por un criterio técnico; **Descartado** = la propuesta se rechazó y se implementó otra solución; **Propio** = escrito por el equipo, con la IA solo como revisor.

| Módulo / fragmento | Cambio | Decisión | Criterio aplicado |
|---|---|---|---|
| `main.py`: dataclasses `Departamento`, `Empleado`, `Proyecto`, `RegistroTiempo` y operaciones de dominio | 1 | Modificado | La IA propuso la estructura; atributos, relaciones bidireccionales y control de duplicados en listas se definieron a mano contra `uml.png` (coherencia con el modelo). |
| `main.py`: `IExportador`, `ExportadorPDF`, `ExportadorExcel`, `ServicioReportes` | 3 | Modificado | La IA propuso varias alternativas de abstracción; se conservó solo la compatible con las responsabilidades del modelo (abstracción, herencia y polimorfismo sin duplicar la generación). |
| `main.py`: `Usuario` con `_contrasena`, propiedad y `verificar_contrasena()` | 3, 7, 9 | Modificado | El borrador exponía la contraseña en la propiedad; se ocultó tras `obtener_contrasena_interna()` y se pasó a hash PBKDF2 con sal (seguridad). |
| `main.py`: `SCHEMA_SQL`, `conectar_bd()`, `inicializar_bd()`, `revertir_si_falla` | 4, 5, Anexo E | Modificado | La IA propuso el esquema inicial; claves primarias, foráneas y la tabla intermedia se revisaron a mano contra el UML; consultas parametrizadas y rollback ante error SQLite (integridad, estabilidad). |
| `main.py`: `actualizar_*` y `eliminar_*` | 4, 7 | Modificado | Hallazgo de la revisión crítica: las actualizaciones eludían las validaciones del modelo; se reutilizaron los validadores (seguridad de datos). |
| `interfaz.py`: menú de consola, lectores `leer_*` y flujo de acceso | 8, 10, 12, 24, 31 | Modificado | Borradores de IA reescritos para separar interfaz de núcleo, eliminar duplicidad y definir el menú en una sola tabla (mantenibilidad; avisos SonarQube). |
| `interfaz.py`: `leer_contrasena()` (`getpass`, luego asteriscos con `msvcrt` en Windows) | 15 y ajustes posteriores | Adoptado | Propuesta de IA verificada en Windows (`msvcrt`) y con `getpass` en otros sistemas; evita mostrar credenciales en pantalla. |
| `main.py`: `obtener_codigo_rol()` / `verificar_codigo_rol()` con `.env` y `hmac.compare_digest` | 27 | Descartado (parcial) | La IA propuso valores por defecto cuando falta la variable; se rechazó para no dejar secretos en el código; la comparación en tiempo constante sí se adoptó. |
| `servicios_externos.py`: `ClienteHTTP` | 28, 32 | Modificado | Del borrador se descartaron `except Exception` genérico, `str(error)` al usuario (fuga de URL con llave) y ausencia de `timeout`; se agregaron reintento, límite de 1 MB y HTTPS obligatorio. |
| `servicios_externos.py`: `ServicioClima`, `ServicioIndicadores` | 28, 29 | Modificado | El borrador usaba `serie[-1]` (dato más antiguo); la exploración real mostró orden descendente y se corrigió a `serie[0]`; lista blanca de indicadores por el 500 de códigos desconocidos. |
| `main.py`: `Pago` y `calcular_pago()` | 29, 36 | Modificado | La IA propuso tarifa por hora en la tabla; se reemplazó por el salario mensual y la fórmula de la Dirección del Trabajo (44 h) (coherencia con el requisito). |
| `servicios_externos.py`: `consultar_con_respaldo()` y tablas `consultas_clima`/`indicadores` | 30 | Descartado (parcial) | La IA propuso caché con expiración; se descartó y se dejó respaldo solo ante fallo, con aviso al usuario (continuidad sin ocultar el estado del servicio). |
| `test_servicios_externos.py`, `test_nucleo.py` | 32, 36-43 | Modificado | Esqueletos de prueba generados por IA y ejecutados uno a uno; varios aserts eran incorrectos (por ejemplo, esperaban ver el texto de un `input()` simulado) y se corrigieron en las pruebas, no en el código. |
| `main.py`: `CifradorDatos`, `cifrar_datos_personales()`, migración de valores heredados | 37 | Modificado | La IA proponía cifrar también nombre y correo y derivar la clave de la contraseña del admin; ambas se descartaron (identificadores y búsquedas; rotación de clave). Fernet adoptado. |
| `main.py`: `migrar_tabla_empleados()` | 36 | Descartado | La IA sugería mantener `rut` como clave primaria y añadir el ID como `UNIQUE`; se reconstruyó la tabla con `id_empleado AUTOINCREMENT` según el requisito. |
| `interfaz.py`: acceso restringido (`registrar_primer_usuario`, `hay_usuarios`) | 38 | Descartado | La IA propuso un "código de invitación" para autoregistro; se cerró el autoregistro y se dejó el registro en RR.HH. |
| `main.py`: `rut_gerente` como clave foránea con `ON DELETE SET NULL` | 39 | Descartado | La IA propuso `gerente: str` libre como en el UML de la Unidad 1; se modeló como empleado existente. |
| `main.py`: escapado CSV de la descripción | 39, 41 | Modificado | La IA concatenaba sin comillas; se aplicó el escapado estándar y luego el módulo `csv`. |
| `main.py` / `interfaz.py`: `desasignar_empleado_proyecto_bd()`, `eliminar_empleado()` con cuenta, `leer_o_conservar()`, `ejecutar_submenu()` | 40 | Modificado | Se descartó borrar las horas al desasignar y dejar la cuenta huérfana; la validación de fecha de fin se movió al lector tras detectar que perdía el formulario. |
| `main.py`: `Informe`, `construir_informe_*`, `ServicioReportes.guardar()` | 41 | Modificado | Se excluyeron dirección, teléfono y salario del informe (cifrado en reposo) y se sanitizó el nombre del archivo con fecha y hora. |
| `main.py`: `validar_contrasena()` | 42 | Modificado | La IA proponía mayúscula, minúscula y símbolo obligatorios; se fijó largo mínimo 8 con letras y dígitos, validado al persistir. |
| `main.py`: `patron_busqueda()` y filtros `LIKE ... ESCAPE` | 43 | Descartado | La IA concatenaba el texto en el `WHERE`; se usó parámetro con comodines escapados (inyección SQL). |
| Documentación: `Readme.md`, `VALIDACION_IA.md`, `uml.mmd` | 2, 35 | Propio (con apoyo) | Redactados por el equipo con la IA como redactor de borradores; cada afirmación se contrastó con el código y las pruebas antes de publicarse. |

---

## Fase 1 - Unidad 2: modelo, POO, SQLite y calidad inicial (cambios 1 a 16 y anexos)

### Cambio 1 - Criterio 2.1.1 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** traducir el modelo UML inicial a clases Python.

#### Implementación

Se crearon las clases `Departamento`, `Empleado`, `Proyecto`, `Usuario` y `RegistroTiempo` mediante `dataclass`. Se representaron las relaciones del modelo con referencias entre objetos y listas de empleados, proyectos y registros de tiempo.

También se agregaron las operaciones `asignar_empleado_a_departamento()`, `asignar_empleado_a_proyecto()` y `registrar_tiempo()` para mantener las relaciones bidireccionales del modelo.

#### Revisión técnica

La estructura fue revisada contra `uml.png`. Se utilizó IA como apoyo para proponer la estructura, pero se eligieron manualmente los atributos, las relaciones y la forma de evitar duplicados en las listas.

#### Validación

La compilación se ejecutó correctamente con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`. El editor tampoco reportó errores en el archivo.

La prueba de instanciación y asociación se ejecutó correctamente y mostró `Prueba 2.1.1 OK`. Se verificó que el empleado quedara relacionado con su departamento y proyecto, que el proyecto quedara en la lista del empleado y que el registro de tiempo quedara asociado al empleado y al proyecto.

El primer intento de prueba produjo un error del cargador dinámico porque el módulo no había sido registrado en `sys.modules`; se corrigió el arnés de prueba y se repitió con resultado exitoso. No fue necesario modificar el modelo por ese error.

### Cambio 2 - Documentación inicial del proyecto

**Fecha:** 2026-09-12
**Archivo creado:** `README.md`
**Objetivo:** documentar el trabajo de la Unidad 2 para facilitar su revisión académica.

#### Implementación

Se creó un README con el objetivo del proyecto, el estado actual del criterio 2.1.1, la correspondencia entre las clases y el UML, la estructura de archivos, los requisitos de ejecución, las validaciones realizadas y las próximas etapas de la Unidad 2.

#### Revisión técnica

El documento fue redactado a partir de la guía de aprendizaje, la rúbrica, `uml.png` y el código vigente de `main.py`. Se evitó presentar como terminadas las funcionalidades que todavía no han sido implementadas, como la base de datos, el CRUD y el manejo avanzado de errores.

#### Validación

Se verificará que el README sea visible desde la carpeta del proyecto, que sus comandos correspondan al estado actual del código y que los criterios pendientes estén diferenciados del criterio 2.1.1 ya validado.

### Cambio 3 - Criterio 2.1.2 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** aplicar encapsulamiento, abstracción, herencia, polimorfismo y reutilización de código.

#### Implementación

La clase `Usuario` ahora mantiene la contraseña en `_contrasena` y ofrece la propiedad `contrasena` junto con `actualizar_contrasena()`. La actualización rechaza contraseñas vacías mediante `ValueError`.

También se creó la abstracción `IExportador` con el método `exportar()`. `ExportadorPDF` y `ExportadorExcel` heredan de ella y generan formatos diferentes. `ServicioReportes` recibe cualquier `IExportador`, demostrando polimorfismo y evitando duplicar la lógica de generación.

#### Revisión técnica

La implementación se contrastó con el UML y con el criterio 2.1.2 de la rúbrica. Se utilizó IA como apoyo para proponer alternativas de abstracción, pero se conservaron únicamente las estructuras compatibles con las responsabilidades del modelo.

#### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.2 OK`.
- Verificación de contraseña privada, actualización controlada y rechazo de valores vacíos.
- Verificación de `ServicioReportes` con `ExportadorPDF` y `ExportadorExcel`.

### Cambio 4 - Criterio 2.1.3 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** integrar una base de datos SQLite y operaciones CRUD coherentes con el UML.

#### Implementación

Se incorporó `sqlite3`, sin dependencias externas, con una ruta predeterminada en `ecotech_solutions.db`. `SCHEMA_SQL` crea las tablas de departamentos, empleados, proyectos, usuarios, registros de tiempo y la tabla intermedia `empleado_proyecto`.

Se implementaron `conectar_bd()`, `inicializar_bd()`, `guardar_departamento()`, `guardar_empleado()`, `listar_empleados()`, `actualizar_empleado()`, `eliminar_empleado()`, `guardar_proyecto()`, `asignar_empleado_proyecto_bd()` y `guardar_registro_tiempo()`.

Las operaciones utilizan consultas parametrizadas, claves foráneas y confirmación explícita mediante `commit()`. Las pruebas pueden usar `:memory:` para evitar generar archivos temporales.

#### Revisión técnica

La estructura de tablas y relaciones se contrastó con `uml.png` y con el requisito 2.1.3 de la rúbrica. Se utilizó IA como apoyo para proponer el esquema inicial, pero se revisaron manualmente las claves primarias, las claves foráneas, la tabla intermedia y los parámetros de las consultas.

#### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.3 SQLite OK`.
- Verificación de creación del esquema SQLite en memoria.
- Verificación del CRUD de empleados.
- Verificación de proyecto, asignación empleado-proyecto y registro de horas.

### Cambio 5 - Cierre del criterio 2.1.3 de la Unidad 2

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** completar el CRUD requerido por la rúbrica para las entidades persistentes del sistema.

#### Implementación

Se agregaron operaciones de consulta, actualización y eliminación para departamentos, proyectos, usuarios y registros de tiempo. El CRUD de empleados ya existente se mantuvo y se amplió con las operaciones para todas las entidades principales.

Además, `guardar_proyecto()` ahora actualiza `proyecto.id_proyecto` con el identificador generado por SQLite. Esto garantiza que los registros de tiempo utilicen el ID real de la base de datos y no un valor inicial del objeto.

Las consultas de usuarios no devuelven la columna de contraseña. Las relaciones entre empleado y proyecto se mantienen mediante la tabla intermedia `empleado_proyecto`.

#### Revisión técnica

Se revisó que cada operación use consultas parametrizadas y que las operaciones devuelvan un resultado booleano o identificador que permita saber si se ejecutaron sobre una entidad existente. La prueba usa una base SQLite en memoria para no mezclar datos de validación con la base local del proyecto.

#### Validación

- Compilación correcta con `py -3 -m py_compile C:\Python\Ecotech_solutions\main.py`.
- Prueba funcional completada con el resultado `Prueba 2.1.3 CRUD completo OK`.
- CRUD verificado para departamentos, empleados, proyectos, usuarios y registros de tiempo.
- Verificación de propagación del ID generado por SQLite en `Proyecto`.
- Verificación de que las consultas de usuarios no expongan contraseñas.

### Cambio 6 - Criterio 2.1.4 de la Unidad 2

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** validar los datos de entrada y rechazar estados inválidos del modelo.

#### Implementación

Se agregó validación de campos obligatorios, identificadores, correos, fechas, horas trabajadas y credenciales. Las entidades lanzan `ValueError` con mensajes descriptivos cuando reciben datos inválidos.

#### Revisión técnica

Las validaciones se incorporaron en `__post_init__()` para que se ejecuten al crear las entidades. Se mantuvieron las relaciones del modelo, el CRUD existente y la abstracción de los exportadores.

#### Validación

- Se creó correctamente un empleado, un proyecto y un registro válido.
- Se rechazó un RUT vacío.
- Se rechazó un correo sin formato básico válido.
- Se rechazó una fecha de fin anterior a la fecha de inicio.
- Se rechazaron horas fuera del rango permitido de 0 a 24.
- La prueba final mostró `Validaciones 2.1.4 OK`.

### Cambio 7 - Criterio 2.1.5 de la Unidad 2

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** revisar críticamente el código apoyado por IA y corregir riesgos verificables.

#### Hallazgo y corrección

La revisión comprobó que `actualizar_empleado()` y `actualizar_registro_tiempo()` podían guardar datos inválidos directamente en SQLite, aunque las entidades rechazaban esos datos al crearse. Se agregaron validaciones reutilizables para textos, fechas y horas en las operaciones CRUD de actualización.

#### Riesgo residual

La contraseña de `Usuario` todavía se almacena en texto plano y puede leerse mediante la propiedad `contrasena`. Esto mantiene la compatibilidad con la implementación académica actual, pero no es adecuado para producción. La mejora recomendada es almacenar un hash seguro y agregar una operación de verificación, antes de implementar autenticación real.

#### Validación

- Se reprodujo el defecto: una actualización aceptaba un nombre vacío, un correo inválido y horas superiores a 24.
- Se verificó que las mismas actualizaciones ahora lanzan `ValueError`.
- La prueba mostró `Revisión 2.1.5: validaciones CRUD OK`.
- `main.py` compiló correctamente con `py -3 -m py_compile main.py`.

### Cambio 8 - Menú conectado a SQLite

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** permitir ejecutar el sistema mediante un menú funcional y persistir los datos en SQLite.

#### Implementación

Se agregó un menú de consola que abre `ecotech_solutions.db`, inicializa las tablas y permite crear y consultar departamentos, empleados y proyectos, asignar empleados, registrar horas y generar reportes.

#### Validación

- Al ejecutar `py -3 main.py` se creó correctamente `ecotech_solutions.db`.
- Se probó la salida mediante la opción `0`.
- Se completó un flujo con departamento, empleado, proyecto, asignación y registro de 4 horas.
- Se generó correctamente un reporte CSV desde los registros almacenados.
- La base local permanece excluida del control de versiones mediante `.gitignore`.
- Se creó y listó un usuario asociado a un empleado sin mostrar su contraseña.

### Cambio 9 - Autenticación y roles

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** proteger el acceso al sistema y separar las funciones administrativas.

#### Implementación

Se agregó un acceso inicial con login y registro. El primer usuario puede registrarse como `admin` o `empleado`; el rol `admin` requiere el código temporal `1234`. La tabla `usuarios` incorpora la columna `rol` mediante una migración compatible con bases existentes.

Las contraseñas nuevas se almacenan usando PBKDF2-SHA256 con sal. Las contraseñas antiguas se aceptan durante la migración y se convierten a hash después de un login correcto. Los usuarios inactivos no pueden iniciar sesión.

La gestión de usuarios y la opción de cambiar roles están restringidas al rol `admin`. Los usuarios empleados pueden utilizar las funciones operativas, pero no administrar cuentas.

#### Validación

- Se verificó la creación de usuarios con hash, sin guardar la contraseña original.
- Se verificó login correcto y rechazo de contraseña incorrecta.
- Se verificó la migración automática de un usuario antiguo en texto plano a PBKDF2.
- Se verificó la incorporación de la columna `rol` en la base SQLite existente.
- No se realizó `commit` ni `push`; los cambios permanecen locales.

#### Observación de seguridad

El código `1234` es temporal y débil, tal como se solicitó para esta etapa. Debe reemplazarse por una variable de entorno o un mecanismo de configuración segura antes de usar el sistema en producción.

### Cambio 10 - Separación de la interfaz de consola

**Fecha:** 2026-09-13
**Archivos creados o modificados:** `interfaz.py`, `main.py`, `Readme.md`
**Objetivo:** mejorar la separacion de responsabilidades antes de continuar con la Unidad 3.

#### Implementación

Se creo `interfaz.py` como punto de entrada para la interfaz de consola. El nuevo modulo concentra el login, los menus, la lectura de entradas, la presentacion de consultas y las acciones iniciadas por el usuario, reutilizando las entidades y operaciones de `main.py`.

`main.py` mantiene un lanzador compatible que delega en `interfaz.mostrar_menu()`, por lo que continua funcionando el comando anterior mientras el README documenta el nuevo punto de entrada.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizo correctamente.
- `import interfaz` finalizo correctamente con el resultado `Importacion de interfaz OK`.
- Se actualizo `Readme.md` con la nueva estructura y el comando de ejecucion.
- No se realizo commit ni push; los cambios permanecen locales.

### Cambio 11 - API pública del núcleo

**Fecha:** 2026-09-13
**Archivo modificado:** `main.py`
**Objetivo:** definir explicitamente las clases y operaciones que puede reutilizar la interfaz separada.

#### Implementación

Se agrego `__all__` a `main.py` con las entidades, validaciones y operaciones de persistencia que forman la API publica del nucleo. `interfaz.py` importa esas capacidades sin depender de una importacion global del modulo.

#### Validación

- Se comprobo que `main.__all__` contiene las operaciones necesarias para importar `interfaz`.
- Se mantuvo la compatibilidad del comando `py -3 main.py`.

### Material privado - Guion de defensa oral (no versionado)

**Fecha:** 2026-09-13
**Archivo local:** `defensa_oral.py`
**Objetivo:** preparar la defensa argumentativa de Maximiliano y Logan sin incorporar el guion al producto publicado.

#### Implementación

Se creo un script independiente con el reparto sugerido, explicaciones del modelo UML,
principios orientados a objetos, SQLite, CRUD, validaciones, autenticacion, seguridad,
separacion arquitectonica, uso responsable de IA y estado real de la Unidad 3.

#### Validación

- `py -3 -m py_compile defensa_oral.py` finalizo correctamente.
- El script se ejecuto y mostro el encabezado y el contenido inicial del guion.
- `defensa_oral.py` se agrego a `.git/info/exclude`, por lo que no sera incluido en un commit.
- No se realizo commit ni push de este material.

### Cambio 12 - Eliminación de duplicidad de la interfaz

**Fecha:** 2026-09-13
**Archivos modificados:** `main.py`, `Readme.md`
**Objetivo:** corregir la duplicidad detectada por SonarQube entre el nucleo y la interfaz.

#### Hallazgo

`main.py` y `interfaz.py` contenian dos implementaciones de las mismas funciones de consola,
incluyendo login, menus, lectura de entradas y reportes. Esto aumentaba el mantenimiento y
provocaba el reporte de codigo duplicado en SonarQube.

#### Implementación

Se eliminaron de `main.py` las funciones de interfaz duplicadas. `interfaz.py` queda como
unico modulo responsable de la consola, mientras `main.py` conserva las entidades,
validaciones, servicios, persistencia SQLite y el lanzador compatible.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizo correctamente.
- `import main` e `import interfaz` finalizaron correctamente.
- Se comprobo que `main.py` ya no expone `crear_empleado_menu`.
- Se debe repetir el analisis de SonarQube para confirmar la desaparicion de la duplicidad.

### Cambio 13 - Ajustes de seguridad y complejidad señalados por SonarQube

**Fecha:** 2026-09-13
**Archivos modificados:** `main.py`, `interfaz.py`, `Readme.md`
**Objetivo:** aplicar los hallazgos de seguridad y mantenibilidad, excepto el código temporal `1234` solicitado para el administrador inicial.

#### Implementación

- `verificar_contrasena()` ahora acepta exclusivamente hashes PBKDF2; se elimina la comparación y migración de contraseñas almacenadas en texto plano.
- La autenticación ya no escribe directamente en `usuario._contrasena` después del login.
- El menú se dividió en `ejecutar_opcion_menu()`, `mostrar_opciones_menu()` y funciones específicas de permisos y registros.
- El manejo de errores del acceso y del menú separa `ValueError`, `PermissionError` y `sqlite3.Error`.
- Se mantuvo `CODIGO_ADMIN = "1234"` sin cambios por decisión explícita para esta etapa.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizó correctamente.
- Se comprobó que un hash PBKDF2 válido autentica y que una contraseña en texto plano se rechaza.
- Se comprobó el despacho de la opción de salida del menú usando una base SQLite en memoria.
- El editor no reportó errores en `main.py` ni `interfaz.py`.

### Cambio 14 - Correcciones de legibilidad detectadas en `main.py`

**Fecha:** 2026-09-13
**Archivo modificado:** `main.py`
**Objetivo:** corregir los avisos asociados al ternario anidado y al literal repetido.

#### Implementación

- El cálculo de `digito_esperado` en `validar_rut()` ahora utiliza `if/elif/else`, evitando un ternario anidado.
- El mensaje `El nombre del departamento` se centralizó en `CAMPO_NOMBRE_DEPARTAMENTO` y se reutiliza en el CRUD y en la entidad.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizó correctamente.
- Se validó un RUT correcto y su formato normalizado.
- Se confirmó el rechazo de `12345678-0` por dígito verificador incorrecto.
- Se comprobó el valor de la constante compartida.

### Cambio 15 - Entrada segura de credenciales en consola

**Fecha:** 2026-09-13
**Archivo modificado:** `interfaz.py`
**Objetivo:** evitar que contraseñas y códigos secretos sean visibles durante su ingreso.

#### Implementación

Se incorporó `getpass()` para solicitar la contraseña durante el login, el registro de usuarios, la creación de usuarios y el código secreto del administrador. Los campos no sensibles continúan utilizando `input()`.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizó correctamente.
- Se comprobó que `interfaz.py` importa `getpass` y lo utiliza en los cuatro puntos sensibles.
- Se actualizó `Readme.md` con el comportamiento de la consola.

### Cambio 16 - Correcciones S1192 y S3776 en la interfaz

**Fecha:** 2026-09-13
**Archivo modificado:** `interfaz.py`
**Objetivo:** corregir literales duplicados y reducir la complejidad cognitiva del inicio de sesión.

#### Implementación

- Se centralizaron el mensaje de contraseña, el mensaje de empleado inexistente y la consulta SQL reutilizada.
- `iniciar_sesion()` se dividió en `registrar_primer_usuario()`, `mostrar_menu_acceso()` y `procesar_opcion_acceso()`.
- Se mantuvo la salida con la opción `0`, el registro del primer usuario y el login existente.

#### Validación

- `py -3 -m py_compile interfaz.py main.py` finalizó correctamente.
- Se comprobó que cada función auxiliar existe una sola vez.
- Se verificó la carga de la interfaz con SQLite en memoria y el procesamiento de una opción no válida.
- El editor no reportó errores en ambos módulos.
- No se realizó commit ni push de este cambio.

### Anexo histórico A - Integridad de registros de tiempo en SQLite

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** reforzar el criterio 2.1.3 evitando registros de horas sin una asignación empleado-proyecto válida.

#### Hallazgo

La tabla `empleado_proyecto` mantenía la relación muchos a muchos, pero `guardar_registro_tiempo()` solo comprobaba mediante claves foráneas que existieran el empleado y el proyecto. Era posible registrar horas aunque ambos no estuvieran relacionados.

#### Implementación

Antes de insertar en `registros_tiempo`, `guardar_registro_tiempo()` consulta la tabla `empleado_proyecto` con parámetros. Si no existe la asignación, lanza `ValueError` y no realiza la inserción.

#### Validación

- Se comprobó que un registro sin asignación empleado-proyecto es rechazado.
- Se comprobó que, después de crear la asignación, el registro de horas se guarda correctamente.
- Se verificó la compilación de `main.py` con el intérprete virtual del proyecto.

#### Resultado

La regla de integridad queda centralizada en la capa de persistencia y se aplica tanto al menú como a las llamadas directas a SQLite.

### Anexo histórico B - Revisión crítica 2.1.5: protección de credenciales

**Fecha:** 2026-09-12  
**Archivo modificado:** `main.py`  
**Objetivo:** corregir el riesgo detectado en la revisión de seguridad del criterio 2.1.5.

#### Hallazgo

La propiedad pública `contrasena` de la clase `Usuario` devolvía el texto original de la contraseña, lo que permitía exponer credenciales sensibles al leer el objeto directamente. Aunque el sistema usaba hash al guardar en la base de datos, la lectura del atributo público era un riesgo verificable y no compatible con principios de seguridad básicos.

#### Implementación

Se modificó la clase `Usuario` para que:

- la propiedad `contrasena` devuelva un valor enmascarado (`********`) y no el secreto real;
- la contraseña real permanezca en un atributo privado (`_contrasena`), usado únicamente en validaciones internas y persistencia;
- se agreguen los métodos `obtener_contrasena_interna()` y `verificar_contrasena()` para controlar el acceso a la contraseña sin exponerla;
- la persistencia use `usuario.obtener_contrasena_interna()` antes de generar el hash.

#### Revisión técnica

La corrección se validó con una prueba directa en Python: al instanciar un usuario y consultar `usuario.contrasena`, el valor devuelto ya no es la contraseña real. La comprobación se realizó con una instancia de prueba y se confirmó que la validación del login se mantiene usando `verificar_contrasena()`.

#### Validación

- Prueba de reproducciòn: `Usuario(1, 'ana', 'supersecreta').contrasena` devolvía la contraseña real antes del cambio.
- Verificación posterior: retorna `********` y no el valor original.
- Compilación correcta con `py -3 -m py_compile main.py`.
- Resultado de la revisión: `Criterio 2.1.5 reforzado con corrección de fuga de credenciales.`

### Anexo histórico C - Revisión de validación de RUT

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** identificar la necesidad de reforzar la validación de entradas sensibles.

#### Hallazgo

La revisión detectó que la validación actual solo comprueba que el RUT no esté vacío y no calcula el dígito verificador.

#### Implementación

No se modificó `main.py` en este cambio. La validación completa del RUT queda pendiente.

#### Verificación ejecutada

Se verificó en el código que `Empleado.__post_init__()` utiliza `validar_texto()` para rechazar valores vacíos, pero acepta cualquier texto no vacío.

#### Resultado

La validación avanzada del RUT se mantiene como mejora pendiente.

### Anexo histórico D - Validación completa del RUT chileno

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** validar el RUT chileno antes de crear empleados y usarlo en relaciones persistentes.

#### Implementación

Se agregó `validar_rut()`, que elimina puntos y espacios, acepta `k` o `K`, calcula el dígito verificador mediante el algoritmo chileno y devuelve el RUT en formato canónico. Los valores con formato incorrecto o dígito verificador inválido producen `ValueError`.

La validación se aplica al crear `Empleado`, actualizar o eliminar empleados, asignar proyectos y buscar empleados desde el menú.

#### Validación

- `11.111.111-1` se acepta y normaliza.
- `12.345.678-9` se rechaza por dígito incorrecto.
- `12345678-0` se rechaza por dígito incorrecto.
- `abc` y RUTs sin formato se rechazan.
- `main.py` compila correctamente y el editor no reporta errores.

#### Resultado

Los empleados y las relaciones persistidas utilizan únicamente RUTs con formato y dígito verificador válidos.

### Anexo histórico E - Manejo de errores y excepciones

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** implementar el criterio 2.1.4 mediante rollback de SQLite y cierre controlado del menú.

#### Implementación

Se agregó `revertir_si_falla()`, un decorador que ejecuta `connection.rollback()` cuando una operación de escritura produce una excepción de SQLite. Se aplicó a las operaciones de inserción, actualización, eliminación y asignación.

También se agregó manejo de errores al abrir o inicializar la base de datos y se controlan `EOFError` y `KeyboardInterrupt` para finalizar la sesión sin traceback.

#### Validación

- Una asignación con un empleado inexistente produjo `sqlite3.IntegrityError` y revirtió la operación.
- La misma conexión permitió realizar después una asignación válida.
- `main.py` compiló correctamente con el intérprete virtual del proyecto.
- El editor no reportó errores en los archivos modificados.

#### Resultado

El sistema mantiene la consistencia de las operaciones SQLite ante errores y finaliza de manera controlada cuando la entrada del usuario se interrumpe.

### Anexo histórico F - Cobertura completa de errores SQLite en el menú

**Fecha:** 2026-09-12
**Archivo modificado:** `main.py`
**Objetivo:** mejorar el criterio 2.1.4 evitando que errores SQLite distintos de `IntegrityError` finalicen el programa.

#### Hallazgo

Los manejadores del acceso y del menú principal capturaban `sqlite3.IntegrityError`, pero dejaban sin manejar otros errores de SQLite, como `sqlite3.OperationalError`.

#### Implementación

Se ampliaron ambos manejadores para capturar `sqlite3.Error`, la clase base de las excepciones SQLite. Se mantiene el rollback automático implementado en el cambio 13.

#### Validación

- Se confirmó que `sqlite3.OperationalError` pertenece a `sqlite3.Error` y queda cubierto por los manejadores.
- `main.py` compiló correctamente.
- El editor no reportó errores en los archivos modificados.

## Fase 2 - Roles, permisos y validación interactiva (cambios 17 a 26)

### Cambio 17 - Registro automático de empleado y usuario

**Fecha:** 2026-09-15  
**Archivos modificados:** `main.py`, `interfaz.py`  
**Objetivo:** evitar que una persona deba registrarse dos veces cuando crea una cuenta de empleado.

#### Implementación

Se agregó `guardar_usuario_con_empleado()`, que inserta el empleado y su usuario asociado en una sola transacción. Los roles `empleado` y `rrhh` solicitan RUT, nombre, apellidos, correo y cargo, y quedan vinculados mediante `rut_empleado`.

#### Validación

- Se confirmó que ambos registros sobreviven al cierre y reapertura de SQLite.
- Se confirmó que un error al crear el usuario revierte también el empleado.
- Se verificó la compilación de `main.py` e `interfaz.py`.

### Cambio 18 - Roles RRHH y permisos por rol

**Fecha:** 2026-09-15  
**Archivos modificados:** `main.py`, `interfaz.py`  
**Objetivo:** incorporar el rol `rrhh` con permisos de gestión diferenciados.

#### Implementación

Se agregó el rol `rrhh` a `ROLES_VALIDOS`. Su clave secreta es `12345` y su registro exige una ficha completa de empleado. `admin` conserva el código `1234`.

RR.HH. puede gestionar departamentos, usuarios, proyectos, asignaciones, horas y reportes, pero no puede cambiar roles ni eliminar usuarios. El cambio de roles y la eliminación de cuentas quedan reservados a `admin`.

#### Validación

- Se probó el guardado de una cuenta `rrhh` junto con su empleado.
- Se verificaron los menús de `admin`, `rrhh` y `empleado`.
- Se comprobó que RR.HH. no ve la opción de cambiar roles.
- Se comprobó que las funciones administrativas rechazan roles no autorizados.

### Cambio 19 - Gestión de departamentos

**Fecha:** 2026-09-15  
**Archivo modificado:** `interfaz.py`  
**Objetivo:** centralizar la gestión de departamentos en una sola opción.

#### Implementación

La opción `Gestionar departamentos` contiene un submenú para crear departamentos o asignar/cambiar el departamento de un empleado. La asignación inicial solo procede si el empleado no tiene departamento; el cambio requiere que ya tenga uno.

#### Validación

- Se comprobó la asignación y posterior cambio de departamento en SQLite.
- Se confirmó que la opción solo aparece para `admin` y `rrhh`.
- Se eliminó de la base local el departamento `RR:HH`; el empleado asociado se conservó sin departamento.

### Cambio 20 - Privacidad de horas y reportes

**Fecha:** 2026-09-15  
**Archivos modificados:** `main.py`, `interfaz.py`  
**Objetivo:** impedir que los empleados consulten información de otros trabajadores.

#### Implementación

`listar_registros_tiempo()` acepta opcionalmente un RUT para filtrar los resultados. Los empleados ven solo sus horas y su reporte; `admin` y `rrhh` pueden consultar la información general.

#### Validación

- Con dos empleados y dos registros, la consulta general devolvió ambos registros.
- La consulta filtrada devolvió únicamente el registro del empleado correspondiente.
- Se comprobó el menú con los textos `Ver mis horas registradas` y `Generar mi reporte`.

### Cambio 21 - Generación automática de usuarios

**Fecha:** 2026-09-15  
**Archivo modificado:** `interfaz.py`  
**Objetivo:** evitar el ingreso manual del nombre de usuario.

#### Implementación

El sistema genera el usuario con la inicial del nombre y el primer apellido, por ejemplo `nlatorre`. Si ya existe, utiliza la inicial y el segundo apellido, por ejemplo `ngonzalez`. Si ambas alternativas existen, informa el conflicto.

#### Validación

- Se verificó la generación del primer usuario.
- Se verificó la selección del segundo apellido ante una colisión.
- Se verificó el mensaje cuando ambas alternativas están ocupadas.
- El usuario generado se muestra al finalizar el registro.

### Cambio 22 - Limpieza y revisión de SQLite

**Fecha:** 2026-09-15  
**Archivo modificado:** `ecotech_solutions.db`  
**Objetivo:** comenzar las pruebas finales con una base limpia.

#### Implementación

Se eliminaron los registros de departamentos, empleados, usuarios, proyectos, asignaciones y horas, conservando las tablas y el esquema SQLite.

#### Validación

Todas las tablas quedaron con cero registros y la base pudo inicializarse nuevamente sin errores.

### Cambio 23 - Eliminación de usuario y conservación de proyectos

**Fecha:** 2026-09-16  
**Archivo modificado:** `main.py`  
**Objetivo:** eliminar correctamente la información del empleado asociado sin perder los proyectos existentes.

#### Implementación

`eliminar_usuario()` identifica el RUT del empleado asociado, elimina el usuario y elimina después al empleado dentro de la misma transacción. La clave foránea `empleado_proyecto` elimina únicamente la asignación del empleado; los proyectos permanecen almacenados para poder asignarlos a otra persona.

#### Validación

- Se confirmó que el usuario eliminado ya no aparece en `usuarios`.
- Se confirmó que el empleado asociado ya no aparece en `empleados`.
- Se confirmó que la asignación correspondiente desaparece de `empleado_proyecto`.
- Se confirmó que el proyecto permanece en `proyectos` y puede reutilizarse.
- La prueba SQLite en memoria finalizó correctamente con el mensaje `OK: el proyecto permanece y se elimina solo la asignacion del empleado`.

### Cambio 24 - Validación interactiva de datos de usuario

**Fecha:** 2026-09-16
**Archivo modificado:** `interfaz.py`
**Objetivo:** mejorar la experiencia de registro evitando reiniciar el formulario ante un dato inválido.

#### Implementación

Se agregaron lectores que repiten únicamente el campo incorrecto para contraseñas, roles,
correo, nombre, apellidos, cargo y RUT opcional. El RUT obligatorio continúa utilizando
su validación de formato y dígito verificador sin solicitar nuevamente los datos ya aceptados.

Además, nombres y apellidos ahora aceptan solo letras y espacios, incluidos caracteres
acentuados, y rechazan números o símbolos con un mensaje explicativo.

#### Validación

- `py -3 -m py_compile interfaz.py main.py` finalizó correctamente.
- Se simularon entradas vacías, correos sin `@` y RUTs con formato inválido.
- Se comprobó que cada error vuelve a solicitar solo el campo correspondiente.
- Se comprobó que `Ana2`, `Pérez!` y `Lopez-2` son rechazados.
- Se comprobó que `Ana Maria`, `Pérez` y `López` son aceptados.
- El editor no reportó errores en `interfaz.py`.

### Cambio 25 - Permisos por rol en proyectos y registros de tiempo

**Fecha:** 2026-09-21
**Archivo modificado:** `interfaz.py`
**Objetivo:** corregir dos fugas de permisos detectadas en una revisión crítica del código.

#### Hallazgos

1. La opción `Ver mis horas registradas` mostraba los registros de todos los empleados: `mostrar_registros_tiempo_menu()` llamaba a `listar_registros_tiempo()` sin el filtro por RUT que sí aplicaba la opción de reportes. Esto contradecía lo documentado en el Cambio 20.
2. Las opciones de crear proyecto, asignar empleado a proyecto y registrar horas no verificaban el rol, por lo que un empleado podía crear proyectos, asignar a otras personas y registrar horas a nombre de cualquier RUT.

#### Implementación

- Se agregaron tres funciones auxiliares: `verificar_gestion()` lanza `PermissionError` cuando el rol no es `admin` ni `rrhh`; `obtener_rut_propio()` devuelve el RUT del empleado vinculado al usuario o falla con `ValueError` si la cuenta no tiene ficha; `obtener_filtro_rut()` devuelve `None` para roles de gestión y el RUT propio para empleados.
- `mostrar_registros_tiempo_menu()` y `mostrar_reportes_menu()` usan `obtener_filtro_rut()`, de modo que ambas opciones aplican la misma regla de privacidad. El listado ahora se muestra en una línea legible por registro en lugar de imprimir el diccionario crudo.
- `crear_proyecto_menu()` y `asignar_proyecto_menu()` reciben el usuario actual y llaman a `verificar_gestion()`.
- `registrar_tiempo_menu()` solicita el RUT solo a `admin` y `rrhh`; para `empleado` usa automáticamente el RUT de su ficha.
- El menú oculta `Crear proyecto` y `Asignar empleado a proyecto` a los empleados y rotula la opción 8 como `Registrar mis horas trabajadas`.

#### Revisión técnica

La revisión fue apoyada por IA para detectar los puntos donde la interfaz no aplicaba la regla de negocio. El equipo decidió mantener la posibilidad de que un empleado registre sus propias horas (es su operación habitual) y restringir únicamente la creación de proyectos y las asignaciones, que corresponden a gestión. Se centralizó la verificación de permisos en una función para evitar repetir la condición en cada opción.

#### Validación

- `py -3 -m py_compile interfaz.py main.py` finalizó correctamente.
- Prueba en SQLite en memoria con dos empleados, un proyecto y un registro de horas por empleado:
  - El usuario `empleado` solo ve sus propios registros en la opción 9; `admin` ve ambos.
  - `crear_proyecto_menu()` y `asignar_proyecto_menu()` rechazan al rol `empleado` con `PermissionError`.
  - `registrar_tiempo_menu()` no solicita RUT al empleado y guarda el registro con su propio RUT; para `admin` sigue solicitando el RUT.
  - El menú del empleado no muestra las opciones 5 y 7 y rotula la opción 8 como `Registrar mis horas trabajadas`; el menú de `admin` conserva todas las opciones.

### Cambio 26 - Avisos de mantenibilidad SonarQube en la interfaz

**Fecha:** 2026-09-21
**Archivo modificado:** `interfaz.py`
**Objetivo:** eliminar los avisos de mantenibilidad reportados por SonarQube tras el Cambio 25.

#### Hallazgos

SonarQube reportó tres avisos de mantenibilidad en `interfaz.py`. Un análisis del árbol sintáctico identificó literales duplicados (regla S1192): `"Opcion no valida."` y `"Seleccione una opcion: "` aparecían cuatro veces cada uno, y `"El empleado indicado no existe."` tres veces pese a que ya existía la constante `MENSAJE_EMPLEADO_INEXISTENTE` sin utilizar. Además, la consulta de empleado por RUT estaba escrita tres veces (una en la constante `CONSULTA_EMPLEADO` y dos en línea), `guardar_empleado` se importaba sin usarse y `crear_usuario_menu()` no estaba enlazada a ninguna opción del menú.

#### Implementación

- Se agregaron las constantes `MENSAJE_OPCION_INVALIDA` y `MENSAJE_SELECCION`, y se reemplazaron todas las apariciones de sus literales.
- Se utilizó `MENSAJE_EMPLEADO_INEXISTENTE` y `CONSULTA_EMPLEADO` en los puntos donde el texto estaba repetido.
- Se eliminó el import de `guardar_empleado`, que no se usaba en la interfaz.
- Se eliminó `crear_usuario_menu()`, código muerto que duplicaba el flujo de `registrar_usuario_menu()` con un nombre de usuario manual; el registro de usuarios sigue disponible mediante la opción `Crear usuario`.
- Los bloques `except` consecutivos que imprimían el mismo mensaje en `mostrar_menu()` e `iniciar_sesion()` se unificaron en una sola cláusula con una tupla de excepciones, lo que reduce la complejidad cognitiva sin cambiar el comportamiento.

#### Revisión técnica

Se comprobó con un recorrido del AST que no quedan literales de mensaje repetidos tres o más veces ni imports sin uso. Se utilizó IA como apoyo para localizar las duplicidades; la decisión de eliminar `crear_usuario_menu()` en lugar de enlazarla se tomó porque el flujo de registro automático de usuarios ya cubre ese caso y evita mantener dos formularios distintos.

#### Validación

- `py -3 -m py_compile interfaz.py` finalizó correctamente.
- Prueba en SQLite en memoria: el mensaje de empleado inexistente coincide con la constante, el registro de horas del empleado sigue funcionando, las opciones inválidas muestran `Opcion no valida.` y el prompt `Seleccione una opcion: ` se sigue mostrando en los menús.

## Fase 3 - Unidad 3: servicios externos y seguridad (cambios 27 a 34)

### Cambio 27 - Unidad 3, paso 1: configuración segura con variables de entorno

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`
**Archivos creados:** `requirements.txt`, `.env.example`
**Objetivo:** iniciar la Unidad 3 (criterio 3.1.2, "controlar el uso de datos sensibles como credenciales o llaves de API") eliminando los secretos escritos en el código y declarando las dependencias oficiales que usará el consumo de APIs.

#### Hallazgos

Los códigos `CODIGO_ADMIN = "1234"` y `CODIGO_RRHH = "12345"` estaban en `main.py`, versionados en GitHub y documentados en el Readme. El propio equipo lo había registrado como limitación temporal. Antes de agregar llaves de API era necesario contar con un mecanismo de configuración que no pasara por el código fuente.

#### Implementación

- `requirements.txt` declara `requests` (librería oficial recomendada por la guía para el consumo de servicios) y `python-dotenv` (carga de `.env`).
- `.env.example` documenta las variables sin valores; `.env` ya estaba excluido en `.gitignore`.
- `main.py` carga `.env` con `load_dotenv(..., override=False)`, de modo que una variable definida en el sistema operativo tiene prioridad sobre el archivo. `DATABASE_PATH` puede sobrescribirse con `ECOTECH_DB_PATH`, lo que facilita pruebas y un futuro despliegue.
- Se reemplazaron las constantes por `VARIABLES_CODIGO_ROL`, `obtener_codigo_rol()` y `verificar_codigo_rol()`. La lectura ocurre en el momento del registro, no al importar el módulo, y la comparación usa `hmac.compare_digest` (tiempo constante), la misma técnica que ya se usaba para las contraseñas.
- Si la variable no existe, `obtener_codigo_rol()` lanza `ValueError` indicando qué variable definir, sin mostrar ningún valor. La interfaz ya captura `ValueError` y muestra el mensaje sin interrumpir el programa.
- `interfaz.py` dejó de importar los códigos y llama a `verificar_codigo_rol(rol, codigo)`.

#### Revisión técnica

Se evaluó con apoyo de IA la alternativa de dejar valores por defecto cuando la variable no existe. Se descartó porque volvería a dejar un secreto conocido en el código y anularía el objetivo del cambio; se prefirió un mensaje explícito de configuración. También se evaluó leer las variables una sola vez al importar el módulo; se descartó porque impide probar el comportamiento cambiando el entorno y porque un `.env` editado en caliente no se reflejaría. Las dependencias se instalan con `pip`; ambas son librerías oficiales publicadas en PyPI y de uso amplio.

#### Validación

- `py -3 -m py_compile main.py interfaz.py` finalizó correctamente.
- Prueba automatizada: los códigos se leen desde `.env`; `verificar_codigo_rol()` acepta el código correcto y rechaza uno incorrecto; un rol sin código y una variable vacía producen mensajes claros; ningún literal `"1234"` ni `"12345"` permanece en `main.py` ni `interfaz.py`.
- Flujo completo de registro de `admin` en SQLite en memoria: un código incorrecto muestra `Codigo secreto incorrecto` y vuelve a solicitarlo; con el código correcto el usuario se crea normalmente.
- `git status` confirma que `.env` no aparece como archivo a versionar.

### Cambio 28 - Unidad 3, paso 2: consumo de la API de clima

**Fecha:** 2026-09-21
**Archivo creado:** `servicios_externos.py`
**Archivos modificados:** `main.py`, `interfaz.py`, `.gitignore`
**Objetivo:** cubrir los criterios 3.1.1 (consumo de servicios externos con librerías oficiales), 3.1.2 (validación de entradas y control de la llave) y 3.1.3 (manejo de errores y continuidad) con la primera integración que pide la guía: información climática para la planificación de proyectos.

#### Implementación

- `ClienteHTTP` encapsula `requests.Session`. Exige HTTPS, aplica `timeout=8` en toda petición, reintenta una vez ante `Timeout` o respuestas 5xx, y convierte cada situación en `ErrorServicioExterno` con un mensaje específico pero sin datos internos: credencial rechazada (401/403), dato no encontrado (404), límite de consultas (429), servicio no disponible (5xx), sin conexión, sin respuesta a tiempo, cuerpo no JSON.
- `IServicioExterno` define el contrato `consultar()`; `ServicioClima` lo implementa sobre OpenWeatherMap. La llave se obtiene de `OPENWEATHER_API_KEY` en el constructor (si falta, el mensaje indica qué variable definir) y viaja únicamente en `params`, por lo que ningún mensaje ni registro la contiene.
- `_interpretar()` valida el esquema de la respuesta (`main.temp`, `main.humidity`, `weather[0].description`), convierte tipos y comprueba rangos plausibles (temperatura entre -90 y 60 °C, humedad entre 0 y 100). Un 200 con contenido inesperado se trata como error, no como dato.
- `validar_ciudad()` restringe la entrada a letras, espacios y guiones (2 a 60 caracteres) antes de salir a la red.
- `main.py`: columna `proyectos.ciudad` en el esquema y migración automática con `ALTER TABLE` para bases existentes (mismo patrón usado antes para `usuarios.rol`); `Proyecto.ciudad` opcional validado en `__post_init__`; `guardar_proyecto()`, `listar_proyectos()` y `actualizar_proyecto()` incluyen la ciudad.
- `interfaz.py`: `leer_ciudad_opcional()` al crear proyectos, la ciudad se muestra en el listado, nueva opción 15 `Consultar clima de un proyecto` para todos los roles, y `ErrorServicioExterno` se captura en el bucle principal junto a los errores ya manejados. Los registros técnicos van a `ecotech.log` mediante `logging`; `*.log` se agregó a `.gitignore`.

#### Revisión técnica

Se solicitó a la IA un primer borrador del cliente y se revisó críticamente. Se descartaron tres prácticas del borrador: (1) capturar `Exception` de forma genérica y mostrar `str(error)` al usuario, porque `requests` incluye la URL completa con `appid` en sus mensajes y eso expondría la llave; se reemplazó por captura específica y mensajes propios. (2) Omitir `timeout`, lo que dejaría la consola bloqueada indefinidamente si el servicio no responde; se fijó un valor explícito. (3) Usar directamente `datos["main"]["temp"]` sin validar, lo que provocaría `KeyError` ante una respuesta parcial; se agregó validación de esquema y rangos. Se conservó del borrador el uso de `requests.Session` y de `params=`, que evita construir la URL a mano.

Se decidió que la ciudad sea opcional y se guarde en el proyecto, en lugar de pedirla en cada consulta, porque así el dato queda validado una vez y la opción de clima solo requiere elegir el proyecto. La validación de ciudad se reutiliza desde `main.py` mediante `validar_ciudad_opcional()` para no duplicar el patrón.

#### Validación

- `py -3 -m py_compile main.py interfaz.py servicios_externos.py` finalizó correctamente.
- Pruebas con `unittest.mock` sobre la sesión HTTP (sin red): respuesta 200 correcta; 401, 404, 429, 500+503, timeout, sin conexión, cuerpo no JSON, JSON sin campos y JSON con valores fuera de rango producen `ErrorServicioExterno` con el mensaje esperado; 500 seguido de 200 devuelve el dato gracias al reintento; en ningún mensaje aparece la llave ni el parámetro `appid`.
- `validar_ciudad()` rechaza vacío, un carácter, texto con `;`, más de 60 caracteres y ciudades con dígitos; acepta y normaliza `Viña del Mar`.
- `ClienteHTTP("http://...")` es rechazado por no usar TLS; sin `OPENWEATHER_API_KEY` el servicio informa qué variable configurar.
- Migración: sobre una tabla `proyectos` antigua sin `ciudad`, `inicializar_bd()` agrega la columna; guardar, listar y actualizar la ciudad funciona; `Proyecto(..., ciudad="Ciudad1")` es rechazado.
- Menú en SQLite en memoria: crear proyecto repite solo el campo ciudad ante `Calama9` y acepta `Calama`; el listado muestra `Ciudad: Calama` y `Sin ciudad`; la opción 15 sobre un proyecto sin ciudad informa el motivo, y con un servicio simulado muestra `18.4 °C, humedad 55%, cielo claro`.
- Prueba en vivo: la llave recién creada en OpenWeatherMap respondió 401 durante la sesión (las llaves nuevas tardan hasta dos horas en activarse); el usuario vio únicamente el mensaje sanitizado `El servicio externo rechazó la credencial configurada`, lo que confirma el comportamiento del criterio 3.1.3. Queda pendiente repetir la consulta real cuando la llave esté activa.

### Cambio 29 - Unidad 3, paso 3: indicadores económicos y cálculo de pagos

**Fecha:** 2026-09-21
**Archivos modificados:** `servicios_externos.py`, `main.py`, `interfaz.py`
**Objetivo:** cubrir la segunda problemática de la guía (gestión de pagos internacionales) consumiendo indicadores económicos desde una API externa y usándolos para calcular pagos ajustados a la moneda del país del proyecto (criterios 3.1.1, 3.1.2 y 3.1.3).

#### Implementación

- `ServicioIndicadores` implementa `IServicioExterno` sobre `https://mindicador.cl/api/{codigo}`, reutilizando `ClienteHTTP` y, por tanto, el mismo timeout, reintento y traducción de errores del servicio de clima. No requiere llave.
- Antes de consultar se exploró la API real: `/api/dolar`, `/api/euro` y `/api/uf` devuelven `serie[0]` con el valor más reciente; un código inexistente responde HTTP 500 con un mensaje de error. Por eso `validar_indicador()` aplica una lista blanca (`INDICADORES_PERMITIDOS`): sin ella, un error de tipeo del usuario se reportaría como "servicio no disponible" y además gastaría el reintento.
- `_interpretar()` valida que exista la serie, que el valor sea numérico y positivo y que la fecha sea ISO y no futura; devuelve un `Indicador` inmutable con código, nombre, moneda, valor, fecha del dato y fecha de consulta.
- En `main.py`: `validar_monto()` (número estrictamente positivo, rechaza booleanos), `sumar_horas_empleado()` (`SUM` sobre `registros_tiempo` con RUT validado) y `calcular_pago()`, que produce un `Pago` con monto en CLP y en la moneda del indicador, redondeados a dos decimales. La lógica de negocio queda en el núcleo, no en la interfaz ni en el módulo de servicios.
- En `interfaz.py`: `leer_indicador()` y `leer_monto()` repiten solo el campo inválido (acepta coma decimal); opción 16 `Consultar indicador economico` para todos los roles; opción 17 `Calcular pago en moneda extranjera` restringida con `verificar_gestion()`, que muestra los empleados, pide RUT y tarifa por hora, obtiene el indicador y presenta el desglose.

#### Revisión técnica

Se pidió a la IA una propuesta para el cálculo de pagos y se evaluaron dos alternativas. La primera guardaba una tarifa por hora en la tabla `empleados`; se descartó en esta etapa porque exigía una migración, cambios en el registro de usuarios y en el CRUD de la Unidad 2 ya validado, sin aportar al criterio evaluado (consumo de la API). Se optó por solicitar la tarifa en el momento del cálculo, validada como monto positivo. La segunda propuesta hacía la conversión dentro de la función del menú; se movió a `calcular_pago()` en `main.py` para que sea probable sin interfaz y reutilizable desde una futura API web.

También se revisó el borrador del servicio: usaba `datos["serie"][-1]` asumiendo orden cronológico ascendente, pero la exploración real mostró que la serie viene en orden descendente (el índice 0 es el más reciente). Se corrigió y se dejó registrado para evitar que la IA repita la suposición.

#### Validación

- `py -3 -m py_compile main.py interfaz.py servicios_externos.py` finalizó correctamente.
- Servicio simulado: `DOLAR ` se normaliza a `dolar` y devuelve valor, fecha y moneda correctos; serie vacía, valor no numérico, valor negativo, fecha futura y cuerpo vacío producen `ErrorServicioExterno` con el mensaje genérico de formato.
- `validar_indicador()` rechaza vacío, `peso`, `dolar; drop` y `bitcoin` indicando las opciones válidas.
- `calcular_pago()`: 10 horas a $15.000 con dólar a 958,42 produce $150.000 CLP y 156,51 USD; horas cero, tarifa negativa, tipo de cambio cero y un booleano como horas son rechazados.
- Menú en SQLite en memoria: un empleado sin horas registradas bloquea el cálculo con un mensaje claro; el rol `empleado` recibe `PermissionError`; con tarifa `abc`, `-3` y luego `15000,5` y con indicador `bitcoin` y luego `dolar`, la opción 17 repite solo el campo inválido y muestra `Total: $187,506.25 CLP = 195.64 USD`; la opción 16 está visible para todos y la 17 solo para gestión.
- Consulta real a mindicador.cl durante la sesión: `Euro: 1099.86 CLP (2026-09-21)`.

### Cambio 30 - Unidad 3, paso 4: persistencia local y respaldo ante fallos

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `servicios_externos.py`, `interfaz.py`
**Objetivo:** cumplir la parte del aprendizaje esperado que exige "persistir datos localmente" y el criterio 3.1.3 ("estructuras de control que permitan la continuidad y estabilidad del sistema"): el sistema debe seguir siendo útil aunque el servicio externo no responda.

#### Implementación

- `SCHEMA_SQL` incorpora `consultas_clima` (ciudad, temperatura, humedad, descripción, fecha de consulta) e `indicadores` (código, nombre, moneda, valor, fecha del dato, fecha de consulta). Se crean con `CREATE TABLE IF NOT EXISTS`, por lo que las bases existentes se actualizan al abrir el programa.
- En `servicios_externos.py`: `guardar_clima()`, `obtener_ultimo_clima()`, `guardar_indicador()` y `obtener_ultimo_indicador()` usan consultas parametrizadas, el decorador `@revertir_si_falla` del núcleo y devuelven los mismos `Clima` e `Indicador` que entrega la API, de modo que la interfaz no distingue el origen salvo por la bandera de respaldo. La búsqueda de clima es insensible a mayúsculas y ambas ordenan por fecha de consulta descendente para entregar el dato más reciente. Los lectores del respaldo pasan por `validar_ciudad()` y `validar_indicador()`, así la lista blanca aplica también a la base local.
- `consultar_con_respaldo(connection, servicio, criterio)` devuelve un `ResultadoConsulta` con el dato, la bandera `desde_respaldo` y el motivo del fallo. Flujo: consulta el servicio; si responde, persiste y devuelve; si lanza `ErrorServicioExterno`, busca el respaldo; si existe lo devuelve con el motivo y registra una advertencia en el log; si no existe, propaga el error original. Un servicio sin respaldo configurado se rechaza con `ValueError`.
- `interfaz.py`: `avisar_respaldo()` imprime `Aviso: <motivo> Se muestra el último dato guardado (consultado <fecha>)`. Las opciones 15, 16 y 17 usan `consultar_con_respaldo()`; `obtener_indicador()` centraliza la lectura del indicador para las opciones 16 y 17.

#### Revisión técnica

El borrador propuesto por la IA implementaba la caché con una política de expiración (por ejemplo, reutilizar el dato guardado durante 30 minutos sin consultar la API). Se descartó: el objetivo académico es demostrar continuidad ante fallos, no ahorrar llamadas, y una caché con expiración ocultaría al usuario si el dato es actual o no. Se prefirió consultar siempre el servicio y usar la base solo como respaldo explícito, informando la fecha del dato. También se evaluó guardar el respaldo en un archivo JSON; se descartó porque el proyecto ya tiene SQLite con transacciones y rollback, y agregar un segundo mecanismo de persistencia duplicaría responsabilidades.

Durante las pruebas se detectó que un dato con fecha posterior a la actual era rechazado por `ServicioIndicadores` y, en consecuencia, la consulta caía al respaldo. Se confirmó que ese es el comportamiento deseado (una fecha futura indica una respuesta corrupta) y se corrigieron los datos de prueba, no el código.

#### Validación

- `py -3 -m py_compile main.py interfaz.py servicios_externos.py` finalizó correctamente.
- Base en memoria: `inicializar_bd()` crea `consultas_clima` e `indicadores`; sin datos, los lectores devuelven `None`.
- Con servicio simulado: una consulta exitosa persiste una fila y no se marca como respaldo; ante `ConnectionError` se devuelve el dato guardado con el motivo; ante 503 sin respaldo se propaga `ErrorServicioExterno`; con dos valores guardados del dólar (958,42 y 960,00), un `Timeout` devuelve 960,00; un servicio desconocido produce `ValueError`; `obtener_ultimo_indicador(c, "bitcoin")` es rechazado por la lista blanca.
- Base en archivo temporal: se guarda un clima, se cierra la conexión, se reabre y ante `Timeout` se recupera el respaldo.
- Menú: opción 15 con el servicio caído muestra `Aviso: ... Se muestra el último dato guardado (consultado 2026-09-21 13:10)` y el clima; opción 16 muestra el aviso y `960.00`; opción 17 calcula `$100,000.00 CLP = 104.17 USD` sobre el respaldo; sin respaldo el error llega al bucle principal con mensaje limpio.

### Cambio 31 - Menú principal en una sola tabla y renumeración

**Fecha:** 2026-09-21
**Archivo modificado:** `interfaz.py`
**Objetivo:** corregir el desorden de la numeración del menú detectado al ejecutar el programa tras el paso 4.

#### Hallazgos

Al probar el sistema, las opciones aparecían fuera de orden (`... 10, 15, 16, 11, 12, 13, 14, 17`) y faltaba el número 3. La causa era estructural: la numeración estaba definida dos veces, en el diccionario de acciones de `ejecutar_opcion_menu()` y en la lista de textos de `mostrar_opciones_menu()`, que además insertaba opciones por posición (`insert(3, ...)`, `insert(5, ...)`). Cada opción nueva de la Unidad 3 se agregó al final de ambas estructuras y el orden visual dejó de corresponder al numérico.

#### Implementación

- Nueva función `construir_opciones_menu(connection, usuario_actual)` que define en una sola tabla el número, el texto (con variante para empleados donde corresponde), el permiso del rol y la acción de cada opción, y devuelve solo las permitidas, ya ordenadas.
- `mostrar_opciones_menu()` y `ejecutar_opcion_menu()` reciben esa lista; la primera la imprime y la segunda la convierte en diccionario para ejecutar. Como ambas parten de la misma fuente, no pueden volver a desalinearse.
- Renumeración consecutiva 1 a 16: se eliminó el hueco del 3 y las opciones de la Unidad 3 (clima, indicador, pago) quedaron en 10, 11 y 12, antes de la gestión de usuarios (13 a 16).
- Efecto colateral positivo: una opción que el rol no ve tampoco existe en su diccionario de acciones, por lo que responde `Opcion no valida.` sin llegar a la función. Las verificaciones internas (`verificar_gestion()`, comprobaciones de `admin`) se conservan como segunda barrera.

#### Revisión técnica

Se evaluó ordenar la lista existente con `sorted(..., key=int)` como arreglo mínimo. Se descartó porque mantenía la duplicación que originó el problema; la solución elegida elimina la causa y reduce el código. Los números de opción cambiaron respecto de lo documentado en los cambios 28 a 30 (15, 16 y 17 pasan a 10, 11 y 12); esas entradas se conservan como historia y el Readme refleja la numeración vigente con una tabla completa.

#### Validación

- `py -3 -m py_compile interfaz.py` finalizó correctamente.
- Para `admin`, `rrhh` y `empleado` los números del menú son estrictamente crecientes: `admin` 1-16, `rrhh` 1-14, `empleado` 2, 3, 5, 7, 8, 9, 10, 11.
- Para `empleado`, la opción `16` (eliminar usuario) responde `Opcion no valida.` sin ejecutar nada; la opción `0` finaliza la sesión; la opción `2` ejecuta el listado de departamentos.

### Cambio 32 - Unidad 3, paso 5: revisión de seguridad final y pruebas automatizadas

**Fecha:** 2026-09-21
**Archivo creado:** `test_servicios_externos.py`
**Archivo modificado:** `servicios_externos.py`
**Objetivo:** cerrar el criterio 3.1.4 con una revisión de seguridad del código de la Unidad 3 apoyada por IA, dejar las pruebas como parte del repositorio y verificar la integración real con ambas APIs.

#### Revisión de seguridad (con apoyo de IA)

Se recorrió `servicios_externos.py`, `main.py` e `interfaz.py` con una lista de verificación propuesta por la IA y revisada por el equipo. Resultado por punto:

| Punto revisado | Resultado | Decisión |
|---|---|---|
| Secretos en el código fuente | Ninguno; llave y códigos en `.env`, cargados con `python-dotenv`. | Sin cambios. |
| Llave en URL, mensajes o logs | La llave viaja solo en `params`; los logs registran la URL base sin query; los mensajes son fijos. | Sin cambios; se agregó una prueba que lo verifica. |
| Verificación TLS | `requests` verifica certificados por defecto; `ClienteHTTP` rechaza URLs sin `https://`. | Sin cambios. |
| Timeout y reintentos | Timeout de 8 s en toda petición; un reintento solo ante timeout o 5xx. | Sin cambios. |
| Validación de entradas | Ciudad por expresión regular, indicador por lista blanca, montos positivos, RUT con dígito verificador. | Sin cambios. |
| Validación de respuestas | Esquema, tipos y rangos comprobados; 200 con contenido inesperado se rechaza. | Sin cambios. |
| Tamaño de la respuesta | **Hallazgo:** `respuesta.json()` se ejecutaba sin límite; un servicio comprometido podría devolver un cuerpo enorme y agotar memoria. | **Corregido:** `MAX_BYTES_RESPUESTA = 1_000_000`; se rechaza el cuerpo mayor con el mensaje genérico de formato y se registra en el log. |
| Aritmética monetaria | `float` con redondeo a dos decimales. | **Limitación aceptada** para el alcance académico; en una nómina real se usaría `decimal.Decimal`. Se documenta para la defensa. |
| Espera entre reintentos | Reintento inmediato, sin espera exponencial. | Aceptado: un solo reintento no genera carga significativa. |
| Contenido del log local | Incluye URL base, código HTTP y ciudad consultada; nunca llaves ni credenciales. | Aceptado; `*.log` excluido del repositorio. |

#### Pruebas automatizadas

`test_servicios_externos.py` contiene 27 pruebas con `unittest` y `unittest.mock`, sin acceso a la red, organizadas en seis clases: validación de entradas, `ClienteHTTP` (cada código de error, timeout, sin conexión, cuerpo no JSON, respuesta demasiado grande, reintento exitoso), `ServicioClima`, `ServicioIndicadores`, cálculo de pagos y respaldo local. La sesión simulada verifica en cada llamada que la URL use HTTPS y que se pase el timeout; el ayudante `assert_error` verifica que ningún mensaje contenga la llave ni `appid`. El registro del módulo se desactiva durante las pruebas porque provocan fallos a propósito.

#### Verificación en vivo

- La llave de OpenWeatherMap, que respondía 401 al crearse (cambio 28), quedó activa durante la sesión: `Santiago: 16.98 °C, humedad 63%, nubes`.
- mindicador.cl respondió correctamente para `euro` (cambio 29).

#### Validación

- `py -3 -m unittest -v test_servicios_externos`: 27 pruebas, todas en verde, en menos de 0,1 s.
- `py -3 -m py_compile servicios_externos.py test_servicios_externos.py` finalizó correctamente.
- El guion privado `defensa_oral.py` se actualizó con dos secciones sobre la Unidad 3 y tres preguntas probables; no forma parte del repositorio.

### Cambio 33 - Avisos de mantenibilidad SonarQube tras la Unidad 3

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `servicios_externos.py`, `test_servicios_externos.py`
**Objetivo:** eliminar los ocho avisos de mantenibilidad reportados por SonarQube después de incorporar el código de la Unidad 3.

#### Hallazgos y correcciones

| Regla | Ubicación | Corrección |
|---|---|---|
| S1192 literal `"utf-8"` repetido cuatro veces | `main.py` | Constante `CODIFICACION` usada en el hash de contraseñas y en la comparación de códigos de rol. |
| S1192 literal `"ID del proyecto: "` repetido tres veces | `interfaz.py` | Constante `MENSAJE_ID_PROYECTO`, en línea con las demás constantes de mensajes. |
| S6903 `datetime.now()` sin zona horaria (dos usos) | `servicios_externos.py` | `datetime.now().astimezone()`: fecha de consulta consciente de la zona local; `fromisoformat` la recupera con su desplazamiento desde SQLite. |
| S1172 parámetro `params` sin uso en el `get` simulado | `test_servicios_externos.py` | Se convirtió en una verificación: los parámetros deben viajar en `params=`, nunca concatenados en la URL. |
| `assert` en una función auxiliar (dos usos) | `test_servicios_externos.py` | Reemplazados por `raise AssertionError(...)` explícitos en `verificar_peticion()`. |
| S3776 complejidad cognitiva de `sesion_simulada` (16) | `test_servicios_externos.py` | Dividida en `verificar_peticion()`, `respuesta_simulada()` y una `sesion_simulada()` más corta. |

#### Revisión técnica

Se descartó silenciar reglas con comentarios `# NOSONAR`: cada aviso tenía una corrección directa y el objetivo del proyecto es demostrar criterio técnico, no ocultar avisos. La regla S1192 de SonarQube para Python no cuenta cadenas formadas solo por letras, dígitos y guion bajo (por ejemplo, claves de columnas como `'rut_empleado'`), por lo que esas no se convirtieron en constantes; hacerlo empeoraría la legibilidad sin beneficio.

#### Validación

- `py -3 -m py_compile` de los cuatro archivos finalizó correctamente.
- `py -3 -m unittest test_servicios_externos`: 27 pruebas en verde después de la refactorización del mock.
- Recorrido del AST sin literales repetidos (según los criterios de S1192), sin imports ni parámetros sin uso y sin funciones sobre 15 de complejidad cognitiva.

### Cambio 34 - Reglas S5778, S5906 y S8572 de SonarQube

**Fecha:** 2026-09-21
**Archivos modificados:** `servicios_externos.py`, `test_servicios_externos.py`
**Objetivo:** cerrar los siete avisos restantes de SonarQube, identificados por su regla, y resolver el conflicto entre una de ellas y la protección de la llave de la API.

#### Hallazgos y correcciones

| Regla | Descripción | Ocurrencias | Corrección |
|---|---|---|---|
| S5778 | Dentro de `assertRaises` debe haber una sola invocación; con `servicio_clima(...).consultar(...)` no queda claro cuál debe lanzar la excepción. | 5 | El servicio o el mock se construye antes del bloque `with`, que queda con la única llamada bajo prueba. |
| S5906 | Debe usarse la aserción más específica: `assertEqual(x, round(y, 2))` es `assertAlmostEqual(x, y, 2)`. | 1 | Aplicado en la prueba de cálculo de pago. |
| S8572 | En un `except`, `logging.error()` pierde el traceback; usar `logging.exception()`. | 1 | Ver decisión más abajo. |

#### Revisión técnica: S8572 frente a la protección de la llave

La regla pide registrar el traceback dentro de los bloques `except`. Se analizó su efecto en cada uno:

- `except ValueError` al decodificar JSON y `except (KeyError, IndexError, TypeError, ValueError)` al interpretar clima e indicadores: las excepciones no contienen la URL ni parámetros; el traceback ayuda a diagnosticar un cambio de formato en la API. Se cambió a `LOGGER.exception()`.
- `except requests.RequestException`: los mensajes de `requests` incluyen la URL completa con la query string, es decir, `appid=<llave>`. Registrar el traceback escribiría la llave en `ecotech.log`, lo que contradice el criterio 3.1.2. Se decidió **no** registrar el traceback en ese caso: se registra el tipo de excepción y la URL base con `LOGGER.warning()`, con un comentario en el código que explica el motivo. Los `LOGGER.error()` que quedan están en ramas `if` sobre códigos HTTP, no en bloques `except`, y no los cubre la regla.

Para que esta decisión quede verificada y no dependa de la memoria del equipo, se agregó la prueba `test_log_no_contiene_la_llave`: captura el registro con `assertLogs`, provoca un `RequestException` cuyo mensaje contiene `appid=` y la llave, un cuerpo no JSON y un JSON incompleto, y comprueba que se emiten tres registros y que ninguno contiene la llave ni `appid`.

#### Validación

- `py -3 -m py_compile servicios_externos.py test_servicios_externos.py` finalizó correctamente.
- `py -3 -m unittest test_servicios_externos`: 28 pruebas en verde (27 anteriores más la del registro técnico).
- Cada bloque `assertRaises` del archivo contiene ahora una sola llamada.

## Fase 4 - Alineación con los requisitos de la Unidad 1 (cambios 35 a 43)

### Cambio 35 - Revisión contra la rúbrica y la guía de la Unidad 1; modelo UML unificado

**Fecha:** 2026-09-21
**Archivo creado:** `uml.mmd`
**Archivos incorporados:** `TI3V21_U1_ES_GUÍA primera parte.pdf` (guía de la Unidad 1 con los requisitos del sistema)
**Objetivo:** verificar el cumplimiento de la rúbrica (22 indicadores) y de los requisitos del sistema definidos en la Unidad 1, y dejar un único modelo de clases que integre el UML original, esos requisitos y el código de las Unidades 2 y 3.

#### Revisión de la rúbrica

Se leyó la rúbrica completa (PDF escaneado, extraído como imagen). Los 13 indicadores grupales suman 30 puntos y los 9 individuales de defensa otros 30. Los indicadores de la Unidad 3 (3.1.1 a 3.1.4) están cubiertos por los cambios 27 a 34. Los riesgos detectados están en la Unidad 2: 2.1.1.G.1 exige correspondencia entre el UML y el código, y 2.1.3.G.5 exige demostrar registro, consulta, actualización y eliminación; el menú solo expone crear y listar para la mayoría de las entidades.

#### Revisión de los requisitos de la Unidad 1

Al contrastar el código con la guía de la Unidad 1 se comprobó que las diferencias entre `uml.png` y `main.py` no eran arbitrarias: los atributos del diagrama provienen de requisitos explícitos. Requisitos aún no implementados: datos personales del empleado (dirección, teléfono, fecha de inicio de contrato, salario) e ID único automático; gerente del departamento; descripción de tareas en el registro de tiempo; edición y eliminación de departamentos y proyectos desde la interfaz; desasignación de empleados de proyectos; informes de las cuatro entidades exportables a archivo; cifrado de datos personales en reposo. Además, la pantalla de acceso permite que cualquier persona cree una cuenta de rol `empleado` sin aprobación, lo que contradice el requisito de que el registro lo realice RR.HH.

#### Modelo unificado

`uml.mmd` (Mermaid `classDiagram`) conserva la notación del diagrama original (visibilidad, multiplicidades, etiquetas de relación) y define el modelo objetivo: las clases de dominio con los atributos de los requisitos, `CifradorDatos`, `Informe` y `ServicioReportes.guardar()`, y las clases de la Unidad 3 (`IServicioExterno`, `ServicioClima`, `ServicioIndicadores`, `ClienteHTTP`, `Clima`, `Indicador`, `ResultadoConsulta`, `Pago`, `ErrorServicioExterno`). El Readme lista las diferencias vigentes entre el modelo y el código hasta que se completen los cambios siguientes.

#### Revisión técnica

Se descartó ajustar el diagrama al código actual (eliminar del modelo los atributos no implementados), porque habría ocultado requisitos sin cumplir. Se decidió que el diagrama sea el objetivo y el código se alinee con él, en este orden: empleado completo con salario usado por el cálculo de pago; cifrado de datos personales; autoregistro limitado al primer usuario; gerente y descripción de tarea; CRUD completo y desasignación en el menú; informes exportables a archivo. El diagrama se generó con apoyo de IA a partir del código y del UML original y se revisó manualmente clase por clase.

#### Validación

- El archivo `uml.mmd` se renderiza en mermaid.live sin errores de sintaxis.
- Cada clase, atributo y método del diagrama corresponde a código existente o a un requisito de la guía de la Unidad 1 identificado en esta revisión.

### Cambio 36 - Alineación con la Unidad 1, paso 1: ficha completa del empleado

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`
**Archivo creado:** `test_nucleo.py`
**Objetivo:** cumplir el requisito "Registro de empleados" de la guía de la Unidad 1 (nombre, dirección, teléfono, correo, fecha de inicio de contrato, salario e ID único automático) y usar el salario en el cálculo de pagos de la Unidad 3, en lugar de pedir una tarifa por teclado.

#### Implementación

- Esquema: `empleados` pasa a tener `id_empleado INTEGER PRIMARY KEY AUTOINCREMENT`, `rut` como `UNIQUE` (sigue siendo la referencia de las claves foráneas existentes) y las columnas `direccion`, `telefono`, `fecha_inicio_contrato` y `salario`.
- Migración: SQLite no permite agregar una clave primaria con `ALTER TABLE`, por lo que `migrar_tabla_empleados()` crea la tabla nueva, copia las filas en el orden original, elimina la antigua y renombra. Las claves foráneas se desactivan solo durante la copia; con ellas activas, `DROP TABLE empleados` habría disparado `ON DELETE CASCADE` en `registros_tiempo` y `empleado_proyecto` y `ON DELETE SET NULL` en `usuarios`. Al terminar se ejecuta `PRAGMA foreign_key_check` y se reactivan las claves foráneas en un bloque `finally`.
- Modelo: `Empleado` incorpora `direccion`, `telefono`, `fecha_inicio_contrato`, `salario` e `id_empleado` como campos opcionales con valor por defecto, de modo que las fichas antiguas siguen siendo válidas y las llamadas posicionales existentes no cambian. Si los datos vienen, se validan: `validar_telefono()` (dígitos, espacios y prefijo `+`, 8 a 15 caracteres), `validar_monto()` para el salario y tipo `date` para la fecha.
- Persistencia: `guardar_empleado()` y `guardar_usuario_con_empleado()` insertan los nuevos campos y asignan `id_empleado` desde `lastrowid`; `listar_empleados()` los devuelve; `actualizar_empleado()` construye un `Empleado` para reutilizar todas las validaciones del modelo antes del `UPDATE`; `fila_a_empleado()` centraliza la conversión fila → objeto y reemplaza los `Empleado(*fila)` posicionales de la interfaz.
- Valor hora: `calcular_tarifa_hora()` aplica la fórmula de la Dirección del Trabajo (sueldo mensual / 30 × 7 / jornada semanal de 44 horas), con las constantes documentadas en el código.
- Interfaz: el registro de `empleado` y `rrhh` solicita dirección, teléfono, fecha de inicio de contrato y salario, repitiendo solo el campo inválido; `Listar empleados` muestra el ID y, solo para `admin` y `rrhh`, la ficha personal; `Calcular pago` deja de pedir la tarifa y usa el salario del empleado, rechazando con un mensaje claro a quien no lo tenga registrado.

#### Revisión técnica

Se evaluó con apoyo de IA mantener `rut` como clave primaria y agregar el ID como columna `UNIQUE` adicional para evitar la reconstrucción de la tabla. Se descartó porque el requisito pide un ID asignado automáticamente por el sistema, lo que en SQLite exige `INTEGER PRIMARY KEY AUTOINCREMENT`; la reconstrucción con claves foráneas desactivadas es el procedimiento documentado por SQLite para este caso y quedó cubierta por pruebas.

La IA propuso mostrar la ficha completa en todos los listados. Se descartó por el requisito de privacidad de datos personales de la guía: un empleado no debe ver la dirección, el teléfono ni el salario de sus compañeros. La ficha se muestra únicamente a los roles de gestión.

Para el valor hora se compararon dos convenciones: dividir el sueldo por 180 horas (práctica habitual con jornada de 45 horas) o aplicar la fórmula de la Dirección del Trabajo con la jornada vigente de 44 horas. Se adoptó la segunda por estar referida a la normativa actual; las constantes permiten ajustarla si la jornada cambia.

#### Validación

- `py -3 -m py_compile main.py interfaz.py test_nucleo.py` finalizó correctamente.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 42 pruebas en verde.
- `test_nucleo.py`: la migración sobre un esquema antiguo con un empleado, un usuario, una asignación y un registro de horas agrega las columnas, asigna `id_empleado = 1`, conserva las cuatro filas dependientes, deja `PRAGMA foreign_key_check` vacío y reactiva las claves foráneas; ejecutarla dos veces no duplica filas. Teléfonos `abc` y `12`, salarios `0` y `-1` y una fecha en texto son rechazados. Guardar asigna el ID y `fila_a_empleado()` devuelve un objeto igual al original. El registro por menú repite solo el teléfono y el salario inválidos y persiste la ficha. El listado básico omite salario y dirección; el detallado los incluye. Con salario de $1.200.000 y 10 horas, el pago muestra `Valor hora: $6,363.64` y `63.64 USD`; sin salario, se rechaza.
- Migración ejecutada sobre una copia de `ecotech_solutions.db` real: 2 empleados, 4 usuarios y 1 departamento conservados, `foreign_key_check` vacío, columnas nuevas presentes. Los empleados existentes quedan con salario sin registrar hasta que se edite su ficha (opción que llega con el CRUD del menú).

### Cambio 37 - Alineación con la Unidad 1, paso 2: cifrado de datos personales

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`, `requirements.txt`, `.env.example`
**Objetivo:** cumplir el requisito "Seguridad de datos sensibles" de la guía de la Unidad 1 ("almacena datos personales de empleados de forma segura utilizando técnicas de cifrado adecuadas") y reforzar el criterio 3.1.2 sobre protección de información sensible.

#### Implementación

- `CifradorDatos` encapsula `cryptography.fernet.Fernet` (AES-128-CBC con HMAC-SHA256 y IV aleatorio, cifrado autenticado). La clave se lee de `ECOTECH_CLAVE_CIFRADO`; si falta o no es válida, el constructor lanza `ValueError` con instrucciones, sin valores. `generar_clave_cifrado()` produce una clave nueva para copiar en `.env`. `obtener_cifrador()` construye el cifrador una sola vez (`lru_cache`).
- `cifrar_datos_personales()` devuelve los tokens de dirección, teléfono y salario (o `None` si el dato no fue informado); se usa en `guardar_empleado()`, `guardar_usuario_con_empleado()` y `actualizar_empleado()`. `descifrar_fila_empleado()` hace la operación inversa y alimenta a `fila_a_empleado()` y a `listar_empleados()`, que ahora devuelve diccionarios con los datos legibles.
- Un token Fernet siempre comienza con `gAAAAA`; `descifrar_valor()` usa ese prefijo para aceptar valores heredados en texto plano, y `cifrar_datos_personales_pendientes()` (llamada desde `inicializar_bd()`) los cifra al arrancar, informando cuántos. La columna `salario` pasa a `TEXT` en el esquema y en la migración, porque almacena tokens.
- Si la clave configurada no corresponde a la base, `descifrar()` traduce `InvalidToken` a un `ValueError` con mensaje claro, que la interfaz muestra sin interrumpir el programa.
- `.env.example` documenta la variable y advierte que perder la clave impide recuperar los datos; `requirements.txt` agrega `cryptography`.

#### Revisión técnica

- Qué cifrar: se pidió a la IA una propuesta y sugirió cifrar también nombre y correo. Se descartó: el RUT, el nombre y el correo funcionan como identificadores (clave única, búsqueda por RUT, generación del nombre de usuario), y cifrarlos con IV aleatorio impediría las restricciones `UNIQUE` y las búsquedas. Se cifran los datos que la guía llama personales y que no participan en consultas: dirección, teléfono y salario.
- Algoritmo: se evaluó `hashlib`/`hmac` (ya usados para contraseñas). Se descartó porque un hash no es reversible y estos datos deben leerse; se necesita cifrado simétrico autenticado. Fernet, de la librería `cryptography`, aporta autenticación (detecta manipulación) y evita elegir modos y IV a mano.
- Gestión de la clave: la IA propuso derivarla de la contraseña del administrador. Se descartó porque cambiar la contraseña dejaría ilegible la base y porque el sistema tiene varios administradores. La clave vive en `.env`, fuera del repositorio, igual que la llave de la API.
- Compatibilidad: en lugar de exigir una base vacía, se conservó la lectura de valores heredados y se agregó la migración automática, para que la base del equipo siga funcionando.

#### Validación

- `py -3 -m py_compile main.py interfaz.py test_nucleo.py` finalizó correctamente.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 47 pruebas en verde. Las cinco nuevas verifican que la base solo contiene tokens (sin rastro de la dirección ni del salario), que cifrar y descifrar devuelve el original y que dos cifrados del mismo texto difieren, que una clave incorrecta produce el mensaje "no corresponde", que una clave vacía o no Fernet se informa, y que los valores en texto plano se cifran al iniciar y luego se leen correctamente.
- Prueba sobre una copia de `ecotech_solutions.db` real: al actualizar la ficha de un empleado con dirección, teléfono y salario, las tres columnas quedan como tokens `gAAAAA…` y `Listar empleados` (detallado) muestra `Los Aromos 45 | +56 9 5555 1234 | Salario: $950,000`.

### Cambio 38 - Alineación con la Unidad 1, paso 3: registro de cuentas restringido

**Fecha:** 2026-09-21
**Archivos modificados:** `interfaz.py`, `test_nucleo.py`
**Objetivo:** cumplir el requisito "el sistema debe permitir a los administradores de recursos humanos registrar nuevos empleados" y el criterio 3.1.2.G.15 (restringir el acceso mediante controles de flujo y sesión), cerrando el autoregistro que permitía a cualquier persona crear una cuenta `empleado` desde la pantalla de acceso.

#### Hallazgo

La opción `Registrar usuario` de la pantalla de acceso estaba disponible siempre y solo exigía código secreto para `admin` y `rrhh`. Cualquier persona con acceso al programa podía crearse una cuenta `empleado`, registrar horas y consultar las APIs, sin intervención de RR.HH.

#### Implementación

- `mostrar_menu_acceso(con_usuarios)` muestra `Registrar administrador inicial` únicamente cuando la tabla `usuarios` está vacía. `procesar_opcion_acceso()` recibe ese estado: con cuentas existentes, la opción `2` responde que el registro lo realiza un administrador o RR.HH. desde el sistema y no crea nada.
- `registrar_usuario_menu()` acepta `rol_forzado`; `registrar_primer_usuario()` lo usa con `"admin"`, de modo que el primer usuario es siempre administrador (con el código `ECOTECH_CODIGO_ADMIN`) y puede crear el resto de las cuentas. Sin esta regla, un primer usuario `empleado` dejaría el sistema sin nadie capaz de registrar cuentas.
- `hay_usuarios()` reemplaza la consulta repetida en el bucle de acceso, que quedó más simple (sin el caso especial `opcion == "2"`).
- `autenticar_usuario()` rechaza usuario o contraseña vacíos antes de consultar la base, como pide la guía ("validar las credenciales ingresadas evitando valores vacíos").

#### Revisión técnica

Se evaluó con apoyo de IA mantener el autoregistro de empleados con un "código de invitación" adicional. Se descartó: seguiría siendo un secreto compartido más que administrar y no corresponde al requisito, que asigna el registro a RR.HH. La creación de cuentas ya existía en la opción 13 con verificación de rol, por lo que el cambio consistió en cerrar la puerta duplicada, no en construir una nueva.

#### Validación

- `py -3 -m py_compile interfaz.py test_nucleo.py` finalizó correctamente.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 52 pruebas en verde. Las cinco nuevas verifican que sin cuentas el menú ofrece registrar el administrador inicial; que ese registro no pregunta el rol y guarda `admin`; que con cuentas la opción no aparece, la entrada `2` responde con el mensaje de RR.HH. y no crea usuarios; que usuario o contraseña vacíos se rechazan sin consultar la base; y que el login correcto devuelve el usuario con su rol.

### Cambio 39 - Alineación con la Unidad 1, paso 4: gerente y descripción de tareas

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`
**Objetivo:** cumplir dos requisitos de la guía de la Unidad 1: "cada departamento tendrá un nombre y un gerente asociado" y "los empleados deben poder ingresar la fecha, la cantidad de horas trabajadas y una breve descripción de las tareas realizadas".

#### Implementación

- Esquema: `departamentos.rut_gerente TEXT REFERENCES empleados(rut) ON DELETE SET NULL` y `registros_tiempo.descripcion_tarea TEXT NOT NULL DEFAULT ''`. Ambas columnas se agregan con `ALTER TABLE ... ADD COLUMN` en `inicializar_bd()` cuando faltan; SQLite lo permite porque tienen valor por defecto nulo o vacío, así que no fue necesaria una reconstrucción como la de `empleados`.
- `Departamento.gerente: Empleado | None` en el modelo; `guardar_departamento()` y `actualizar_departamento()` aceptan el RUT del gerente; `asignar_gerente_departamento()` lo asigna o lo quita (`None`); `verificar_gerente()` normaliza el RUT y exige que exista como empleado. `listar_departamentos()` devuelve el nombre completo del gerente mediante `LEFT JOIN`.
- `RegistroTiempo.descripcion_tarea` con `validar_descripcion_tarea()` (texto obligatorio cuando se informa, máximo 200 caracteres). Se persiste en `guardar_registro_tiempo()`, se lee en `listar_registros_tiempo()` y se puede modificar en `actualizar_registro_tiempo()`. Los registros anteriores conservan una descripción vacía.
- Exportadores: `ExportadorPDF` agrega la descripción al final de cada línea; `ExportadorExcel` agrega la columna `descripcion_tarea` entre comillas, duplicando las comillas internas según el formato CSV.
- Interfaz: crear departamento pide un gerente opcional; el submenú de departamentos incorpora `3. Asignar o cambiar gerente`; el listado de departamentos muestra el gerente; registrar horas solicita la descripción (`leer_descripcion_tarea()` repite solo ese campo si está vacía o es demasiado larga); el listado de registros y los reportes la incluyen.

#### Revisión técnica

- La IA propuso `gerente` como texto libre, como en el UML de la Unidad 1 (`director: str`). Se descartó: un gerente es un empleado de la empresa, y modelarlo como clave foránea evita duplicar nombres, permite mostrar sus datos desde la ficha y define qué pasa si el empleado se elimina (`ON DELETE SET NULL`, para no borrar el departamento).
- Se evaluó exigir que el gerente pertenezca al departamento que dirige. Se descartó porque la guía no lo pide y la organización puede designar un gerente de otra área; la restricción se puede agregar más adelante sin cambiar el esquema.
- Para el CSV la IA sugirió concatenar la descripción sin comillas. Se corrigió: una descripción con comas rompería las columnas; se aplica el escapado estándar de CSV (campo entre comillas, comillas internas duplicadas), verificado por prueba.

#### Validación

- `py -3 -m py_compile main.py interfaz.py test_nucleo.py` y `ruff check --select F` sin nombres indefinidos.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 60 pruebas en verde. Las ocho nuevas verifican la migración de ambas columnas sobre una base antigua (registro previo con descripción vacía); crear departamento con gerente, quitarlo, rechazar un RUT inexistente y un departamento inexistente; que eliminar al gerente deja el departamento sin gerente sin borrarlo; que el modelo rechaza un gerente que no es `Empleado`; que la descripción se normaliza, se persiste, se actualiza y rechaza más de 200 caracteres; que ambos exportadores la incluyen (CSV con escapado de comillas); y los flujos de menú de registro de horas (repite la descripción vacía) y de creación y asignación de gerente.
- Migración sobre una copia de `ecotech_solutions.db` real: columnas agregadas y `foreign_key_check` vacío.

### Cambio 40 - Alineación con la Unidad 1, paso 5: CRUD completo desde el menú

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`, `.gitignore` (base de datos retirada del repositorio)
**Objetivo:** cumplir los requisitos de la guía de la Unidad 1 "gestionar departamentos (crear, modificar y eliminar)", "gestionar proyectos (crear, actualizar y eliminar)" y "asignar y desasignar empleados de proyectos", y cerrar el indicador 2.1.3.G.5 (operaciones CRUD accesibles desde la aplicación). Las funciones `actualizar_*` y `eliminar_*` existían en `main.py` desde la Unidad 2, pero el menú solo ofrecía crear y listar.

#### Implementación

- `main.py`: `desasignar_empleado_proyecto_bd()` elimina la fila de `empleado_proyecto` y devuelve si existía; `listar_empleados_proyecto()` y `contar_registros_proyecto()` apoyan los flujos del menú; `desasignar_empleado_de_proyecto()` es la operación de dominio simétrica a `asignar_empleado_a_proyecto()` prevista en `uml.mmd`. `eliminar_departamento()` rechaza con mensaje claro un departamento con empleados (antes fallaba con un error de clave foránea de SQLite). `eliminar_empleado()` elimina también la cuenta de acceso vinculada en la misma transacción.
- `interfaz.py`: submenús `Gestionar departamentos` (crear, editar nombre, eliminar, gerente, departamento de empleado), `Gestionar empleados` (editar ficha, eliminar) y `Gestionar proyectos` (crear, editar, eliminar, asignar, desasignar), y la opción `Editar o eliminar registros de tiempo` para todos los roles. `ejecutar_submenu()` reemplaza los bucles repetidos de cada submenú. `leer_o_conservar()` implementa la edición campo por campo (Enter conserva el valor actual; un error repite solo ese campo) reutilizando los conversores `a_fecha()`, `a_fecha_fin()`, `a_monto()`, `a_horas()` y `validar_correo()`, que ahora también usan los formularios de alta. `confirmar()` exige `s` antes de eliminar. `obtener_fila_empleado()`, `obtener_proyecto()` y `obtener_departamento()` centralizan las búsquedas por identificador. El menú principal pasa de 16 a 17 opciones, con cada entidad en el par `Gestionar … / Listar …`.
- Reglas de negocio aplicadas en el menú: no se puede eliminar la propia ficha; al editar un empleado se conserva su departamento; al editar un departamento se conserva su gerente; eliminar un proyecto informa cuántos registros de horas se perderán; desasignar conserva las horas.

#### Revisión técnica

- Desasignar y horas registradas: la IA propuso borrar los registros del empleado en ese proyecto al desasignarlo, para mantener la coherencia con la regla "debe estar asignado para registrar horas". Se descartó: las horas son trabajo realizado, se necesitan para el informe y el cálculo de pago, y la regla solo debe impedir registros nuevos. El menú lo informa expresamente.
- Eliminar empleado y cuenta: la IA sugirió dejar la cuenta y confiar en `ON DELETE SET NULL`. Se descartó porque la cuenta seguiría activa sin ficha y con permisos de empleado; se elimina en la misma transacción, igual que ya hacía `eliminar_usuario()` en sentido inverso.
- Edición: la primera versión pedía todos los campos de nuevo. Se reemplazó por `leer_o_conservar()` para que el usuario solo escriba lo que cambia; la validación de la fecha de fin respecto del inicio se movió al lector (`a_fecha_fin()`) porque, validada solo en `actualizar_proyecto()`, un error hacía perder el formulario completo (detectado por una prueba).
- Eliminar departamento con empleados: se prefirió rechazar la operación con un mensaje a reasignar automáticamente o dejar a los empleados sin departamento, porque esa decisión corresponde a RR.HH.
- Se retiró `ecotech_solutions.db` del control de versiones (ya figuraba en `.gitignore`): contiene datos cifrados con la clave de cada equipo y se regenera vacía al primer inicio.

#### Validación

- `py -3 -m py_compile main.py interfaz.py test_nucleo.py` y `ruff check --select F` sin nombres indefinidos.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 71 pruebas en verde. Las once nuevas verifican: desasignar conserva las horas, impide registros nuevos y es idempotente (base y dominio); eliminar un departamento con empleados se rechaza y sin empleados funciona; eliminar un empleado borra su cuenta y sus horas; editar la ficha con Enter conserva los valores, repite solo el teléfono y el salario inválidos y mantiene la dirección cifrada; eliminar empleado exige confirmación y rechaza la propia ficha; editar y eliminar departamento conservan el gerente e informan un ID inexistente; editar proyecto repite solo la fecha de fin anterior al inicio, desasignar informa al empleado y falla si no estaba asignado, y eliminar borra asignaciones y registros; un empleado no puede editar registros ajenos y sí los propios (horas con coma decimal); el submenú vuelve con `0` y rechaza opciones inválidas; el menú principal agrupa el CRUD por entidad y el rol `empleado` ve las opciones 2, 4, 6, 7, 8, 9, 10, 11 y 12.
- Ejecución manual sobre una base nueva: registro del administrador inicial, creación de departamento, proyecto y empleado, edición con Enter, desasignación y eliminaciones con confirmación.

### Cambio 41 - Alineación con la Unidad 1, paso 6: informes exportados a archivo

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`, `.gitignore`, `uml.png` (render de `uml.mmd`)
**Objetivo:** cumplir el requisito "generar informes de empleados, departamentos, proyectos y registros de tiempo, exportables a PDF o Excel" de la guía de la Unidad 1. Hasta ahora el sistema solo mostraba en pantalla un informe de horas; no generaba archivos ni cubría las otras tres entidades. Con este cambio el código coincide con `uml.mmd`.

#### Implementación

- `Informe` (dataclass inmutable): título, columnas y filas. Valida que haya columnas y que cada fila tenga un valor por columna; `nombre_archivo` deriva un nombre seguro del título (solo letras, dígitos y guiones bajos). `construir_informe_registros()`, `construir_informe_empleados()`, `construir_informe_departamentos()` y `construir_informe_proyectos()` construyen el informe a partir de las filas que ya devuelven las funciones `listar_*`.
- `IExportador` gana `extension` y `codificacion`; `exportar()` recibe un `Informe` en lugar de una lista de registros, de modo que un mismo exportador sirve para las cuatro entidades. `ExportadorPDF` alinea las columnas (`.txt`); `ExportadorExcel` usa el módulo `csv` (escapado estándar) y codificación `utf-8-sig` para que Excel reconozca los acentos.
- `ServicioReportes.guardar(informe, carpeta)` crea la carpeta si no existe y escribe `<nombre>_<AAAAMMDD_HHMMSS>.<extension>`, devolviendo la ruta.
- Interfaz: la opción 10 pasa a un submenú (horas, empleados, departamentos, proyectos) para `admin` y `rrhh`; el rol `empleado` obtiene directamente el informe de sus horas. `leer_exportador()` repite el formato hasta recibir `1` o `2`; `exportar_informe()` muestra el contenido, lo guarda en `informes/` (junto a la base de datos) e imprime la ruta. Se eliminó la construcción artificial de objetos `Empleado`/`Proyecto` con valores ficticios ("Reporte", "reporte@ecotech.cl") que usaba el informe anterior.
- `informes/` se agrega a `.gitignore`. El diagrama `uml.mmd` no cambia: `IExportador.codificacion` y la propiedad derivada `Informe.nombre_archivo` son detalles de formato de archivo, y las funciones `construir_informe_*` son constructoras de datos, no parte del modelo de clases. Con este paso el código coincide con `uml.mmd`, por lo que se incorpora `uml.png` renderizado desde mermaid.live.

#### Revisión técnica

- Datos personales en el informe de empleados: la IA incluyó dirección, teléfono y salario porque el listado detallado de RR.HH. los muestra. Se descartó: un archivo en `informes/` queda fuera del cifrado en reposo de la base y podría copiarse o enviarse; el informe lleva solo datos laborales (ID, RUT, nombre, correo, cargo, departamento, fecha de contrato). La prueba verifica que ninguno de los tres datos aparece.
- CSV: se reemplazó la concatenación manual con comillas duplicadas (Cambio 39) por `csv.writer`, que resuelve comas, comillas y saltos de línea en cualquier columna, no solo en la descripción. Se conservó la prueba original del escapado para comprobar que el resultado es el mismo.
- Nombre del archivo: la IA proponía usar el título tal cual. Se sanitiza con una expresión regular para evitar caracteres inválidos en Windows y se agrega fecha y hora para no sobrescribir informes anteriores.
- PDF real: se evaluó generar PDF binario con una librería externa (`reportlab`, `fpdf2`). Se mantuvo la representación de texto porque la guía admite "PDF o Excel" y el proyecto no exige dependencias adicionales para la defensa; el diseño con `IExportador` permite agregar un `ExportadorPDFBinario` sin tocar el servicio ni el menú.

#### Validación

- `py -3 -m py_compile main.py interfaz.py test_nucleo.py` y `ruff check --select F` sin nombres indefinidos.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 77 pruebas en verde. Las seis nuevas verifican la validación e inmutabilidad de `Informe` y su nombre de archivo; la alineación de columnas y el vacío para `None` en texto; el escapado de comas y comillas en CSV; que `guardar()` crea la carpeta, usa la extensión del exportador y escribe el BOM en CSV; que el informe de empleados excluye dirección, teléfono y salario; y que el menú no genera archivo sin datos, repite un formato inválido y guarda el informe de departamentos en la carpeta indicada.

### Cambio 42 - Alineación con la Unidad 1, paso 7: política de contraseñas

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`
**Objetivo:** cumplir el requisito "autenticación robusta con contraseñas seguras" de la guía de la Unidad 1 y reforzar el criterio 3.1.2. Hasta ahora la única condición era que la contraseña no estuviera vacía.

#### Implementación

- `validar_contrasena()` en `main.py`: al menos `LARGO_MINIMO_CONTRASENA` (8) caracteres, con al menos una letra y un dígito; los espacios en los bordes se descartan. Se aplica en `generar_hash_contrasena()`, único punto por el que pasa toda contraseña que se persiste (`guardar_usuario()` y `guardar_usuario_con_empleado()`), y en `Usuario.actualizar_contrasena()`, de modo que ninguna ruta de código puede guardar una contraseña débil.
- `leer_contrasena_nueva()` en la interfaz muestra la política antes de pedir la contraseña y repite solo ese campo ante un valor inválido; se usa en el registro de cuentas. `leer_contrasena_validada()` se conserva para los códigos secretos de rol, que no están sujetos a la política.
- El login no valida la política (solo rechaza vacíos): las cuentas creadas antes de este cambio deben poder seguir entrando; la política se exige al crear o cambiar la contraseña.

#### Revisión técnica

- La IA propuso exigir además mayúscula, minúscula y símbolo. Se descartó: para un sistema interno de consola la combinación de largo mínimo y letras + dígitos es suficiente y no empuja a los usuarios a anotar la contraseña; la función centraliza la regla y puede endurecerse en una sola línea.
- Se evaluó validar en el constructor de `Usuario`. Se descartó porque el objeto también representa a la sesión autenticada (con la contraseña sustituida por asteriscos) y a filas leídas de la base (hash), que no deben cumplir la política. Validar al persistir es el punto correcto.
- Hallazgo propio: al revisar `__all__` para exportar `validar_contrasena` se comprobó que el Cambio 41 lo había eliminado por error (el reemplazo del bloque de informes abarcó la lista, que estaba entre `ServicioReportes` y las operaciones de dominio). El programa no se vio afectado porque `interfaz.py` importa nombres explícitos, pero la API pública documentada en el Readme había desaparecido. Se restauró generándola desde los nombres públicos del módulo (87 entradas), con lo que además quedó completa (antes faltaban `actualizar_*`, `eliminar_*` y otros).

#### Validación

- `py -3 -m py_compile` y `ruff check --select F` sin errores.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 81 pruebas en verde. Las cuatro nuevas verifican que la validación acepta una contraseña válida (recortando espacios) y rechaza vacía, corta, sin dígitos, sin letras o solo espacios; que `guardar_usuario()` no persiste una contraseña débil y que `actualizar_contrasena()` la rechaza; que el menú repite la contraseña con el mensaje correspondiente hasta que cumple; y que el código secreto `1234` sigue aceptándose para registrar al administrador. Las pruebas existentes que persistían la contraseña `clave` se actualizaron a una que cumple la política.

### Cambio 43 - Alineación con la Unidad 1, paso 8: búsquedas

**Fecha:** 2026-09-21
**Archivos modificados:** `main.py`, `interfaz.py`, `test_nucleo.py`
**Objetivo:** cumplir el requisito "creación, edición, búsquedas y eliminación de departamentos" de la guía de la Unidad 1 (la búsqueda era lo único que faltaba) y ofrecer la misma búsqueda para empleados, que es la entidad con más filas.

#### Implementación

- `listar_departamentos(connection, filtro=None)` y `listar_empleados(connection, filtro=None)` aceptan un texto opcional: departamentos por nombre; empleados por RUT, nombre o apellido. La coincidencia es parcial y sin distinguir mayúsculas (`LIKE` de SQLite). Sin filtro se comportan igual que antes, por lo que ningún flujo existente cambió.
- `patron_busqueda()` valida el texto y escapa `\\`, `%` y `_` antes de envolverlo en `%…%`; las consultas usan `ESCAPE '\\'` para que esos caracteres se busquen literalmente.
- Interfaz: las opciones 2 y 4 pasan a `Listar o buscar …` y piden un filtro opcional (`leer_filtro()`; Enter lista todo). Los mensajes distinguen "no hay registros" de "no hay coincidencias con 'x'". Los listados internos que preceden a pedir un RUT o un ID no piden filtro.

#### Revisión técnica

- La IA propuso construir la cláusula `WHERE` concatenando el texto del usuario en la consulta. Se descartó por inyección SQL: el patrón viaja como parámetro y solo la estructura de la consulta se arma en código.
- Sin escapar los comodines, buscar `%` devolvería todos los departamentos y `_` coincidiría con cualquier carácter; la prueba `test_los_comodines_de_like_se_tratan_como_texto` cubre ambos casos con un departamento llamado `100% Verde`.
- Se evaluó buscar también por correo y cargo. Se dejó fuera para mantener el filtro predecible; agregar columnas es una línea en la consulta.
- No se buscan dirección ni teléfono porque están cifrados con IV aleatorio: `LIKE` no puede compararlos y descifrar toda la tabla para filtrar en memoria anularía el propósito del cifrado.

#### Validación

- `py -3 -m py_compile` y `ruff check --select F` sin errores.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 85 pruebas en verde. Las cuatro nuevas verifican la coincidencia parcial sin distinguir mayúsculas y el filtro vacío; el escapado de `%` y `_`; la búsqueda de empleados por RUT, nombre y apellido; y el menú (Enter lista todo, texto filtra, sin coincidencias informa el filtro).

## Fase 5 - Documentación y cierre (cambios 44 a 48)

### Cambio 44 - Inventario de fragmentos apoyados por IA

**Fecha:** 2026-09-21
**Archivos modificados:** `VALIDACION_IA.md`, `Readme.md`
**Objetivo:** cumplir el indicador 2.1.5 de la defensa ("identificar con transparencia qué fragmentos del código fueron apoyados o generados preliminarmente mediante herramientas de IA") con una vista única, ya que hasta ahora esa información estaba repartida en los 43 cambios.

#### Implementación

Se agregó la sección "Inventario de fragmentos apoyados por IA" al inicio de este archivo: una tabla por fragmento (módulo y funciones o clases), el cambio donde se documenta, la decisión (adoptado, modificado, descartado, propio) y el criterio técnico aplicado (seguridad, coherencia con el modelo, estabilidad, mantenibilidad). El Readme enlaza la sección desde el criterio 2.1.5.

#### Revisión técnica

La tabla se construyó leyendo las secciones "Revisión técnica" de cada cambio, no de memoria; cada fila cita el cambio que la respalda para que el evaluador pueda verificarla. Se prefirió clasificar por fragmento y no por archivo completo, porque en los tres módulos conviven código adoptado y código reescrito.

#### Validación

- Cada fila referencia un cambio existente y funciones presentes en el código actual (`grep` de los nombres citados en `main.py`, `interfaz.py` y `servicios_externos.py`).

### Cambio 45 - Reorganización del Readme orientada a la evaluación

**Fecha:** 2026-09-21
**Archivo modificado:** `Readme.md`
**Objetivo:** que el docente encuentre en menos de un minuto qué se evalúa, dónde está la evidencia y cómo ejecutar el sistema. El Readme había crecido de forma incremental durante 44 cambios y mezclaba estado, instrucciones, criterios y un historial de verificaciones de más de 30 puntos.

#### Implementación

Nueva estructura con índice: (1) resumen por unidad con enlaces a la evidencia; (2) inicio rápido con `.env` y primer inicio; (3) menú y comportamientos clave; (4) arquitectura y UML; (5) cumplimiento por unidad en tres tablas (requisitos U1, criterios U2, criterios U3); (6) seguridad; (7) servicios externos; (8) pruebas; (9) decisiones técnicas destacadas con referencia a su cambio; (10) uso de IA; (11) anexo con las verificaciones manuales condensadas. Se corrigieron referencias desactualizadas (opciones de clima, indicador y pago pasaron a 11-13; el menú de `admin` llega a 17; el modelo proviene de la Unidad 1, no de la 2) y una frase mal concatenada en la descripción de `test_nucleo.py`.

#### Revisión técnica

No se eliminó contenido sustantivo: las validaciones históricas se resumieron en el anexo y las decisiones de diseño se concentraron en una tabla que remite al cambio que las justifica, para que el evaluador pueda verificar cada afirmación. Cada dato del Readme (iteraciones PBKDF2, timeout, conteo de pruebas, numeración del menú) se contrastó con el código antes de publicarlo.

#### Validación

- Los enlaces internos del índice siguen la convención de anclas de GitHub.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 85 pruebas en verde (sin cambios de código).

### Cambio 46 - Reorganización de este registro por fases y por criterio

**Fecha:** 2026-09-21
**Archivo modificado:** `VALIDACION_IA.md`
**Objetivo:** que el evaluador pueda ir directamente a la evidencia de un criterio o al origen de un fragmento sin leer 1 300 líneas en orden cronológico, conservando íntegro el historial.

#### Implementación

- Portada con la estructura común de cada entrada y tres rutas de lectura (inventario, mapa por criterio, índice).
- Índice completo con enlaces, agrupado en cinco fases: Unidad 2 inicial (cambios 1 a 16 y anexos), roles y validación interactiva (17 a 26), Unidad 3 (27 a 34), alineación con la Unidad 1 (35 a 43) y documentación y cierre (44 en adelante).
- Nueva tabla **Mapa por criterio de la rúbrica** (2.1.1 a 2.1.5 y 3.1.1 a 3.1.4) que remite a los cambios donde está la evidencia.
- Los cambios pasan de nivel 2 a nivel 3 bajo el encabezado de su fase; sus subsecciones, a nivel 4. Se unificaron los títulos internos sin tilde (`Implementacion`, `Validacion`) y tres títulos de cambio (10, 11 y 12). El contenido de cada entrada no se modificó.

#### Revisión técnica

La reorganización se hizo con un script que separa las entradas por encabezado, las agrupa y regenera el índice; luego un segundo script comparó línea por línea el contenido anterior con el nuevo (0 líneas perdidas) y comprobó que todas las anclas del índice apuntan a un encabezado existente. Se prefirió agrupar por fase y no por criterio para no duplicar entradas: un mismo cambio suele aportar evidencia a varios criterios, y para eso está el mapa.

#### Validación

- Script de verificación: 45 cambios, 6 anexos y el material privado presentes; 0 líneas de contenido perdidas; 0 anclas rotas.
- `py -3 -m unittest test_nucleo test_servicios_externos`: 85 pruebas en verde (sin cambios de código).

### Cambio 47 - Estructura del repositorio

**Fecha:** 2026-09-23
**Archivos movidos:** `test_nucleo.py` y `test_servicios_externos.py` a `tests/`; `uml.mmd` y `uml.png` a `docs/`; `Rubrica.pdf` y las guías de las unidades a `docs/evaluacion/`
**Archivo agregado:** `docs/uml_original_unidad1.png` (diagrama entregado en la Unidad 1)
**Archivos modificados:** `Readme.md`
**Objetivo:** que quien abra el repositorio vea primero lo que evalúa la rúbrica (el Readme, el registro de validación y los tres módulos ejecutables) y no una lista de quince archivos donde el código, las pruebas, los diagramas y los PDF de la asignatura estaban al mismo nivel.

#### Implementación

- Los tres módulos (`main.py`, `interfaz.py`, `servicios_externos.py`) se mantienen en la raíz: mover el código a `src/` obligaría a configurar rutas o a instalar el paquete para ejecutar `py -3 main.py`, que es la forma documentada de usar el sistema.
- `tests/` incluye un `__init__.py` con el comando de ejecución en su docstring. Sin ese archivo, `unittest discover` falla con "Start directory is not importable"; con él funcionan tanto `py -3 -m unittest discover -s tests -t .` como `py -3 -m unittest tests.test_nucleo`. Las pruebas siguen importando `main` e `interfaz` porque se ejecutan desde la raíz.
- `docs/` reúne el modelo (`uml.mmd`, `uml.png`) y, en `docs/evaluacion/`, la rúbrica y las guías de las tres unidades.
- Se incorporó el diagrama original de la Unidad 1 como `docs/uml_original_unidad1.png`. Estaba solo en el equipo; conservarlo permite contrastar el modelo inicial (`director: str`, `password_hash`, `estado`, sin cifrado ni servicios externos) con el modelo vigente, que es lo que pide la comparación entre modelo inicial y modelo final.
- `Readme.md` actualiza el árbol del proyecto, las rutas de las suites y el comando de pruebas.

#### Revisión técnica

Se evaluó mover también los módulos a `src/` y renombrar `Readme.md` como `README.md`. Lo primero se descartó por el costo de ejecución descrito arriba; lo segundo, porque en Windows un cambio que solo altera mayúsculas obliga a un renombrado en dos pasos y GitHub muestra igual el archivo actual. Se comprobó que ningún módulo ni prueba abre por ruta los archivos movidos: `DATABASE_PATH` y la carpeta `informes/` se calculan desde `main.py`, que no cambió de lugar.

#### Validación

- `py -3 -m unittest discover -s tests -t .`: 85 pruebas en verde desde la nueva ubicación, antes y después de mover los archivos.
- `git mv` conserva el historial de cada archivo.

### Cambio 48 - Ficha de empleado obligatoria para toda cuenta

**Fecha:** 2026-09-23
**Archivos modificados:** `interfaz.py`, `tests/test_nucleo.py`, `Readme.md`
**Objetivo:** corregir que el registro de una cuenta `admin` no pidiera el RUT ni el resto de la ficha. Se detectó al probar el primer arranque: el administrador inicial quedaba sin identificación de persona.

#### Hallazgo

`registrar_usuario_menu()` creaba la ficha solo cuando el rol era `empleado` o `rrhh`. Como el primer usuario es siempre `admin`, ese registro saltaba RUT, correo, cargo, dirección, teléfono, fecha de contrato y salario. La cuenta quedaba con `rut_empleado` nulo: no aparecía en el listado de empleados, no podía registrar sus propias horas ni calcular su pago, y nada la vinculaba a una persona.

#### Implementación

- La ficha pasa a ser obligatoria para cualquier rol: se eliminó la condición y con ella la rama que guardaba un usuario sin empleado, de modo que `registrar_usuario_menu()` siempre usa `guardar_usuario_con_empleado()`, que inserta empleado y usuario en una sola transacción. `guardar_usuario` salió del import de la interfaz (sigue en la API pública del núcleo, que la usan las pruebas).
- El mensaje de confirmación informa el RUT de la ficha creada.
- `Usuario.empleado` sigue admitiendo `None` en el modelo: representa también la sesión autenticada y las filas de cuentas anteriores a este cambio, que deben poder iniciar sesión.

#### Revisión técnica

El diseño anterior suponía que `admin` podía ser una cuenta técnica del sistema y no un trabajador de la empresa. Se revisó contra la guía de la Unidad 1, que modela a las personas como empleados con RUT e ID automático y no contempla cuentas sin persona; además, la asimetría producía efectos que un evaluador notaría en la demostración (el administrador no figuraba entre los empleados). Se evaluó pedir solo el RUT y dejar el resto vacío: se descartó porque la ficha incompleta obligaría a editarla después y porque `Empleado` ya exige correo y cargo. También se evaluó preguntar si se desea asociar una ficha: se descartó por dejar abierta la posibilidad de cuentas sin RUT, que es justamente el defecto corregido.

Queda una limitación conocida: crear una cuenta para alguien que ya tiene ficha falla por el `UNIQUE` del RUT, porque este flujo siempre inserta un empleado nuevo. Es el mismo comportamiento que ya tenían `empleado` y `rrhh`; vincular una cuenta a una ficha existente sería una opción aparte del menú.

#### Validación

- `py -3 -m unittest discover -s tests -t .`: 86 pruebas en verde. La prueba del primer administrador ahora comprueba que la cuenta queda con `rut_empleado`, que el empleado aparece en el listado con su cargo y que recibe el `id_empleado` automático; la nueva prueba verifica que un RUT con dígito verificador incorrecto se repite sin reiniciar el formulario y que el registro termina con el RUT válido.
- Prueba manual sobre una base nueva: el registro del administrador inicial solicita RUT, correo, cargo, dirección, teléfono, fecha de contrato y salario, y la opción 4 lo muestra en el listado de empleados.
