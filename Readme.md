# EcoTechSolutions

## Proyecto de la Unidad 2

Sistema de gestión de empleados para la empresa EcoTechSolutions, desarrollado en Python a partir del modelo UML definido para el proyecto.

La Unidad 2 se enfoca en la implementación orientada a objetos, la coherencia entre el diseño UML y el código, la integración posterior con una base de datos, las operaciones CRUD, la validación de datos y el manejo de errores.

## Objetivo

Construir una solución funcional que permita representar y gestionar:

- Departamentos.
- Empleados.
- Proyectos.
- Usuarios del sistema.
- Registros de tiempo trabajado.

El desarrollo se realiza de forma incremental. Cada avance se revisa técnicamente y se documenta en `VALIDACION_IA.md`.

## Estado actual

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

## Correspondencia con el UML

La implementación utiliza `dataclass` para representar las entidades del diagrama y anotaciones de tipo para expresar sus relaciones:

- Un empleado puede pertenecer a un departamento.
- Un empleado puede participar en varios proyectos.
- Un proyecto puede tener varios empleados asignados.
- Un registro de tiempo pertenece a un empleado y a un proyecto.
- Un usuario puede estar asociado a un empleado.

El diagrama original se encuentra en `uml.png`.

## Estructura actual

```text
Ecotech_solutions/
├── main.py
├── README.md
├── VALIDACION_IA.md
├── Rubrica.pdf
├── TI3V21_U2_U3_ES02_GUÍA.docx
└── uml.png
```

## Requisitos

- Python 3.10 o superior.
- No se requieren dependencias externas para la etapa actual.

## Ejecución

Desde la carpeta del proyecto:

```powershell
py -3 main.py
```

La salida esperada es:

```text
Modelo de EcoTechSolutions cargado correctamente.
```

## Validaciones realizadas

- Compilación de `main.py` con `py -3 -m py_compile`.
- Diagnóstico del editor sin errores.
- Instanciación de las entidades principales.
- Verificación de las relaciones entre departamento, empleado, proyecto y registro de tiempo.
- Verificación de que las relaciones no agreguen duplicados.

## Próximas etapas de la Unidad 2

1. Aplicar encapsulamiento, abstracción y reutilización de código según el criterio 2.1.2.
2. Integrar una base de datos y operaciones CRUD según el criterio 2.1.3.
3. Incorporar validaciones y manejo de excepciones según el criterio 2.1.4.
4. Revisar y validar críticamente el código apoyado por IA según el criterio 2.1.5.

## Registro de cambios y uso de IA

`VALIDACION_IA.md` registra cada cambio relevante, las decisiones técnicas, el apoyo utilizado de herramientas de IA y las pruebas realizadas. El código generado o sugerido por IA se revisa y ajusta antes de considerarlo parte de la solución final.
