"""Interfaz de consola para EcoTechSolutions."""

from datetime import date
import sqlite3

from main import (
	CODIGO_ADMIN,
	DATABASE_PATH,
	ROLES_VALIDOS,
	Empleado,
	ExportadorExcel,
	ExportadorPDF,
	Proyecto,
	RegistroTiempo,
	ServicioReportes,
	Usuario,
	asignar_empleado_proyecto_bd,
	conectar_bd,
	guardar_departamento,
	guardar_empleado,
	guardar_proyecto,
	guardar_registro_tiempo,
	guardar_usuario,
	inicializar_bd,
	listar_departamentos,
	listar_empleados,
	listar_proyectos,
	listar_registros_tiempo,
	listar_usuarios,
	validar_horas,
	validar_rut,
	validar_texto,
	verificar_contrasena,
)


def leer_entero(mensaje: str, permitir_vacio: bool = False) -> int | None:
	"""Solicita un numero entero y repite hasta recibir un valor valido."""

	while True:
		valor = input(mensaje).strip()
		if permitir_vacio and not valor:
			return None
		try:
			return int(valor)
		except ValueError:
			print("Ingrese un numero entero valido.")


def leer_fecha(mensaje: str, permitir_vacio: bool = False) -> date | None:
	"""Solicita una fecha con formato YYYY-MM-DD."""

	while True:
		valor = input(mensaje).strip()
		if permitir_vacio and not valor:
			return None
		try:
			return date.fromisoformat(valor)
		except ValueError:
			print("Ingrese una fecha valida con formato YYYY-MM-DD.")


def leer_horas() -> float:
	"""Solicita una cantidad de horas valida."""

	while True:
		try:
			return validar_horas(float(input("Horas trabajadas: ").strip()))
		except ValueError as error:
			print(error)


def registrar_usuario_menu(connection: sqlite3.Connection) -> None:
	"""Registra un usuario y solicita el codigo adicional para ser admin."""

	nombre_usuario = validar_texto(input("Nombre de usuario: "), "El nombre de usuario")
	contrasena = validar_texto(input("Contrasena: "), "La contraseña")
	rol = input("Rol (admin/empleado): ").strip().lower()
	if rol not in ROLES_VALIDOS:
		raise ValueError("El rol debe ser admin o empleado.")
	if rol == "admin" and input("Codigo secreto de administrador: ").strip() != CODIGO_ADMIN:
		raise ValueError("Codigo secreto incorrecto.")

	mostrar_empleados(connection)
	rut_empleado = input("RUT del empleado (Enter si no corresponde): ").strip()
	empleado = None
	if rut_empleado:
		rut_empleado = validar_rut(rut_empleado)
		empleado_row = connection.execute(
			"SELECT rut, nombre, apellido, correo, cargo "
			"FROM empleados WHERE rut = ?",
			(rut_empleado,),
		).fetchone()
		if not empleado_row:
			raise ValueError("El empleado indicado no existe.")
		empleado = Empleado(*empleado_row)

	usuario = Usuario(0, nombre_usuario, contrasena, empleado=empleado, rol=rol)
	guardar_usuario(connection, usuario)
	print("Usuario registrado correctamente.")


def autenticar_usuario(connection: sqlite3.Connection) -> Usuario | None:
	"""Solicita credenciales y devuelve el usuario autenticado."""

	nombre_usuario = input("Usuario: ").strip()
	contrasena = input("Contrasena: ").strip()
	fila = connection.execute(
		"SELECT id_usuario, nombre_usuario, contrasena, activo, rut_empleado, rol "
		"FROM usuarios WHERE nombre_usuario = ?",
		(nombre_usuario,),
	).fetchone()
	if not fila or not fila["activo"] or not verificar_contrasena(
		contrasena, fila["contrasena"]
	):
		print("Usuario, contraseña o estado de cuenta no válidos.")
		return None

	usuario = Usuario(
		fila["id_usuario"],
		fila["nombre_usuario"],
		"********",
		bool(fila["activo"]),
		rol=fila["rol"] or "empleado",
	)
	return usuario


