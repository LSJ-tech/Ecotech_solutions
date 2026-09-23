# Credenciales y base de datos de prueba

Esta guía permite ejecutar el sistema con datos ya cargados, sin registrar nada a mano.

> **Sobre estas credenciales.** Todos los datos de esta base son **ficticios**: los RUT se generaron con dígito verificador válido, y las personas, los proyectos y los sueldos son inventados. Por eso las contraseñas y la clave de cifrado de esta base se publican aquí. La clave con la que el equipo cifra su propia base de trabajo **no está en el repositorio**: vive en el archivo `.env` local, que `.gitignore` excluye.

## 1. Preparar el entorno

Tras clonar el repositorio, desde su carpeta raíz:

```powershell
py -3 -m pip install -r requirements.txt
copy .env.demo .env
py -3 main.py
```

Eso es todo: `.env.demo` ya trae los códigos de rol, la ruta de la base de demostración y su clave de cifrado, de modo que el sistema arranca con los datos cargados.

Qué contiene esa configuración:

| Variable | Valor | Para qué |
|---|---|---|
| `ECOTECH_CODIGO_ADMIN` | `1234` | Se pide al **crear** una cuenta `admin`, no al iniciar sesión |
| `ECOTECH_CODIGO_RRHH` | `12345` | Ídem para una cuenta `rrhh` |
| `ECOTECH_DB_PATH` | `docs/demo/ecotech_demo.db` | La base de demostración incluida en el repositorio |
| `ECOTECH_CLAVE_CIFRADO` | `AF5eSoRH_Oxn…` | Clave Fernet con la que está cifrada esa base |
| `OPENWEATHER_API_KEY` | (vacía) | Credencial personal, no se publica. **No hace falta**: sin ella la consulta de clima usa Open-Meteo, que no exige llave ni registro, y entrega los mismos datos. Los indicadores económicos (opción 12) tampoco necesitan llave |

Si se prefiere partir de cero, `copy .env.example .env` deja el archivo vacío para completarlo a mano.

Para partir de una base vacía, basta con borrar `ECOTECH_DB_PATH` del `.env` y registrar el administrador inicial desde la pantalla de acceso. Para volver a generar la base de demostración desde cero:

```powershell
py -3 datos_ejemplo.py
```

Escribe en la base que indique `ECOTECH_DB_PATH`, así que con el `.env` de arriba regenera la base de demostración.

## 2. Cuentas disponibles

| Usuario | Contraseña | Rol | Persona | Qué permite probar |
|---|---|---|---|---|
| `lsilva` | `EcoTech2026` | admin | Logan Silva Jara | Todo el menú: gestión, roles y eliminación de cuentas |
| `cfuentes` | `Talento2026` | rrhh | Camila Fuentes Muñoz | Gestión completa salvo cambiar roles y eliminar cuentas |
| `mmorales` | `Panel2026sol` | empleado | Matías Morales Ñanco | Vista restringida; tiene 14 horas en dos proyectos |
| `jtapia` | `Sensor2026rio` | empleado | Javiera Tapia Cárdenas | Vista restringida; gerente de Investigación y Desarrollo |
| `scontreras` | `Faena2026norte` | empleado | Sebastián Contreras Vidal | Vista restringida; trabaja en la faena de Calama |
| `avergara` | `Datos2026bio` | empleado | Antonia Vergara Soto | Vista restringida; sin proyectos en curso |

Los códigos `1234` y `12345` se solicitan al **crear** una cuenta `admin` o `rrhh`, no al iniciar sesión.

## 3. Qué contiene la base

- **6 empleados**, cada uno con su cuenta. Dirección, teléfono y salario están cifrados en el archivo.
- **4 departamentos**: Desarrollo Sostenible, Investigación y Desarrollo, Recursos Humanos y Ventas (este último sin gerente ni empleados, a propósito).
- **5 proyectos** con ciudad chilena, para consultar el clima: Calama, Temuco, Santiago, Valparaíso y Concepción.
- **8 registros de horas** con su descripción de tarea.
- **3 indicadores económicos** y **el clima de las cinco ciudades** guardados como respaldo local (2026-09-23), de modo que las opciones 11 y 12 responden aunque el servicio externo falle.

## 4. Recorrido sugerido

Cada punto corresponde a un criterio de la rúbrica.

| Qué probar | Cómo | Criterio |
|---|---|---|
| CRUD completo | Con `lsilva`: crear un departamento (1 → 1), editarlo (1 → 2), listarlo (2) y eliminarlo (1 → 3) | 2.1.3 |
| Integridad referencial | Intentar eliminar "Desarrollo Sostenible", que tiene empleados: el sistema lo impide y explica por qué | 2.1.3 |
| Validación de entradas | Al crear un usuario, escribir el RUT `12345678-9` (dígito verificador incorrecto) o un teléfono con letras: se repite solo ese campo | 2.1.4 |
| Manejo de errores | Escribir un número de opción que no aparece en el menú, o una fecha con formato inválido: el sistema informa y continúa | 2.1.4 |
| Permisos por rol | Entrar como `mmorales` y comparar el menú con el de `lsilva`; escribir `14` (Crear usuario), que no está visible para ese rol | 3.1.2 |
| Gestión de contraseñas | Con cualquier cuenta, opción 18: se exige la contraseña vigente y la nueva debe cumplir la política. Con `lsilva`, opción 19: restablecer la de otra cuenta | 3.1.2 |
| Cifrado en reposo | Abrir `docs/demo/ecotech_demo.db` con cualquier visor SQLite: las columnas `direccion`, `telefono` y `salario` contienen tokens `gAAAAA…` | 3.1.2 |
| Enmascarado del RUT | Con `mmorales`, opción 4: su RUT aparece completo y los de sus compañeros como `****4531-4` | 3.1.2 |
| Informes exportados | Con `lsilva`, opción 10: elegir entidad y formato; el archivo queda en `informes/` | 2.1.2 |
| Consumo de API | Opción 11 (clima del proyecto, vía Open-Meteo sin llave) y opción 12 (indicador económico) | 3.1.1 |
| Continuidad ante fallos | Desconectar la red y repetir la opción 12: se muestra el último valor guardado con su fecha y un aviso | 3.1.3 |
| Cálculo con datos externos | Con `lsilva`, opción 13, RUT `12873094-K`: convierte 14 horas a dólar o euro | 3.1.1 |

## 5. Pruebas automatizadas

```powershell
py -3 -m unittest discover -s tests -t .
```

Son 117 pruebas y no necesitan red ni base de datos: los servicios externos se simulan y las bases se crean en memoria.
