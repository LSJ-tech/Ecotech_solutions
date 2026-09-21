"""Interfaz de consola para EcoTechSolutions."""

from datetime import date
from getpass import getpass
from typing import Callable
import logging
import sqlite3
import sys

if sys.platform == "win32":
	import msvcrt

from main import (
	CAMPO_NOMBRE_DEPARTAMENTO,
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
	asignar_empleado_departamento_bd,
	asignar_gerente_departamento,
	calcular_pago,
	calcular_tarifa_hora,
	conectar_bd,
	fila_a_empleado,
	guardar_departamento,
	guardar_proyecto,
	guardar_registro_tiempo,
	guardar_usuario,
	guardar_usuario_con_empleado,
	eliminar_usuario,
	inicializar_bd,
	listar_departamentos,
	listar_empleados,
	listar_proyectos,
	listar_registros_tiempo,
	listar_usuarios,
	sumar_horas_empleado,
	validar_descripcion_tarea,
	validar_horas,
	validar_monto,
	validar_rut,
	validar_telefono,
	validar_texto,
	verificar_codigo_rol,
	verificar_contrasena,
)
from servicios_externos import (
	INDICADORES_PERMITIDOS,
	ErrorServicioExterno,
	ResultadoConsulta,
	ServicioClima,
	ServicioIndicadores,
	consultar_con_respaldo,
	validar_ciudad,
	validar_indicador,
)

MENSAJE_CONTRASENA = "Contrasena: "
MENSAJE_EMPLEADO_INEXISTENTE = "El empleado indicado no existe."
MENSAJE_OPCION_INVALIDA = "Opcion no valida."
MENSAJE_SELECCION = "Seleccione una opcion: "
MENSAJE_ID_PROYECTO = "ID del proyecto: "
ROLES_GESTION = {"admin", "rrhh"}
CONSULTA_EMPLEADO = "SELECT * FROM empleados WHERE rut = ?"


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


def leer_texto(mensaje: str, campo: str) -> str:
	"""Solicita texto obligatorio y repite solo el campo incorrecto."""

	while True:
		try:
			return validar_texto(input(mensaje), campo)
		except ValueError as error:
			print(error)


def leer_nombre(mensaje: str, campo: str) -> str:
	"""Solicita un nombre compuesto solo por letras y espacios."""

	while True:
		valor = leer_texto(mensaje, campo)
		if all(caracter.isalpha() or caracter.isspace() for caracter in valor):
			return valor
		print(f"{campo} solo puede contener letras y espacios.")


def leer_rut(mensaje: str = "RUT (ejemplo: 19616711-0): ") -> str:
	"""Solicita un RUT y lo valida antes de continuar."""

	while True:
		try:
			return validar_rut(input(mensaje))
		except ValueError as error:
			print(error)


def leer_rut_opcional(
	mensaje: str = "RUT del empleado (Enter para dejar sin asignar): "
) -> str | None:
	"""Solicita un RUT opcional y repite solo si su formato es inválido."""

	while True:
		valor = input(mensaje).strip()
		if not valor:
			return None
		try:
			return validar_rut(valor)
		except ValueError as error:
			print(error)


def leer_contrasena_validada(mensaje: str = MENSAJE_CONTRASENA) -> str:
	"""Solicita una contraseña no vacía y conserva el resto del formulario."""

	while True:
		try:
			return validar_texto(leer_contrasena(mensaje), "La contraseña")
		except ValueError as error:
			print(error)


def leer_contrasena(mensaje: str) -> str:
	"""Lee una contraseña mostrando un asterisco por cada carácter."""

	if sys.platform != "win32":
		return getpass(mensaje)
	print(mensaje, end="", flush=True)
	caracteres = []
	while True:
		caracter = msvcrt.getwch()
		if caracter in ("\r", "\n"):
			print()
			return "".join(caracteres)
		if caracter == "\003":
			raise KeyboardInterrupt
		if caracter == "\b":
			if caracteres:
				caracteres.pop()
				print("\b \b", end="", flush=True)
			continue
		if caracter >= " ":
			caracteres.append(caracter)
			print("*", end="", flush=True)


