"""Modelo inicial de EcoTechSolutions correspondiente al criterio 2.1.1."""

from __future__ import annotations

from abc import ABC, abstractmethod
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


class Usuario:
	"""Representa las credenciales de acceso de un empleado."""

	def __init__(
		self,
		id_usuario: int,
		nombre_usuario: str,
		contrasena: str,
		activo: bool = True,
		empleado: Empleado | None = None,
	) -> None:
		self.id_usuario = id_usuario
		self.nombre_usuario = nombre_usuario
		self._contrasena = contrasena
		self.activo = activo
		self.empleado = empleado

	@property
	def contrasena(self) -> str:
		"""Permite validar credenciales sin exponer el atributo interno."""

		return self._contrasena

	def actualizar_contrasena(self, nueva_contrasena: str) -> None:
		"""Actualiza la contraseña a través de una operación controlada."""

		if not nueva_contrasena:
			raise ValueError("La contraseña no puede estar vacía.")
		self._contrasena = nueva_contrasena


@dataclass
class RegistroTiempo:
	"""Registra las horas trabajadas por un empleado en un proyecto."""

	id_registro: int
	fecha: date
	horas: float
	empleado: Empleado
	proyecto: Proyecto


class IExportador(ABC):
	"""Define el contrato común para generar informes."""

	@abstractmethod
	def exportar(self, registros: list[RegistroTiempo]) -> str:
		"""Convierte registros de tiempo a un formato de salida."""


class ExportadorPDF(IExportador):
	"""Genera una representación de texto con formato de informe PDF."""

	def exportar(self, registros: list[RegistroTiempo]) -> str:
		lineas = ["Informe de horas trabajadas", "=" * 28]
		lineas.extend(
			f"{registro.fecha}: {registro.empleado.nombre} "
			f"- {registro.proyecto.nombre} - {registro.horas} horas"
			for registro in registros
		)
		return "\n".join(lineas)


class ExportadorExcel(IExportador):
	"""Genera datos separados por comas para una hoja de cálculo."""

	def exportar(self, registros: list[RegistroTiempo]) -> str:
		lineas = ["fecha,empleado,proyecto,horas"]
		lineas.extend(
			f"{registro.fecha},{registro.empleado.nombre},"
			f"{registro.proyecto.nombre},{registro.horas}"
			for registro in registros
		)
		return "\n".join(lineas)


class ServicioReportes:
	"""Usa cualquier exportador compatible sin duplicar la lógica."""

	def __init__(self, exportador: IExportador) -> None:
		self._exportador = exportador

	def generar(self, registros: list[RegistroTiempo]) -> str:
		return self._exportador.exportar(registros)


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
