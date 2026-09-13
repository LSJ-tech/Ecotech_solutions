"""Modelo inicial de EcoTechSolutions correspondiente al criterio 2.1.1."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from functools import wraps
from pathlib import Path
from typing import Any, Callable
import hashlib
import hmac
import re
import secrets
import sqlite3


DATABASE_PATH = Path(__file__).with_name("ecotech_solutions.db")
CODIGO_ADMIN = "1234"
ROLES_VALIDOS = {"admin", "empleado"}

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
	 rol TEXT NOT NULL DEFAULT 'empleado',
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


def validar_texto(valor: str, campo: str) -> str:
	"""Valida que un campo de texto obligatorio tenga contenido."""

	if not isinstance(valor, str) or not valor.strip():
		raise ValueError(f"{campo} no puede estar vacío.")
	return valor.strip()


def validar_rut(valor: str) -> str:
	"""Normaliza y valida un RUT chileno con su dígito verificador."""

	valor = validar_texto(valor, "El RUT")
	normalizado = valor.replace(".", "").replace(" ", "").upper()
	coincidencia = re.fullmatch(r"(\d{1,8})-([\dK])", normalizado)
	if coincidencia is None:
		raise ValueError("El RUT debe tener el formato 12345678-5.")

	cuerpo, digito = coincidencia.groups()
	suma = 0
	multiplicador = 2
	for caracter in reversed(cuerpo):
		suma += int(caracter) * multiplicador
		multiplicador = 2 if multiplicador == 7 else multiplicador + 1

	resto = 11 - (suma % 11)
	digito_esperado = "0" if resto == 11 else "K" if resto == 10 else str(resto)
	if digito != digito_esperado:
		raise ValueError("El dígito verificador del RUT no es válido.")
	return f"{int(cuerpo)}-{digito_esperado}"


def validar_horas(horas: float) -> float:
	"""Valida el rango permitido para un registro de tiempo."""

	if not isinstance(horas, (int, float)) or not 0 < horas <= 24:
		raise ValueError("Las horas deben ser mayores que 0 y menores o iguales a 24.")
	return float(horas)


def conectar_bd(
	db_path: str | Path = DATABASE_PATH,
) -> sqlite3.Connection:
	"""Abre una conexión SQLite con filas accesibles por nombre de columna."""

	connection = sqlite3.connect(str(db_path))
	connection.row_factory = sqlite3.Row
	connection.execute("PRAGMA foreign_keys = ON")
	return connection


def revertir_si_falla(funcion: Callable[..., Any]) -> Callable[..., Any]:
	"""Revierte la transacción cuando una operación SQLite falla."""

	@wraps(funcion)
	def envoltura(
		connection: sqlite3.Connection, *args: Any, **kwargs: Any
	) -> Any:
		try:
			return funcion(connection, *args, **kwargs)
		except sqlite3.Error:
			connection.rollback()
			raise

	return envoltura


def inicializar_bd(connection: sqlite3.Connection) -> None:
	"""Crea las tablas del sistema si todavía no existen."""

	connection.executescript(SCHEMA_SQL)
	columnas_usuarios = {
		fila["name"] for fila in connection.execute("PRAGMA table_info(usuarios)")
	}
	if "rol" not in columnas_usuarios:
		connection.execute(
			"ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'empleado'"
		)
	connection.commit()


def generar_hash_contrasena(contrasena: str) -> str:
	"""Genera un hash PBKDF2 con sal para no guardar contrasenas planas."""

	contrasena = validar_texto(contrasena, "La contraseña")
	sal = secrets.token_bytes(16)
	hash_contrasena = hashlib.pbkdf2_hmac(
		"sha256", contrasena.encode("utf-8"), sal, 120_000
	)
	return f"pbkdf2_sha256$120000${sal.hex()}${hash_contrasena.hex()}"


def verificar_contrasena(contrasena: str, almacenada: str) -> bool:
	"""Verifica hashes nuevos y permite migrar usuarios antiguos en texto plano."""

	if not almacenada.startswith("pbkdf2_sha256$"):
		return hmac.compare_digest(contrasena, almacenada)
	try:
		algoritmo, iteraciones, sal_hex, hash_hex = almacenada.split("$", 3)
		hash_calculado = hashlib.pbkdf2_hmac(
			"sha256",
			contrasena.encode("utf-8"),
			bytes.fromhex(sal_hex),
			int(iteraciones),
		)
		return hmac.compare_digest(hash_calculado.hex(), hash_hex)
	except (ValueError, TypeError):
		return False


@revertir_si_falla
def guardar_departamento(connection: sqlite3.Connection, nombre: str) -> int:
	"""Inserta un departamento y devuelve su identificador."""

	nombre = validar_texto(nombre, "El nombre del departamento")
	cursor = connection.execute(
		"INSERT INTO departamentos (nombre) VALUES (?)", (nombre,)
	)
	connection.commit()
	return int(cursor.lastrowid)


@revertir_si_falla
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


@revertir_si_falla
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

	rut = validar_rut(rut)
	nombre = validar_texto(nombre, "El nombre")
	apellido = validar_texto(apellido, "El apellido")
	correo = validar_texto(correo, "El correo")
	cargo = validar_texto(cargo, "El cargo")
	if "@" not in correo:
		raise ValueError("El correo debe tener un formato válido.")
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


@revertir_si_falla
def eliminar_empleado(connection: sqlite3.Connection, rut: str) -> bool:
	"""Elimina un empleado y devuelve si existía."""

	rut = validar_rut(rut)
	cursor = connection.execute("DELETE FROM empleados WHERE rut = ?", (rut,))
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
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
	proyecto.id_proyecto = int(cursor.lastrowid)
	return proyecto.id_proyecto


def listar_departamentos(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Consulta todos los departamentos almacenados."""

	return list(
		connection.execute(
			"SELECT id_departamento, nombre FROM departamentos ORDER BY nombre"
		)
	)