def normalizar_rol(valor: str) -> str:
	"""Normaliza el nombre del rol RR.HH. para guardarlo como rrhh."""

	return valor.strip().lower().replace(".", "").replace(":", "")


def leer_telefono() -> str:
	"""Solicita un teléfono y repite solo ese campo si el formato es inválido."""

	while True:
		try:
			return validar_telefono(input("Telefono (ejemplo: +56 9 1234 5678): "))
		except ValueError as error:
			print(error)


def leer_rol() -> str:
	"""Solicita un rol válido y explica las opciones permitidas."""

	while True:
		rol = normalizar_rol(input("Rol (admin/empleado/rrhh): "))
		if rol in ROLES_VALIDOS:
			return rol
		print("El rol debe ser admin, empleado o rrhh.")


def leer_correo() -> str:
	"""Solicita un correo con un formato básico válido."""

	while True:
		correo = leer_texto("Correo: ", "El correo")
		if "@" in correo:
			return correo
		print("El correo debe tener un formato válido, por ejemplo nombre@dominio.cl.")


def generar_nombre_usuario(
	connection: sqlite3.Connection,
	nombre: str,
	primer_apellido: str,
	segundo_apellido: str,
) -> str:
	"""Genera un usuario con la inicial del nombre y un apellido."""

	nombre = validar_texto(nombre, "El nombre").lower()
	primer_apellido = validar_texto(primer_apellido, "El primer apellido").lower()
	segundo_apellido = validar_texto(segundo_apellido, "El segundo apellido").lower()
	usuarios = {
		fila[0]
		for fila in connection.execute("SELECT nombre_usuario FROM usuarios")
	}
	base = f"{nombre[0]}{primer_apellido}"
	if base not in usuarios:
		return base
	segundo_usuario = f"{nombre[0]}{segundo_apellido}"
	if segundo_usuario not in usuarios:
		return segundo_usuario
	raise ValueError("Ya existen usuarios con ambos apellidos. Use otro nombre o apellido.")


def verificar_gestion(usuario_actual: Usuario, accion: str) -> None:
	"""Lanza PermissionError si el rol actual no puede ejecutar la acción."""

	if usuario_actual.rol not in ROLES_GESTION:
		raise PermissionError(f"Solo admin o rrhh pueden {accion}.")


def obtener_rut_propio(usuario_actual: Usuario) -> str:
	"""Devuelve el RUT del empleado vinculado al usuario o falla si no existe."""

	if usuario_actual.empleado is None:
		raise ValueError("Su cuenta no está asociada a un empleado.")
	return usuario_actual.empleado.rut


def obtener_filtro_rut(usuario_actual: Usuario) -> str | None:
	"""Devuelve None para roles de gestión y el RUT propio para empleados."""

	if usuario_actual.rol in ROLES_GESTION:
		return None
	return obtener_rut_propio(usuario_actual)


def leer_descripcion_tarea() -> str:
	"""Solicita la breve descripción de las tareas realizadas."""

	while True:
		try:
			return validar_descripcion_tarea(input("Descripcion breve de las tareas: "))
		except ValueError as error:
			print(error)


def leer_horas() -> float:
	"""Solicita una cantidad de horas valida."""

	while True:
		try:
			return validar_horas(float(input("Horas trabajadas: ").strip()))
		except ValueError as error:
			print(error)


def leer_ciudad_opcional(
	mensaje: str = "Ciudad del proyecto (Enter si no aplica): ",
) -> str | None:
	"""Solicita una ciudad opcional y repite solo si el formato es inválido."""

	while True:
		valor = input(mensaje).strip()
		if not valor:
			return None
		try:
			return validar_ciudad(valor)
		except ValueError as error:
			print(error)


def avisar_respaldo(resultado: ResultadoConsulta) -> None:
	"""Informa cuando el dato proviene del respaldo local y no del servicio."""

	if resultado.desde_respaldo:
		print(
			f"Aviso: {resultado.motivo} Se muestra el último dato guardado "
			f"(consultado {resultado.dato.fecha_consulta:%Y-%m-%d %H:%M})."
		)


