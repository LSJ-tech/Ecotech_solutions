"""Pruebas de la Unidad 3 sin acceso a la red.

Ejecutar con: py -3 -m unittest -v test_servicios_externos
"""

from datetime import date
from unittest.mock import MagicMock
import logging
import os
import unittest

import requests

import main
import servicios_externos as se

# Las pruebas provocan fallos a propósito; el registro técnico no aporta en esta salida.
logging.getLogger("ecotech.servicios").disabled = True


RESPUESTA_CLIMA = {
	"name": "Calama",
	"main": {"temp": 21.0, "humidity": 12},
	"weather": [{"description": "despejado"}],
}
RESPUESTA_DOLAR = {
	"nombre": "Dólar observado",
	"serie": [{"fecha": "2026-09-20T03:00:00.000Z", "valor": 958.42}],
}
LLAVE_PRUEBA = "llave-de-prueba"


def sesion_simulada(status=200, json=None, exc=None, secuencia=None, tamano=100):
	"""Crea una sesión falsa de requests que responde según los parámetros."""

	sesion = MagicMock()

	def get(url, params=None, timeout=None):
		assert url.startswith("https://"), "toda petición debe usar HTTPS"
		assert timeout == se.TIMEOUT_SEGUNDOS, "toda petición debe llevar timeout"
		if secuencia:
			item = secuencia.pop(0)
			if isinstance(item, Exception):
				raise item
			estado, cuerpo = item
		else:
			if exc:
				raise exc
			estado, cuerpo = status, json
		respuesta = MagicMock()
		respuesta.status_code = estado
		respuesta.content = b"x" * tamano
		if cuerpo is ValueError:
			respuesta.json.side_effect = ValueError("no es JSON")
		else:
			respuesta.json.return_value = cuerpo
		return respuesta

	sesion.get.side_effect = get
	return sesion


def servicio_clima(**kwargs):
	cliente = se.ClienteHTTP(se.ServicioClima.URL_BASE, sesion=sesion_simulada(**kwargs))
	return se.ServicioClima(cliente=cliente, llave=LLAVE_PRUEBA)


def servicio_indicadores(**kwargs):
	cliente = se.ClienteHTTP(se.ServicioIndicadores.URL_BASE, sesion=sesion_simulada(**kwargs))
	return se.ServicioIndicadores(cliente=cliente)


class PruebasValidacionEntradas(unittest.TestCase):
	def test_ciudad_valida_se_normaliza(self):
		self.assertEqual(se.validar_ciudad("  Viña del Mar "), "Viña del Mar")

	def test_ciudad_invalida_se_rechaza(self):
		for ciudad in ["", "S", "Santiago; DROP TABLE", "x" * 61, "Valpo123"]:
			with self.subTest(ciudad=ciudad), self.assertRaises(ValueError):
				se.validar_ciudad(ciudad)

	def test_indicador_fuera_de_lista_blanca_se_rechaza(self):
		for indicador in ["", "peso", "dolar; drop", "bitcoin"]:
			with self.subTest(indicador=indicador), self.assertRaises(ValueError):
				se.validar_indicador(indicador)

	def test_indicador_se_normaliza(self):
		self.assertEqual(se.validar_indicador(" DOLAR "), "dolar")

	def test_cliente_exige_https(self):
		with self.assertRaises(ValueError):
			se.ClienteHTTP("http://inseguro.example")


class PruebasClienteHTTP(unittest.TestCase):
	def assert_error(self, fragmento, **kwargs):
		with self.assertRaises(se.ErrorServicioExterno) as contexto:
			servicio_clima(**kwargs).consultar("Santiago")
		mensaje = str(contexto.exception)
		self.assertIn(fragmento, mensaje)
		self.assertNotIn(LLAVE_PRUEBA, mensaje, "el mensaje nunca debe contener la llave")
		self.assertNotIn("appid", mensaje)

	def test_credencial_rechazada(self):
		self.assert_error("rechazó la credencial", status=401, json={"message": "Invalid API key"})

	def test_no_encontrado(self):
		self.assert_error("no encontró", status=404, json={})

	def test_limite_de_consultas(self):
		self.assert_error("límite", status=429, json={})

	def test_servidor_caido_tras_reintento(self):
		self.assert_error("no está disponible", secuencia=[(500, {}), (503, {})])

	def test_reintento_exitoso_tras_500(self):
		clima = servicio_clima(secuencia=[(500, {}), (200, RESPUESTA_CLIMA)]).consultar("Santiago")
		self.assertEqual(clima.temperatura, 21.0)

	def test_timeout(self):
		self.assert_error("no respondió a tiempo", exc=requests.Timeout())

	def test_sin_conexion(self):
		self.assert_error("conectar", exc=requests.ConnectionError())

	def test_cuerpo_no_json(self):
		self.assert_error("formato esperado", status=200, json=ValueError)

	def test_respuesta_demasiado_grande(self):
		self.assert_error(
			"formato esperado", status=200, json=RESPUESTA_CLIMA, tamano=se.MAX_BYTES_RESPUESTA + 1
		)


