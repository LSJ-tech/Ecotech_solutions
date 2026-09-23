"""Pruebas del núcleo de dominio y persistencia (Unidad 2 y requisitos de la Unidad 1).

Ejecutar con: py -3 -m unittest -v test_nucleo
"""

from datetime import date
from pathlib import Path
import builtins
import contextlib
import io
import os
import shutil
import tempfile
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
		usuario = main.Usuario(0, "aperez", "Clave1234", rol="empleado")
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
		ui.leer_contrasena = lambda mensaje: "Clave1234"
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
		ui.leer_contrasena = lambda mensaje: "1234" if "Codigo" in mensaje else "Clave1234"
		os.environ["ECOTECH_CODIGO_ADMIN"] = "1234"

	def tearDown(self):
		self.connection.close()

	def test_sin_usuarios_el_menu_ofrece_registrar_administrador(self):
		salida = ejecutar_con_entradas(lambda: ui.mostrar_menu_acceso(False), ["0"])
		self.assertIn("2. Registrar administrador inicial", salida)

	def test_primer_usuario_se_crea_como_admin_con_su_ficha(self):
		salida = ejecutar_con_entradas(
			lambda: ui.procesar_opcion_acceso(self.connection, "2", False),
			# No se pide rol (contraseña y código vienen simulados), pero sí la ficha completa.
			["Ana", "Perez", "Soto", RUT, "ana@x.cl", "Jefa de proyectos", "Av. Uno 1",
			 "+56 9 1234 5678", "2025-03-01", "1200000"],
		)
		self.assertIn("debe ser administrador", salida)
		self.assertIn("Su usuario es: aperez", salida)
		fila = self.connection.execute("SELECT rol, rut_empleado FROM usuarios").fetchone()
		self.assertEqual((fila["rol"], fila["rut_empleado"]), ("admin", RUT))
		# La cuenta admin queda vinculada a una ficha real, con su ID automático.
		empleado = main.listar_empleados(self.connection)[0]
		self.assertEqual((empleado["rut"], empleado["cargo"]), (RUT, "Jefa de proyectos"))
		self.assertEqual(empleado["id_empleado"], 1)

	def test_el_rut_invalido_se_repite_sin_reiniciar_el_formulario(self):
		salida = ejecutar_con_entradas(
			lambda: ui.registrar_usuario_menu(self.connection, rol_forzado="admin"),
			["Ana", "Perez", "Soto", "12345678-9", RUT, "ana@x.cl", "Dev", "Av. Uno 1",
			 "+56 9 1234 5678", "2025-03-01", "1200000"],
		)
		self.assertIn("dígito verificador", salida)
		self.assertIn("Su usuario es: aperez", salida)
		self.assertEqual(
			self.connection.execute("SELECT rut_empleado FROM usuarios").fetchone()[0], RUT
		)

	def test_con_usuarios_no_hay_autoregistro(self):
		main.guardar_usuario(self.connection, main.Usuario(0, "admin", "Clave1234", rol="admin"))
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
		ui.leer_contrasena = lambda mensaje: "Clave1234"
		salida = ejecutar_con_entradas(lambda: ui.autenticar_usuario(self.connection), [""])
		self.assertIn("no pueden estar vacíos", salida)

	def test_login_correcto_devuelve_usuario_con_rol(self):
		main.guardar_usuario(self.connection, main.Usuario(0, "admin", "Clave1234", rol="admin"))
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
		main.guardar_registro_tiempo(
			self.connection,
			main.RegistroTiempo(0, date(2026, 1, 2), 8, self.empleado, proyecto, 'Tarea "A"'),
		)
		informe = main.construir_informe_registros(main.listar_registros_tiempo(self.connection))
		self.assertIn('| Tarea "A"', main.ExportadorPDF().exportar(informe))
		csv = main.ExportadorExcel().exportar(informe)
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