def consultar_clima_menu(connection: sqlite3.Connection) -> None:
	"""Consulta el clima actual de la ciudad de un proyecto."""

	mostrar_proyectos(connection)
	id_proyecto = leer_entero(MENSAJE_ID_PROYECTO)
	fila = connection.execute(
		"SELECT nombre, ciudad FROM proyectos WHERE id_proyecto = ?", (id_proyecto,)
	).fetchone()
	if fila is None:
		raise ValueError("El proyecto indicado no existe.")
	if not fila["ciudad"]:
		raise ValueError("El proyecto no tiene una ciudad asignada.")
	resultado = consultar_con_respaldo(connection, ServicioClima(), fila["ciudad"])
	avisar_respaldo(resultado)
	clima = resultado.dato
	print(
		f"Clima en {clima.ciudad} para el proyecto {fila['nombre']}: "
		f"{clima.temperatura:.1f} °C, humedad {clima.humedad}%, {clima.descripcion} "
		f"(consultado {clima.fecha_consulta:%Y-%m-%d %H:%M})"
	)


def leer_indicador() -> str:
	"""Solicita un indicador de la lista blanca y repite hasta recibir uno válido."""

	opciones = ", ".join(
		f"{codigo} ({moneda})" for codigo, moneda in sorted(INDICADORES_PERMITIDOS.items())
	)
	while True:
		try:
			return validar_indicador(input(f"Indicador [{opciones}]: "))
		except ValueError as error:
			print(error)


def leer_monto(mensaje: str, campo: str) -> float:
	"""Solicita un monto positivo y repite solo ese campo ante un valor inválido."""

	while True:
		valor = input(mensaje).strip().replace(",", ".")
		try:
			return validar_monto(float(valor), campo)
		except ValueError:
			print(f"{campo} debe ser un número mayor que 0.")


def obtener_indicador(connection: sqlite3.Connection) -> ResultadoConsulta:
	"""Solicita un indicador y lo consulta con respaldo local."""

	return consultar_con_respaldo(connection, ServicioIndicadores(), leer_indicador())


def consultar_indicador_menu(connection: sqlite3.Connection) -> None:
	"""Muestra el valor vigente de un indicador económico."""

	resultado = obtener_indicador(connection)
	avisar_respaldo(resultado)
	indicador = resultado.dato
	print(
		f"{indicador.nombre}: ${indicador.valor:,.2f} CLP por {indicador.moneda} "
		f"(valor del {indicador.fecha:%Y-%m-%d}, consultado "
		f"{indicador.fecha_consulta:%Y-%m-%d %H:%M})"
	)


