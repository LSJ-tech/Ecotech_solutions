"""Interfaz de consola para EcoTechSolutions."""

from datetime import date
from getpass import getpass
from pathlib import Path
from typing import Any, Callable
import logging
import sqlite3
import sys

if sys.platform == "win32":
	import msvcrt

from main import (
	CAMPO_NOMBRE_DEPARTAMENTO,
	DATABASE_PATH,
	LARGO_MINIMO_CONTRASENA,
	ROLES_VALIDOS,
	Empleado,
	ExportadorExcel,
	ExportadorPDF,
	IExportador,
	Informe,
	Proyecto,
	RegistroTiempo,
	ServicioReportes,
	Usuario,
	actualizar_departamento,
	actualizar_empleado,
	actualizar_proyecto,
	actualizar_registro_tiempo,
	asignar_empleado_proyecto_bd,
	asignar_empleado_departamento_bd,
	asignar_gerente_departamento,
	calcular_pago,
	calcular_tarifa_hora,
	conectar_bd,
	construir_informe_departamentos,
	construir_informe_empleados,
	construir_informe_proyectos,
	construir_informe_registros,
	enmascarar_rut,
	contar_registros_proyecto,
	desasignar_empleado_proyecto_bd,
	fila_a_empleado,
	guardar_departamento,
	guardar_proyecto,
	guardar_registro_tiempo,
	guardar_usuario_con_empleado,
	eliminar_departamento,
	eliminar_empleado,
	eliminar_proyecto,
	eliminar_registro_tiempo,
	eliminar_usuario,
	inicializar_bd,
	listar_departamentos,
	listar_empleados,
	listar_empleados_proyecto,
	listar_proyectos,
	listar_registros_tiempo,
	listar_usuarios,
	sumar_horas_empleado,
	validar_contrasena,
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
MENSAJE_ID_DEPARTAMENTO = "ID del departamento: "
MENSAJE_PROYECTO_INEXISTENTE = "El proyecto indicado no existe."
MENSAJE_DEPARTAMENTO_INEXISTENTE = "El departamento indicado no existe."
MENSAJE_ENTER_CONSERVA = "Enter conserva el valor actual."
MENSAJE_CANCELADO = "Operacion cancelada."
MENSAJE_VOLVER = "\nPresione Enter para volver al menu... "
# Errores previstos de una operacion: se informan sin cortar la sesion.
ERRORES_ESPERADOS = (ValueError, PermissionError, sqlite3.Error, ErrorServicioExterno)
CARPETA_INFORMES = DATABASE_PATH.with_name("informes")
ROLES_GESTION = {"admin", "rrhh"}
CONSULTA_EMPLEADO = "SELECT * FROM empleados WHERE rut = ?"
CONSULTA_PROYECTO = (
	"SELECT id_proyecto, nombre, descripcion, fecha_inicio, fecha_fin, ciudad "
	"FROM proyectos WHERE id_proyecto = ?"
)
OpcionMenu = tuple[str, str, Callable[[], None]]


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


def a_fecha(valor: str) -> date:
	"""Convierte texto YYYY-MM-DD en fecha con un mensaje de error legible."""

	try:
		return date.fromisoformat(valor.strip())
	except ValueError:
		raise ValueError("Ingrese una fecha valida con formato YYYY-MM-DD.") from None


def a_monto(valor: str, campo: str) -> float:
	"""Convierte texto en un monto positivo aceptando coma decimal."""

	try:
		return validar_monto(float(valor.strip().replace(",", ".")), campo)
	except ValueError:
		raise ValueError(f"{campo} debe ser un número mayor que 0.") from None


def a_fecha_fin(valor: str, fecha_inicio: date) -> date:
	"""Convierte la fecha de fin y comprueba que no preceda al inicio, para repetir solo ese campo."""

	fecha_fin = a_fecha(valor)
	if fecha_fin < fecha_inicio:
		raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")
	return fecha_fin


def a_horas(valor: str) -> float:
	"""Convierte texto en una cantidad de horas válida."""

	try:
		horas = float(valor.strip().replace(",", "."))
	except ValueError:
		raise ValueError("Las horas deben ser un número.") from None
	return validar_horas(horas)


def validar_correo(valor: str) -> str:
	"""Valida un correo con un formato básico (texto no vacío con @)."""

	correo = validar_texto(valor, "El correo")
	if "@" not in correo:
		raise ValueError("El correo debe tener un formato válido, por ejemplo nombre@dominio.cl.")
	return correo


def leer_o_conservar(mensaje: str, actual: Any, convertir: Callable[[str], Any]) -> Any:
	"""Solicita un valor mostrando el actual; Enter lo conserva y un error repite solo ese campo."""

	if actual in (None, ""):
		mostrado = "sin registrar"
	elif isinstance(actual, float):
		mostrado = f"{actual:,.10g}"
	else:
		mostrado = str(actual)
	while True:
		valor = input(f"{mensaje} [{mostrado}]: ").strip()
		if not valor:
			return actual
		try:
			return convertir(valor)
		except ValueError as error:
			print(error)


def pausar() -> None:
	"""Espera a que la persona confirme antes de redibujar el menu.

	Sin esta pausa el menu se imprime de inmediato y empuja hacia arriba el
	resultado recien mostrado (un listado, un informe o un mensaje de error).
	"""

	input(MENSAJE_VOLVER)


def confirmar(mensaje: str) -> bool:
	"""Pide una confirmación explícita antes de una acción irreversible."""

	return input(f"{mensaje} (s/n): ").strip().lower() == "s"


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


def leer_rut(mensaje: str = "RUT (formato 12345678-5, con guion y digito verificador): ") -> str:
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


def leer_contrasena_nueva(mensaje: str = MENSAJE_CONTRASENA) -> str:
	"""Solicita una contraseña nueva que cumpla la política y repite solo ese campo."""

	print(
		f"La contraseña debe tener al menos {LARGO_MINIMO_CONTRASENA} caracteres "
		"y combinar letras y números."
	)
	while True:
		try:
			return validar_contrasena(leer_contrasena(mensaje))
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
		try:
			return validar_correo(input("Correo: "))
		except ValueError as error:
			print(error)


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
			return a_horas(input("Horas trabajadas: "))
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


def obtener_fila_empleado(connection: sqlite3.Connection, rut: str) -> sqlite3.Row:
	"""Devuelve la fila del empleado o falla si no existe."""

	fila = connection.execute(CONSULTA_EMPLEADO, (rut,)).fetchone()
	if fila is None:
		raise ValueError(MENSAJE_EMPLEADO_INEXISTENTE)
	return fila


def obtener_proyecto(connection: sqlite3.Connection, id_proyecto: int) -> sqlite3.Row:
	"""Devuelve la fila del proyecto o falla si no existe."""

	fila = connection.execute(CONSULTA_PROYECTO, (id_proyecto,)).fetchone()
	if fila is None:
		raise ValueError(MENSAJE_PROYECTO_INEXISTENTE)
	return fila


def obtener_departamento(connection: sqlite3.Connection, id_departamento: int) -> sqlite3.Row:
	"""Devuelve la fila del departamento (con su gerente) o falla si no existe."""

	for fila in listar_departamentos(connection):
		if fila["id_departamento"] == id_departamento:
			return fila
	raise ValueError(MENSAJE_DEPARTAMENTO_INEXISTENTE)


def ejecutar_accion(accion: Callable[[], Any]) -> None:
	"""Ejecuta una acción del menú, informa los errores previstos y espera antes de volver.

	Una acción que ya mostró su propia pausa (un submenú) devuelve un valor
	verdadero, para no pedir Enter dos veces al encadenarse.
	"""

	try:
		if not accion():
			pausar()
	except ERRORES_ESPERADOS as error:
		print(f"No se pudo completar la operacion: {error}")
		pausar()


def ejecutar_submenu(titulo: str, opciones: list[OpcionMenu]) -> bool:
	"""Muestra un submenú y lo repite hasta que se elija `0. Volver`.

	Devuelve True para avisar a quien lo invocó que este submenú ya pausó
	después de cada acción.
	"""

	acciones = {numero: accion for numero, _texto, accion in opciones}
	while True:
		print(f"\n=== {titulo} ===")
		for numero, descripcion, _accion in opciones:
			print(f"{numero}. {descripcion}")
		print("0. Volver")
		opcion = input(MENSAJE_SELECCION).strip()
		if opcion == "0":
			return True
		if opcion not in acciones:
			print(MENSAJE_OPCION_INVALIDA)
			continue
		ejecutar_accion(acciones[opcion])


def consultar_clima_menu(connection: sqlite3.Connection) -> None:
	"""Consulta el clima actual de la ciudad de un proyecto."""

	mostrar_proyectos(connection)
	fila = obtener_proyecto(connection, leer_entero(MENSAJE_ID_PROYECTO))
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
		try:
			return a_monto(input(mensaje), campo)
		except ValueError as error:
			print(error)


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
	empleado = fila_a_empleado(obtener_fila_empleado(connection, rut))
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

	contrasena = leer_contrasena_nueva()
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
	# Toda cuenta pertenece a una persona de la empresa, también las de admin:
	# sin ficha no habría RUT que la identifique ni podría registrar sus horas.
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
	guardar_usuario_con_empleado(connection, usuario, empleado)
	print(
		f"Usuario registrado correctamente. Su usuario es: {nombre_usuario} "
		f"(ficha de empleado {rut_empleado})."
	)


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


def leer_filtro(mensaje: str) -> str | None:
	"""Solicita un texto de búsqueda opcional; Enter devuelve None (sin filtro)."""

	return input(mensaje).strip() or None


def mostrar_departamentos(connection: sqlite3.Connection, filtro: str | None = None) -> None:
	"""Muestra los departamentos, todos o los que coinciden con el filtro por nombre."""

	departamentos = listar_departamentos(connection, filtro)
	if not departamentos:
		print(
			f"No hay departamentos que coincidan con '{filtro}'."
			if filtro
			else "No hay departamentos registrados."
		)
		return
	for departamento in departamentos:
		gerente = departamento["gerente"] or "Sin gerente"
		print(f"{departamento['id_departamento']}: {departamento['nombre']} | Gerente: {gerente}")


def listar_departamentos_menu(connection: sqlite3.Connection) -> None:
	"""Lista todos los departamentos o busca por nombre."""

	mostrar_departamentos(
		connection, leer_filtro("Buscar por nombre (Enter para listar todos): ")
	)


def rut_para_mostrar(rut: str, usuario_actual: Usuario | None) -> str:
	"""Devuelve el RUT completo salvo que lo consulte un empleado y no sea el suyo."""

	if usuario_actual is None or usuario_actual.rol in ROLES_GESTION:
		return rut
	propio = usuario_actual.empleado.rut if usuario_actual.empleado else None
	return rut if rut == propio else enmascarar_rut(rut)


def mostrar_empleados(
	connection: sqlite3.Connection,
	detallado: bool = False,
	filtro: str | None = None,
	usuario_actual: Usuario | None = None,
) -> None:
	"""Muestra los empleados (todos o filtrados).

	Los datos personales se incluyen solo si detallado es True. Con usuario_actual
	informado, un rol sin permisos de gestión ve enmascarado el RUT de los demás;
	las llamadas internas, todas dentro de flujos de gestión, lo omiten.
	"""

	gestion = usuario_actual is None or usuario_actual.rol in ROLES_GESTION
	empleados = listar_empleados(connection, filtro, buscar_por_rut=gestion)
	if not empleados:
		print(
			f"No hay empleados que coincidan con '{filtro}'."
			if filtro
			else "No hay empleados registrados."
		)
		return
	for empleado in empleados:
		linea = (
			f"{empleado['id_empleado']}. {rut_para_mostrar(empleado['rut'], usuario_actual)}: "
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


def listar_empleados_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Lista todos los empleados o busca por RUT, nombre o apellido.

	La búsqueda se resuelve en la base con el RUT completo, de modo que enmascarar
	lo que se muestra no impide encontrar a nadie.
	"""

	gestion = usuario_actual.rol in ROLES_GESTION
	# Quien no puede ver el RUT ajeno tampoco lo busca: evita confirmar uno adivinado.
	campos = "RUT, nombre o apellido" if gestion else "nombre o apellido"
	mostrar_empleados(
		connection,
		gestion,
		leer_filtro(f"Buscar por {campos} (Enter para listar todos): "),
		usuario_actual,
	)


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
	id_departamento = leer_entero(MENSAJE_ID_DEPARTAMENTO)
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
	id_departamento = leer_entero(MENSAJE_ID_DEPARTAMENTO)
	asignar_empleado_departamento_bd(connection, rut, id_departamento)
	mensaje = "cambiado" if cambiar else "asignado"
	print(f"Departamento {mensaje} correctamente.")


def editar_departamento_menu(connection: sqlite3.Connection) -> None:
	"""Cambia el nombre de un departamento conservando su gerente."""

	mostrar_departamentos(connection)
	fila = obtener_departamento(connection, leer_entero(MENSAJE_ID_DEPARTAMENTO))
	print(MENSAJE_ENTER_CONSERVA)
	nombre = leer_o_conservar(
		"Nombre", fila["nombre"], lambda valor: validar_texto(valor, CAMPO_NOMBRE_DEPARTAMENTO)
	)
	actualizar_departamento(connection, fila["id_departamento"], nombre, fila["rut_gerente"])
	print("Departamento actualizado correctamente.")


def eliminar_departamento_menu(connection: sqlite3.Connection) -> None:
	"""Elimina un departamento sin empleados, previa confirmación."""

	mostrar_departamentos(connection)
	fila = obtener_departamento(connection, leer_entero(MENSAJE_ID_DEPARTAMENTO))
	if not confirmar(f"Se eliminará el departamento {fila['nombre']}. ¿Confirma?"):
		print(MENSAJE_CANCELADO)
		return
	eliminar_departamento(connection, fila["id_departamento"])
	print("Departamento eliminado correctamente.")


def gestionar_departamento_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> bool:
	"""Muestra las opciones para asignar o cambiar el departamento de un empleado."""

	verificar_gestion(usuario_actual, "gestionar departamentos")
	return ejecutar_submenu(
		"GESTIONAR DEPARTAMENTO DE EMPLEADO",
		[
			("1", "Asignar departamento",
				lambda: actualizar_departamento_empleado_menu(connection, cambiar=False)),
			("2", "Cambiar departamento",
				lambda: actualizar_departamento_empleado_menu(connection, cambiar=True)),
		],
	)


def gestionar_departamentos_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> bool:
	"""Muestra las opciones de creación, edición, eliminación y gestión de departamentos."""

	verificar_gestion(usuario_actual, "gestionar departamentos")
	return ejecutar_submenu(
		"GESTIONAR DEPARTAMENTOS",
		[
			("1", "Crear departamento", lambda: crear_departamento_menu(connection)),
			("2", "Editar nombre de departamento", lambda: editar_departamento_menu(connection)),
			("3", "Eliminar departamento", lambda: eliminar_departamento_menu(connection)),
			("4", "Asignar o cambiar gerente", lambda: asignar_gerente_menu(connection)),
			("5", "Asignar o cambiar departamento de empleado",
				lambda: gestionar_departamento_menu(connection, usuario_actual)),
		],
	)


def editar_empleado_menu(connection: sqlite3.Connection) -> None:
	"""Edita la ficha de un empleado campo por campo; Enter conserva cada valor."""

	mostrar_empleados(connection, detallado=True)
	fila = obtener_fila_empleado(connection, leer_rut())
	actual = fila_a_empleado(fila)
	print(MENSAJE_ENTER_CONSERVA)
	nombre = leer_o_conservar("Nombre", actual.nombre, lambda v: validar_texto(v, "El nombre"))
	apellido = leer_o_conservar(
		"Apellido", actual.apellido, lambda v: validar_texto(v, "El apellido")
	)
	correo = leer_o_conservar("Correo", actual.correo, validar_correo)
	cargo = leer_o_conservar("Cargo", actual.cargo, lambda v: validar_texto(v, "El cargo"))
	direccion = leer_o_conservar(
		"Direccion", actual.direccion, lambda v: validar_texto(v, "La dirección")
	)
	telefono = leer_o_conservar("Telefono", actual.telefono, validar_telefono)
	fecha_inicio_contrato = leer_o_conservar(
		"Fecha de inicio de contrato (YYYY-MM-DD)", actual.fecha_inicio_contrato, a_fecha
	)
	salario = leer_o_conservar(
		"Salario mensual en CLP", actual.salario, lambda v: a_monto(v, "El salario")
	)
	actualizar_empleado(
		connection,
		actual.rut,
		nombre=nombre,
		apellido=apellido,
		correo=correo,
		cargo=cargo,
		direccion=direccion,
		telefono=telefono,
		fecha_inicio_contrato=fecha_inicio_contrato,
		salario=salario,
		id_departamento=fila["id_departamento"],
	)
	print("Ficha actualizada correctamente.")


def eliminar_empleado_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Elimina un empleado, su cuenta y sus horas, previa confirmación."""

	mostrar_empleados(connection)
	rut = leer_rut()
	if usuario_actual.empleado is not None and usuario_actual.empleado.rut == rut:
		raise ValueError("No puede eliminar su propia ficha.")
	obtener_fila_empleado(connection, rut)
	horas = sumar_horas_empleado(connection, rut)
	if not confirmar(
		f"Se eliminará la ficha, su cuenta de acceso y {horas:g} horas registradas. ¿Confirma?"
	):
		print(MENSAJE_CANCELADO)
		return
	eliminar_empleado(connection, rut)
	print("Empleado eliminado correctamente.")


def gestionar_empleados_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> bool:
	"""Muestra las opciones de edición y eliminación de empleados."""

	verificar_gestion(usuario_actual, "gestionar empleados")
	return ejecutar_submenu(
		"GESTIONAR EMPLEADOS",
		[
			("1", "Editar ficha de empleado", lambda: editar_empleado_menu(connection)),
			("2", "Eliminar empleado",
				lambda: eliminar_empleado_menu(connection, usuario_actual)),
		],
	)


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


def editar_proyecto_menu(connection: sqlite3.Connection) -> None:
	"""Edita un proyecto campo por campo; Enter conserva cada valor."""

	mostrar_proyectos(connection)
	fila = obtener_proyecto(connection, leer_entero(MENSAJE_ID_PROYECTO))
	print(MENSAJE_ENTER_CONSERVA)
	nombre = leer_o_conservar(
		"Nombre", fila["nombre"], lambda v: validar_texto(v, "El nombre del proyecto")
	)
	descripcion = leer_o_conservar(
		"Descripcion", fila["descripcion"], lambda v: validar_texto(v, "La descripción")
	)
	fecha_inicio = leer_o_conservar(
		"Fecha de inicio (YYYY-MM-DD)", date.fromisoformat(fila["fecha_inicio"]), a_fecha
	)
	fecha_fin = leer_o_conservar(
		"Fecha de fin (YYYY-MM-DD)",
		date.fromisoformat(fila["fecha_fin"]) if fila["fecha_fin"] else None,
		lambda v: a_fecha_fin(v, fecha_inicio),
	)
	ciudad = leer_o_conservar("Ciudad", fila["ciudad"], validar_ciudad)
	actualizar_proyecto(
		connection,
		fila["id_proyecto"],
		nombre=nombre,
		descripcion=descripcion,
		fecha_inicio=fecha_inicio,
		fecha_fin=fecha_fin,
		ciudad=ciudad,
	)
	print("Proyecto actualizado correctamente.")


def eliminar_proyecto_menu(connection: sqlite3.Connection) -> None:
	"""Elimina un proyecto con sus asignaciones y horas, previa confirmación."""

	mostrar_proyectos(connection)
	fila = obtener_proyecto(connection, leer_entero(MENSAJE_ID_PROYECTO))
	registros = contar_registros_proyecto(connection, fila["id_proyecto"])
	if not confirmar(
		f"Se eliminará el proyecto {fila['nombre']}, sus asignaciones y "
		f"{registros} registro(s) de horas. ¿Confirma?"
	):
		print(MENSAJE_CANCELADO)
		return
	eliminar_proyecto(connection, fila["id_proyecto"])
	print("Proyecto eliminado correctamente.")


def mostrar_empleados_proyecto(connection: sqlite3.Connection, id_proyecto: int) -> None:
	"""Muestra los empleados asignados a un proyecto."""

	asignados = listar_empleados_proyecto(connection, id_proyecto)
	if not asignados:
		print("El proyecto no tiene empleados asignados.")
		return
	for empleado in asignados:
		print(f"{empleado['rut']}: {empleado['nombre']} {empleado['apellido']} | {empleado['cargo']}")


def desasignar_proyecto_menu(connection: sqlite3.Connection) -> None:
	"""Quita a un empleado de un proyecto; sus horas registradas se conservan."""

	mostrar_proyectos(connection)
	fila = obtener_proyecto(connection, leer_entero(MENSAJE_ID_PROYECTO))
	mostrar_empleados_proyecto(connection, fila["id_proyecto"])
	rut = leer_rut("RUT del empleado: ")
	if not desasignar_empleado_proyecto_bd(connection, rut, fila["id_proyecto"]):
		raise ValueError("El empleado no está asignado a ese proyecto.")
	print("Empleado desasignado del proyecto; sus horas registradas se conservan.")


def gestionar_proyectos_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> bool:
	"""Muestra las opciones de creación, edición, eliminación y asignación de proyectos."""

	verificar_gestion(usuario_actual, "gestionar proyectos")
	return ejecutar_submenu(
		"GESTIONAR PROYECTOS",
		[
			("1", "Crear proyecto", lambda: crear_proyecto_menu(connection, usuario_actual)),
			("2", "Editar proyecto", lambda: editar_proyecto_menu(connection)),
			("3", "Eliminar proyecto", lambda: eliminar_proyecto_menu(connection)),
			("4", "Asignar empleado a proyecto",
				lambda: asignar_proyecto_menu(connection, usuario_actual)),
			("5", "Desasignar empleado de proyecto",
				lambda: desasignar_proyecto_menu(connection)),
		],
	)


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


def leer_exportador() -> IExportador:
	"""Solicita el formato del informe y devuelve el exportador correspondiente."""

	while True:
		formato = input("Formato (1=PDF texto, 2=Excel CSV): ").strip()
		if formato == "1":
			return ExportadorPDF()
		if formato == "2":
			return ExportadorExcel()
		print(MENSAJE_OPCION_INVALIDA)


def exportar_informe(informe: Informe, carpeta: Path | None = None) -> None:
	"""Muestra el informe en pantalla y lo guarda en la carpeta de informes."""

	if not informe.filas:
		print(f"No hay datos para {informe.titulo.lower()}.")
		return
	servicio = ServicioReportes(leer_exportador())
	print("\n" + servicio.generar(informe))
	ruta = servicio.guardar(informe, carpeta or CARPETA_INFORMES)
	print(f"Informe guardado en: {ruta}")


def informe_registros_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Informe de horas; los empleados solo obtienen el propio."""

	filas = listar_registros_tiempo(connection, obtener_filtro_rut(usuario_actual))
	exportar_informe(construir_informe_registros(filas))


def mostrar_reportes_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> bool | None:
	"""Genera y guarda el informe de la entidad elegida; los empleados solo el de sus horas."""

	if usuario_actual.rol not in ROLES_GESTION:
		informe_registros_menu(connection, usuario_actual)
		return
	return ejecutar_submenu(
		"GENERAR INFORME",
		[
			("1", "Horas trabajadas", lambda: informe_registros_menu(connection, usuario_actual)),
			("2", "Empleados (sin datos personales cifrados)",
				lambda: exportar_informe(construir_informe_empleados(listar_empleados(connection)))),
			("3", "Departamentos",
				lambda: exportar_informe(construir_informe_departamentos(listar_departamentos(connection)))),
			("4", "Proyectos",
				lambda: exportar_informe(construir_informe_proyectos(listar_proyectos(connection)))),
		],
	)


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


def mostrar_registros(registros: list[sqlite3.Row]) -> None:
	"""Imprime registros de tiempo, una línea por registro."""

	for registro in registros:
		print(
			f"{registro['id_registro']}: {registro['fecha']} | "
			f"{registro['empleado']} ({registro['rut_empleado']}) | "
			f"{registro['proyecto']} | {registro['horas']} horas"
			+ (f" | {registro['descripcion_tarea']}" if registro["descripcion_tarea"] else "")
		)


def mostrar_registros_tiempo_menu(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> None:
	"""Muestra los registros de tiempo permitidos para el rol actual."""

	registros = listar_registros_tiempo(connection, obtener_filtro_rut(usuario_actual))
	if not registros:
		print("No hay registros de tiempo.")
		return
	mostrar_registros(registros)


def obtener_registro_visible(
	connection: sqlite3.Connection, usuario_actual: Usuario
) -> sqlite3.Row:
	"""Lista los registros que el rol puede tocar y devuelve el elegido por ID.

	Un empleado solo ve (y por lo tanto solo puede elegir) sus propios registros.
	"""

	registros = listar_registros_tiempo(connection, obtener_filtro_rut(usuario_actual))
	if not registros:
		raise ValueError("No hay registros de tiempo para editar o eliminar.")
	mostrar_registros(registros)
	id_registro = leer_entero("ID del registro: ")
	for fila in registros:
		if fila["id_registro"] == id_registro:
			return fila
	raise ValueError("El registro indicado no existe o no le pertenece.")


def editar_registro_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Edita fecha, horas y descripción de un registro; Enter conserva cada valor."""

	fila = obtener_registro_visible(connection, usuario_actual)
	print(MENSAJE_ENTER_CONSERVA)
	fecha = leer_o_conservar("Fecha (YYYY-MM-DD)", date.fromisoformat(fila["fecha"]), a_fecha)
	horas = leer_o_conservar("Horas trabajadas", float(fila["horas"]), a_horas)
	descripcion_tarea = leer_o_conservar(
		"Descripcion breve de las tareas", fila["descripcion_tarea"], validar_descripcion_tarea
	)
	actualizar_registro_tiempo(
		connection,
		fila["id_registro"],
		fecha=fecha,
		horas=horas,
		descripcion_tarea=descripcion_tarea,
	)
	print("Registro actualizado correctamente.")


def eliminar_registro_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> None:
	"""Elimina un registro de tiempo previa confirmación."""

	fila = obtener_registro_visible(connection, usuario_actual)
	if not confirmar(
		f"Se eliminará el registro {fila['id_registro']} "
		f"({fila['fecha']}, {fila['horas']:g} horas). ¿Confirma?"
	):
		print(MENSAJE_CANCELADO)
		return
	eliminar_registro_tiempo(connection, fila["id_registro"])
	print("Registro eliminado correctamente.")


def gestionar_registros_menu(connection: sqlite3.Connection, usuario_actual: Usuario) -> bool:
	"""Muestra las opciones de edición y eliminación de registros de tiempo."""

	return ejecutar_submenu(
		"EDITAR O ELIMINAR REGISTROS DE TIEMPO",
		[
			("1", "Editar registro", lambda: editar_registro_menu(connection, usuario_actual)),
			("2", "Eliminar registro", lambda: eliminar_registro_menu(connection, usuario_actual)),
		],
	)


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
		("2", "Listar o buscar departamentos", True,
			lambda: listar_departamentos_menu(connection)),
		("3", "Gestionar empleados", gestion,
			lambda: gestionar_empleados_menu(connection, usuario_actual)),
		("4", "Listar o buscar empleados", True,
			lambda: listar_empleados_menu(connection, usuario_actual)),
		("5", "Gestionar proyectos", gestion,
			lambda: gestionar_proyectos_menu(connection, usuario_actual)),
		("6", "Listar proyectos", True, lambda: mostrar_proyectos(connection)),
		("7", etiqueta("Registrar horas trabajadas", "Registrar mis horas trabajadas"), True,
			lambda: registrar_tiempo_menu(connection, usuario_actual)),
		("8", etiqueta("Ver registros de tiempo", "Ver mis horas registradas"), True,
			lambda: mostrar_registros_tiempo_menu(connection, usuario_actual)),
		("9", etiqueta("Editar o eliminar registros de tiempo", "Editar o eliminar mis registros"),
			True, lambda: gestionar_registros_menu(connection, usuario_actual)),
		("10", etiqueta("Generar reporte", "Generar mi reporte"), True,
			lambda: mostrar_reportes_menu(connection, usuario_actual)),
		("11", "Consultar clima de un proyecto", True, lambda: consultar_clima_menu(connection)),
		("12", "Consultar indicador economico", True,
			lambda: consultar_indicador_menu(connection)),
		("13", "Calcular pago en moneda extranjera", gestion,
			lambda: calcular_pago_menu(connection, usuario_actual)),
		("14", "Crear usuario", gestion, lambda: crear_usuario_admin_menu(connection, usuario_actual)),
		("15", "Listar usuarios", gestion,
			lambda: listar_usuarios_admin_menu(connection, usuario_actual)),
		("16", "Cambiar rol de usuario", admin, lambda: cambiar_rol_menu(connection, usuario_actual)),
		("17", "Eliminar usuario", admin,
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
	ejecutar_accion(accion)
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
			if not ejecutar_opcion_menu(opciones, opcion):
				break
	except (EOFError, KeyboardInterrupt):
		print("\nSesion finalizada por el usuario.")
	finally:
		connection.close()


if __name__ == "__main__":
	mostrar_menu()