class PruebasCrudCompleto(unittest.TestCase):
	"""Edición, eliminación y desasignación desde el núcleo y desde el menú."""

	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		self.empleado = empleado_completo()
		main.guardar_empleado(self.connection, self.empleado)
		self.proyecto = main.Proyecto(0, "Proy", "Desc", date(2026, 1, 1))
		main.guardar_proyecto(self.connection, self.proyecto)
		main.asignar_empleado_proyecto_bd(self.connection, RUT, self.proyecto.id_proyecto)
		main.guardar_registro_tiempo(
			self.connection,
			main.RegistroTiempo(0, date(2026, 1, 2), 8, self.empleado, self.proyecto, "Cableado"),
		)
		self.admin = main.Usuario(1, "admin", "x", rol="admin")
		self.cuenta_empleado = main.Usuario(2, "aperez", "Clave1234", empleado=self.empleado, rol="empleado")

	def tearDown(self):
		self.connection.close()

	def _contar(self, tabla):
		return self.connection.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]

	def test_desasignar_conserva_horas_e_impide_registrar_nuevas(self):
		self.assertTrue(main.desasignar_empleado_proyecto_bd(self.connection, RUT, self.proyecto.id_proyecto))
		self.assertFalse(main.desasignar_empleado_proyecto_bd(self.connection, RUT, self.proyecto.id_proyecto))
		self.assertEqual(self._contar("registros_tiempo"), 1)
		self.assertEqual(main.listar_empleados_proyecto(self.connection, self.proyecto.id_proyecto), [])
		with self.assertRaises(ValueError):
			main.guardar_registro_tiempo(
				self.connection,
				main.RegistroTiempo(0, date(2026, 1, 3), 2, self.empleado, self.proyecto, "Nada"),
			)

	def test_desasignar_en_el_dominio_es_simetrico(self):
		main.asignar_empleado_a_proyecto(self.empleado, self.proyecto)
		main.desasignar_empleado_de_proyecto(self.empleado, self.proyecto)
		self.assertEqual((self.empleado.proyectos, self.proyecto.empleados), ([], []))
		main.desasignar_empleado_de_proyecto(self.empleado, self.proyecto)  # idempotente

	def test_eliminar_departamento_con_empleados_se_rechaza(self):
		id_departamento = main.guardar_departamento(self.connection, "Ventas")
		main.asignar_empleado_departamento_bd(self.connection, RUT, id_departamento)
		with self.assertRaisesRegex(ValueError, "1 empleado"):
			main.eliminar_departamento(self.connection, id_departamento)
		self.assertEqual(self._contar("departamentos"), 1)
		main.eliminar_empleado(self.connection, RUT)
		self.assertTrue(main.eliminar_departamento(self.connection, id_departamento))

	def test_eliminar_empleado_borra_su_cuenta_y_sus_horas(self):
		main.guardar_usuario(self.connection, self.cuenta_empleado)
		self.assertEqual(self._contar("usuarios"), 1)
		self.assertTrue(main.eliminar_empleado(self.connection, RUT))
		self.assertEqual((self._contar("usuarios"), self._contar("registros_tiempo")), (0, 0))
		self.assertFalse(main.eliminar_empleado(self.connection, RUT))

	def test_menu_edita_ficha_conservando_valores_con_enter(self):
		salida = ejecutar_con_entradas(
			lambda: ui.editar_empleado_menu(self.connection),
			[RUT, "", "", "", "Lider", "", "abc", "+56 9 8888 7777", "", "-5", "1500000"],
		)
		self.assertIn("Ficha actualizada", salida)
		self.assertIn("solo puede contener", salida)  # el teléfono inválido repitió solo ese campo
		ficha = main.listar_empleados(self.connection)[0]
		self.assertEqual((ficha["nombre"], ficha["cargo"], ficha["telefono"]), ("Ana", "Lider", "+56 9 8888 7777"))
		self.assertEqual(ficha["salario"], 1_500_000.0)
		self.assertEqual(ficha["direccion"], "Av. Siempre Viva 123")

	def test_menu_elimina_empleado_solo_con_confirmacion(self):
		salida = ejecutar_con_entradas(
			lambda: ui.eliminar_empleado_menu(self.connection, self.admin), [RUT, "n"]
		)
		self.assertIn("cancelada", salida)
		self.assertEqual(self._contar("empleados"), 1)
		with self.assertRaisesRegex(ValueError, "propia ficha"):
			ejecutar_con_entradas(
				lambda: ui.eliminar_empleado_menu(self.connection, self.cuenta_empleado), [RUT]
			)
		salida = ejecutar_con_entradas(
			lambda: ui.eliminar_empleado_menu(self.connection, self.admin), [RUT, "s"]
		)
		self.assertIn("eliminado correctamente", salida)
		self.assertEqual(self._contar("empleados"), 0)

	def test_menu_edita_y_elimina_departamento(self):
		id_departamento = main.guardar_departamento(self.connection, "Ventas", RUT)
		salida = ejecutar_con_entradas(
			lambda: ui.editar_departamento_menu(self.connection), [str(id_departamento), "Comercial"]
		)
		self.assertIn("actualizado", salida)
		fila = main.listar_departamentos(self.connection)[0]
		self.assertEqual((fila["nombre"], fila["gerente"]), ("Comercial", "Ana Perez"))
		salida = ejecutar_con_entradas(
			lambda: ui.eliminar_departamento_menu(self.connection), [str(id_departamento), "s"]
		)
		self.assertIn("eliminado", salida)
		self.assertEqual(self._contar("departamentos"), 0)
		with self.assertRaisesRegex(ValueError, "no existe"):
			ejecutar_con_entradas(lambda: ui.editar_departamento_menu(self.connection), ["99"])

	def test_menu_edita_elimina_y_desasigna_proyecto(self):
		id_proyecto = str(self.proyecto.id_proyecto)
		salida = ejecutar_con_entradas(
			lambda: ui.editar_proyecto_menu(self.connection),
			[id_proyecto, "", "", "", "2025-12-31", "2026-06-30", "Temuco"],
		)
		self.assertIn("anterior a la fecha de inicio", salida)
		fila = main.listar_proyectos(self.connection)[0]
		self.assertEqual((fila["nombre"], fila["fecha_fin"], fila["ciudad"]), ("Proy", "2026-06-30", "Temuco"))
		salida = ejecutar_con_entradas(
			lambda: ui.desasignar_proyecto_menu(self.connection), [id_proyecto, RUT]
		)
		self.assertIn("Ana Perez", salida)
		self.assertIn("se conservan", salida)
		with self.assertRaisesRegex(ValueError, "no está asignado"):
			ejecutar_con_entradas(lambda: ui.desasignar_proyecto_menu(self.connection), [id_proyecto, RUT])
		salida = ejecutar_con_entradas(
			lambda: ui.eliminar_proyecto_menu(self.connection), [id_proyecto, "s"]
		)
		self.assertIn("eliminado correctamente", salida)
		self.assertEqual((self._contar("proyectos"), self._contar("registros_tiempo")), (0, 0))

	def test_menu_registro_empleado_solo_toca_los_propios(self):
		otro = empleado_completo("22222222-2", "otro@x.cl")
		main.guardar_empleado(self.connection, otro)
		main.asignar_empleado_proyecto_bd(self.connection, otro.rut, self.proyecto.id_proyecto)
		id_ajeno = main.guardar_registro_tiempo(
			self.connection, main.RegistroTiempo(0, date(2026, 1, 5), 3, otro, self.proyecto, "Ajeno")
		)
		with self.assertRaisesRegex(ValueError, "no le pertenece"):
			ejecutar_con_entradas(
				lambda: ui.editar_registro_menu(self.connection, self.cuenta_empleado), [str(id_ajeno)]
			)
		salida = ejecutar_con_entradas(
			lambda: ui.editar_registro_menu(self.connection, self.cuenta_empleado),
			["1", "", "x", "6,5", ""],
		)
		self.assertIn("deben ser un número", salida)
		self.assertIn("actualizado", salida)
		fila = main.listar_registros_tiempo(self.connection, RUT)[0]
		self.assertEqual((fila["horas"], fila["descripcion_tarea"]), (6.5, "Cableado"))
		salida = ejecutar_con_entradas(
			lambda: ui.eliminar_registro_menu(self.connection, self.admin), [str(id_ajeno), "s"]
		)
		self.assertIn("eliminado", salida)
		self.assertEqual(self._contar("registros_tiempo"), 1)

	def test_submenu_vuelve_con_cero_y_rechaza_opciones_invalidas(self):
		llamadas = []
		salida = ejecutar_con_entradas(
			lambda: ui.ejecutar_submenu("PRUEBA", [("1", "Accion", lambda: llamadas.append(1))]),
			["9", "1"],
		)
		self.assertIn("Opcion no valida", salida)
		self.assertEqual(llamadas, [1])
		ejecutar_con_entradas(
			lambda: ui.ejecutar_submenu("PRUEBA", [("1", "Accion", lambda: llamadas.append(2))]),
			["0"],
		)
		self.assertEqual(llamadas, [1])

	def test_menu_principal_agrupa_crud_por_entidad(self):
		gestion = [texto for _n, texto, _a in ui.construir_opciones_menu(self.connection, self.admin)]
		self.assertEqual(gestion[:6], [
			"Gestionar departamentos", "Listar o buscar departamentos", "Gestionar empleados",
			"Listar o buscar empleados", "Gestionar proyectos", "Listar proyectos",
		])
		empleado = ui.construir_opciones_menu(self.connection, self.cuenta_empleado)
		numeros = [numero for numero, _t, _a in empleado]
		self.assertEqual(numeros, ["2", "4", "6", "7", "8", "9", "10", "11", "12"])
		self.assertIn(("9", "Editar o eliminar mis registros"), [(n, t) for n, t, _a in empleado])