def calcular_pago_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Calcula el pago de un empleado en moneda extranjera según sus horas registradas."""

	verificar_gestion(usuario_actual, "calcular pagos")
	mostrar_empleados(connection, detallado=True)
	rut = leer_rut()
	fila = connection.execute(CONSULTA_EMPLEADO, (rut,)).fetchone()
	if fila is None:
		raise ValueError(MENSAJE_EMPLEADO_INEXISTENTE)
	empleado = fila_a_empleado(fila)
	if empleado.salario is None:
		raise ValueError("El empleado no tiene salario registrado para calcular un pago.")
	horas = sumar_horas_empleado(connection, rut)
	if horas <= 0:
		raise ValueError("El empleado no tiene horas registradas para calcular un pago.")
	tarifa = calcular_tarifa_hora(empleado.salario)
	resultado = obtener_indicador(connection)
	avisar_respaldo(resultado)
	indicador = resultado.dato
	pago = calcular_pago(rut, horas, tarifa, indicador.moneda, indicador.valor)
	print(
		f"Horas registradas: {pago.horas:g} | Salario: ${empleado.salario:,.0f} CLP "
		f"| Valor hora: ${pago.tarifa_hora_clp:,.2f} CLP\n"
		f"Total: ${pago.monto_clp:,.2f} CLP = {pago.monto_moneda:,.2f} {pago.moneda} "
		f"({indicador.nombre} a ${pago.valor_cambio:,.2f} del {indicador.fecha:%Y-%m-%d})"
	)


def registrar_usuario_menu(
	connection: sqlite3.Connection, rol_forzado: str | None = None
) -> None:
	"""Registra un usuario; con rol_forzado no se pregunta el rol (primer administrador)."""

	contrasena = leer_contrasena_validada()
	rol = rol_forzado or leer_rol()
	if rol in ROLES_GESTION:
		while True:
			codigo = leer_contrasena_validada("Codigo secreto: ")
			if verificar_codigo_rol(rol, codigo):
				break
			print("Codigo secreto incorrecto. Intente nuevamente.")

	nombre = leer_nombre("Nombre: ", "El nombre")
	primer_apellido = leer_nombre("Primer apellido: ", "El primer apellido")
	segundo_apellido = leer_nombre("Segundo apellido: ", "El segundo apellido")
	nombre_usuario = generar_nombre_usuario(
		connection, nombre, primer_apellido, segundo_apellido
	)
	empleado = None
	if rol in {"empleado", "rrhh"}:
		rut_empleado = leer_rut()
		empleado = Empleado(
			rut_empleado,
			nombre,
			f"{primer_apellido} {segundo_apellido}",
			leer_correo(),
			leer_texto("Cargo: ", "El cargo"),
			direccion=leer_texto("Direccion: ", "La dirección"),
			telefono=leer_telefono(),
			fecha_inicio_contrato=leer_fecha("Fecha de inicio de contrato (YYYY-MM-DD): "),
			salario=leer_monto("Salario mensual en CLP: ", "El salario"),
		)

	usuario = Usuario(0, nombre_usuario, contrasena, empleado=empleado, rol=rol)
	if empleado:
		guardar_usuario_con_empleado(connection, usuario, empleado)
	else:
		guardar_usuario(connection, usuario)
	print(f"Usuario registrado correctamente. Su usuario es: {nombre_usuario}")


def autenticar_usuario(connection: sqlite3.Connection) -> Usuario | None:
	"""Solicita credenciales y devuelve el usuario autenticado."""

	nombre_usuario = input("Usuario: ").strip()
	contrasena = leer_contrasena(MENSAJE_CONTRASENA).strip()
	if not nombre_usuario or not contrasena:
		print("El usuario y la contraseña no pueden estar vacíos.")
		return None
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
	empleado_row = (
		connection.execute(CONSULTA_EMPLEADO, (fila["rut_empleado"],)).fetchone()
		if fila["rut_empleado"]
		else None
	)
	usuario = Usuario(
		fila["id_usuario"],
		fila["nombre_usuario"],
		"********",
		bool(fila["activo"]),
		empleado=fila_a_empleado(empleado_row) if empleado_row else None,
		rol=fila["rol"] or "empleado",
	)
	return usuario


def registrar_primer_usuario(connection: sqlite3.Connection) -> None:
	"""Registra el administrador inicial y comunica errores de datos o SQLite."""

	print("No existen usuarios. El primer usuario debe ser administrador.")
	try:
		registrar_usuario_menu(connection, rol_forzado="admin")
	except (ValueError, sqlite3.IntegrityError) as error:
		print(f"No se pudo registrar: {error}")


def hay_usuarios(connection: sqlite3.Connection) -> bool:
	"""Indica si ya existe al menos una cuenta en el sistema."""

	return connection.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] > 0


def mostrar_menu_acceso(con_usuarios: bool) -> str:
	"""Muestra las opciones de acceso; el registro solo existe para el primer administrador."""

	print("\n=== ACCESO ECOTECH SOLUTIONS ===")
	print("1. Iniciar sesion")
	if not con_usuarios:
		print("2. Registrar administrador inicial")
	print("0. Salir")
	return input(MENSAJE_SELECCION).strip()


def procesar_opcion_acceso(
	connection: sqlite3.Connection, opcion: str, con_usuarios: bool
) -> Usuario | None:
	"""Procesa una opcion de acceso y devuelve el usuario autenticado."""

	if opcion == "1":
		return autenticar_usuario(connection)
	if opcion == "2" and not con_usuarios:
		registrar_primer_usuario(connection)
		return None
	if opcion == "2":
		# El registro de cuentas es una función de RR.HH. dentro del sistema, no del acceso.
		print("El registro de cuentas lo realiza un administrador o RR.HH. desde el sistema.")
		return None
	print(MENSAJE_OPCION_INVALIDA)
	return None


def iniciar_sesion(connection: sqlite3.Connection) -> Usuario | None:
	"""Muestra el acceso inicial antes de abrir el sistema."""

	while True:
		con_usuarios = hay_usuarios(connection)
		opcion = mostrar_menu_acceso(con_usuarios)
		if opcion == "0":
			return None
		try:
			usuario = procesar_opcion_acceso(connection, opcion, con_usuarios)
			if usuario:
				return usuario
		except (ValueError, sqlite3.Error) as error:
			print(f"No se pudo completar el acceso: {error}")


def mostrar_departamentos(connection: sqlite3.Connection) -> None:
	"""Muestra los departamentos almacenados."""

	departamentos = listar_departamentos(connection)
	if not departamentos:
		print("No hay departamentos registrados.")
		return
	for departamento in departamentos:
		gerente = departamento["gerente"] or "Sin gerente"
		print(f"{departamento['id_departamento']}: {departamento['nombre']} | Gerente: {gerente}")


def mostrar_empleados(connection: sqlite3.Connection, detallado: bool = False) -> None:
	"""Muestra los empleados; los datos personales solo se incluyen si detallado es True."""

	empleados = listar_empleados(connection)
	if not empleados:
		print("No hay empleados registrados.")
		return
	for empleado in empleados:
		linea = (
			f"{empleado['id_empleado']}. {empleado['rut']}: "
			f"{empleado['nombre']} {empleado['apellido']} | {empleado['cargo']} | "
			f"{empleado['correo']} | Departamento: {empleado['departamento'] or 'Sin asignar'}"
		)
		if detallado:
			salario = (
				f"${empleado['salario']:,.0f}" if empleado["salario"] is not None else "Sin registrar"
			)
			linea += (
				f"\n    Direccion: {empleado['direccion'] or 'Sin registrar'} | "
				f"Telefono: {empleado['telefono'] or 'Sin registrar'} | "
				f"Contrato desde: {empleado['fecha_inicio_contrato'] or 'Sin registrar'} | "
				f"Salario: {salario}"
			)
		print(linea)


def mostrar_proyectos(connection: sqlite3.Connection) -> None:
	"""Muestra los proyectos almacenados."""

	proyectos = listar_proyectos(connection)
	if not proyectos:
		print("No hay proyectos registrados.")
		return
	for proyecto in proyectos:
		fin = proyecto["fecha_fin"] or "En curso"
		ciudad = proyecto["ciudad"] or "Sin ciudad"
		print(
			f"{proyecto['id_proyecto']}: {proyecto['nombre']} | "
			f"Inicio: {proyecto['fecha_inicio']} | Fin: {fin} | Ciudad: {ciudad}"
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
	nuevo_rol = normalizar_rol(
		validar_texto(input("Nuevo rol (admin/empleado/rrhh): "), "El rol")
	)
	if nuevo_rol not in ROLES_VALIDOS:
		raise ValueError("El rol debe ser admin, empleado o rrhh.")
	if nuevo_rol == "rrhh":
		rut_empleado = connection.execute(
			"SELECT rut_empleado FROM usuarios WHERE id_usuario = ?",
			(id_usuario,),
		).fetchone()
		if not rut_empleado or not rut_empleado[0]:
			raise ValueError("El rol rrhh debe estar asociado a un empleado.")
	cursor = connection.execute(
		"UPDATE usuarios SET rol = ? WHERE id_usuario = ?",
		(nuevo_rol, id_usuario),
	)
	connection.commit()
	if cursor.rowcount != 1:
		raise ValueError("El usuario indicado no existe.")
	print("Rol actualizado correctamente.")


def crear_departamento_menu(connection: sqlite3.Connection) -> None:
	"""Crea un departamento desde el menu."""

	nombre = leer_texto("Nombre del departamento: ", CAMPO_NOMBRE_DEPARTAMENTO)
	mostrar_empleados(connection)
	rut_gerente = leer_rut_opcional("RUT del gerente (Enter para dejar sin gerente): ")
	id_departamento = guardar_departamento(connection, nombre, rut_gerente)
	print(f"Departamento creado con ID {id_departamento}.")


def asignar_gerente_menu(connection: sqlite3.Connection) -> None:
	"""Asigna o cambia el gerente de un departamento."""

	mostrar_departamentos(connection)
	id_departamento = leer_entero("ID del departamento: ")
	mostrar_empleados(connection)
	rut_gerente = leer_rut_opcional("RUT del gerente (Enter para quitar el gerente): ")
	asignar_gerente_departamento(connection, id_departamento, rut_gerente)
	print("Gerente actualizado correctamente." if rut_gerente else "Departamento sin gerente.")


def actualizar_departamento_empleado_menu(
	connection: sqlite3.Connection, cambiar: bool
) -> None:
	"""Asigna o cambia el departamento de un empleado."""

	mostrar_empleados(connection)
	rut = leer_rut()
	departamento_actual = connection.execute(
		"SELECT id_departamento FROM empleados WHERE rut = ?", (rut,)
	).fetchone()
	if departamento_actual is None:
		raise ValueError(MENSAJE_EMPLEADO_INEXISTENTE)
	if cambiar and departamento_actual[0] is None:
		raise ValueError("El empleado no tiene un departamento para cambiar.")
	if not cambiar and departamento_actual[0] is not None:
		raise ValueError("El empleado ya tiene un departamento asignado.")
	mostrar_departamentos(connection)
	id_departamento = leer_entero("ID del departamento: ")
	asignar_empleado_departamento_bd(connection, rut, id_departamento)
	mensaje = "cambiado" if cambiar else "asignado"
	print(f"Departamento {mensaje} correctamente.")


def gestionar_departamento_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Muestra las opciones para asignar o cambiar departamentos."""

	if usuario_actual.rol not in ROLES_GESTION:
		raise PermissionError("Solo admin o rrhh pueden gestionar departamentos.")
	while True:
		print(
			"\n=== GESTIONAR DEPARTAMENTO DE EMPLEADO ===\n"
			"1. Asignar departamento\n"
			"2. Cambiar departamento\n"
			"0. Volver"
		)
		opcion = input(MENSAJE_SELECCION).strip()
		if opcion == "0":
			return
		if opcion == "1":
			actualizar_departamento_empleado_menu(connection, cambiar=False)
			return
		if opcion == "2":
			actualizar_departamento_empleado_menu(connection, cambiar=True)
			return
		print(MENSAJE_OPCION_INVALIDA)


