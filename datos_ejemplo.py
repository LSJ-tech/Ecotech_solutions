"""Genera una base de datos de demostración con datos ficticios chilenos.

Sirve para probar el sistema sin registrar todo a mano. Ejecutar desde la raíz
del proyecto:

	py -3 datos_ejemplo.py                      crea ecotech_solutions.db si está vacía
	py -3 datos_ejemplo.py ruta\\a\\otra.db       usa otra ruta

Las contraseñas de las cuentas creadas están en `docs/CREDENCIALES_PRUEBA.md`.
El script se niega a escribir sobre una base que ya tiene cuentas.
"""

from datetime import date
from pathlib import Path
import sys

from main import (
	Empleado,
	Proyecto,
	RegistroTiempo,
	Usuario,
	asignar_empleado_departamento_bd,
	asignar_empleado_proyecto_bd,
	conectar_bd,
	guardar_departamento,
	guardar_proyecto,
	guardar_registro_tiempo,
	guardar_usuario_con_empleado,
	inicializar_bd,
)

# usuario, rol, contraseña, nombre, apellidos, RUT, cargo, dirección, teléfono,
# fecha de contrato, salario y departamento.
PERSONAS = [
	("admin", "EcoTech2026", "Logan", "Silva Jara", "16284531-4",
	 "Administrador de sistemas", "Los Aromos 452, Nunoa", "+56 9 6721 4508",
	 date(2024, 3, 1), 2_300_000, "Investigacion y Desarrollo"),
	("rrhh", "Talento2026", "Camila", "Fuentes Munoz", "17902456-K",
	 "Jefa de Recursos Humanos", "Av. Providencia 1840", "+56 9 8234 1190",
	 date(2024, 6, 15), 1_850_000, "Recursos Humanos"),
	("empleado", "Panel2026sol", "Matias", "Morales Nanco", "12873094-K",
	 "Ingeniero de proyectos", "Bulnes 233, Temuco", "+56 9 5512 7733",
	 date(2025, 1, 6), 2_100_000, "Desarrollo Sostenible"),
	("empleado", "Sensor2026rio", "Javiera", "Tapia Cardenas", "20145678-9",
	 "Desarrolladora de software", "Av. Matta 967, Santiago", "+56 9 7745 2208",
	 date(2025, 3, 10), 1_600_000, "Investigacion y Desarrollo"),
	("empleado", "Faena2026norte", "Sebastian", "Contreras Vidal", "15234876-2",
	 "Tecnico en terreno", "Granaderos 88, Calama", "+56 9 6690 3417",
	 date(2025, 8, 1), 950_000, "Desarrollo Sostenible"),
	("empleado", "Datos2026bio", "Antonia", "Vergara Soto", "18456123-9",
	 "Analista de datos", "Freire 1120, Concepcion", "+56 9 9058 6621",
	 date(2026, 2, 17), 1_450_000, "Investigacion y Desarrollo"),
]

# Nombre del departamento y RUT de su gerente. Ventas queda sin gerente a propósito,
# para mostrar ese caso en el listado.
DEPARTAMENTOS = [
	("Desarrollo Sostenible", "12873094-K"),
	("Investigacion y Desarrollo", "20145678-9"),
	("Ventas", None),
	("Recursos Humanos", "17902456-K"),
]

# La ciudad es la que consulta el servicio de clima.
PROYECTOS = [
	("Planta fotovoltaica Atacama", "Instalacion de 4.000 paneles en el desierto",
	 date(2026, 3, 2), None, "Calama"),
	("Parque eolico Renaico", "Mantencion predictiva de 12 aerogeneradores",
	 date(2026, 1, 15), date(2026, 11, 28), "Temuco"),
	("Monitoreo hidrico rio Maipo", "Sensores de caudal y calidad del agua",
	 date(2026, 5, 4), None, "Santiago"),
	("Techos solares Valparaiso", "Paneles en edificios publicos del puerto",
	 date(2026, 6, 1), date(2026, 12, 19), "Valparaiso"),
	("Reciclaje industrial Biobio", "Planta piloto de residuos plasticos",
	 date(2026, 4, 7), None, "Concepcion"),
]