class PruebasInformes(unittest.TestCase):
	"""Informe genérico, exportadores y escritura a archivo."""

	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		self.carpeta = Path(tempfile.mkdtemp()) / "informes"
		self.admin = main.Usuario(1, "admin", "x", rol="admin")

	def tearDown(self):
		self.connection.close()
		shutil.rmtree(self.carpeta.parent, ignore_errors=True)

	def test_informe_valida_su_estructura_y_es_inmutable(self):
		informe = main.Informe("Informe: horas / 2026", ["a", "b"], [(1, None)])
		self.assertEqual((informe.columnas, informe.filas), (("a", "b"), ((1, None),)))
		self.assertEqual(informe.nombre_archivo, "informe_horas_2026")
		with self.assertRaises(AttributeError):
			informe.titulo = "otro"
		for titulo, columnas, filas in [(" ", ["a"], []), ("T", [], []), ("T", ["a"], [(1, 2)])]:
			with self.subTest(titulo=titulo, columnas=columnas), self.assertRaises(ValueError):
				main.Informe(titulo, columnas, filas)

	def test_exportador_pdf_alinea_columnas_y_omite_none(self):
		informe = main.Informe("Prueba", ["nombre", "ciudad"], [("Paneles", None), ("Eolico", "Temuco")])
		lineas = main.ExportadorPDF().exportar(informe).splitlines()
		self.assertEqual(lineas[:2], ["Prueba", "======"])
		self.assertEqual(lineas[2], "nombre  | ciudad")
		self.assertEqual(lineas[3], "--------+-------")
		self.assertEqual(lineas[4], "Paneles |")
		self.assertEqual(lineas[5], "Eolico  | Temuco")

	def test_exportador_excel_escapa_comas_y_comillas(self):
		informe = main.Informe("Prueba", ["nombre", "nota"], [("Uno, dos", 'Dijo "hola"'), ("Tres", None)])
		lineas = main.ExportadorExcel().exportar(informe).splitlines()
		self.assertEqual(lineas, ["nombre,nota", '"Uno, dos","Dijo ""hola"""', "Tres,"])

	def test_guardar_crea_la_carpeta_y_usa_la_extension_del_exportador(self):
		informe = main.Informe("Informe de proyectos", ["id", "nombre"], [(1, "Paneles")])
		ruta_csv = main.ServicioReportes(main.ExportadorExcel()).guardar(informe, self.carpeta)
		ruta_txt = main.ServicioReportes(main.ExportadorPDF()).guardar(informe, self.carpeta)
		self.assertEqual((ruta_csv.suffix, ruta_txt.suffix), (".csv", ".txt"))
		self.assertTrue(ruta_csv.name.startswith("informe_de_proyectos_"))
		self.assertEqual(ruta_csv.read_bytes()[:3], b"\xef\xbb\xbf")  # BOM para Excel
		self.assertEqual(ruta_csv.read_text(encoding="utf-8-sig"), "id,nombre\n1,Paneles\n")
		self.assertIn("1  | Paneles", ruta_txt.read_text(encoding="utf-8"))

	def test_informe_de_empleados_excluye_los_datos_cifrados(self):
		main.guardar_empleado(self.connection, empleado_completo())
		informe = main.construir_informe_empleados(main.listar_empleados(self.connection))
		self.assertNotIn("salario", informe.columnas)
		texto = main.ExportadorExcel().exportar(informe)
		for dato in ("Av. Siempre Viva", "+56 9 1234 5678", "1200000", "1,200,000"):
			self.assertNotIn(dato, texto)
		self.assertIn("ana@x.cl,Dev", texto)

	def test_menu_genera_y_guarda_informes_por_entidad(self):
		main.guardar_departamento(self.connection, "Ventas")
		cuenta = main.Usuario(2, "e", "x", empleado=empleado_completo(), rol="empleado")
		ui.CARPETA_INFORMES = self.carpeta
		# Un empleado sin horas no pasa por el submenú y no genera archivo.
		salida = ejecutar_con_entradas(lambda: ui.mostrar_reportes_menu(self.connection, cuenta))
		self.assertIn("No hay datos", salida)
		self.assertFalse(self.carpeta.exists())
		# Gestión elige la entidad y el formato; una opción de formato inválida se repite.
		salida = ejecutar_con_entradas(
			lambda: ui.mostrar_reportes_menu(self.connection, self.admin), ["3", "9", "1"]
		)
		self.assertIn("Opcion no valida", salida)
		self.assertIn("Informe de departamentos", salida)
		self.assertIn("Informe guardado en:", salida)
		archivos = list(self.carpeta.glob("informe_de_departamentos_*.txt"))
		self.assertEqual(len(archivos), 1)
		self.assertIn("Ventas", archivos[0].read_text(encoding="utf-8"))