def gestionar_departamentos_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Muestra las opciones de creación y gestión de departamentos."""

	if usuario_actual.rol not in ROLES_GESTION:
		raise PermissionError("Solo admin o rrhh pueden gestionar departamentos.")
	while True:
		print(
			"\n=== GESTIONAR DEPARTAMENTOS ===\n"
			"1. Crear departamento\n"
			"2. Asignar o cambiar departamento de empleado\n"
			"3. Asignar o cambiar gerente\n"
			"0. Volver"
		)
		opcion = input(MENSAJE_SELECCION).strip()
		if opcion == "0":
			return
		if opcion == "1":
			crear_departamento_menu(connection)
			return
		if opcion == "2":
			gestionar_departamento_menu(connection, usuario_actual)
			return
		if opcion == "3":
			asignar_gerente_menu(connection)
			return
		print(MENSAJE_OPCION_INVALIDA)


def crear_proyecto_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Crea un proyecto desde el menu."""

	verificar_gestion(usuario_actual, "crear proyectos")
	fecha_inicio = leer_fecha("Fecha de inicio (YYYY-MM-DD): ")
	fecha_fin = leer_fecha("Fecha de fin (YYYY-MM-DD, Enter si sigue en curso): ", True)
	proyecto = Proyecto(
		0,
		input("Nombre del proyecto: "),
		input("Descripcion: "),
		fecha_inicio,
		fecha_fin,
		leer_ciudad_opcional(),
	)
	print(f"Proyecto creado con ID {guardar_proyecto(connection, proyecto)}.")


