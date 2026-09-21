"""Pruebas del núcleo de dominio y persistencia (Unidad 2 y requisitos de la Unidad 1).

Ejecutar con: py -3 -m unittest -v test_nucleo
"""

from datetime import date
import builtins
import contextlib
import io
import os
import unittest

import main
import interfaz as ui

# Las pruebas usan una clave de cifrado propia, independiente del .env del equipo.
CLAVE_PRUEBAS = main.generar_clave_cifrado()
os.environ[main.VARIABLE_CLAVE_CIFRADO] = CLAVE_PRUEBAS
main.obtener_cifrador.cache_clear()


ESQUEMA_ANTIGUO = """
CREATE TABLE departamentos (
 id_departamento INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL UNIQUE);
CREATE TABLE empleados (
 rut TEXT PRIMARY KEY, nombre TEXT NOT NULL, apellido TEXT NOT NULL,
 correo TEXT NOT NULL UNIQUE, cargo TEXT NOT NULL, id_departamento INTEGER,
 FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento));
CREATE TABLE proyectos (
 id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
 descripcion TEXT NOT NULL, fecha_inicio TEXT NOT NULL, fecha_fin TEXT);
CREATE TABLE empleado_proyecto (
 rut_empleado TEXT NOT NULL, id_proyecto INTEGER NOT NULL,
 PRIMARY KEY (rut_empleado, id_proyecto),
 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE CASCADE,
 FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE);
CREATE TABLE usuarios (
 id_usuario INTEGER PRIMARY KEY AUTOINCREMENT, nombre_usuario TEXT NOT NULL UNIQUE,
 contrasena TEXT NOT NULL, activo INTEGER NOT NULL DEFAULT 1, rut_empleado TEXT UNIQUE,
 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE SET NULL);
CREATE TABLE registros_tiempo (
 id_registro INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL,
 horas REAL NOT NULL CHECK (horas > 0 AND horas <= 24), rut_empleado TEXT NOT NULL,
 id_proyecto INTEGER NOT NULL,
 FOREIGN KEY (rut_empleado) REFERENCES empleados(rut) ON DELETE CASCADE,
 FOREIGN KEY (id_proyecto) REFERENCES proyectos(id_proyecto) ON DELETE CASCADE);
INSERT INTO departamentos (nombre) VALUES ('Ventas');
INSERT INTO empleados VALUES ('11111111-1', 'Ana', 'Perez', 'ana@x.cl', 'Dev', 1);
INSERT INTO proyectos (nombre, descripcion, fecha_inicio) VALUES ('Proy', 'Desc', '2026-01-01');
INSERT INTO empleado_proyecto VALUES ('11111111-1', 1);
INSERT INTO usuarios (nombre_usuario, contrasena, rut_empleado) VALUES ('aperez', 'x', '11111111-1');
INSERT INTO registros_tiempo (fecha, horas, rut_empleado, id_proyecto) VALUES ('2026-01-02', 8, '11111111-1', 1);
"""

RUT = "11111111-1"


def empleado_completo(rut=RUT, correo="ana@x.cl"):
	return main.Empleado(
		rut, "Ana", "Perez", correo, "Dev",
		direccion="Av. Siempre Viva 123",
		telefono="+56 9 1234 5678",
		fecha_inicio_contrato=date(2025, 3, 1),
		salario=1_200_000,
	)


def ejecutar_con_entradas(funcion, entradas=()):
	"""Ejecuta una función de menú con entradas simuladas y devuelve lo impreso."""

	iterador = iter(entradas)
	salida = io.StringIO()
	original = builtins.input
	builtins.input = lambda *_: next(iterador)
	try:
		with contextlib.redirect_stdout(salida):
			funcion()
	finally:
		builtins.input = original
	return salida.getvalue()