def iniciar_sesion(connection: sqlite3.Connection) -> Usuario | None:
	"""Muestra el acceso inicial antes de abrir el sistema."""

	while True:
		cantidad_usuarios = connection.execute(
			"SELECT COUNT(*) FROM usuarios"
		).fetchone()[0]
		print("\n=== ACCESO ECOTECH SOLUTIONS ===")
		if not cantidad_usuarios:
			print("No existen usuarios. Debe registrar el primer usuario.")
			try:
				registrar_usuario_menu(connection)
			except (ValueError, sqlite3.IntegrityError) as error:
				print(f"No se pudo registrar: {error}")
				continue
			continue
		print("1. Iniciar sesion")
		print("2. Registrar usuario")
		print("0. Salir")
		opcion = input("Seleccione una opcion: ").strip()
		try:
			if opcion == "1":
				usuario = autenticar_usuario(connection)
				if usuario:
					return usuario
			elif opcion == "2":
				registrar_usuario_menu(connection)
			elif opcion == "0":
				return None
			else:
				print("Opcion no valida.")
		except ValueError as error:
			print(f"No se pudo completar el acceso: {error}")
		except sqlite3.Error as error:
			print(f"No se pudo completar el acceso: {error}")


def mostrar_departamentos(connection: sqlite3.Connection) -> None:
	"""Muestra los departamentos almacenados."""

	departamentos = listar_departamentos(connection)
	if not departamentos:
		print("No hay departamentos registrados.")
		return
	for departamento in departamentos:
		print(f"{departamento['id_departamento']}: {departamento['nombre']}")


def mostrar_empleados(connection: sqlite3.Connection) -> None:
	"""Muestra los empleados almacenados."""

	empleados = listar_empleados(connection)
	if not empleados:
		print("No hay empleados registrados.")
		return
	for empleado in empleados:
		print(
			f"{empleado['rut']}: {empleado['nombre']} {empleado['apellido']} | "
			f"{empleado['cargo']} | {empleado['correo']} | "
			f"Departamento: {empleado['departamento'] or 'Sin asignar'}"
		)


def mostrar_proyectos(connection: sqlite3.Connection) -> None:
	"""Muestra los proyectos almacenados."""

	proyectos = listar_proyectos(connection)
	if not proyectos:
		print("No hay proyectos registrados.")
		return
	for proyecto in proyectos:
		fin = proyecto["fecha_fin"] or "En curso"
		print(
			f"{proyecto['id_proyecto']}: {proyecto['nombre']} | "
			f"Inicio: {proyecto['fecha_inicio']} | Fin: {fin}"
		)


def mostrar_usuarios(connection: sqlite3.Connection) -> None:
	"""Muestra los usuarios sin exponer sus contrasenas."""

	usuarios = listar_usuarios(connection)
	if not usuarios:
		print("No hay usuarios registrados.")
		return
	for usuario in usuarios:
		estado = "Activo" if usuario["activo"] else "Inactivo"
		print(
			f"{usuario['id_usuario']}: {usuario['nombre_usuario']} | "
			f"Rol: {usuario['rol']} | {estado} | "
			f"Empleado: {usuario['rut_empleado'] or 'Sin asignar'}"
		)