def asignar_proyecto_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Asigna un empleado a un proyecto y persiste la relacion."""

	verificar_gestion(usuario_actual, "asignar empleados a proyectos")
	mostrar_empleados(connection)
	rut = validar_rut(input("RUT del empleado: "))
	mostrar_proyectos(connection)
	id_proyecto = leer_entero(MENSAJE_ID_PROYECTO)
	asignar_empleado_proyecto_bd(connection, rut, id_proyecto)
	print("Empleado asignado al proyecto.")


def registrar_tiempo_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Registra horas trabajadas; los empleados solo pueden registrar las propias."""

	if usuario_actual.rol in ROLES_GESTION:
		mostrar_empleados(connection)
		rut = validar_rut(input("RUT del empleado: "))
	else:
		rut = obtener_rut_propio(usuario_actual)
	mostrar_proyectos(connection)
	id_proyecto = leer_entero(MENSAJE_ID_PROYECTO)
	fecha = leer_fecha("Fecha (YYYY-MM-DD): ")
	horas = leer_horas()
	descripcion_tarea = leer_descripcion_tarea()
	empleado_row = connection.execute(CONSULTA_EMPLEADO, (rut,)).fetchone()
	proyecto_row = connection.execute(
		"SELECT id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin "
		"FROM proyectos WHERE id_proyecto = ?",
		(id_proyecto,),
	).fetchone()
	if not empleado_row or not proyecto_row:
		raise ValueError("El empleado o proyecto indicado no existe.")
	empleado = fila_a_empleado(empleado_row)
	proyecto = Proyecto(
		proyecto_row["id_proyecto"],
		proyecto_row["nombre"],
		proyecto_row["descripcion"],
		date.fromisoformat(proyecto_row["fecha_inicio"]),
		date.fromisoformat(proyecto_row["fecha_fin"])
		if proyecto_row["fecha_fin"]
		else None,
	)
	guardar_registro_tiempo(
		connection, RegistroTiempo(0, fecha, horas, empleado, proyecto, descripcion_tarea)
	)
	print("Registro de tiempo guardado correctamente.")


