"""Consumo seguro de servicios externos para EcoTechSolutions (Unidad 3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Generic, TypeVar
import logging
import os
import re
import sqlite3

import requests

from main import revertir_si_falla, validar_texto

T = TypeVar("T")


TIMEOUT_SEGUNDOS = 8
REINTENTOS_SERVIDOR = 1
MENSAJE_RESPUESTA_INVALIDA = "La respuesta del servicio externo no tiene el formato esperado."
PATRON_CIUDAD = re.compile(r"[A-Za-zÁÉÍÓÚÑáéíóúñü' -]{2,60}")
# Indicadores de mindicador.cl permitidos y la moneda que representan.
INDICADORES_PERMITIDOS = {"dolar": "USD", "euro": "EUR", "uf": "UF"}

# El registro técnico va a un archivo local; nunca incluye llaves ni parámetros.
LOGGER = logging.getLogger("ecotech.servicios")


class ErrorServicioExterno(Exception):
	"""Error con un mensaje apto para mostrar al usuario, sin datos sensibles."""


def validar_ciudad(valor: str) -> str:
	"""Acepta nombres de ciudad con letras, espacios y guiones antes de consultar la API."""

	valor = validar_texto(valor, "La ciudad")
	if PATRON_CIUDAD.fullmatch(valor) is None:
		raise ValueError(
			"La ciudad solo puede contener letras, espacios y guiones (2 a 60 caracteres)."
		)
	return valor


def validar_indicador(valor: str) -> str:
	"""Acepta solo indicadores de la lista blanca antes de consultar la API."""

	valor = validar_texto(valor, "El indicador").lower()
	if valor not in INDICADORES_PERMITIDOS:
		opciones = ", ".join(sorted(INDICADORES_PERMITIDOS))
		raise ValueError(f"El indicador debe ser uno de: {opciones}.")
	return valor


class ClienteHTTP:
	"""Encapsula requests con timeout, reintentos y errores traducidos al usuario."""

	def __init__(
		self,
		base_url: str,
		timeout: float = TIMEOUT_SEGUNDOS,
		sesion: requests.Session | None = None,
	) -> None:
		if not base_url.startswith("https://"):
			raise ValueError("El servicio externo debe usar HTTPS.")
		self._base_url = base_url.rstrip("/")
		self._timeout = timeout
		self._sesion = sesion or requests.Session()

	def obtener_json(self, ruta: str, parametros: dict[str, Any]) -> dict[str, Any]:
		"""Realiza un GET y devuelve el JSON, o lanza ErrorServicioExterno."""

		url = f"{self._base_url}/{ruta.lstrip('/')}"
		for intento in range(REINTENTOS_SERVIDOR + 1):
			try:
				respuesta = self._sesion.get(url, params=parametros, timeout=self._timeout)
			except requests.Timeout as error:
				LOGGER.warning("Timeout al consultar %s", url)
				if intento < REINTENTOS_SERVIDOR:
					continue
				raise ErrorServicioExterno(
					"El servicio externo no respondió a tiempo. Intente más tarde."
				) from error
			except requests.ConnectionError as error:
				LOGGER.warning("Sin conexión al consultar %s", url)
				raise ErrorServicioExterno(
					"No fue posible conectar con el servicio externo. Revise su conexión."
				) from error
			except requests.RequestException as error:
				LOGGER.error("Error de requests al consultar %s: %s", url, type(error).__name__)
				raise ErrorServicioExterno("Ocurrió un error al consultar el servicio externo.") from error

			if respuesta.status_code >= 500 and intento < REINTENTOS_SERVIDOR:
				LOGGER.warning("HTTP %s en %s; reintentando", respuesta.status_code, url)
				continue
			return self._procesar_respuesta(respuesta, url)
		raise ErrorServicioExterno("El servicio externo no está disponible.")

	@staticmethod
	def _procesar_respuesta(respuesta: requests.Response, url: str) -> dict[str, Any]:
		"""Traduce el código HTTP a un mensaje seguro y valida que el cuerpo sea JSON."""

		codigo = respuesta.status_code
		if codigo in (401, 403):
			LOGGER.error("HTTP %s en %s: credencial rechazada", codigo, url)
			raise ErrorServicioExterno(
				"El servicio externo rechazó la credencial configurada. Avise al administrador."
			)
		if codigo == 404:
			raise ErrorServicioExterno("El servicio externo no encontró el dato solicitado.")
		if codigo == 429:
			raise ErrorServicioExterno(
				"Se alcanzó el límite de consultas del servicio externo. Intente más tarde."
			)
		if codigo >= 500:
			LOGGER.error("HTTP %s en %s", codigo, url)
			raise ErrorServicioExterno("El servicio externo no está disponible.")
		if codigo != 200:
			LOGGER.error("HTTP %s inesperado en %s", codigo, url)
			raise ErrorServicioExterno("El servicio externo devolvió una respuesta inesperada.")
		try:
			datos = respuesta.json()
		except ValueError as error:
			LOGGER.error("Cuerpo no JSON en %s", url)
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA) from error
		if not isinstance(datos, dict):
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA)
		return datos


@dataclass(frozen=True)
class Clima:
	"""Datos climáticos relevantes para planificar un proyecto."""

	ciudad: str
	temperatura: float
	humedad: int
	descripcion: str
	fecha_consulta: datetime


class IServicioExterno(ABC):
	"""Contrato común para los servicios externos consumidos por el sistema."""

	@abstractmethod
	def consultar(self, criterio: str) -> Any:
		"""Consulta el servicio a partir de un criterio ya validado."""


class ServicioClima(IServicioExterno):
	"""Consulta el clima actual de una ciudad en OpenWeatherMap."""

	URL_BASE = "https://api.openweathermap.org/data/2.5"
	VARIABLE_LLAVE = "OPENWEATHER_API_KEY"

	def __init__(self, cliente: ClienteHTTP | None = None, llave: str | None = None) -> None:
		self._cliente = cliente or ClienteHTTP(self.URL_BASE)
		self._llave = (llave or os.environ.get(self.VARIABLE_LLAVE, "")).strip()
		if not self._llave:
			raise ErrorServicioExterno(
				f"El servicio de clima no está configurado. Defina {self.VARIABLE_LLAVE} en .env."
			)

	def consultar(self, criterio: str) -> Clima:
		ciudad = validar_ciudad(criterio)
		datos = self._cliente.obtener_json(
			"weather",
			{"q": ciudad, "appid": self._llave, "units": "metric", "lang": "es"},
		)
		return self._interpretar(ciudad, datos)

	@staticmethod
	def _interpretar(ciudad: str, datos: dict[str, Any]) -> Clima:
		"""Extrae y valida los campos usados; cualquier ausencia o tipo erróneo se rechaza."""

		try:
			principal = datos["main"]
			temperatura = float(principal["temp"])
			humedad = int(principal["humidity"])
			descripcion = str(datos["weather"][0]["description"]).strip()
		except (KeyError, IndexError, TypeError, ValueError) as error:
			LOGGER.error("Clima con formato inesperado para %s", ciudad)
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA) from error
		if not -90 <= temperatura <= 60 or not 0 <= humedad <= 100 or not descripcion:
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA)
		return Clima(
			ciudad=str(datos.get("name") or ciudad),
			temperatura=temperatura,
			humedad=humedad,
			descripcion=descripcion,
			fecha_consulta=datetime.now(),
		)


@dataclass(frozen=True)
class Indicador:
	"""Valor vigente de un indicador económico expresado en pesos chilenos."""

	codigo: str
	nombre: str
	moneda: str
	valor: float
	fecha: date
	fecha_consulta: datetime


class ServicioIndicadores(IServicioExterno):
	"""Consulta indicadores económicos chilenos en mindicador.cl (sin llave)."""

	URL_BASE = "https://mindicador.cl/api"

	def __init__(self, cliente: ClienteHTTP | None = None) -> None:
		self._cliente = cliente or ClienteHTTP(self.URL_BASE)

	def consultar(self, criterio: str) -> Indicador:
		codigo = validar_indicador(criterio)
		datos = self._cliente.obtener_json(codigo, {})
		return self._interpretar(codigo, datos)

	@staticmethod
	def _interpretar(codigo: str, datos: dict[str, Any]) -> Indicador:
		"""Toma el valor más reciente de la serie y valida tipo, rango y fecha."""

		try:
			ultimo = datos["serie"][0]
			valor = float(ultimo["valor"])
			fecha = date.fromisoformat(str(ultimo["fecha"])[:10])
			nombre = str(datos.get("nombre") or codigo).strip()
		except (KeyError, IndexError, TypeError, ValueError) as error:
			LOGGER.error("Indicador con formato inesperado: %s", codigo)
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA) from error
		if valor <= 0 or fecha > date.today():
			raise ErrorServicioExterno(MENSAJE_RESPUESTA_INVALIDA)
		return Indicador(
			codigo=codigo,
			nombre=nombre,
			moneda=INDICADORES_PERMITIDOS[codigo],
			valor=valor,
			fecha=fecha,
			fecha_consulta=datetime.now(),
		)


@revertir_si_falla
def guardar_clima(connection: sqlite3.Connection, clima: Clima) -> int:
	"""Persiste una consulta de clima para usarla como respaldo local."""

	cursor = connection.execute(
		"""
		INSERT INTO consultas_clima
		(ciudad, temperatura, humedad, descripcion, fecha_consulta)
		VALUES (?, ?, ?, ?, ?)
		""",
		(
			clima.ciudad,
			clima.temperatura,
			clima.humedad,
			clima.descripcion,
			clima.fecha_consulta.isoformat(timespec="seconds"),
		),
	)
	connection.commit()
	return int(cursor.lastrowid)


def obtener_ultimo_clima(connection: sqlite3.Connection, ciudad: str) -> Clima | None:
	"""Devuelve la consulta de clima más reciente guardada para una ciudad."""

	fila = connection.execute(
		"""
		SELECT ciudad, temperatura, humedad, descripcion, fecha_consulta
		FROM consultas_clima
		WHERE lower(ciudad) = lower(?)
		ORDER BY fecha_consulta DESC, id_consulta DESC
		LIMIT 1
		""",
		(validar_ciudad(ciudad),),
	).fetchone()
	if fila is None:
		return None
	return Clima(
		ciudad=fila["ciudad"],
		temperatura=float(fila["temperatura"]),
		humedad=int(fila["humedad"]),
		descripcion=fila["descripcion"],
		fecha_consulta=datetime.fromisoformat(fila["fecha_consulta"]),
	)


@revertir_si_falla
def guardar_indicador(connection: sqlite3.Connection, indicador: Indicador) -> int:
	"""Persiste el valor de un indicador para usarlo como respaldo local."""

	cursor = connection.execute(
		"""
		INSERT INTO indicadores
		(codigo, nombre, moneda, valor, fecha, fecha_consulta)
		VALUES (?, ?, ?, ?, ?, ?)
		""",
		(
			indicador.codigo,
			indicador.nombre,
			indicador.moneda,
			indicador.valor,
			indicador.fecha.isoformat(),
			indicador.fecha_consulta.isoformat(timespec="seconds"),
		),
	)
	connection.commit()
	return int(cursor.lastrowid)


def obtener_ultimo_indicador(
	connection: sqlite3.Connection, codigo: str
) -> Indicador | None:
	"""Devuelve el valor más reciente guardado para un indicador."""

	fila = connection.execute(
		"""
		SELECT codigo, nombre, moneda, valor, fecha, fecha_consulta
		FROM indicadores
		WHERE codigo = ?
		ORDER BY fecha_consulta DESC, id_indicador DESC
		LIMIT 1
		""",
		(validar_indicador(codigo),),
	).fetchone()
	if fila is None:
		return None
	return Indicador(
		codigo=fila["codigo"],
		nombre=fila["nombre"],
		moneda=fila["moneda"],
		valor=float(fila["valor"]),
		fecha=date.fromisoformat(fila["fecha"]),
		fecha_consulta=datetime.fromisoformat(fila["fecha_consulta"]),
	)


@dataclass(frozen=True)
class ResultadoConsulta(Generic[T]):
	"""Dato obtenido de un servicio externo o, si falló, del respaldo local."""

	dato: T
	desde_respaldo: bool
	motivo: str | None = None


def consultar_con_respaldo(
	connection: sqlite3.Connection,
	servicio: IServicioExterno,
	criterio: str,
) -> ResultadoConsulta[Any]:
	"""Consulta el servicio; si falla, entrega el último dato guardado o propaga el error."""

	if isinstance(servicio, ServicioClima):
		guardar, obtener = guardar_clima, obtener_ultimo_clima
	elif isinstance(servicio, ServicioIndicadores):
		guardar, obtener = guardar_indicador, obtener_ultimo_indicador
	else:
		raise ValueError("El servicio indicado no tiene respaldo local configurado.")

	try:
		dato = servicio.consultar(criterio)
	except ErrorServicioExterno as error:
		respaldo = obtener(connection, criterio)
		if respaldo is None:
			raise
		LOGGER.warning("Usando respaldo local para %r: %s", criterio, error)
		return ResultadoConsulta(respaldo, True, str(error))
	guardar(connection, dato)
	return ResultadoConsulta(dato, False)


__all__ = [
	"INDICADORES_PERMITIDOS",
	"Clima",
	"ResultadoConsulta",
	"consultar_con_respaldo",
	"guardar_clima",
	"guardar_indicador",
	"obtener_ultimo_clima",
	"obtener_ultimo_indicador",
	"ClienteHTTP",
	"ErrorServicioExterno",
	"IServicioExterno",
	"Indicador",
	"ServicioClima",
	"ServicioIndicadores",
	"validar_ciudad",
	"validar_indicador",
]
