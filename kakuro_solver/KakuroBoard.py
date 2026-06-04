"""
KakuroBoard.py
==============
Representación del tablero de Kakuro.

Almacena:
  - Dimensiones del tablero.
  - Tipo de cada celda: NEGRA, PISTA o JUGABLE.
  - Pistas de suma horizontal y vertical para celdas de pista.
  - Secuencias: listas de celdas jugables agrupadas por pista.

No contiene lógica CSP. Es la fuente de verdad estructural
que FileParser construye y CSPModel consulta.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────
# TIPOS DE CELDA
# ─────────────────────────────────────────────

class TipoCelda(Enum):
    """Tipo de cada celda en el tablero de Kakuro."""
    NEGRA   = auto()   # Celda bloqueada (esquina superior izquierda típica)
    PISTA   = auto()   # Celda negra con pistas de suma (derecha y/o abajo)
    JUGABLE = auto()   # Celda blanca que el solver debe rellenar


# ─────────────────────────────────────────────
# CELDA
# ─────────────────────────────────────────────

@dataclass
class Celda:
    """
    Representa una celda individual del tablero.

    Attributes:
        fila:      Índice de fila (0-based).
        col:       Índice de columna (0-based).
        tipo:      TipoCelda (NEGRA, PISTA o JUGABLE).
        pista_h:   Suma pista horizontal (solo celdas PISTA, puede ser None).
        pista_v:   Suma pista vertical (solo celdas PISTA, puede ser None).
    """
    fila:    int
    col:     int
    tipo:    TipoCelda
    pista_h: Optional[int] = None
    pista_v: Optional[int] = None


# ─────────────────────────────────────────────
# SECUENCIA
# ─────────────────────────────────────────────

@dataclass
class Secuencia:
    """
    Grupo de celdas jugables consecutivas con una pista de suma.

    Equivalente a un 'grupo' en el solver de Sudoku, pero con
    la suma objetivo asociada.

    Attributes:
        suma:      Valor que deben sumar las celdas de la secuencia.
        celdas:    Lista de identificadores de celdas jugables (ej: "r2c3").
        direccion: "H" (horizontal) o "V" (vertical).
    """
    suma:      int
    celdas:    List[str]
    direccion: str


# ─────────────────────────────────────────────
# TABLERO
# ─────────────────────────────────────────────

class KakuroBoard:
    """
    Tablero completo de Kakuro.

    Attributes:
        filas:      Número de filas del tablero.
        cols:       Número de columnas del tablero.
        grilla:     Matriz 2D de objetos Celda.
        secuencias: Lista de todas las Secuencias (H y V).
        jugables:   Lista de IDs de celdas jugables (variables CSP).
    """

    def __init__(self, filas: int, cols: int):
        self.filas = filas
        self.cols  = cols
        self.grilla: List[List[Celda]] = []
        self.secuencias: List[Secuencia] = []
        self.jugables: List[str] = []

    @staticmethod
    def celda_id(fila: int, col: int) -> str:
        """
        Genera el identificador único de una celda.

        Usa 'r{fila}c{col}' con índices 0-based internamente.
        Ejemplo: fila=1, col=3 -> 'r1c3'

        Args:
            fila: Índice de fila (0-based).
            col:  Índice de columna (0-based).

        Returns:
            String identificador de la celda.
        """
        return f"r{fila}c{col}"

    def get_celda(self, fila: int, col: int) -> Celda:
        """
        Accede a una celda por sus coordenadas.

        Args:
            fila: Índice de fila (0-based).
            col:  Índice de columna (0-based).

        Returns:
            Objeto Celda en esa posición.
        """
        return self.grilla[fila][col]

    def agregar_secuencia(self, secuencia: Secuencia) -> None:
        """
        Registra una secuencia en el tablero.

        Args:
            secuencia: Objeto Secuencia a agregar.
        """
        self.secuencias.append(secuencia)

    def registrar_jugables(self) -> None:
        """
        Recorre la grilla y registra los IDs de celdas jugables.
        Debe llamarse después de construir la grilla completa.
        """
        self.jugables = [
            KakuroBoard.celda_id(f, c)
            for f in range(self.filas)
            for c in range(self.cols)
            if self.grilla[f][c].tipo == TipoCelda.JUGABLE
        ]

    def mostrar(self, solucion: Optional[Dict[str, int]] = None) -> None:
        """
        Imprime el tablero en consola.

        Si se provee una solución, muestra los valores asignados
        en las celdas jugables. Si no, muestra '?' en las jugables.

        Args:
            solucion: Diccionario celda_id -> valor asignado (opcional).
        """
        print()
        ancho = 6  # ancho de cada celda en caracteres

        for f in range(self.filas):
            fila_str = ""
            for c in range(self.cols):
                celda = self.grilla[f][c]
                cid   = KakuroBoard.celda_id(f, c)

                if celda.tipo == TipoCelda.JUGABLE:
                    if solucion and cid in solucion:
                        fila_str += f"  [{solucion[cid]}]  "
                    else:
                        fila_str += "  [?]  "

                elif celda.tipo == TipoCelda.NEGRA:
                    fila_str += " ■■■■■ "

                else:  # PISTA
                    h = str(celda.pista_h) if celda.pista_h else " "
                    v = str(celda.pista_v) if celda.pista_v else " "
                    fila_str += f"\\{v:>2}/{h:<2}"

            print(fila_str)

        print()
