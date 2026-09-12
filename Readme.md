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

## Requisitos

- Python 3.10 o superior.
- No se requieren dependencias externas para la etapa actual.
- SQLite se utiliza mediante la librería estándar `sqlite3`.

## Estructura del proyecto

```text
Ecotech_solutions/
├── main.py
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
- Rollback automático ante errores de SQLite.
- Cierre controlado ante interrupciones del usuario o fin de entrada.

### Criterio 2.1.5: revisión crítica del código apoyado por IA

**Estado: completado.**

La revisión detectó que algunas operaciones de actualización SQLite podían saltarse las validaciones aplicadas al crear entidades. Se corrigió el problema reutilizando las validaciones de texto, fechas y horas en las operaciones CRUD.

Además, se reforzó la seguridad del modelo de usuario: la propiedad `contrasena` ya no expone el valor real en texto plano, y el acceso interno se controla mediante `obtener_contrasena_interna()` y `verificar_contrasena()`. Esto evita fugas de credenciales por lectura directa del objeto y mantiene el flujo de autenticación y persistencia bajo validación explícita.

La revisión crítica se documenta en `VALIDACION_IA.md`, donde se describen los hallazgos, las decisiones técnicas y la validación de cada mejora.

## Ejecución

Desde la carpeta del proyecto:

```powershell
py -3 main.py
```

Al iniciar, el programa crea `ecotech_solutions.db` si no existe, crea sus tablas y muestra un menú para:

- Crear y listar departamentos, empleados y proyectos.
- Asignar empleados a proyectos.
- Registrar horas trabajadas.
- Consultar registros de tiempo.
- Crear y listar usuarios asociados a empleados.
- Solicitar login antes de entrar al menú principal.
- Registrar usuarios con rol `admin` o `empleado`.
- Permitir que solo un administrador cambie el rol de otro usuario.
- Generar reportes en formato de texto tipo PDF o CSV tipo Excel.

Para cerrar el programa se selecciona la opción `0`. La base de datos se guarda localmente y no se sube a GitHub porque está incluida en `.gitignore`.

En el primer inicio se debe registrar el primer usuario. Para seleccionar el rol `admin` se solicita el código temporal `1234`. Los usuarios nuevos se guardan con hash PBKDF2; los usuarios antiguos se migran automáticamente al iniciar sesión.

Actualmente los roles disponibles son `admin` y `empleado`. La opción de cambiar roles es exclusiva del administrador y permite promover o quitar permisos administrativos a otro usuario.

La salida inicial esperada es:

```text
Base de datos conectada: ecotech_solutions.db
=== ECOTECH SOLUTIONS ===
```

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
- Prueba de registro, login, roles y migración de contraseñas.
- Validación del RUT chileno con cálculo del dígito verificador y rechazo de formatos inválidos.

## Registro de cambios y uso de IA

`VALIDACION_IA.md` registra cada cambio relevante, las decisiones técnicas, el apoyo utilizado de herramientas de IA y las pruebas realizadas. El código generado o sugerido por IA se revisa y ajusta antes de considerarlo parte de la solución final.
