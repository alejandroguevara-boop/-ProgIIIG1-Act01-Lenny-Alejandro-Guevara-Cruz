"""
test_kakuro.py
==============
Suite de pruebas para el solver de Kakuro.

Ejecucion:
    python test_kakuro.py
"""

import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from Constraints import combinaciones_validas, allDif, sum_constraint
from CSPModel import CSPModel
from FileParser import FileParser, FormatoInvalidoError
from KakuroBoard import KakuroBoard, TipoCelda, Secuencia, Celda
from KakuroSolver import resolver
from Utils import esta_completo, hay_conflicto, copiar_estado


# ─────────────────────────────────────────────────────────────
# TABLEROS DEL PROYECTO (los tres reales de dificultad Muy dificil)
# ─────────────────────────────────────────────────────────────

BOARD_EQAVX = os.path.join(BASE_DIR, "ProgIIIG1-Act08-KK5EQAVX-Board.txt")
BOARD_LFAWU = os.path.join(BASE_DIR, "ProgIIIG1-Act08-KK5LFAWU-Board.txt")
BOARD_ILQKG = os.path.join(BASE_DIR, "ProgIIIG1-Act08-KK5ILQKG-Board.txt")

# Tablero minimo construido en memoria para tests unitarios rapidos.
# V col1=3, V col2=4, H fila1=3, H fila2=4
# Solucion unica: r1c1=2,r1c2=1,r2c1=1,r2c2=3
TABLERO_MINIMO = (
    "X    3\\    4\\\n"
    "\\3   O      O\n"
    "\\4   O      O\n"
    "X    X      X\n"
)

SOLUCION_MINIMO = {"r1c1": 2, "r1c2": 1, "r2c1": 1, "r2c2": 3}


def crear_desde_texto(contenido: str) -> KakuroBoard:
    nombre = os.path.join(BASE_DIR, "_tmp_test.txt")
    with open(nombre, "w") as f:
        f.write(contenido)
    try:
        return FileParser.parsear(nombre)
    finally:
        if os.path.exists(nombre):
            os.remove(nombre)


# ─────────────────────────────────────────────────────────────
# TEST 1: COMBINACIONES VALIDAS
# ─────────────────────────────────────────────────────────────

class TestCombinacionesValidas(unittest.TestCase):

    def test_suma_3_dos_celdas(self):
        combos = combinaciones_validas(3, 2)
        self.assertEqual(len(combos), 1)
        self.assertIn((1, 2), combos)

    def test_suma_17_dos_celdas(self):
        combos = combinaciones_validas(17, 2)
        self.assertEqual(len(combos), 1)
        self.assertIn((8, 9), combos)

    def test_suma_35_cinco_celdas(self):
        combos = combinaciones_validas(35, 5)
        self.assertEqual(len(combos), 1)
        self.assertIn((5, 6, 7, 8, 9), combos)

    def test_suma_45_nueve_celdas(self):
        combos = combinaciones_validas(45, 9)
        self.assertEqual(len(combos), 1)
        self.assertIn(tuple(range(1, 10)), combos)

    def test_suma_imposible(self):
        self.assertEqual(len(combinaciones_validas(2, 2)), 0)

    def test_cache(self):
        self.assertIs(combinaciones_validas(10, 3), combinaciones_validas(10, 3))


# ─────────────────────────────────────────────────────────────
# TEST 2: UTILS
# ─────────────────────────────────────────────────────────────

class TestUtils(unittest.TestCase):

    def test_esta_completo(self):
        self.assertTrue(esta_completo({"A": {1}, "B": {3}}))
        self.assertFalse(esta_completo({"A": {1, 2}, "B": {3}}))

    def test_hay_conflicto(self):
        self.assertTrue(hay_conflicto({"A": set(), "B": {3}}))
        self.assertFalse(hay_conflicto({"A": {1}, "B": {3}}))

    def test_copiar_estado_independiente(self):
        original = {"A": {1, 2}, "B": {3, 4}}
        copia = copiar_estado(original)
        copia["A"].discard(1)
        self.assertIn(1, original["A"])


