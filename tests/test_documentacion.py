"""Comprueba que la documentación siga coincidiendo con el proyecto.

Las cifras del `Readme.md` (cantidad de cambios registrados y de pruebas por
suite) y las rutas que menciona se desactualizan con facilidad. Estas pruebas
las contrastan con la realidad, de modo que un descuido falla aquí y no queda
en la entrega.
"""

import re
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
README = (RAIZ / "Readme.md").read_text(encoding="utf-8")
VALIDACION = (RAIZ / "VALIDACION_IA.md").read_text(encoding="utf-8")


def contar_pruebas(modulo: str) -> int:
	"""Cuenta las pruebas de una suite sin ejecutarlas."""

	return unittest.defaultTestLoader.loadTestsFromName(modulo).countTestCases()


class PruebasDocumentacion(unittest.TestCase):
	def test_cada_cambio_esta_en_el_indice(self):
		entradas = re.findall(r"^### (Cambio \d+) - ", VALIDACION, re.M)
		indice = re.findall(r"^  - \[(Cambio \d+) - ", VALIDACION, re.M)
		self.assertEqual(entradas, indice, "el índice y las entradas de VALIDACION_IA no coinciden")
		numeros = [int(entrada.split()[1]) for entrada in entradas]
		self.assertEqual(numeros, sorted(numeros), "los cambios no están en orden")

	def test_el_readme_cita_la_cantidad_real_de_cambios(self):
		registrados = len(re.findall(r"^### Cambio \d+ - ", VALIDACION, re.M))
		citados = set(re.findall(r"(\d+) cambios", README))
		self.assertEqual(citados, {str(registrados)})

	def test_el_readme_cita_la_cantidad_real_de_pruebas(self):
		suites = {
			"tests/test_nucleo.py": contar_pruebas("tests.test_nucleo"),
			"tests/test_servicios_externos.py": contar_pruebas("tests.test_servicios_externos"),
			"tests/test_documentacion.py": contar_pruebas("tests.test_documentacion"),
		}
		for ruta, total in suites.items():
			with self.subTest(suite=ruta):
				self.assertIn(f"`{ruta}` | {total} |", README, f"{ruta} tiene {total} pruebas")
		self.assertIn(f"**{sum(suites.values())} automatizadas**", README)

	def test_los_archivos_que_menciona_el_readme_existen(self):
		# El arbol del Readme muestra los nombres indentados bajo su carpeta, sin
		# repetir el prefijo, asi que basta con que el archivo exista en el proyecto.
		citados = re.findall(r"^[│├└─\s]*([\w./-]+\.(?:py|md|png|mmd|db|example))", README, re.M)
		for ruta in sorted(set(citados)):
			with self.subTest(ruta=ruta):
				nombre = Path(ruta).name
				existe = (RAIZ / ruta).exists() or any(RAIZ.rglob(nombre))
				self.assertTrue(existe, f"el Readme menciona {ruta}, que no existe")


if __name__ == "__main__":
	unittest.main()