class PruebasServicioClima(unittest.TestCase):
	def test_respuesta_correcta(self):
		clima = servicio_clima(json=RESPUESTA_CLIMA).consultar("Calama")
		self.assertEqual((clima.ciudad, clima.temperatura, clima.humedad), ("Calama", 21.0, 12))
		self.assertEqual(clima.descripcion, "despejado")

	def test_respuesta_malformada(self):
		casos = [
			{},
			{"main": {"temp": "x"}},
			{"main": {"temp": 999, "humidity": 5}, "weather": [{"description": "?"}]},
			{"main": {"temp": 20, "humidity": 5}, "weather": []},
		]
		for cuerpo in casos:
			with self.subTest(cuerpo=cuerpo), self.assertRaises(se.ErrorServicioExterno):
				servicio_clima(json=cuerpo).consultar("Calama")

	def test_sin_llave_configurada(self):
		original = os.environ.pop(se.ServicioClima.VARIABLE_LLAVE, None)
		try:
			with self.assertRaises(se.ErrorServicioExterno) as contexto:
				se.ServicioClima()
			self.assertIn(se.ServicioClima.VARIABLE_LLAVE, str(contexto.exception))
		finally:
			if original is not None:
				os.environ[se.ServicioClima.VARIABLE_LLAVE] = original


class PruebasServicioIndicadores(unittest.TestCase):
	def test_respuesta_correcta(self):
		indicador = servicio_indicadores(json=RESPUESTA_DOLAR).consultar("dolar")
		self.assertEqual(indicador.moneda, "USD")
		self.assertEqual(indicador.valor, 958.42)
		self.assertEqual(indicador.fecha, date(2026, 9, 20))

	def test_respuesta_malformada(self):
		casos = [
			{},
			{"serie": []},
			{"serie": [{"valor": "abc", "fecha": "2026-01-01"}]},
			{"serie": [{"valor": -5, "fecha": "2026-01-01"}]},
			{"serie": [{"valor": 5, "fecha": "2099-01-01"}]},
		]
		for cuerpo in casos:
			with self.subTest(cuerpo=cuerpo), self.assertRaises(se.ErrorServicioExterno):
				servicio_indicadores(json=cuerpo).consultar("dolar")


class PruebasCalculoPago(unittest.TestCase):
	def test_conversion_con_redondeo(self):
		pago = main.calcular_pago("11111111-1", 10, 15000, "usd", 958.42)
		self.assertEqual(pago.monto_clp, 150000.0)
		self.assertEqual(pago.moneda, "USD")
		self.assertEqual(pago.monto_moneda, round(150000 / 958.42, 2))

	def test_valores_no_positivos_se_rechazan(self):
		casos = [(0, 1, 1), (1, -1, 1), (1, 1, 0), (True, 1, 1)]
		for horas, tarifa, cambio in casos:
			with self.subTest(horas=horas, tarifa=tarifa, cambio=cambio), self.assertRaises(ValueError):
				main.calcular_pago("11111111-1", horas, tarifa, "USD", cambio)


class PruebasRespaldoLocal(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)

	def tearDown(self):
		self.connection.close()

	def test_consulta_exitosa_se_persiste(self):
		resultado = se.consultar_con_respaldo(self.connection, servicio_clima(json=RESPUESTA_CLIMA), "Calama")
		self.assertFalse(resultado.desde_respaldo)
		filas = self.connection.execute("SELECT COUNT(*) FROM consultas_clima").fetchone()[0]
		self.assertEqual(filas, 1)

	def test_fallo_usa_respaldo_con_motivo(self):
		se.consultar_con_respaldo(self.connection, servicio_clima(json=RESPUESTA_CLIMA), "Calama")
		resultado = se.consultar_con_respaldo(
			self.connection, servicio_clima(exc=requests.ConnectionError()), "calama"
		)
		self.assertTrue(resultado.desde_respaldo)
		self.assertEqual(resultado.dato.ciudad, "Calama")
		self.assertIn("conectar", resultado.motivo)

	def test_fallo_sin_respaldo_propaga_error(self):
		with self.assertRaises(se.ErrorServicioExterno):
			se.consultar_con_respaldo(self.connection, servicio_clima(status=503, json={}), "Antofagasta")

	def test_respaldo_entrega_el_mas_reciente(self):
		se.consultar_con_respaldo(self.connection, servicio_indicadores(json=RESPUESTA_DOLAR), "dolar")
		nuevo = {"nombre": "Dólar observado", "serie": [{"fecha": "2026-09-21T03:00:00.000Z", "valor": 960.0}]}
		se.consultar_con_respaldo(self.connection, servicio_indicadores(json=nuevo), "dolar")
		resultado = se.consultar_con_respaldo(
			self.connection, servicio_indicadores(exc=requests.Timeout()), "DOLAR"
		)
		self.assertTrue(resultado.desde_respaldo)
		self.assertEqual(resultado.dato.valor, 960.0)

	def test_lista_blanca_aplica_al_respaldo(self):
		with self.assertRaises(ValueError):
			se.obtener_ultimo_indicador(self.connection, "bitcoin")

	def test_servicio_sin_respaldo_configurado(self):
		with self.assertRaises(ValueError):
			se.consultar_con_respaldo(self.connection, MagicMock(spec=se.IServicioExterno), "x")


if __name__ == "__main__":
	unittest.main()