def mostrar_reportes_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Genera el reporte seleccionado con los registros de SQLite."""

	filas = listar_registros_tiempo(connection, obtener_filtro_rut(usuario_actual))
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
				fila["id_registro"],
				date.fromisoformat(fila["fecha"]),
				fila["horas"],
				empleado,
				proyecto,
				fila["descripcion_tarea"] or "",
			)
		)
	formato = input("Formato (1=PDF texto, 2=Excel CSV): ").strip()
	exportador = ExportadorPDF() if formato == "1" else ExportadorExcel()
	print("\n" + ServicioReportes(exportador).generar(registros))


def crear_usuario_admin_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Crea un usuario verificando los permisos administrativos."""

	if usuario_actual.rol not in ROLES_GESTION:
		raise PermissionError("Solo admin o rrhh pueden crear usuarios desde el menu.")
	registrar_usuario_menu(connection)


def listar_usuarios_admin_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Lista usuarios verificando los permisos administrativos."""

	if usuario_actual.rol not in ROLES_GESTION:
		raise PermissionError("Solo admin o rrhh pueden listar usuarios.")
	mostrar_usuarios(connection)


def eliminar_usuario_admin_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Permite al admin eliminar otro usuario, incluso si es admin."""

	if usuario_actual.rol != "admin":
		raise PermissionError("Solo un administrador puede eliminar usuarios.")
	mostrar_usuarios(connection)
	id_usuario = leer_entero("ID del usuario a eliminar: ")
	if id_usuario == usuario_actual.id_usuario:
		raise ValueError("No puede eliminar su propia cuenta.")
	if not eliminar_usuario(connection, id_usuario):
		raise ValueError("El usuario indicado no existe.")
	print("Usuario eliminado correctamente.")


