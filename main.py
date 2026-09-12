"""Modelo inicial de EcoTechSolutions correspondiente al criterio 2.1.1."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import sqlite3


DATABASE_PATH = Path(__file__).with_name("ecotech_solutions.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS departamentos (
	 id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
	 nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS empleados (
	 rut TEXT PRIMARY KEY,
	 nombre TEXT NOT NULL,
	 apellido TEXT NOT NULL,
	 correo TEXT NOT NULL UNIQUE,
	 cargo TEXT NOT NULL,
	 id_departamento INTEGER,
	 FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

CREATE TABLE IF NOT EXISTS proyectos (
	 id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
	 nombre TEXT NOT NULL,
	 descripcion TEXT NOT NULL,
	 fecha_inicio TEXT NOT NULL,
	 fecha_fin TEXT
);

CREATE TABLE IF NOT EXISTS empleado_proyecto (
	 rut_empleado TEXT NOT NULL,
	 id_proyecto INTEGER NOT NULL,
	 PRIMARY KEY (rut_empleado, id_proyecto),
	 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE CASCADE,
	 FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS usuarios (
	 id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
	 nombre_usuario TEXT NOT NULL UNIQUE,
	 contrasena TEXT NOT NULL,
	 activo INTEGER NOT NULL DEFAULT 1,
	 rut_empleado TEXT UNIQUE,
	 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS registros_tiempo (
	 id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
	 fecha TEXT NOT NULL,
	 horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24),
	 rut_empleado TEXT NOT NULL,
	 id_proyecto INTEGER NOT NULL,
	 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE CASCADE,
	 FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
);
"""


def conectar_bd(
	db_path: str | Path = DATABASE_PATH,
) -> sqlite3.Connection:
	"""Abre una conexión SQLite con filas accesibles por nombre de columna."""

	connection = sqlite3.connect(str(db_path))
	connection.row_factory = sqlite3.Row
	connection.execute("PRAGMA foreign_keys = ON")
	return connection


def inicializar_bd(connection: sqlite3.Connection) -> None:
	"""Crea las tablas del sistema si todavía no existen."""

	connection.executescript(SCHEMA_SQL)
	connection.commit()


def guardar_departamento(connection: sqlite3.Connection, nombre: str) -> int:
	"""Inserta un departamento y devuelve su identificador."""

	cursor = connection.execute(
		"INSERT INTO departamentos (nombre) VALUES (?)", (nombre,)
	)
	connection.commit()
	return int(cursor.lastrowid)


def guardar_empleado(
	connection: sqlite3.Connection,
	empleado: Empleado,
	id_departamento: int | None = None,
) -> None:
	"""Inserta un empleado usando parámetros para evitar SQL injection."""

	connection.execute(
		"""
		INSERT INTO empleados
		(rut, nombre, apellido, correo, cargo, id_departamento)
		VALUES (?, ?, ?, ?, ?, ?)
		""",
		(
			empleado.rut,
			empleado.nombre,
			empleado.apellido,
			empleado.correo,
			empleado.cargo,
			id_departamento,
		),
	)
	connection.commit()


def listar_empleados(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Devuelve los empleados almacenados junto con su departamento."""

	return list(
		connection.execute(
			"""
			SELECT e.rut, e.nombre, e.apellido, e.correo, e.cargo,
			       d.nombre AS departamento
			FROM empleados AS e
			LEFT JOIN departamentos AS d
			       ON d.id_departamento = e.id_departamento
			ORDER BY e.apellido, e.nombre
			"""
		)
	)


def actualizar_empleado(
	connection: sqlite3.Connection,
	rut: str,
	*,
	nombre: str,
	apellido: str,
	correo: str,
	cargo: str,
	id_departamento: int | None = None,
) -> bool:
	"""Actualiza los datos de un empleado y devuelve si existía."""

	cursor = connection.execute(
		"""
		UPDATE empleados
		SET nombre = ?, apellido = ?, correo = ?, cargo = ?,
		    id_departamento = ?
		WHERE rut = ?
		""",
		(nombre, apellido, correo, cargo, id_departamento, rut),
	)
	connection.commit()
	return cursor.rowcount == 1


def eliminar_empleado(connection: sqlite3.Connection, rut: str) -> bool:
	"""Elimina un empleado y devuelve si existía."""

	cursor = connection.execute("DELETE FROM empleados WHERE rut = ?", (rut,))
	connection.commit()
	return cursor.rowcount == 1


def guardar_proyecto(connection: sqlite3.Connection, proyecto: Proyecto) -> int:
	"""Inserta un proyecto y devuelve su identificador."""

	cursor = connection.execute(
		"""
		INSERT INTO proyectos
		(nombre, descripcion, fecha_inicio, fecha_fin)
		VALUES (?, ?, ?, ?)
		""",
		(
			proyecto.nombre,
			proyecto.descripcion,
			proyecto.fecha_inicio.isoformat(),
			proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None,
		),
	)
	connection.commit()
	return int(cursor.lastrowid)


def asignar_empleado_proyecto_bd(
	connection: sqlite3.Connection, rut: str, id_proyecto: int
) -> None:
	"""Persiste la relación muchos a muchos entre empleado y proyecto."""

	connection.execute(
		"""
		INSERT INTO empleado_proyecto (rut_empleado, id_proyecto)
		VALUES (?, ?)
		""",
		(rut, id_proyecto),
	)
	connection.commit()


def guardar_registro_tiempo(
	connection: sqlite3.Connection, registro: RegistroTiempo
) -> int:
	"""Persiste un registro de horas asociado a empleado y proyecto."""

	cursor = connection.execute(
		"""
		INSERT INTO registros_tiempo
		(fecha, horas, rut_empleado, id_proyecto)
		VALUES (?, ?, ?, ?)
		""",
		(
			registro.fecha.isoformat(),
			registro.horas,
			registro.empleado.rut,
			registro.proyecto.id_proyecto,
		),
	)
	connection.commit()
	return int(cursor.lastrowid)


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