class PruebasPoliticaContrasenas(unittest.TestCase):
	"""Política de contraseñas aplicada al persistir y al registrar desde el menú."""

	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)

	def tearDown(self):
		self.connection.close()

	def test_validar_contrasena_exige_largo_letras_y_digitos(self):
		self.assertEqual(main.validar_contrasena("  Clave1234 "), "Clave1234")
		for invalida in ["", "corta1", "soloLetras", "12345678", "        "]:
			with self.subTest(invalida=invalida), self.assertRaises(ValueError):
				main.validar_contrasena(invalida)

	def test_persistir_y_actualizar_pasan_por_la_politica(self):
		with self.assertRaisesRegex(ValueError, "8 caracteres"):
			main.guardar_usuario(self.connection, main.Usuario(0, "u", "corta1", rol="admin"))
		self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0], 0)
		usuario = main.Usuario(0, "u", "Clave1234", rol="admin")
		with self.assertRaisesRegex(ValueError, "letras y números"):
			usuario.actualizar_contrasena("solo-letras")
		usuario.actualizar_contrasena("Nueva5678")
		self.assertTrue(main.verificar_contrasena("Nueva5678", main.generar_hash_contrasena("Nueva5678")))

	def test_menu_repite_la_contrasena_hasta_cumplir_la_politica(self):
		intentos = iter(["corta1", "sinnumeros", "Clave1234"])
		ui.leer_contrasena = lambda mensaje: next(intentos)
		salida = ejecutar_con_entradas(
			lambda: ui.registrar_usuario_menu(self.connection, rol_forzado="empleado"),
			["Ana", "Perez", "Soto", RUT, "ana@x.cl", "Dev", "Av. Uno 1", "+56 9 1234 5678",
			 "2025-03-01", "1200000"],
		)
		self.assertIn("8 caracteres", salida)
		self.assertIn("letras y números", salida)
		self.assertIn("registrado correctamente", salida)

	def test_el_codigo_secreto_no_esta_sujeto_a_la_politica(self):
		os.environ["ECOTECH_CODIGO_ADMIN"] = "1234"
		ui.leer_contrasena = lambda mensaje: "1234" if "Codigo" in mensaje else "Clave1234"
		salida = ejecutar_con_entradas(
			lambda: ui.registrar_usuario_menu(self.connection, rol_forzado="admin"),
			["Logan", "Silva", "Jara", RUT, "logan@x.cl", "Admin", "Av. Uno 1",
			 "+56 9 1234 5678", "2025-03-01", "1200000"],
		)
		self.assertIn("lsilva", salida)


