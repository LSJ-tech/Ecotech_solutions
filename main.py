"""Modelo inicial de EcoTechSolutions correspondiente al criterio 2.1.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Departamento:
	"""Representa un departamento y los empleados que lo integran."""

	id_departamento: int
	nombre: str
	empleados: list[Empleado] = field(default_factory=list)


@dataclass
class Empleado:
	"""Representa a un empleado de la empresa."""

	rut: str
	nombre: str
	apellido: str
	correo: str
	cargo: str
	departamento: Departamento | None = None
	proyectos: list[Proyecto] = field(default_factory=list)
	registros_tiempo: list[RegistroTiempo] = field(default_factory=list)


@dataclass
class Proyecto:
	"""Representa un proyecto y los empleados asignados."""

	id_proyecto: int
	nombre: str
	descripcion: str
	fecha_inicio: date
	fecha_fin: date | None = None
	empleados: list[Empleado] = field(default_factory=list)
	registros_tiempo: list[RegistroTiempo] = field(default_factory=list)


@dataclass
class Usuario:
	"""Representa las credenciales de acceso de un empleado."""

	id_usuario: int
	nombre_usuario: str
	contrasena: str
	activo: bool = True
	empleado: Empleado | None = None


@dataclass
class RegistroTiempo:
	"""Registra las horas trabajadas por un empleado en un proyecto."""

	id_registro: int
	fecha: date
	horas: float
	empleado: Empleado
	proyecto: Proyecto


def asignar_empleado_a_departamento(
	empleado: Empleado, departamento: Departamento
) -> None:
	"""Establece la relación entre un empleado y su departamento."""

	empleado.departamento = departamento
	if empleado not in departamento.empleados:
		departamento.empleados.append(empleado)


def asignar_empleado_a_proyecto(empleado: Empleado, proyecto: Proyecto) -> None:
	"""Establece la relación de asignación entre un empleado y un proyecto."""

	if empleado not in proyecto.empleados:
		proyecto.empleados.append(empleado)
	if proyecto not in empleado.proyectos:
		empleado.proyectos.append(proyecto)


def registrar_tiempo(registro: RegistroTiempo) -> None:
	"""Asocia un registro de tiempo con sus entidades relacionadas."""

	if registro not in registro.empleado.registros_tiempo:
		registro.empleado.registros_tiempo.append(registro)
	if registro not in registro.proyecto.registros_tiempo:
		registro.proyecto.registros_tiempo.append(registro)


if __name__ == "__main__":
	print("Modelo de EcoTechSolutions cargado correctamente.")