# ─────────────────────────────────────────────────────────────
# TEST 3: RESTRICCIONES
# ─────────────────────────────────────────────────────────────

class TestAllDif(unittest.TestCase):

    def test_elimina_singleton(self):
        doms = {"A": {1}, "B": {1, 2, 3}, "C": {1, 3}}
        cambio = allDif(doms, ["A", "B", "C"])
        self.assertTrue(cambio)
        self.assertNotIn(1, doms["B"])
        self.assertNotIn(1, doms["C"])

    def test_sin_singleton_no_cambia(self):
        doms = {"A": {1, 2}, "B": {2, 3}}
        self.assertFalse(allDif(doms, ["A", "B"]))


class TestSumConstraint(unittest.TestCase):

    def test_suma_3_reduce(self):
        doms = {"A": set(range(1, 10)), "B": set(range(1, 10))}
        sum_constraint(doms, ["A", "B"], suma_objetivo=3)
        self.assertEqual(doms["A"], {1, 2})
        self.assertEqual(doms["B"], {1, 2})

    def test_suma_17_reduce(self):
        doms = {"A": set(range(1, 10)), "B": set(range(1, 10))}
        sum_constraint(doms, ["A", "B"], suma_objetivo=17)
        self.assertEqual(doms["A"], {8, 9})
        self.assertEqual(doms["B"], {8, 9})

    def test_imposible_genera_conflicto(self):
        doms = {"A": {5}, "B": {5}}
        sum_constraint(doms, ["A", "B"], suma_objetivo=3)
        self.assertTrue(hay_conflicto(doms))


# ─────────────────────────────────────────────────────────────
# TEST 4: PARSER
# ─────────────────────────────────────────────────────────────

class TestFileParser(unittest.TestCase):

    def test_tablero_minimo_dimensiones(self):
        b = crear_desde_texto(TABLERO_MINIMO)
        self.assertEqual(b.filas, 4)
        self.assertEqual(b.cols, 3)
        self.assertEqual(len(b.jugables), 4)

    def test_secuencias_extraidas(self):
        b = crear_desde_texto(TABLERO_MINIMO)
        dirs = {s.direccion for s in b.secuencias}
        self.assertIn("H", dirs)
        self.assertIn("V", dirs)

    def test_tipo_celdas(self):
        b = crear_desde_texto(TABLERO_MINIMO)
        self.assertEqual(b.grilla[0][0].tipo, TipoCelda.NEGRA)
        self.assertEqual(b.grilla[1][1].tipo, TipoCelda.JUGABLE)
        self.assertEqual(b.grilla[0][1].tipo, TipoCelda.PISTA)

    def test_token_invalido(self):
        with self.assertRaises(FormatoInvalidoError):
            crear_desde_texto("X  ZZZ  O\n\\3  O  O\n\\4  O  O\nX  X  X\n")

    def test_archivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            FileParser.parsear("_no_existe.txt")

    def test_ignora_comentarios(self):
        b = crear_desde_texto("# comentario\n" + TABLERO_MINIMO)
        self.assertEqual(b.filas, 4)


# ─────────────────────────────────────────────────────────────
# TEST 5: MODELO CSP
# ─────────────────────────────────────────────────────────────

class TestCSPModel(unittest.TestCase):

    def setUp(self):
        self.board  = crear_desde_texto(TABLERO_MINIMO)
        self.modelo = CSPModel(self.board)

    def test_variables_son_jugables(self):
        self.assertEqual(set(self.modelo.var_doms.keys()), set(self.board.jugables))

    def test_dominios_no_vacios(self):
        for v, dom in self.modelo.var_doms.items():
            self.assertGreater(len(dom), 0, f"Dominio de {v} vacio.")

    def test_dos_constraints_por_secuencia(self):
        self.assertEqual(len(self.modelo.constraints), len(self.board.secuencias) * 2)

    def test_vecinos_horizontales(self):
        self.assertIn("r1c2", self.modelo.neighbours["r1c1"])

    def test_vecinos_verticales(self):
        self.assertIn("r2c1", self.modelo.neighbours["r1c1"])