class PruebasMigracionEmpleados(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		self.connection.executescript(ESQUEMA_ANTIGUO)

	def tearDown(self):
		self.connection.close()

	def test_agrega_columnas_y_conserva_datos_y_relaciones(self):
		main.inicializar_bd(self.connection)
		columnas = {f["name"] for f in self.connection.execute("PRAGMA table_info(empleados)")}
		self.assertTrue(
			{"id_empleado", "direccion", "telefono", "fecha_inicio_contrato", "salario"} <= columnas
		)
		fila = self.connection.execute("SELECT * FROM empleados").fetchone()
		self.assertEqual((fila["id_empleado"], fila["rut"], fila["id_departamento"]), (1, RUT, 1))
		# Las filas dependientes no fueron borradas por las claves foráneas durante la copia.
		self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM registros_tiempo").fetchone()[0], 1)
		self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM empleado_proyecto").fetchone()[0], 1)
		self.assertEqual(
			self.connection.execute("SELECT rut_empleado FROM usuarios").fetchone()[0], RUT
		)
		self.assertEqual(self.connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
		self.assertEqual(self.connection.execute("PRAGMA foreign_key_check").fetchall(), [])

	def test_migracion_es_idempotente(self):
		main.inicializar_bd(self.connection)
		main.inicializar_bd(self.connection)
		self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM empleados").fetchone()[0], 1)


class PruebasModeloEmpleado(unittest.TestCase):
	def test_ficha_completa_se_valida_y_normaliza(self):
		empleado = empleado_completo()
		self.assertEqual(empleado.telefono, "+56 9 1234 5678")
		self.assertEqual(empleado.salario, 1_200_000.0)
		self.assertEqual(empleado.id_empleado, 0)

	def test_ficha_antigua_sin_datos_personales_sigue_siendo_valida(self):
		empleado = main.Empleado(RUT, "Ana", "Perez", "ana@x.cl", "Dev")
		self.assertEqual((empleado.direccion, empleado.telefono), ("", ""))
		self.assertIsNone(empleado.salario)

	def test_datos_personales_invalidos_se_rechazan(self):
		casos = [
			{"telefono": "abc"},
			{"telefono": "12"},
			{"salario": 0},
			{"salario": -1},
			{"fecha_inicio_contrato": "2025-01-01"},
		]
		for campos in casos:
			with self.subTest(campos=campos), self.assertRaises(ValueError):
				main.Empleado(RUT, "Ana", "Perez", "ana@x.cl", "Dev", **campos)

	def test_tarifa_hora_segun_direccion_del_trabajo(self):
		# 1.200.000 / 30 x 7 / 44 = 6.363,64
		self.assertAlmostEqual(main.calcular_tarifa_hora(1_200_000), 6363.64, 2)
		with self.assertRaises(ValueError):
			main.calcular_tarifa_hora(0)


class PruebasPersistenciaEmpleado(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)

	def tearDown(self):
		self.connection.close()

	def test_guardar_asigna_id_y_persiste_datos_personales(self):
		empleado = empleado_completo()
		main.guardar_empleado(self.connection, empleado)
		self.assertEqual(empleado.id_empleado, 1)
		fila = self.connection.execute("SELECT * FROM empleados WHERE rut = ?", (RUT,)).fetchone()
		leido = main.fila_a_empleado(fila)
		self.assertEqual(leido, empleado)

	def test_listar_incluye_datos_personales(self):
		main.guardar_empleado(self.connection, empleado_completo())
		fila = main.listar_empleados(self.connection)[0]
		self.assertEqual(fila["salario"], 1_200_000.0)
		self.assertEqual(fila["fecha_inicio_contrato"], "2025-03-01")

	def test_actualizar_valida_y_guarda_los_nuevos_campos(self):
		main.guardar_empleado(self.connection, empleado_completo())
		actualizado = main.actualizar_empleado(
			self.connection, RUT, nombre="Ana", apellido="Perez", correo="ana@x.cl",
			cargo="Lead", direccion="Calle 2", telefono="987654321",
			fecha_inicio_contrato=date(2024, 1, 1), salario=1_500_000,
		)
		self.assertTrue(actualizado)
		leido = main.fila_a_empleado(self.connection.execute("SELECT * FROM empleados").fetchone())
		self.assertEqual((leido.cargo, leido.salario, leido.telefono), ("Lead", 1_500_000.0, "987654321"))
		with self.assertRaises(ValueError):
			main.actualizar_empleado(
				self.connection, RUT, nombre="Ana", apellido="Perez", correo="ana@x.cl",
				cargo="Lead", salario=-5,
			)

	def test_usuario_con_empleado_guarda_la_ficha_completa(self):
		usuario = main.Usuario(0, "aperez", "clave", rol="empleado")
		main.guardar_usuario_con_empleado(self.connection, usuario, empleado_completo())
		leido = main.fila_a_empleado(self.connection.execute("SELECT * FROM empleados").fetchone())
		self.assertEqual((leido.direccion, leido.salario), ("Av. Siempre Viva 123", 1_200_000.0))


class PruebasCifradoDatosPersonales(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)

	def tearDown(self):
		self.connection.close()
		os.environ[main.VARIABLE_CLAVE_CIFRADO] = CLAVE_PRUEBAS
		main.obtener_cifrador.cache_clear()

	def test_la_base_solo_contiene_tokens(self):
		main.guardar_empleado(self.connection, empleado_completo())
		fila = self.connection.execute("SELECT direccion, telefono, salario FROM empleados").fetchone()
		for valor in fila:
			self.assertTrue(str(valor).startswith(main.PREFIJO_TOKEN_FERNET), valor)
		self.assertNotIn("Siempre Viva", str(tuple(fila)))
		self.assertNotIn("1200000", str(tuple(fila)))

	def test_cifrar_y_descifrar_devuelve_el_original(self):
		cifrador = main.CifradorDatos(CLAVE_PRUEBAS)
		token = cifrador.cifrar("Av. Uno 1")
		self.assertNotEqual(token, "Av. Uno 1")
		self.assertEqual(cifrador.descifrar(token), "Av. Uno 1")
		self.assertNotEqual(cifrador.cifrar("Av. Uno 1"), token, "cada cifrado usa un IV distinto")

	def test_clave_incorrecta_produce_mensaje_claro(self):
		main.guardar_empleado(self.connection, empleado_completo())
		os.environ[main.VARIABLE_CLAVE_CIFRADO] = main.generar_clave_cifrado()
		main.obtener_cifrador.cache_clear()
		with self.assertRaises(ValueError) as contexto:
			main.listar_empleados(self.connection)
		self.assertIn("no corresponde", str(contexto.exception))

	def test_clave_ausente_o_invalida_se_informa(self):
		with self.assertRaises(ValueError) as contexto:
			main.CifradorDatos("   ")
		self.assertIn(main.VARIABLE_CLAVE_CIFRADO, str(contexto.exception))
		with self.assertRaises(ValueError):
			main.CifradorDatos("clave-que-no-es-fernet")

	def test_valores_heredados_en_texto_plano_se_cifran_al_iniciar(self):
		self.connection.execute(
			"INSERT INTO empleados (rut, nombre, apellido, correo, cargo, direccion, telefono, salario) "
			"VALUES (?, 'Ana', 'Perez', 'ana@x.cl', 'Dev', 'Calle 5', '912345678', 900000)",
			(RUT,),
		)
		self.connection.commit()
		self.assertEqual(main.cifrar_datos_personales_pendientes(self.connection), 1)
		self.assertEqual(main.cifrar_datos_personales_pendientes(self.connection), 0)
		fila = self.connection.execute("SELECT direccion, salario FROM empleados").fetchone()
		self.assertTrue(str(fila["direccion"]).startswith(main.PREFIJO_TOKEN_FERNET))
		leido = main.fila_a_empleado(self.connection.execute("SELECT * FROM empleados").fetchone())
		self.assertEqual((leido.direccion, leido.telefono, leido.salario), ("Calle 5", "912345678", 900000.0))


class PruebasMenuEmpleado(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		self.admin = main.Usuario(1, "admin", "x", rol="admin")
		self.empleado = main.Usuario(2, "e", "x", rol="empleado")

	def tearDown(self):
		self.connection.close()

	def test_registro_pide_ficha_completa_y_repite_solo_el_campo_invalido(self):
		ui.leer_contrasena = lambda mensaje: "clave"
		salida = ejecutar_con_entradas(
			lambda: ui.registrar_usuario_menu(self.connection),
			["empleado", "Ana", "Perez", "Soto", RUT, "ana@x.cl", "Dev",
			 "Av. Uno 1", "abc", "+56 9 1234 5678", "2025-03-01", "-1", "1200000"],
		)
		self.assertIn("El teléfono solo puede contener", salida)
		self.assertIn("El salario debe ser un número mayor que 0.", salida)
		self.assertIn("Su usuario es: aperez", salida)
		leido = main.fila_a_empleado(self.connection.execute("SELECT * FROM empleados").fetchone())
		self.assertEqual((leido.telefono, leido.salario), ("+56 9 1234 5678", 1_200_000.0))

	def test_listado_oculta_datos_personales_a_empleados(self):
		main.guardar_empleado(self.connection, empleado_completo())
		basico = ejecutar_con_entradas(lambda: ui.mostrar_empleados(self.connection))
		detallado = ejecutar_con_entradas(lambda: ui.mostrar_empleados(self.connection, detallado=True))
		self.assertNotIn("Salario", basico)
		self.assertNotIn("Siempre Viva", basico)
		self.assertIn("Salario: $1,200,000", detallado)
		self.assertIn("Siempre Viva", detallado)

	def test_pago_usa_el_salario_del_empleado(self):
		empleado = empleado_completo()
		main.guardar_empleado(self.connection, empleado)
		proyecto = main.Proyecto(0, "Proy", "Desc", date(2026, 1, 1))
		main.guardar_proyecto(self.connection, proyecto)
		main.asignar_empleado_proyecto_bd(self.connection, RUT, proyecto.id_proyecto)
		main.guardar_registro_tiempo(
			self.connection, main.RegistroTiempo(0, date(2026, 1, 2), 10, empleado, proyecto)
		)
		indicador = ui.ResultadoConsulta(
			ui.ServicioIndicadores._interpretar(
				"dolar", {"nombre": "Dólar", "serie": [{"fecha": "2026-01-02", "valor": 1000.0}]}
			),
			False,
		)
		ui.obtener_indicador = lambda connection: indicador
		salida = ejecutar_con_entradas(
			lambda: ui.calcular_pago_menu(self.connection, self.admin), [RUT]
		)
		# 10 horas x 6.363,64 = 63.636,40 CLP = 63,64 USD
		self.assertIn("Valor hora: $6,363.64", salida)
		self.assertIn("63.64 USD", salida)

	def test_pago_sin_salario_se_rechaza(self):
		main.guardar_empleado(self.connection, main.Empleado(RUT, "Ana", "Perez", "ana@x.cl", "Dev"))
		with self.assertRaises(ValueError) as contexto:
			ejecutar_con_entradas(lambda: ui.calcular_pago_menu(self.connection, self.admin), [RUT])
		self.assertIn("salario", str(contexto.exception))


class PruebasAcceso(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		ui.leer_contrasena = lambda mensaje: "1234" if "Codigo" in mensaje else "clave"
		os.environ["ECOTECH_CODIGO_ADMIN"] = "1234"

	def tearDown(self):
		self.connection.close()

	def test_sin_usuarios_el_menu_ofrece_registrar_administrador(self):
		salida = ejecutar_con_entradas(lambda: ui.mostrar_menu_acceso(False), ["0"])
		self.assertIn("2. Registrar administrador inicial", salida)

	def test_primer_usuario_se_crea_como_admin_sin_preguntar_rol(self):
		salida = ejecutar_con_entradas(
			lambda: ui.procesar_opcion_acceso(self.connection, "2", False),
			["Ana", "Perez", "Soto"],  # no se pide rol: contraseña y código vienen simulados
		)
		self.assertIn("debe ser administrador", salida)
		self.assertIn("Su usuario es: aperez", salida)
		fila = self.connection.execute("SELECT rol FROM usuarios").fetchone()
		self.assertEqual(fila["rol"], "admin")

	def test_con_usuarios_no_hay_autoregistro(self):
		main.guardar_usuario(self.connection, main.Usuario(0, "admin", "clave", rol="admin"))
		self.assertTrue(ui.hay_usuarios(self.connection))
		salida = ejecutar_con_entradas(lambda: ui.mostrar_menu_acceso(True), ["0"])
		self.assertNotIn("Registrar", salida)
		salida = ejecutar_con_entradas(lambda: ui.procesar_opcion_acceso(self.connection, "2", True))
		self.assertIn("lo realiza un administrador o RR.HH.", salida)
		self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0], 1)

	def test_login_rechaza_credenciales_vacias_sin_consultar(self):
		ui.leer_contrasena = lambda mensaje: "   "
		salida = ejecutar_con_entradas(lambda: ui.autenticar_usuario(self.connection), ["admin"])
		self.assertIn("no pueden estar vacíos", salida)
		ui.leer_contrasena = lambda mensaje: "clave"
		salida = ejecutar_con_entradas(lambda: ui.autenticar_usuario(self.connection), [""])
		self.assertIn("no pueden estar vacíos", salida)

	def test_login_correcto_devuelve_usuario_con_rol(self):
		main.guardar_usuario(self.connection, main.Usuario(0, "admin", "clave", rol="admin"))
		resultado = {}
		ejecutar_con_entradas(
			lambda: resultado.setdefault("u", ui.autenticar_usuario(self.connection)), ["admin"]
		)
		self.assertEqual(resultado["u"].rol, "admin")


class PruebasGerenteYDescripcionTarea(unittest.TestCase):
	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		self.empleado = empleado_completo()
		main.guardar_empleado(self.connection, self.empleado)
		self.admin = main.Usuario(1, "admin", "x", rol="admin")

	def tearDown(self):
		self.connection.close()

	def test_migracion_agrega_gerente_y_descripcion_a_base_antigua(self):
		antigua = main.conectar_bd(":memory:")
		antigua.executescript(ESQUEMA_ANTIGUO)
		main.inicializar_bd(antigua)
		self.assertIn("rut_gerente", {f["name"] for f in antigua.execute("PRAGMA table_info(departamentos)")})
		self.assertIn("descripcion_tarea", {f["name"] for f in antigua.execute("PRAGMA table_info(registros_tiempo)")})
		fila = antigua.execute("SELECT descripcion_tarea FROM registros_tiempo").fetchone()
		self.assertEqual(fila["descripcion_tarea"], "")
		antigua.close()

	def test_departamento_con_gerente(self):
		id_departamento = main.guardar_departamento(self.connection, "Ventas", RUT)
		fila = main.listar_departamentos(self.connection)[0]
		self.assertEqual((fila["id_departamento"], fila["gerente"]), (id_departamento, "Ana Perez"))
		main.asignar_gerente_departamento(self.connection, id_departamento, None)
		self.assertIsNone(main.listar_departamentos(self.connection)[0]["gerente"])
		with self.assertRaises(ValueError):
			main.asignar_gerente_departamento(self.connection, id_departamento, "22222222-2")
		with self.assertRaises(ValueError):
			main.asignar_gerente_departamento(self.connection, 99, RUT)

	def test_gerente_eliminado_deja_el_departamento_sin_gerente(self):
		id_departamento = main.guardar_departamento(self.connection, "Ventas", RUT)
		main.eliminar_empleado(self.connection, RUT)
		self.assertIsNone(main.listar_departamentos(self.connection)[0]["rut_gerente"])
		self.assertEqual(id_departamento, 1)

	def test_modelo_departamento_valida_gerente(self):
		departamento = main.Departamento(1, "Ventas", gerente=self.empleado)
		self.assertEqual(departamento.gerente.rut, RUT)
		with self.assertRaises(ValueError):
			main.Departamento(1, "Ventas", gerente="no es empleado")

	def _proyecto_asignado(self):
		proyecto = main.Proyecto(0, "Proy", "Desc", date(2026, 1, 1))
		main.guardar_proyecto(self.connection, proyecto)
		main.asignar_empleado_proyecto_bd(self.connection, RUT, proyecto.id_proyecto)
		return proyecto

	def test_registro_con_descripcion_se_valida_y_persiste(self):
		proyecto = self._proyecto_asignado()
		registro = main.RegistroTiempo(
			0, date(2026, 1, 2), 8, self.empleado, proyecto, "  Instalacion de paneles  "
		)
		self.assertEqual(registro.descripcion_tarea, "Instalacion de paneles")
		main.guardar_registro_tiempo(self.connection, registro)
		fila = main.listar_registros_tiempo(self.connection)[0]
		self.assertEqual(fila["descripcion_tarea"], "Instalacion de paneles")
		with self.assertRaises(ValueError):
			main.RegistroTiempo(0, date(2026, 1, 2), 8, self.empleado, proyecto, "x" * 201)
		self.assertTrue(
			main.actualizar_registro_tiempo(
				self.connection, fila["id_registro"], fecha=date(2026, 1, 3), horas=4,
				descripcion_tarea="Revision",
			)
		)
		self.assertEqual(main.listar_registros_tiempo(self.connection)[0]["descripcion_tarea"], "Revision")

	def test_exportadores_incluyen_la_descripcion(self):
		proyecto = self._proyecto_asignado()
		registros = [main.RegistroTiempo(1, date(2026, 1, 2), 8, self.empleado, proyecto, 'Tarea "A"')]
		self.assertIn("- Tarea \"A\"", main.ExportadorPDF().exportar(registros))
		csv = main.ExportadorExcel().exportar(registros)
		self.assertIn("descripcion_tarea", csv.splitlines()[0])
		self.assertTrue(csv.splitlines()[1].endswith(',"Tarea ""A"""'))

	def test_menu_registra_horas_con_descripcion_y_repite_si_esta_vacia(self):
		proyecto = self._proyecto_asignado()
		salida = ejecutar_con_entradas(
			lambda: ui.registrar_tiempo_menu(self.connection, self.admin),
			[RUT, str(proyecto.id_proyecto), "2026-01-02", "6", "", "Cableado"],
		)
		self.assertIn("no puede estar vacío", salida)
		self.assertIn("guardado correctamente", salida)
		listado = ejecutar_con_entradas(lambda: ui.mostrar_registros_tiempo_menu(self.connection, self.admin))
		self.assertIn("| Cableado", listado)

	def test_menu_crea_departamento_y_asigna_gerente(self):
		salida = ejecutar_con_entradas(
			lambda: ui.crear_departamento_menu(self.connection), ["Ventas", ""]
		)
		self.assertIn("creado con ID 1", salida)
		salida = ejecutar_con_entradas(lambda: ui.asignar_gerente_menu(self.connection), ["1", RUT])
		self.assertIn("Gerente actualizado", salida)
		listado = ejecutar_con_entradas(lambda: ui.mostrar_departamentos(self.connection))
		self.assertIn("Gerente: Ana Perez", listado)


if __name__ == "__main__":
	unittest.main()