ASIGNACIONES = [
	("16284531-4", "Monitoreo hidrico rio Maipo"),
	("12873094-K", "Planta fotovoltaica Atacama"),
	("12873094-K", "Parque eolico Renaico"),
	("20145678-9", "Monitoreo hidrico rio Maipo"),
	("15234876-2", "Planta fotovoltaica Atacama"),
	("18456123-9", "Reciclaje industrial Biobio"),
]

REGISTROS = [
	("16284531-4", "Monitoreo hidrico rio Maipo", date(2026, 9, 15), 6,
	 "Configuracion de respaldos y control de acceso al sistema"),
	("16284531-4", "Monitoreo hidrico rio Maipo", date(2026, 9, 17), 7.5,
	 "Integracion del panel de sensores con la base de datos"),
	("16284531-4", "Monitoreo hidrico rio Maipo", date(2026, 9, 19), 5.5,
	 "Revision de registros tecnicos y pruebas de la API de clima"),
	("12873094-K", "Planta fotovoltaica Atacama", date(2026, 9, 15), 8,
	 "Revision de estructuras de montaje en faena"),
	("12873094-K", "Parque eolico Renaico", date(2026, 9, 16), 6,
	 "Informe de vibraciones de la turbina 7"),
	("20145678-9", "Monitoreo hidrico rio Maipo", date(2026, 9, 17), 7.5,
	 "Desarrollo del panel de sensores"),
	("15234876-2", "Planta fotovoltaica Atacama", date(2026, 9, 18), 9,
	 "Cableado y puesta a tierra del sector norte"),
	("18456123-9", "Reciclaje industrial Biobio", date(2026, 9, 19), 5,
	 "Analisis de volumenes de residuos procesados"),
]


def nombre_de_usuario(nombre: str, apellidos: str) -> str:
	"""Reproduce la regla del sistema: inicial del nombre y primer apellido."""

	from main import normalizar_identificador

	return normalizar_identificador(nombre[0] + apellidos.split()[0])


def cargar(db_path: str | Path | None = None) -> None:
	"""Crea el esquema y carga los datos de ejemplo si la base no tiene cuentas."""

	connection = conectar_bd(db_path) if db_path else conectar_bd()
	try:
		inicializar_bd(connection)
		if connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]:
			print("La base ya tiene cuentas registradas: no se carga nada.")
			return

		empleados = {}
		for (rol, clave, nombre, apellidos, rut, cargo, direccion, telefono,
		     contrato, salario, _departamento) in PERSONAS:
			empleado = Empleado(
				rut, nombre, apellidos,
				f"{nombre_de_usuario(nombre, apellidos)}@ecotech.cl", cargo,
				direccion=direccion, telefono=telefono,
				fecha_inicio_contrato=contrato, salario=salario,
			)
			usuario = Usuario(
				0, nombre_de_usuario(nombre, apellidos), clave, empleado=empleado, rol=rol
			)
			guardar_usuario_con_empleado(connection, usuario, empleado)
			empleados[rut] = empleado

		departamentos = {
			nombre: guardar_departamento(connection, nombre, rut_gerente)
			for nombre, rut_gerente in DEPARTAMENTOS
		}
		for persona in PERSONAS:
			asignar_empleado_departamento_bd(connection, persona[4], departamentos[persona[10]])

		proyectos = {}
		for nombre, descripcion, inicio, fin, ciudad in PROYECTOS:
			proyecto = Proyecto(0, nombre, descripcion, inicio, fin, ciudad)
			guardar_proyecto(connection, proyecto)
			proyectos[nombre] = proyecto

		for rut, nombre_proyecto in ASIGNACIONES:
			asignar_empleado_proyecto_bd(connection, rut, proyectos[nombre_proyecto].id_proyecto)

		for rut, nombre_proyecto, fecha, horas, descripcion in REGISTROS:
			guardar_registro_tiempo(
				connection,
				RegistroTiempo(
					0, fecha, horas, empleados[rut], proyectos[nombre_proyecto], descripcion
				),
			)

		print(f"Datos de ejemplo cargados en {connection.execute('PRAGMA database_list').fetchone()[2]}")
		for tabla in ("usuarios", "empleados", "departamentos", "proyectos",
		              "empleado_proyecto", "registros_tiempo"):
			total = connection.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
			print(f"  {tabla:20} {total}")
	finally:
		connection.close()


if __name__ == "__main__":
	cargar(sys.argv[1] if len(sys.argv) > 1 else None)