# ─────────────────────────────────────────────────────────────
# TEST 6: SOLUCION TABLERO MINIMO
# ─────────────────────────────────────────────────────────────

class TestSolucionMinimo(unittest.TestCase):

    def _verificar(self, board, sol):
        for s in board.secuencias:
            vals = [sol[c] for c in s.celdas]
            self.assertEqual(sum(vals), s.suma,
                f"{s.direccion} {s.celdas}: suma {sum(vals)} != {s.suma}")
            self.assertEqual(len(set(vals)), len(vals),
                f"{s.direccion} {s.celdas}: valores repetidos {vals}")

    def test_resuelve_y_verifica(self):
        board = crear_desde_texto(TABLERO_MINIMO)
        sol   = resolver(board, verbose=False)
        self.assertIsNotNone(sol)
        self._verificar(board, sol)
        self.assertEqual(sol, SOLUCION_MINIMO)

    def test_imposible_retorna_none(self):
        # suma 2 con 2 celdas: imposible
        contenido = "X    3\\    4\\\n\\2   O      O\n\\4   O      O\nX    X      X\n"
        board = crear_desde_texto(contenido)
        self.assertIsNone(resolver(board, verbose=False))


# ─────────────────────────────────────────────────────────────
# TEST 7: TABLEROS REALES MUY DIFICIL
# ─────────────────────────────────────────────────────────────

class TestTablerosMuyDificil(unittest.TestCase):
    """
    Resuelve y verifica los tres tableros reales de dificultad Muy dificil
    de SudokuMania.com.ar. Estos son los tableros del proyecto.
    """

    def _verificar(self, board, sol, codigo):
        self.assertIsNotNone(sol, f"{codigo}: el solver no encontro solucion.")
        for s in board.secuencias:
            vals = [sol[c] for c in s.celdas]
            self.assertEqual(sum(vals), s.suma,
                f"{codigo} {s.direccion} {s.celdas}: suma {sum(vals)} != {s.suma}")
            self.assertEqual(len(set(vals)), len(vals),
                f"{codigo} {s.direccion} {s.celdas}: valores repetidos {vals}")

    def test_KK5EQAVX(self):
        board = FileParser.parsear(BOARD_EQAVX)
        sol   = resolver(board, verbose=False)
        self._verificar(board, sol, "KK5EQAVX")

    def test_KK5LFAWU(self):
        board = FileParser.parsear(BOARD_LFAWU)
        sol   = resolver(board, verbose=False)
        self._verificar(board, sol, "KK5LFAWU")

    def test_KK5ILQKG(self):
        board = FileParser.parsear(BOARD_ILQKG)
        sol   = resolver(board, verbose=False)
        self._verificar(board, sol, "KK5ILQKG")


# ─────────────────────────────────────────────────────────────
# EJECUCION
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("    KAKURO SOLVER - SUITE DE PRUEBAS")
    print("=" * 55 + "\n")

    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCombinacionesValidas))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestAllDif))
    suite.addTests(loader.loadTestsFromTestCase(TestSumConstraint))
    suite.addTests(loader.loadTestsFromTestCase(TestFileParser))
    suite.addTests(loader.loadTestsFromTestCase(TestCSPModel))
    suite.addTests(loader.loadTestsFromTestCase(TestSolucionMinimo))
    suite.addTests(loader.loadTestsFromTestCase(TestTablerosMuyDificil))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 55)
    if result.wasSuccessful():
        print("  Todas las pruebas pasaron.")
    else:
        print(f"  {len(result.failures)} falla(s), {len(result.errors)} error(es).")
    print("=" * 55 + "\n")
