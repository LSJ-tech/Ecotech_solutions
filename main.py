"""Modelo inicial de EcoTechSolutions correspondiente al criterio 2.1.1."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable
import hashlib
import hmac
import os
import re
import secrets
import sqlite3

from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv


# Carga las variables de .env sin sobrescribir las ya definidas en el sistema.
load_dotenv(Path(__file__).with_name(".env"), override=False)

DATABASE_PATH = Path(
	os.environ.get("ECOTECH_DB_PATH") or Path(__file__).with_name("ecotech_solutions.db")
)
VARIABLES_CODIGO_ROL = {
	"admin": "ECOTECH_CODIGO_ADMIN",
	"rrhh": "ECOTECH_CODIGO_RRHH",
}
ROLES_VALIDOS = {"admin", "empleado", "rrhh"}
CAMPO_NOMBRE_DEPARTAMENTO = "El nombre del departamento"
LARGO_MAXIMO_DESCRIPCION_TAREA = 200
CODIFICACION = "utf-8"
# Valor hora según la fórmula de la Dirección del Trabajo: sueldo mensual / 30 x 7 / jornada semanal.
JORNADA_SEMANAL_HORAS = 44
DIAS_MES = 30
DIAS_SEMANA = 7
PATRON_TELEFONO = re.compile(r"\+?[\d ]{8,15}")
VARIABLE_CLAVE_CIFRADO = "ECOTECH_CLAVE_CIFRADO"
# Todo token Fernet comienza con este prefijo (versión 0x80 en base64 url-safe).
PREFIJO_TOKEN_FERNET = "gAAAAA"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS departamentos (
	 id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
	 nombre TEXT NOT NULL UNIQUE,
	 rut_gerente TEXT REFERENCES empleados(rut) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS empleados (
	 id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
	 rut TEXT NOT NULL UNIQUE,
	 nombre TEXT NOT NULL,
	 apellido TEXT NOT NULL,
	 correo TEXT NOT NULL UNIQUE,
	 cargo TEXT NOT NULL,
	 direccion TEXT,
	 telefono TEXT,
	 fecha_inicio_contrato TEXT,
	 salario TEXT,
	 id_departamento INTEGER,
	 FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

CREATE TABLE IF NOT EXISTS proyectos (
	 id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
	 nombre TEXT NOT NULL,
	 descripcion TEXT NOT NULL,
	 fecha_inicio TEXT NOT NULL,
	 fecha_fin TEXT,
	 ciudad TEXT
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
	 descripcion_tarea TEXT NOT NULL DEFAULT '',
	 rut_empleado TEXT NOT NULL,
	 id_proyecto INTEGER NOT NULL,
	 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE CASCADE,
	 FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS consultas_clima (
	 id_consulta INTEGER PRIMARY KEY AUTOINCREMENT,
	 ciudad TEXT NOT NULL,
	 temperatura REAL NOT NULL,
	 humedad INTEGER NOT NULL,
	 descripcion TEXT NOT NULL,
	 fecha_consulta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS indicadores (
	 id_indicador INTEGER PRIMARY KEY AUTOINCREMENT,
	 codigo TEXT NOT NULL,
	 nombre TEXT NOT NULL,
	 moneda TEXT NOT NULL,
	 valor REAL NOT NULL,
	 fecha TEXT NOT NULL,
	 fecha_consulta TEXT NOT NULL
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
	if resto == 11:
		digito_esperado = "0"
	elif resto == 10:
		digito_esperado = "K"
	else:
		digito_esperado = str(resto)
	if digito != digito_esperado:
		raise ValueError("El dígito verificador del RUT no es válido.")
	return f"{int(cuerpo)}-{digito_esperado}"


def obtener_codigo_rol(rol: str) -> str:
	"""Lee desde el entorno el código secreto exigido para registrar un rol."""

	variable = VARIABLES_CODIGO_ROL.get(rol)
	if variable is None:
		raise ValueError(f"El rol {rol} no requiere código secreto.")
	codigo = os.environ.get(variable, "").strip()
	if not codigo:
		raise ValueError(
			f"No está configurado el código para el rol {rol}. "
			f"Defina {variable} en el archivo .env."
		)
	return codigo


def verificar_codigo_rol(rol: str, codigo: str) -> bool:
	"""Compara el código ingresado en tiempo constante para evitar fugas por tiempo."""

	return hmac.compare_digest(codigo.encode(CODIFICACION), obtener_codigo_rol(rol).encode(CODIFICACION))


def validar_ciudad_opcional(valor: str | None) -> str | None:
	"""Normaliza la ciudad de un proyecto; vacío significa sin ciudad."""

	if valor is None or not str(valor).strip():
		return None
	from servicios_externos import validar_ciudad

	return validar_ciudad(str(valor))


class CifradorDatos:
	"""Cifra y descifra datos personales en reposo con Fernet (AES-128-CBC + HMAC-SHA256)."""

	def __init__(self, clave: str | None = None) -> None:
		clave = (clave or os.environ.get(VARIABLE_CLAVE_CIFRADO, "")).strip()
		if not clave:
			raise ValueError(
				f"No está configurada la clave de cifrado. Defina {VARIABLE_CLAVE_CIFRADO} "
				"en .env (puede generarla con generar_clave_cifrado())."
			)
		try:
			self._fernet = Fernet(clave.encode(CODIFICACION))
		except (ValueError, TypeError) as error:
			raise ValueError("La clave de cifrado configurada no es válida.") from error

	def cifrar(self, texto: str) -> str:
		"""Devuelve el token cifrado de un texto."""

		return self._fernet.encrypt(texto.encode(CODIFICACION)).decode(CODIFICACION)

	def descifrar(self, token: str) -> str:
		"""Recupera el texto original; falla si la clave no corresponde a la base."""

		try:
			return self._fernet.decrypt(token.encode(CODIFICACION)).decode(CODIFICACION)
		except InvalidToken as error:
			raise ValueError(
				"No fue posible descifrar los datos personales: la clave configurada "
				"no corresponde a la base de datos."
			) from error


def generar_clave_cifrado() -> str:
	"""Genera una clave Fernet nueva para copiar en .env."""

	return Fernet.generate_key().decode(CODIFICACION)


@lru_cache(maxsize=1)
def obtener_cifrador() -> CifradorDatos:
	"""Devuelve el cifrador configurado en el entorno (se construye una sola vez)."""

	return CifradorDatos()


@dataclass(frozen=True)
class DatosPersonalesCifrados:
	"""Tokens listos para persistir; None cuando el dato no fue informado."""

	direccion: str | None
	telefono: str | None
	salario: str | None


def cifrar_datos_personales(empleado: Empleado) -> DatosPersonalesCifrados:
	"""Cifra dirección, teléfono y salario antes de guardarlos."""

	cifrador = obtener_cifrador()
	return DatosPersonalesCifrados(
		direccion=cifrador.cifrar(empleado.direccion) if empleado.direccion else None,
		telefono=cifrador.cifrar(empleado.telefono) if empleado.telefono else None,
		salario=cifrador.cifrar(repr(empleado.salario)) if empleado.salario is not None else None,
	)


def descifrar_valor(token: str | None) -> str | None:
	"""Descifra un valor almacenado; acepta None y valores heredados sin cifrar."""

	if token is None:
		return None
	token = str(token)
	if not token.startswith(PREFIJO_TOKEN_FERNET):
		return token
	return obtener_cifrador().descifrar(token)


def descifrar_fila_empleado(fila: sqlite3.Row) -> dict[str, Any]:
	"""Convierte una fila de empleados en un diccionario con los datos personales legibles."""

	datos = dict(fila)
	datos["direccion"] = descifrar_valor(fila["direccion"]) or ""
	datos["telefono"] = descifrar_valor(fila["telefono"]) or ""
	salario = descifrar_valor(fila["salario"])
	datos["salario"] = float(salario) if salario is not None else None
	return datos


def cifrar_datos_personales_pendientes(connection: sqlite3.Connection) -> int:
	"""Cifra valores guardados en texto plano por versiones anteriores; devuelve cuántos."""

	pendientes = connection.execute(
		"""
		SELECT id_empleado, direccion, telefono, salario FROM empleados
		WHERE (direccion IS NOT NULL AND direccion NOT LIKE ?)
		   OR (telefono IS NOT NULL AND telefono NOT LIKE ?)
		   OR (salario IS NOT NULL AND CAST(salario AS TEXT) NOT LIKE ?)
		""",
		(PREFIJO_TOKEN_FERNET + "%",) * 3,
	).fetchall()
	if not pendientes:
		return 0
	cifrador = obtener_cifrador()

	def token(valor: Any) -> str | None:
		if valor is None:
			return None
		valor = str(valor)
		return valor if valor.startswith(PREFIJO_TOKEN_FERNET) else cifrador.cifrar(valor)

	for fila in pendientes:
		connection.execute(
			"UPDATE empleados SET direccion = ?, telefono = ?, salario = ? WHERE id_empleado = ?",
			(token(fila["direccion"]), token(fila["telefono"]), token(fila["salario"]), fila["id_empleado"]),
		)
	connection.commit()
	return len(pendientes)


def validar_descripcion_tarea(valor: str) -> str:
	"""Valida la breve descripción de las tareas de un registro de tiempo."""

	valor = validar_texto(valor, "La descripción de la tarea")
	if len(valor) > LARGO_MAXIMO_DESCRIPCION_TAREA:
		raise ValueError(
			f"La descripción de la tarea no puede superar {LARGO_MAXIMO_DESCRIPCION_TAREA} caracteres."
		)
	return valor


def validar_telefono(valor: str) -> str:
	"""Acepta teléfonos con dígitos, espacios y prefijo + (8 a 15 caracteres)."""

	valor = validar_texto(valor, "El teléfono")
	if PATRON_TELEFONO.fullmatch(valor) is None:
		raise ValueError("El teléfono solo puede contener dígitos, espacios y un prefijo +.")
	return valor


def calcular_tarifa_hora(salario_mensual: float) -> float:
	"""Convierte un sueldo mensual en valor hora con la fórmula de la Dirección del Trabajo."""

	salario_mensual = validar_monto(salario_mensual, "El salario")
	return round(salario_mensual / DIAS_MES * DIAS_SEMANA / JORNADA_SEMANAL_HORAS, 2)


def fila_a_empleado(fila: sqlite3.Row) -> Empleado:
	"""Construye un Empleado desde una fila de la tabla empleados."""

	datos = descifrar_fila_empleado(fila)
	return Empleado(
		datos["rut"],
		datos["nombre"],
		datos["apellido"],
		datos["correo"],
		datos["cargo"],
		direccion=datos["direccion"],
		telefono=datos["telefono"],
		fecha_inicio_contrato=date.fromisoformat(datos["fecha_inicio_contrato"])
		if datos["fecha_inicio_contrato"]
		else None,
		salario=datos["salario"],
		id_empleado=int(datos["id_empleado"]),
	)


def validar_monto(valor: float, campo: str) -> float:
	"""Valida un monto numérico estrictamente positivo (tarifas, tipos de cambio)."""

	if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
		raise ValueError(f"{campo} debe ser un número mayor que 0.")
	return float(valor)


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
	columnas_proyectos = {
		fila["name"] for fila in connection.execute("PRAGMA table_info(proyectos)")
	}
	if "ciudad" not in columnas_proyectos:
		connection.execute("ALTER TABLE proyectos ADD COLUMN ciudad TEXT")
	connection.commit()
	columnas_empleados = {
		fila["name"] for fila in connection.execute("PRAGMA table_info(empleados)")
	}
	if "id_empleado" not in columnas_empleados:
		migrar_tabla_empleados(connection)
	columnas_departamentos = {
		fila["name"] for fila in connection.execute("PRAGMA table_info(departamentos)")
	}
	if "rut_gerente" not in columnas_departamentos:
		connection.execute(
			"ALTER TABLE departamentos ADD COLUMN rut_gerente TEXT "
			"REFERENCES empleados(rut) ON DELETE SET NULL"
		)
	columnas_registros = {
		fila["name"] for fila in connection.execute("PRAGMA table_info(registros_tiempo)")
	}
	if "descripcion_tarea" not in columnas_registros:
		connection.execute(
			"ALTER TABLE registros_tiempo ADD COLUMN descripcion_tarea TEXT NOT NULL DEFAULT ''"
		)
	connection.commit()
	cifrar_datos_personales_pendientes(connection)


def migrar_tabla_empleados(connection: sqlite3.Connection) -> None:
	"""Reconstruye empleados con ID automático y datos personales, conservando filas y FK."""

	# Las claves foráneas se desactivan solo durante la copia: con ellas activas,
	# DROP TABLE dispararía ON DELETE CASCADE / SET NULL en usuarios y registros.
	connection.commit()
	connection.execute("PRAGMA foreign_keys = OFF")
	try:
		connection.executescript(
			"""
			CREATE TABLE empleados_nueva (
			 id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
			 rut TEXT NOT NULL UNIQUE,
			 nombre TEXT NOT NULL,
			 apellido TEXT NOT NULL,
			 correo TEXT NOT NULL UNIQUE,
			 cargo TEXT NOT NULL,
			 direccion TEXT,
			 telefono TEXT,
			 fecha_inicio_contrato TEXT,
			 salario TEXT,
			 id_departamento INTEGER,
			 FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
			);
			INSERT INTO empleados_nueva
			(rut, nombre, apellido, correo, cargo, id_departamento)
			SELECT rut, nombre, apellido, correo, cargo, id_departamento
			FROM empleados ORDER BY rowid;
			DROP TABLE empleados;
			ALTER TABLE empleados_nueva RENAME TO empleados;
			"""
		)
		problemas = connection.execute("PRAGMA foreign_key_check").fetchall()
		if problemas:
			raise sqlite3.IntegrityError("La migración de empleados dejó claves foráneas inválidas.")
	finally:
		connection.execute("PRAGMA foreign_keys = ON")


def generar_hash_contrasena(contrasena: str) -> str:
	"""Genera un hash PBKDF2 con sal para no guardar contrasenas planas."""

	contrasena = validar_texto(contrasena, "La contraseña")
	sal = secrets.token_bytes(16)
	hash_contrasena = hashlib.pbkdf2_hmac(
		"sha256", contrasena.encode(CODIFICACION), sal, 120_000
	)
	return f"pbkdf2_sha256$120000${sal.hex()}${hash_contrasena.hex()}"


def verificar_contrasena(contrasena: str, almacenada: str) -> bool:
	"""Verifica una contraseña almacenada como hash PBKDF2."""

	if not almacenada.startswith("pbkdf2_sha256$"):
		return False
	try:
		_algoritmo, iteraciones, sal_hex, hash_hex = almacenada.split("$", 3)
		hash_calculado = hashlib.pbkdf2_hmac(
			"sha256",
			contrasena.encode(CODIFICACION),
			bytes.fromhex(sal_hex),
			int(iteraciones),
		)
		return hmac.compare_digest(hash_calculado.hex(), hash_hex)
	except (ValueError, TypeError):
		return False


@revertir_si_falla
def guardar_departamento(
	connection: sqlite3.Connection, nombre: str, rut_gerente: str | None = None
) -> int:
	"""Inserta un departamento, opcionalmente con su gerente, y devuelve su identificador."""

	nombre = validar_texto(nombre, CAMPO_NOMBRE_DEPARTAMENTO)
	rut_gerente = verificar_gerente(connection, rut_gerente)
	cursor = connection.execute(
		"INSERT INTO departamentos (nombre, rut_gerente) VALUES (?, ?)", (nombre, rut_gerente)
	)
	connection.commit()
	return int(cursor.lastrowid)


def verificar_gerente(connection: sqlite3.Connection, rut: str | None) -> str | None:
	"""Normaliza el RUT del gerente y comprueba que corresponda a un empleado existente."""

	if rut is None or not str(rut).strip():
		return None
	rut = validar_rut(rut)
	if connection.execute("SELECT 1 FROM empleados WHERE rut = ?", (rut,)).fetchone() is None:
		raise ValueError("El gerente indicado no existe como empleado.")
	return rut


@revertir_si_falla
def asignar_gerente_departamento(
	connection: sqlite3.Connection, id_departamento: int, rut_gerente: str | None
) -> None:
	"""Asigna (o quita, con None) el gerente de un departamento existente."""

	rut_gerente = verificar_gerente(connection, rut_gerente)
	cursor = connection.execute(
		"UPDATE departamentos SET rut_gerente = ? WHERE id_departamento = ?",
		(rut_gerente, id_departamento),
	)
	if cursor.rowcount != 1:
		raise ValueError("El departamento indicado no existe.")
	connection.commit()


@revertir_si_falla
def guardar_empleado(
	connection: sqlite3.Connection,
	empleado: Empleado,
	id_departamento: int | None = None,
) -> None:
	"""Inserta un empleado usando parámetros para evitar SQL injection."""

	cifrado = cifrar_datos_personales(empleado)
	cursor = connection.execute(
		"""
		INSERT INTO empleados
		(rut, nombre, apellido, correo, cargo, direccion, telefono,
		 fecha_inicio_contrato, salario, id_departamento)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""",
		(
			empleado.rut,
			empleado.nombre,
			empleado.apellido,
			empleado.correo,
			empleado.cargo,
			cifrado.direccion,
			cifrado.telefono,
			empleado.fecha_inicio_contrato.isoformat()
			if empleado.fecha_inicio_contrato
			else None,
			cifrado.salario,
			id_departamento,
		),
	)
	connection.commit()
	empleado.id_empleado = int(cursor.lastrowid)


@revertir_si_falla
def asignar_empleado_departamento_bd(
	connection: sqlite3.Connection, rut: str, id_departamento: int
) -> None:
	"""Asigna un departamento existente a un empleado existente."""

	rut = validar_rut(rut)
	departamento = connection.execute(
		"SELECT 1 FROM departamentos WHERE id_departamento = ?",
		(id_departamento,),
	).fetchone()
	if departamento is None:
		raise ValueError("El departamento indicado no existe.")
	cursor = connection.execute(
		"UPDATE empleados SET id_departamento = ? WHERE rut = ?",
		(id_departamento, rut),
	)
	if cursor.rowcount != 1:
		raise ValueError("El empleado indicado no existe.")
	connection.commit()


def listar_empleados(connection: sqlite3.Connection) -> list[dict[str, Any]]:
	"""Devuelve los empleados con su departamento y los datos personales descifrados."""

	return [
		descifrar_fila_empleado(fila)
		for fila in connection.execute(
			"""
			SELECT e.id_empleado, e.rut, e.nombre, e.apellido, e.correo, e.cargo,
			       e.direccion, e.telefono, e.fecha_inicio_contrato, e.salario,
			       d.nombre AS departamento
			FROM empleados AS e
			LEFT JOIN departamentos AS d
			       ON d.id_departamento = e.id_departamento
			ORDER BY e.apellido, e.nombre
			"""
		)
	]


@revertir_si_falla
def actualizar_empleado(
	connection: sqlite3.Connection,
	rut: str,
	*,
	nombre: str,
	apellido: str,
	correo: str,
	cargo: str,
	direccion: str = "",
	telefono: str = "",
	fecha_inicio_contrato: date | None = None,
	salario: float | None = None,
	id_departamento: int | None = None,
) -> bool:
	"""Actualiza los datos de un empleado y devuelve si existía."""

	# Reutiliza las validaciones del modelo para que ninguna actualización las eluda.
	empleado = Empleado(
		rut,
		nombre,
		apellido,
		correo,
		cargo,
		direccion=direccion,
		telefono=telefono,
		fecha_inicio_contrato=fecha_inicio_contrato,
		salario=salario,
	)
	cifrado = cifrar_datos_personales(empleado)
	cursor = connection.execute(
		"""
		UPDATE empleados
		SET nombre = ?, apellido = ?, correo = ?, cargo = ?, direccion = ?,
		    telefono = ?, fecha_inicio_contrato = ?, salario = ?, id_departamento = ?
		WHERE rut = ?
		""",
		(
			empleado.nombre,
			empleado.apellido,
			empleado.correo,
			empleado.cargo,
			cifrado.direccion,
			cifrado.telefono,
			empleado.fecha_inicio_contrato.isoformat()
			if empleado.fecha_inicio_contrato
			else None,
			cifrado.salario,
			id_departamento,
			empleado.rut,
		),
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
		(nombre, descripcion, fecha_inicio, fecha_fin, ciudad)
		VALUES (?, ?, ?, ?, ?)
		""",
		(
			proyecto.nombre,
			proyecto.descripcion,
			proyecto.fecha_inicio.isoformat(),
			proyecto.fecha_fin.isoformat() if proyecto.fecha_fin else None,
			proyecto.ciudad,
		),
	)
	connection.commit()
	proyecto.id_proyecto = int(cursor.lastrowid)
	return proyecto.id_proyecto