def cambiar_rol_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Permite al administrador cambiar el rol de otro usuario."""

	if usuario_actual.rol != "admin":
		raise PermissionError("Solo un administrador puede cambiar roles.")
	mostrar_usuarios(connection)
	id_usuario = leer_entero("ID del usuario: ")
	if id_usuario == usuario_actual.id_usuario:
		raise ValueError("No puede cambiar su propio rol desde esta opcion.")
	nuevo_rol = validar_texto(input("Nuevo rol (admin/empleado): "), "El rol").lower()
	if nuevo_rol not in ROLES_VALIDOS:
		raise ValueError("El rol debe ser admin o empleado.")
	cursor = connection.execute(
		"UPDATE usuarios SET rol = ? WHERE id_usuario = ?",
		(nuevo_rol, id_usuario),
	)
	connection.commit()
	if cursor.rowcount != 1:
		raise ValueError("El usuario indicado no existe.")
	print("Rol actualizado correctamente.")


def crear_usuario_menu(connection: sqlite3.Connection) -> None:
	"""Crea un usuario desde el menu."""

	mostrar_empleados(connection)
	nombre_usuario = input("Nombre de usuario: ")
	contrasena = input("Contrasena: ")
	rut_empleado = input("RUT del empleado (Enter para dejar sin asignar): ").strip()
	empleado = None
	if rut_empleado:
		rut_empleado = validar_rut(rut_empleado)
		empleado_row = connection.execute(
			"SELECT rut, nombre, apellido, correo, cargo "
			"FROM empleados WHERE rut = ?",
			(rut_empleado,),
		).fetchone()
		if not empleado_row:
			raise ValueError("El empleado indicado no existe.")
		empleado = Empleado(*empleado_row)
	usuario = Usuario(0, nombre_usuario, contrasena, empleado=empleado)
	id_usuario = guardar_usuario(connection, usuario)
	print(f"Usuario creado con ID {id_usuario}.")


def crear_departamento_menu(connection: sqlite3.Connection) -> None:
	"""Crea un departamento desde el menu."""

	id_departamento = guardar_departamento(connection, input("Nombre del departamento: "))
	print(f"Departamento creado con ID {id_departamento}.")


def crear_empleado_menu(connection: sqlite3.Connection) -> None:
	"""Crea un empleado desde el menu."""

	mostrar_departamentos(connection)
	empleado = Empleado(
		input("RUT: "),
		input("Nombre: "),
		input("Apellido: "),
		input("Correo: "),
		input("Cargo: "),
	)
	id_departamento = leer_entero(
		"ID del departamento (Enter para dejar sin asignar): ", True
	)
	guardar_empleado(connection, empleado, id_departamento)
	print("Empleado creado correctamente.")


def crear_proyecto_menu(connection: sqlite3.Connection) -> None:
	"""Crea un proyecto desde el menu."""

	fecha_inicio = leer_fecha("Fecha de inicio (YYYY-MM-DD): ")
	fecha_fin = leer_fecha("Fecha de fin (YYYY-MM-DD, Enter si sigue en curso): ", True)
	proyecto = Proyecto(
		0,
		input("Nombre del proyecto: "),
		input("Descripcion: "),
		fecha_inicio,
		fecha_fin,
	)
	print(f"Proyecto creado con ID {guardar_proyecto(connection, proyecto)}.")


def asignar_proyecto_menu(connection: sqlite3.Connection) -> None:
	"""Asigna un empleado a un proyecto y persiste la relacion."""

	mostrar_empleados(connection)
	rut = validar_rut(input("RUT del empleado: "))
	mostrar_proyectos(connection)
	id_proyecto = leer_entero("ID del proyecto: ")
	asignar_empleado_proyecto_bd(connection, rut, id_proyecto)
	print("Empleado asignado al proyecto.")


def registrar_tiempo_menu(connection: sqlite3.Connection) -> None:
	"""Registra horas trabajadas desde el menu."""

	mostrar_empleados(connection)
	rut = validar_rut(input("RUT del empleado: "))
	mostrar_proyectos(connection)
	id_proyecto = leer_entero("ID del proyecto: ")
	fecha = leer_fecha("Fecha (YYYY-MM-DD): ")
	horas = leer_horas()
	empleado_row = connection.execute(
		"SELECT rut, nombre, apellido, correo, cargo FROM empleados WHERE rut = ?",
		(rut,),
	).fetchone()
	proyecto_row = connection.execute(
		"SELECT id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin "
		"FROM proyectos WHERE id_proyecto = ?",
		(id_proyecto,),
	).fetchone()
	if not empleado_row or not proyecto_row:
		raise ValueError("El empleado o proyecto indicado no existe.")
	empleado = Empleado(*empleado_row)
	proyecto = Proyecto(
		proyecto_row["id_proyecto"],
		proyecto_row["nombre"],
		proyecto_row["descripcion"],
		date.fromisoformat(proyecto_row["fecha_inicio"]),
		date.fromisoformat(proyecto_row["fecha_fin"])
		if proyecto_row["fecha_fin"]
		else None,
	)
	guardar_registro_tiempo(connection, RegistroTiempo(0, fecha, horas, empleado, proyecto))
	print("Registro de tiempo guardado correctamente.")


def mostrar_reportes_menu(connection: sqlite3.Connection) -> None:
	"""Genera el reporte seleccionado con los registros de SQLite."""

	filas = listar_registros_tiempo(connection)
	if not filas:
		print("No hay registros de tiempo para reportar.")
		return
	registros = []
	for fila in filas:
		empleado = Empleado(
			fila["rut_empleado"], fila["empleado"], "Reporte", "reporte@ecotech.cl", "Consulta"
		)
		proyecto = Proyecto(
			fila["id_proyecto"], fila["proyecto"], "Reporte", date.fromisoformat(fila["fecha"])
		)
		registros.append(
			RegistroTiempo(
				fila["id_registro"], date.fromisoformat(fila["fecha"]), fila["horas"], empleado, proyecto
			)
		)
	formato = input("Formato (1=PDF texto, 2=Excel CSV): ").strip()
	exportador = ExportadorPDF() if formato == "1" else ExportadorExcel()
	print("\n" + ServicioReportes(exportador).generar(registros))


def crear_usuario_admin_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Crea un usuario verificando los permisos administrativos."""

	if usuario_actual.rol != "admin":
		raise PermissionError("Solo un administrador puede crear usuarios desde el menu.")
	crear_usuario_menu(connection)


