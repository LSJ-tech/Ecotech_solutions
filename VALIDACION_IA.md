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