class PruebasBusquedas(unittest.TestCase):
	"""Búsqueda parcial de departamentos y empleados desde el núcleo y el menú."""

	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		for nombre in ("Ventas", "Investigacion y Desarrollo", "Desarrollo Sostenible", "100% Verde"):
			main.guardar_departamento(self.connection, nombre)
		main.guardar_empleado(self.connection, empleado_completo())
		main.guardar_empleado(self.connection, empleado_completo("22222222-2", "beto@x.cl"))
		self.connection.execute("UPDATE empleados SET nombre = 'Beto', apellido = 'Rojas' WHERE rut = '22222222-2'")
		self.connection.commit()
		self.admin = main.Usuario(1, "admin", "x", rol="admin")

	def tearDown(self):
		self.connection.close()

	def test_departamentos_por_nombre_parcial_sin_distinguir_mayusculas(self):
		nombres = [d["nombre"] for d in main.listar_departamentos(self.connection, "desarrollo")]
		self.assertEqual(nombres, ["Desarrollo Sostenible", "Investigacion y Desarrollo"])
		self.assertEqual(len(main.listar_departamentos(self.connection, "")), 4)
		self.assertEqual(main.listar_departamentos(self.connection, "zzz"), [])

	def test_los_comodines_de_like_se_tratan_como_texto(self):
		self.assertEqual(main.patron_busqueda("a%b_c"), "%a\\%b\\_c%")
		self.assertEqual([d["nombre"] for d in main.listar_departamentos(self.connection, "%")], ["100% Verde"])
		self.assertEqual(main.listar_departamentos(self.connection, "_"), [])

	def test_empleados_por_rut_nombre_o_apellido(self):
		self.assertEqual([e["rut"] for e in main.listar_empleados(self.connection, "2222")], ["22222222-2"])
		self.assertEqual([e["nombre"] for e in main.listar_empleados(self.connection, "ana")], ["Ana"])
		self.assertEqual([e["apellido"] for e in main.listar_empleados(self.connection, "roj")], ["Rojas"])
		self.assertEqual(len(main.listar_empleados(self.connection)), 2)

	def test_menu_lista_todo_con_enter_y_busca_con_texto(self):
		salida = ejecutar_con_entradas(lambda: ui.listar_departamentos_menu(self.connection), [""])
		self.assertIn("Ventas", salida)
		self.assertIn("100% Verde", salida)
		salida = ejecutar_con_entradas(lambda: ui.listar_departamentos_menu(self.connection), ["ventas"])
		self.assertIn("Ventas", salida)
		self.assertNotIn("Verde", salida)
		salida = ejecutar_con_entradas(lambda: ui.listar_departamentos_menu(self.connection), ["nada"])
		self.assertIn("No hay departamentos que coincidan con 'nada'", salida)
		salida = ejecutar_con_entradas(lambda: ui.listar_empleados_menu(self.connection, self.admin), ["beto"])
		self.assertIn("Beto Rojas", salida)
		self.assertNotIn("Ana", salida)