@revertir_si_falla
def actualizar_departamento(
	connection: sqlite3.Connection, id_departamento: int, nombre: str
) -> bool:
	"""Actualiza un departamento y devuelve si existía."""

	nombre = validar_texto(nombre, "El nombre del departamento")
	cursor = connection.execute(
		"UPDATE departamentos SET nombre = ? WHERE id_departamento = ?",
		(nombre, id_departamento),
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def eliminar_departamento(connection: sqlite3.Connection, id_departamento: int) -> bool:
	"""Elimina un departamento y devuelve si existía."""

	cursor = connection.execute(
		"DELETE FROM departamentos WHERE id_departamento = ?", (id_departamento,)
	)
	connection.commit()
	return cursor.rowcount == 1


def listar_proyectos(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Consulta todos los proyectos almacenados."""

	return list(
		connection.execute(
			"""
			SELECT id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin
			FROM proyectos ORDER BY fecha_inicio, nombre
			"""
		)
	)


@revertir_si_falla
def actualizar_proyecto(
	connection: sqlite3.Connection,
	id_proyecto: int,
	*,
	nombre: str,
	descripcion: str,
	fecha_inicio: date,
	fecha_fin: date | None = None,
) -> bool:
	"""Actualiza un proyecto y devuelve si existía."""

	nombre = validar_texto(nombre, "El nombre del proyecto")
	descripcion = validar_texto(descripcion, "La descripción")
	if not isinstance(fecha_inicio, date):
		raise ValueError("La fecha de inicio debe ser una fecha válida.")
	if fecha_fin is not None:
		if not isinstance(fecha_fin, date):
			raise ValueError("La fecha de fin debe ser una fecha válida.")
		if fecha_fin < fecha_inicio:
			raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
	cursor = connection.execute(
		"""
		UPDATE proyectos
		SET nombre = ?, descripcion = ?, fecha_inicio = ?, fecha_fin = ?
		WHERE id_proyecto = ?
		""",
		(
			nombre,
			descripcion,
			fecha_inicio.isoformat(),
			fecha_fin.isoformat() if fecha_fin else None,
			id_proyecto,
		),
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def eliminar_proyecto(connection: sqlite3.Connection, id_proyecto: int) -> bool:
	"""Elimina un proyecto y devuelve si existía."""

	cursor = connection.execute(
		"DELETE FROM proyectos WHERE id_proyecto = ?", (id_proyecto,)
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def guardar_usuario(connection: sqlite3.Connection, usuario: Usuario) -> int:
	"""Inserta un usuario asociado opcionalmente a un empleado."""

	cursor = connection.execute(
		"""
		INSERT INTO usuarios
		(nombre_usuario, contrasena, activo, rut_empleado, rol)
		VALUES (?, ?, ?, ?, ?)
		""",
		(
			usuario.nombre_usuario,
			generar_hash_contrasena(usuario.obtener_contrasena_interna()),
			int(usuario.activo),
			usuario.empleado.rut if usuario.empleado else None,
			usuario.rol,
		),
	)
	connection.commit()
	usuario.id_usuario = int(cursor.lastrowid)
	return usuario.id_usuario


def listar_usuarios(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Consulta los usuarios sin devolver su contraseña."""

	return list(
		connection.execute(
			"""
			SELECT id_usuario, nombre_usuario, activo, rut_empleado, rol
			FROM usuarios ORDER BY nombre_usuario
			"""
		)
	)


@revertir_si_falla
def actualizar_usuario(
	connection: sqlite3.Connection,
	id_usuario: int,
	*,
	nombre_usuario: str,
	activo: bool,
) -> bool:
	"""Actualiza los datos no sensibles de un usuario."""

	nombre_usuario = validar_texto(nombre_usuario, "El nombre de usuario")
	cursor = connection.execute(
		"""
		UPDATE usuarios SET nombre_usuario = ?, activo = ?
		WHERE id_usuario = ?
		""",
		(nombre_usuario, int(activo), id_usuario),
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def eliminar_usuario(connection: sqlite3.Connection, id_usuario: int) -> bool:
	"""Elimina un usuario y devuelve si existía."""

	cursor = connection.execute(
		"DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,)
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def asignar_empleado_proyecto_bd(
	connection: sqlite3.Connection, rut: str, id_proyecto: int
) -> None:
	"""Persiste la relación muchos a muchos entre empleado y proyecto."""

	rut = validar_rut(rut)
	connection.execute(
		"""
		INSERT INTO empleado_proyecto (rut_empleado, id_proyecto)
		VALUES (?, ?)
		""",
		(rut, id_proyecto),
	)
	connection.commit()


@revertir_si_falla
def guardar_registro_tiempo(
	connection: sqlite3.Connection, registro: RegistroTiempo
) -> int:
	"""Persiste un registro de horas asociado a empleado y proyecto."""

	asignacion = connection.execute(
		"""
		SELECT 1
		FROM empleado_proyecto
		WHERE rut_empleado = ? AND id_proyecto = ?
		""",
		(registro.empleado.rut, registro.proyecto.id_proyecto),
	).fetchone()
	if asignacion is None:
		raise ValueError(
			"El empleado debe estar asignado al proyecto antes de registrar horas."
		)

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


def listar_registros_tiempo(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Consulta registros de tiempo con sus referencias principales."""

	return list(
		connection.execute(
			"""
			SELECT r.id_registro, r.fecha, r.horas, r.rut_empleado,
			       r.id_proyecto, e.nombre AS empleado, p.nombre AS proyecto
			FROM registros_tiempo AS r
			JOIN empleados AS e ON e.rut = r.rut_empleado
			JOIN proyectos AS p ON p.id_proyecto = r.id_proyecto
			ORDER BY r.fecha, r.id_registro
			"""
		)
	)


@revertir_si_falla
def actualizar_registro_tiempo(
	connection: sqlite3.Connection,
	id_registro: int,
	*,
	fecha: date,
	horas: float,
) -> bool:
	"""Actualiza fecha y horas de un registro de tiempo."""

	if not isinstance(fecha, date):
		raise ValueError("La fecha del registro debe ser una fecha válida.")
	horas = validar_horas(horas)
	cursor = connection.execute(
		"""
		UPDATE registros_tiempo SET fecha = ?, horas = ?
		WHERE id_registro = ?
		""",
		(fecha.isoformat(), horas, id_registro),
	)
	connection.commit()
	return cursor.rowcount == 1


@revertir_si_falla
def eliminar_registro_tiempo(connection: sqlite3.Connection, id_registro: int) -> bool:
	"""Elimina un registro de tiempo y devuelve si existía."""

	cursor = connection.execute(
		"DELETE FROM registros_tiempo WHERE id_registro = ?", (id_registro,)
	)
	connection.commit()
	return cursor.rowcount == 1


@dataclass
class Departamento:
	"""Representa un departamento y los empleados que lo integran."""

	id_departamento: int
	nombre: str
	empleados: list[Empleado] = field(default_factory=list)

	def __post_init__(self) -> None:
		if self.id_departamento < 0:
			raise ValueError("El identificador del departamento no puede ser negativo.")
		self.nombre = validar_texto(self.nombre, "El nombre del departamento")


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

	def __post_init__(self) -> None:
		self.rut = validar_rut(self.rut)
		self.nombre = validar_texto(self.nombre, "El nombre")
		self.apellido = validar_texto(self.apellido, "El apellido")
		self.correo = validar_texto(self.correo, "El correo")
		self.cargo = validar_texto(self.cargo, "El cargo")
		if "@" not in self.correo:
			raise ValueError("El correo debe tener un formato válido.")


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

	def __post_init__(self) -> None:
		if self.id_proyecto < 0:
			raise ValueError("El identificador del proyecto no puede ser negativo.")
		self.nombre = validar_texto(self.nombre, "El nombre del proyecto")
		self.descripcion = validar_texto(self.descripcion, "La descripción")
		if not isinstance(self.fecha_inicio, date):
			raise ValueError("La fecha de inicio debe ser una fecha válida.")
		if self.fecha_fin is not None:
			if not isinstance(self.fecha_fin, date):
				raise ValueError("La fecha de fin debe ser una fecha válida.")
			if self.fecha_fin < self.fecha_inicio:
				raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")


class Usuario:
	"""Representa las credenciales de acceso de un empleado."""

	def __init__(
		self,
		id_usuario: int,
		nombre_usuario: str,
		contrasena: str,
		activo: bool = True,
		empleado: Empleado | None = None,
		rol: str = "empleado",
	) -> None:
		if id_usuario < 0:
			raise ValueError("El identificador del usuario no puede ser negativo.")
		self.id_usuario = id_usuario
		self.nombre_usuario = validar_texto(nombre_usuario, "El nombre de usuario")
		self._contrasena = validar_texto(contrasena, "La contraseña")
		self.activo = activo
		self.empleado = empleado
		self.rol = validar_texto(rol, "El rol").lower()
		if self.rol not in ROLES_VALIDOS:
			raise ValueError("El rol debe ser admin o empleado.")

	@property
	def contrasena(self) -> str:
		"""Evita exponer la contraseña en texto plano."""

		return "********"

	def obtener_contrasena_interna(self) -> str:
		"""Devuelve la contraseña real solo para uso interno de validación y persistencia."""

		return self._contrasena

	def verificar_contrasena(self, contrasena: str) -> bool:
		"""Valida la contraseña ingresada sin exponer la almacenada."""

		return verificar_contrasena(contrasena, self._contrasena)

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

	def __post_init__(self) -> None:
		if self.id_registro < 0:
			raise ValueError("El identificador del registro no puede ser negativo.")
		if not isinstance(self.fecha, date):
			raise ValueError("La fecha del registro debe ser una fecha válida.")
		self.horas = validar_horas(self.horas)
		if not isinstance(self.empleado, Empleado):
			raise ValueError("El registro debe estar asociado a un empleado válido.")
		if not isinstance(self.proyecto, Proyecto):
			raise ValueError("El registro debe estar asociado a un proyecto válido.")


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


__all__ = [
	"CODIGO_ADMIN",
	"DATABASE_PATH",
	"ROLES_VALIDOS",
	"Departamento",
	"Empleado",
	"ExportadorExcel",
	"ExportadorPDF",
	"IExportador",
	"Proyecto",
	"RegistroTiempo",
	"ServicioReportes",
	"Usuario",
	"asignar_empleado_a_departamento",
	"asignar_empleado_a_proyecto",
	"asignar_empleado_proyecto_bd",
	"conectar_bd",
	"generar_hash_contrasena",
	"guardar_departamento",
	"guardar_empleado",
	"guardar_proyecto",
	"guardar_registro_tiempo",
	"guardar_usuario",
	"inicializar_bd",
	"listar_departamentos",
	"listar_empleados",
	"listar_proyectos",
	"listar_registros_tiempo",
	"listar_usuarios",
	"validar_horas",
	"validar_rut",
	"validar_texto",
	"verificar_contrasena",
]


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
	from interfaz import mostrar_menu

	mostrar_menu()
