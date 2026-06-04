"""
__main__.py
===========
Punto de entrada del solver de Kakuro.

Resuelve los tres tableros de dificultad Muy dificil por defecto,
o un tablero especifico si se pasa como argumento.

Uso:
    python kakuro_solver/                          # resuelve los 3 tableros
    python kakuro_solver/ ProgIIIG1-Act08-KK5EQAVX-Board.txt
    python kakuro_solver/ mi_tablero.txt --silencioso
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from FileParser import FileParser, FormatoInvalidoError  # noqa: E402
from KakuroSolver import resolver                         # noqa: E402

TABLEROS_PROYECTO = [
    "ProgIIIG1-Act08-KK5EQAVX-Board.txt",
    "ProgIIIG1-Act08-KK5LFAWU-Board.txt",
    "ProgIIIG1-Act08-KK5ILQKG-Board.txt",
]


def resolver_ruta(path: str) -> str:
    """Busca el archivo en el directorio actual y luego en el del proyecto."""
    if os.path.isfile(path):
        return path
    alternativa = os.path.join(BASE_DIR, path)
    if os.path.isfile(alternativa):
        return alternativa
    return path


def resolver_tablero(path: str, verbose: bool) -> bool:
    """
    Parsea y resuelve un tablero. Retorna True si encontro solucion.
    """
    print(f"\n{'='*55}")
    print(f"  Tablero: {os.path.basename(path)}")
    print(f"{'='*55}")

    try:
        board = FileParser.parsear(path)
    except FileNotFoundError:
        print(f"  ERROR: Archivo no encontrado: {path}")
        return False
    except FormatoInvalidoError as e:
        print(f"  ERROR de formato: {e}")
        return False

    print(f"  Celdas jugables : {len(board.jugables)}")
    print(f"  Secuencias      : {len(board.secuencias)}")

    solucion = resolver(board, verbose=verbose)

    if solucion:
        board.mostrar(solucion)
        return True
    else:
        print("  Sin solucion.")
        return False


def main() -> None:
    verbose = "--silencioso" not in sys.argv
    args    = [a for a in sys.argv[1:] if not a.startswith("--")]

    print("\n" + "=" * 55)
    print("       KAKURO SOLVER  —  CSP ENGINE")
    print("       Dificultad: Muy dificil")
    print("=" * 55)

    # Sin argumentos: resolver los 3 tableros del proyecto.
    if not args:
        resultados = []
        for nombre in TABLEROS_PROYECTO:
            path = os.path.join(BASE_DIR, nombre)
            ok   = resolver_tablero(path, verbose)
            resultados.append((nombre, ok))

        print(f"\n{'='*55}")
        print("  RESUMEN")
        print(f"{'='*55}")
        for nombre, ok in resultados:
            estado = "RESUELTO  ✓" if ok else "SIN SOLUCION  ✗"
            print(f"  {estado}  {nombre}")
        print()

    # Con argumento: resolver el tablero indicado.
    else:
        path = resolver_ruta(args[0])
        ok   = resolver_tablero(path, verbose)
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