class PruebasEnmascaradoRut(unittest.TestCase):
	"""El cuerpo del RUT se oculta a quien no tiene permisos de gestión."""

	def setUp(self):
		self.connection = main.conectar_bd(":memory:")
		main.inicializar_bd(self.connection)
		self.empleado = empleado_completo()
		main.guardar_empleado(self.connection, self.empleado)
		self.otro = empleado_completo("9876543-3", "beto@x.cl")
		main.guardar_empleado(self.connection, self.otro)
		self.admin = main.Usuario(1, "admin", "Clave1234", rol="admin")
		self.cuenta = main.Usuario(2, "aperez", "Clave1234", empleado=self.empleado, rol="empleado")

	def tearDown(self):
		self.connection.close()

	def test_enmascara_el_cuerpo_y_conserva_el_verificador(self):
		self.assertEqual(main.enmascarar_rut("12345678-5"), "****5678-5")
		self.assertEqual(main.enmascarar_rut("9876543-3"), "***6543-3")
		# El verificador queda a la vista porque se recalcula desde el cuerpo.
		self.assertTrue(main.enmascarar_rut("11111111-1").endswith("-1"))
		# Un cuerpo más corto que los dígitos visibles se devuelve sin cambios.
		self.assertEqual(main.enmascarar_rut("123-6"), "123-6")

	def test_un_empleado_ve_su_rut_completo_y_los_demas_enmascarados(self):
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, self.cuenta), [""]
		)
		self.assertIn(RUT, salida)                 # el propio, completo
		self.assertIn("***6543-3", salida)         # el ajeno, enmascarado
		self.assertNotIn("9876543-3", salida)
		self.assertNotIn("Salario", salida)        # sigue sin ver datos personales

	def test_gestion_ve_los_rut_completos(self):
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, self.admin), [""]
		)
		self.assertIn(RUT, salida)
		self.assertIn("9876543-3", salida)
		self.assertNotIn("*", salida)

	def test_un_empleado_no_puede_confirmar_un_rut_buscandolo(self):
		# Enmascarar no serviria si el RUT se pudiera verificar con una busqueda.
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, self.cuenta), ["9876543"]
		)
		self.assertIn("No hay empleados que coincidan", salida)
		# Por nombre si encuentra, y lo muestra enmascarado.
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, self.cuenta), ["perez"]
		)
		self.assertIn("***6543-3", salida)
		self.assertIn("beto@x.cl", salida)

	def test_gestion_conserva_la_busqueda_por_rut(self):
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, self.admin), ["9876543"]
		)
		self.assertIn("9876543-3", salida)
		self.assertNotIn(RUT, salida)

	def test_una_cuenta_sin_ficha_no_ve_ningun_rut_completo(self):
		sin_ficha = main.Usuario(3, "sinficha", "Clave1234", rol="empleado")
		salida = ejecutar_con_entradas(
			lambda: ui.listar_empleados_menu(self.connection, sin_ficha), [""]
		)
		for rut in (RUT, "9876543-3"):
			self.assertNotIn(rut, salida)


if __name__ == "__main__":
	unittest.main()