def mostrar_registros_tiempo_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Muestra los registros de tiempo permitidos para el rol actual."""

	registros = listar_registros_tiempo(connection, obtener_filtro_rut(usuario_actual))
	if not registros:
		print("No hay registros de tiempo.")
		return
	for registro in registros:
		print(
			f"{registro['id_registro']}: {registro['fecha']} | "
			f"{registro['empleado']} ({registro['rut_empleado']}) | "
			f"{registro['proyecto']} | {registro['horas']} horas"
			+ (f" | {registro['descripcion_tarea']}" if registro["descripcion_tarea"] else "")
		)


OpcionMenu = tuple[str, str, Callable[[], None]]


def construir_opciones_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> list[OpcionMenu]:
	"""Devuelve las opciones (numero, descripcion, accion) permitidas para el rol, en orden."""

	gestion = usuario_actual.rol in ROLES_GESTION
	admin = usuario_actual.rol == "admin"

	def etiqueta(general: str, propia: str) -> str:
		return general if gestion else propia

	# Una sola tabla define numero, texto, permiso y accion; asi la numeracion no se desalinea.
	opciones = [
		("1", "Gestionar departamentos", gestion,
			lambda: gestionar_departamentos_menu(connection, usuario_actual)),
		("2", "Listar departamentos", True, lambda: mostrar_departamentos(connection)),
		("3", "Listar empleados", True, lambda: mostrar_empleados(connection, detallado=gestion)),
		("4", "Crear proyecto", gestion, lambda: crear_proyecto_menu(connection, usuario_actual)),
		("5", "Listar proyectos", True, lambda: mostrar_proyectos(connection)),
		("6", "Asignar empleado a proyecto", gestion,
			lambda: asignar_proyecto_menu(connection, usuario_actual)),
		("7", etiqueta("Registrar horas trabajadas", "Registrar mis horas trabajadas"), True,
			lambda: registrar_tiempo_menu(connection, usuario_actual)),
		("8", etiqueta("Ver registros de tiempo", "Ver mis horas registradas"), True,
			lambda: mostrar_registros_tiempo_menu(connection, usuario_actual)),
		("9", etiqueta("Generar reporte", "Generar mi reporte"), True,
			lambda: mostrar_reportes_menu(connection, usuario_actual)),
		("10", "Consultar clima de un proyecto", True, lambda: consultar_clima_menu(connection)),
		("11", "Consultar indicador economico", True,
			lambda: consultar_indicador_menu(connection)),
		("12", "Calcular pago en moneda extranjera", gestion,
			lambda: calcular_pago_menu(connection, usuario_actual)),
		("13", "Crear usuario", gestion, lambda: crear_usuario_admin_menu(connection, usuario_actual)),
		("14", "Listar usuarios", gestion,
			lambda: listar_usuarios_admin_menu(connection, usuario_actual)),
		("15", "Cambiar rol de usuario", admin, lambda: cambiar_rol_menu(connection, usuario_actual)),
		("16", "Eliminar usuario", admin,
			lambda: eliminar_usuario_admin_menu(connection, usuario_actual)),
	]
	return [(numero, texto, accion) for numero, texto, permitido, accion in opciones if permitido]


def mostrar_opciones_menu(opciones: list[OpcionMenu]) -> None:
	"""Muestra las opciones permitidas para el rol actual."""

	print("\n=== ECOTECH SOLUTIONS ===")
	for numero, descripcion, _accion in opciones:
		print(f"{numero}. {descripcion}")
	print("0. Salir")


def ejecutar_opcion_menu(opciones: list[OpcionMenu], opcion: str) -> bool:
	"""Ejecuta una opcion del menu y devuelve si debe continuar."""

	if opcion == "0":
		print("Sesion finalizada.")
		return False
	acciones = {numero: accion for numero, _texto, accion in opciones}
	accion = acciones.get(opcion)
	if accion is None:
		print(MENSAJE_OPCION_INVALIDA)
		return True
	accion()
	return True


def mostrar_menu() -> None:
	"""Ejecuta el menu principal conectado a la base de datos local."""

	# Los detalles técnicos de los servicios externos van a un archivo, no a la consola.
	logging.basicConfig(
		filename=DATABASE_PATH.with_name("ecotech.log"),
		level=logging.WARNING,
		format="%(asctime)s %(levelname)s %(name)s: %(message)s",
	)
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
		opciones = construir_opciones_menu(connection, usuario_actual)
		while True:
			mostrar_opciones_menu(opciones)
			opcion = input(MENSAJE_SELECCION).strip()
			try:
				if not ejecutar_opcion_menu(opciones, opcion):
					break
			except (
				ValueError,
				PermissionError,
				sqlite3.Error,
				ErrorServicioExterno,
			) as error:
				print(f"No se pudo completar la operacion: {error}")
	except (EOFError, KeyboardInterrupt):
		print("\nSesion finalizada por el usuario.")
	finally:
		connection.close()


if __name__ == "__main__":
	mostrar_menu()