def listar_usuarios_admin_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Lista usuarios verificando los permisos administrativos."""

	if usuario_actual.rol != "admin":
		raise PermissionError("Solo un administrador puede listar usuarios.")
	mostrar_usuarios(connection)


def mostrar_registros_tiempo_menu(connection: sqlite3.Connection) -> None:
	"""Muestra los registros de tiempo almacenados."""

	for registro in listar_registros_tiempo(connection):
		print(dict(registro))


def ejecutar_opcion_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario, opcion: str
) -> bool:
	"""Ejecuta una opcion del menu y devuelve si debe continuar."""

	acciones = {
		"1": lambda: crear_departamento_menu(connection),
		"2": lambda: mostrar_departamentos(connection),
		"3": lambda: crear_empleado_menu(connection),
		"4": lambda: mostrar_empleados(connection),
		"5": lambda: crear_proyecto_menu(connection),
		"6": lambda: mostrar_proyectos(connection),
		"7": lambda: asignar_proyecto_menu(connection),
		"8": lambda: registrar_tiempo_menu(connection),
		"9": lambda: mostrar_registros_tiempo_menu(connection),
		"10": lambda: mostrar_reportes_menu(connection),
		"11": lambda: crear_usuario_admin_menu(connection, usuario_actual),
		"12": lambda: listar_usuarios_admin_menu(connection, usuario_actual),
		"13": lambda: cambiar_rol_menu(connection, usuario_actual),
	}
	if opcion == "0":
		print("Sesion finalizada.")
		return False
	accion = acciones.get(opcion)
	if accion is None:
		print("Opcion no valida.")
		return True
	accion()
	return True


def mostrar_opciones_menu() -> None:
	"""Muestra las opciones disponibles del sistema."""

	print(
		"\n=== ECOTECH SOLUTIONS ===\n"
		"1. Crear departamento\n"
		"2. Listar departamentos\n"
		"3. Crear empleado\n"
		"4. Listar empleados\n"
		"5. Crear proyecto\n"
		"6. Listar proyectos\n"
		"7. Asignar empleado a proyecto\n"
		"8. Registrar horas trabajadas\n"
		"9. Ver registros de tiempo\n"
		"10. Generar reporte\n"
		"11. Crear usuario\n"
		"12. Listar usuarios\n"
		"13. Cambiar rol de usuario (solo admin)\n"
		"0. Salir"
	)


def mostrar_menu() -> None:
	"""Ejecuta el menu principal conectado a la base de datos local."""

	try:
		connection = conectar_bd()
		inicializar_bd(connection)
	except sqlite3.Error as error:
		print(f"No se pudo iniciar la base de datos: {error}")
		return
	try:
		usuario_actual = iniciar_sesion(connection)
		if usuario_actual is None:
			print("Sesion finalizada.")
			return
		print(
			f"\nSesion iniciada: {usuario_actual.nombre_usuario} "
			f"(rol: {usuario_actual.rol})"
		)
		print(f"Base de datos conectada: {DATABASE_PATH.name}")
		while True:
			mostrar_opciones_menu()
			opcion = input("Seleccione una opcion: ").strip()
			try:
				if not ejecutar_opcion_menu(connection, usuario_actual, opcion):
					break
			except ValueError as error:
				print(f"No se pudo completar la operacion: {error}")
			except PermissionError as error:
				print(f"No se pudo completar la operacion: {error}")
			except sqlite3.Error as error:
				print(f"No se pudo completar la operacion: {error}")
	except (EOFError, KeyboardInterrupt):
		print("\nSesion finalizada por el usuario.")
	finally:
		connection.close()


if __name__ == "__main__":
	mostrar_menu()