def listar_departamentos(connection: sqlite3.Connection) -> list[sqlite3.Row]:
	"""Consulta todos los departamentos almacenados."""

	return list(
		connection.execute(
			"""
			SELECT d.id_departamento, d.nombre, d.rut_gerente,
			       e.nombre || ' ' || e.apellido AS gerente
			FROM departamentos AS d
			LEFT JOIN empleados AS e ON e.rut = d.rut_gerente
			ORDER BY d.nombre
			"""
		)
	)


@revertir_si_falla
def actualizar_departamento(
	connection: sqlite3.Connection,
	id_departamento: int,
	nombre: str,
	rut_gerente: str | None = None,
) -> bool:
	"""Actualiza nombre y gerente de un departamento y devuelve si existía."""

	nombre = validar_texto(nombre, CAMPO_NOMBRE_DEPARTAMENTO)
	rut_gerente = verificar_gerente(connection, rut_gerente)
	cursor = connection.execute(
		"UPDATE departamentos SET nombre = ?, rut_gerente = ? WHERE id_departamento = ?",
		(nombre, rut_gerente, id_departamento),
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
			SELECT id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin, ciudad
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
	ciudad: str | None = None,
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
	ciudad = validar_ciudad_opcional(ciudad)
	cursor = connection.execute(
		"""
		UPDATE proyectos
		SET nombre = ?, descripcion = ?, fecha_inicio = ?, fecha_fin = ?, ciudad = ?
		WHERE id_proyecto = ?
		""",
		(
			nombre,
			descripcion,
			fecha_inicio.isoformat(),
			fecha_fin.isoformat() if fecha_fin else None,
			ciudad,
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


@revertir_si_falla
def guardar_usuario_con_empleado(
	connection: sqlite3.Connection,
	usuario: Usuario,
	empleado: Empleado,
	id_departamento: int | None = None,
) -> int:
	"""Inserta un empleado y su usuario asociado en una sola transacción."""

	cifrado = cifrar_datos_personales(empleado)
	cursor_empleado = connection.execute(
		"""
		INSERT INTO empleados
		(rut, nombre, apellido, correo, cargo, direccion, telefono,
		 fecha_inicio_contrato, salario, id_departamento)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""",
		(
			empleado.rut,
			empleado.nombre,
			empleado.apellido,
			empleado.correo,
			empleado.cargo,
			cifrado.direccion,
			cifrado.telefono,
			empleado.fecha_inicio_contrato.isoformat()
			if empleado.fecha_inicio_contrato
			else None,
			cifrado.salario,
			id_departamento,
		),
	)
	empleado.id_empleado = int(cursor_empleado.lastrowid)
	usuario.empleado = empleado
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
			empleado.rut,
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
	"""Elimina un usuario y su empleado asociado, si existe."""

	fila = connection.execute(
		"SELECT rut_empleado FROM usuarios WHERE id_usuario = ?", (id_usuario,)
	).fetchone()
	if fila is None:
		return False
	cursor = connection.execute(
		"DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,)
	)
	if fila["rut_empleado"]:
		connection.execute("DELETE FROM empleados WHERE rut = ?", (fila["rut_empleado"],))
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
		(fecha, horas, descripcion_tarea, rut_empleado, id_proyecto)
		VALUES (?, ?, ?, ?, ?)
		""",
		(
			registro.fecha.isoformat(),
			registro.horas,
			registro.descripcion_tarea,
			registro.empleado.rut,
			registro.proyecto.id_proyecto,
		),
	)
	connection.commit()
	return int(cursor.lastrowid)


def sumar_horas_empleado(connection: sqlite3.Connection, rut: str) -> float:
	"""Devuelve el total de horas registradas por un empleado."""

	fila = connection.execute(
		"SELECT COALESCE(SUM(horas), 0) FROM registros_tiempo WHERE rut_empleado = ?",
		(validar_rut(rut),),
	).fetchone()
	return float(fila[0])


def listar_registros_tiempo(
	connection: sqlite3.Connection, rut_empleado: str | None = None
) -> list[sqlite3.Row]:
	"""Consulta registros de todos o de un empleado específico."""

	consulta = """
		SELECT r.id_registro, r.fecha, r.horas, r.descripcion_tarea, r.rut_empleado,
		       r.id_proyecto, e.nombre AS empleado, p.nombre AS proyecto
		FROM registros_tiempo AS r
		JOIN empleados AS e ON e.rut = r.rut_empleado
		JOIN proyectos AS p ON p.id_proyecto = r.id_proyecto
	"""
	parametros: tuple[str, ...] = ()
	if rut_empleado is not None:
		consulta += " WHERE r.rut_empleado = ?"
		parametros = (validar_rut(rut_empleado),)
	consulta += " ORDER BY r.fecha, r.id_registro"
	return list(connection.execute(consulta, parametros))


@revertir_si_falla
def actualizar_registro_tiempo(
	connection: sqlite3.Connection,
	id_registro: int,
	*,
	fecha: date,
	horas: float,
	descripcion_tarea: str = "",
) -> bool:
	"""Actualiza fecha, horas y descripción de un registro de tiempo."""

	if not isinstance(fecha, date):
		raise ValueError("La fecha del registro debe ser una fecha válida.")
	horas = validar_horas(horas)
	descripcion_tarea = validar_descripcion_tarea(descripcion_tarea) if descripcion_tarea else ""
	cursor = connection.execute(
		"""
		UPDATE registros_tiempo SET fecha = ?, horas = ?, descripcion_tarea = ?
		WHERE id_registro = ?
		""",
		(fecha.isoformat(), horas, descripcion_tarea, id_registro),
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
	gerente: Empleado | None = None
	empleados: list[Empleado] = field(default_factory=list)

	def __post_init__(self) -> None:
		if self.id_departamento < 0:
			raise ValueError("El identificador del departamento no puede ser negativo.")
		self.nombre = validar_texto(self.nombre, CAMPO_NOMBRE_DEPARTAMENTO)
		if self.gerente is not None and not isinstance(self.gerente, Empleado):
			raise ValueError("El gerente debe ser un empleado válido.")


@dataclass
class Empleado:
	"""Representa a un empleado de la empresa."""

	rut: str
	nombre: str
	apellido: str
	correo: str
	cargo: str
	direccion: str = ""
	telefono: str = ""
	fecha_inicio_contrato: date | None = None
	salario: float | None = None
	id_empleado: int = 0
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
		# Los datos personales son opcionales para fichas antiguas, pero si vienen se validan.
		self.direccion = self.direccion.strip() if self.direccion else ""
		self.telefono = validar_telefono(self.telefono) if self.telefono else ""
		if self.fecha_inicio_contrato is not None and not isinstance(
			self.fecha_inicio_contrato, date
		):
			raise ValueError("La fecha de inicio de contrato debe ser una fecha válida.")
		if self.salario is not None:
			self.salario = validar_monto(self.salario, "El salario")
		if self.id_empleado < 0:
			raise ValueError("El identificador del empleado no puede ser negativo.")


@dataclass
class Proyecto:
	"""Representa un proyecto y los empleados asignados."""

	id_proyecto: int
	nombre: str
	descripcion: str
	fecha_inicio: date
	fecha_fin: date | None = None
	ciudad: str | None = None
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
		self.ciudad = validar_ciudad_opcional(self.ciudad)


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
			raise ValueError("El rol debe ser admin, empleado o rrhh.")

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
	descripcion_tarea: str = ""

	def __post_init__(self) -> None:
		if self.id_registro < 0:
			raise ValueError("El identificador del registro no puede ser negativo.")
		if not isinstance(self.fecha, date):
			raise ValueError("La fecha del registro debe ser una fecha válida.")
		self.horas = validar_horas(self.horas)
		# Vacío solo para registros anteriores a la Unidad 1 alineada; si viene, se valida.
		self.descripcion_tarea = (
			validar_descripcion_tarea(self.descripcion_tarea) if self.descripcion_tarea else ""
		)
		if not isinstance(self.empleado, Empleado):
			raise ValueError("El registro debe estar asociado a un empleado válido.")
		if not isinstance(self.proyecto, Proyecto):
			raise ValueError("El registro debe estar asociado a un proyecto válido.")


@dataclass(frozen=True)
class Pago:
	"""Resultado del cálculo de pago de un empleado en una moneda extranjera."""

	rut: str
	horas: float
	tarifa_hora_clp: float
	monto_clp: float
	moneda: str
	valor_cambio: float
	monto_moneda: float


def calcular_pago(
	rut: str, horas: float, tarifa_hora_clp: float, moneda: str, valor_cambio: float
) -> Pago:
	"""Convierte horas trabajadas a pesos y luego a la moneda del país del proyecto."""

	rut = validar_rut(rut)
	horas = validar_monto(horas, "Las horas trabajadas")
	tarifa_hora_clp = validar_monto(tarifa_hora_clp, "La tarifa por hora")
	valor_cambio = validar_monto(valor_cambio, "El tipo de cambio")
	moneda = validar_texto(moneda, "La moneda").upper()
	monto_clp = round(horas * tarifa_hora_clp, 2)
	return Pago(
		rut=rut,
		horas=horas,
		tarifa_hora_clp=tarifa_hora_clp,
		monto_clp=monto_clp,
		moneda=moneda,
		valor_cambio=valor_cambio,
		monto_moneda=round(monto_clp / valor_cambio, 2),
	)


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
			+ (f" - {registro.descripcion_tarea}" if registro.descripcion_tarea else "")
			for registro in registros
		)
		return "\n".join(lineas)


class ExportadorExcel(IExportador):
	"""Genera datos separados por comas para una hoja de cálculo."""

	def exportar(self, registros: list[RegistroTiempo]) -> str:
		lineas = ["fecha,empleado,proyecto,horas,descripcion_tarea"]
		lineas.extend(
			f"{registro.fecha},{registro.empleado.nombre},"
			f"{registro.proyecto.nombre},{registro.horas},"
			f"\"{registro.descripcion_tarea.replace(chr(34), chr(34) * 2)}\""
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
	"DATABASE_PATH",
	"ROLES_VALIDOS",
	"VARIABLES_CODIGO_ROL",
	"CifradorDatos",
	"Departamento",
	"Empleado",
	"ExportadorExcel",
	"ExportadorPDF",
	"IExportador",
	"Pago",
	"Proyecto",
	"RegistroTiempo",
	"ServicioReportes",
	"Usuario",
	"asignar_empleado_a_departamento",
	"asignar_empleado_a_proyecto",
	"asignar_empleado_departamento_bd",
	"asignar_empleado_proyecto_bd",
	"asignar_gerente_departamento",
	"calcular_pago",
	"calcular_tarifa_hora",
	"cifrar_datos_personales_pendientes",
	"conectar_bd",
	"fila_a_empleado",
	"generar_clave_cifrado",
	"obtener_cifrador",
	"generar_hash_contrasena",
	"guardar_departamento",
	"guardar_empleado",
	"guardar_proyecto",
	"guardar_registro_tiempo",
	"guardar_usuario",
	"guardar_usuario_con_empleado",
	"inicializar_bd",
	"listar_departamentos",
	"listar_empleados",
	"listar_proyectos",
	"listar_registros_tiempo",
	"listar_usuarios",
	"obtener_codigo_rol",
	"sumar_horas_empleado",
	"validar_ciudad_opcional",
	"validar_descripcion_tarea",
	"validar_horas",
	"validar_monto",
	"validar_rut",
	"validar_telefono",
	"validar_texto",
	"verificar_codigo_rol",
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
