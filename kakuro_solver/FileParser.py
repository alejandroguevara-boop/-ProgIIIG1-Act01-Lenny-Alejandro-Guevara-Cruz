r"""
FileParser.py
=============
Lee archivos .txt de tableros de Kakuro y construye un KakuroBoard.

═══════════════════════════════════════════════════════════════
FORMATO DEL ARCHIVO .TXT
═══════════════════════════════════════════════════════════════

Cada línea es una fila. Cada celda está separada por espacios.

TIPOS DE CELDA:
─────────────────────────────────────────────────────────────
  X          Celda negra sin pistas (esquinas, bordes).

  O          Celda jugable (a rellenar por el solver).

  V\         Pista SOLO vertical: la columna de abajo suma V.
             Ejemplo:  16\   significa columna suma 16.

  \H         Pista SOLO horizontal: la fila a la derecha suma H.
             Ejemplo:  \7    significa fila suma 7.

  V\H        Pista VERTICAL y HORIZONTAL al mismo tiempo.
             Ejemplo:  16\7  significa columna=16 y fila=7.
─────────────────────────────────────────────────────────────

REGLA MNEMÓNICA:
  La barra \ divide los dos números como en el tablero visual:
    - Número ANTES de \  →  va hacia ABAJO  (vertical)
    - Número DESPUÉS de \ →  va hacia la DERECHA (horizontal)

═══════════════════════════════════════════════════════════════
EJEMPLO COMPLETO — Tablero 6x6
═══════════════════════════════════════════════════════════════

  X     16\    3\    X
  \7    O      O     X
  \9    O      O     X
  X     X      X     X

Interpretación:
  - Celda (0,1): pista vertical 16 → las celdas (1,1) y (2,1) suman 16.
  - Celda (0,2): pista vertical 3  → las celdas (1,2) y (2,2) suman 3.
  - Celda (1,0): pista horizontal 7 → las celdas (1,1) y (1,2) suman 7.
  - Celda (2,0): pista horizontal 9 → las celdas (2,1) y (2,2) suman 9.

═══════════════════════════════════════════════════════════════
EJEMPLO CON PISTA DOBLE
═══════════════════════════════════════════════════════════════

  X      X      16\3   X
  X      \23    O      O
  X      \14    O      O
  X      X      X      X

  Celda (0,2) tiene pista vertical=16 Y pista horizontal=3.

═══════════════════════════════════════════════════════════════
CONSEJOS PARA TRANSCRIBIR DESDE EL TABLERO
═══════════════════════════════════════════════════════════════

Al mirar una celda negra con diagonal en el tablero:
  - El número en la mitad SUPERIOR de la diagonal → escríbelo ANTES de \
  - El número en la mitad INFERIOR de la diagonal → escríbelo DESPUÉS de \
  - Si solo hay un número, fíjate en qué mitad está para saber si es V\ o \H
  - Si no hay número en alguna mitad, simplemente no lo escribas (V\ o \H)

Líneas que empiezan con # son comentarios y se ignoran.
"""

from typing import List
from KakuroBoard import KakuroBoard, Celda, Secuencia, TipoCelda


class FormatoInvalidoError(Exception):
    """Error lanzado cuando el archivo tiene formato incorrecto."""
    pass


class FileParser:
    """
    Parsea archivos .txt de Kakuro y construye un KakuroBoard.
    """

    @staticmethod
    def parsear(path: str) -> KakuroBoard:
        """
        Lee el archivo y construye el KakuroBoard completo.

        Args:
            path: Ruta al archivo .txt del tablero.

        Returns:
            KakuroBoard construido y listo para CSPModel.

        Raises:
            FormatoInvalidoError: Si el archivo tiene formato incorrecto.
            FileNotFoundError:    Si el archivo no existe.
        """
        lineas        = FileParser._leer_lineas(path)
        grilla_tokens = FileParser._tokenizar(lineas)

        n_filas = len(grilla_tokens)
        n_cols  = len(grilla_tokens[0])

        board = KakuroBoard(n_filas, n_cols)

        FileParser._construir_grilla(board, grilla_tokens)
        board.registrar_jugables()
        FileParser._extraer_secuencias_h(board)
        FileParser._extraer_secuencias_v(board)

        return board

    # ─────────────────────────────────────────────
    # LECTURA Y TOKENIZACIÓN
    # ─────────────────────────────────────────────

    @staticmethod
    def _leer_lineas(path: str) -> List[str]:
        """Lee el archivo filtrando comentarios y líneas vacías."""
        with open(path, "r", encoding="utf-8") as f:
            lineas = [
                linea.strip()
                for linea in f
                if linea.strip() and not linea.strip().startswith("#")
            ]
        if not lineas:
            raise FormatoInvalidoError("El archivo está vacío.")
        return lineas

    @staticmethod
    def _tokenizar(lineas: List[str]) -> List[List[str]]:
        """
        Divide cada línea en tokens y verifica consistencia de columnas.
        """
        grilla  = [linea.split() for linea in lineas]
        n_cols  = len(grilla[0])

        for i, fila in enumerate(grilla):
            if len(fila) != n_cols:
                raise FormatoInvalidoError(
                    f"Fila {i+1} tiene {len(fila)} columnas, "
                    f"se esperaban {n_cols}."
                )
        return grilla

    # ─────────────────────────────────────────────
    # PARSEO DE TOKENS
    # ─────────────────────────────────────────────

    @staticmethod
    def _parsear_token(token: str, fila: int, col: int) -> Celda:
        r"""
        Convierte un token de texto en un objeto Celda.

        TOKENS VÁLIDOS:
          X        →  Celda NEGRA
          O        →  Celda JUGABLE
          V\       →  Pista vertical V (solo hacia abajo)
          \\H      →  Pista horizontal H (solo hacia la derecha)
          V\\H     →  Pista vertical V y horizontal H

        La barra \\ separa vertical (antes) de horizontal (después).
        Si un lado está vacío, esa dirección no tiene pista.

        Args:
            token: String del token (ya en mayúsculas).
            fila:  Índice de fila (para mensajes de error).
            col:   Índice de columna (para mensajes de error).

        Returns:
            Objeto Celda correspondiente.

        Raises:
            FormatoInvalidoError: Si el token no es reconocible.
        """
        t = token.upper()

        # ── Celda negra ───────────────────────────────────────────
        if t == "X":
            return Celda(fila, col, TipoCelda.NEGRA)

        # ── Celda jugable ─────────────────────────────────────────
        if t == "O":
            return Celda(fila, col, TipoCelda.JUGABLE)

        # ── Celda con pista (contiene \) ──────────────────────────
        if "\\" in t:
            partes = t.split("\\")

            if len(partes) != 2:
                raise FormatoInvalidoError(
                    f"Token inválido en fila {fila+1}, col {col+1}: '{token}'.\n"
                    "  Formato esperado: 'V\\H', 'V\\' o '\\H'\n"
                    "  Ejemplos: '16\\3', '16\\', '\\7'"
                )

            str_v, str_h = partes

            # Parsear pista vertical (antes de \)
            pista_v = None
            if str_v:
                try:
                    pista_v = int(str_v)
                except ValueError:
                    raise FormatoInvalidoError(
                        f"Pista vertical no numérica en fila {fila+1}, "
                        f"col {col+1}: '{str_v}' en token '{token}'."
                    )

            # Parsear pista horizontal (después de \)
            pista_h = None
            if str_h:
                try:
                    pista_h = int(str_h)
                except ValueError:
                    raise FormatoInvalidoError(
                        f"Pista horizontal no numérica en fila {fila+1}, "
                        f"col {col+1}: '{str_h}' en token '{token}'."
                    )

            # Si no hay ninguna pista, es equivalente a negra.
            if pista_v is None and pista_h is None:
                return Celda(fila, col, TipoCelda.NEGRA)

            return Celda(fila, col, TipoCelda.PISTA, pista_h, pista_v)

        # ── Token desconocido ─────────────────────────────────────
        raise FormatoInvalidoError(
            f"Token desconocido en fila {fila+1}, col {col+1}: '{token}'.\n"
            "  Tokens válidos:\n"
            "    X      → celda negra\n"
            "    O      → celda jugable\n"
            "    16\\   → pista vertical 16\n"
            "    \\7    → pista horizontal 7\n"
            "    16\\7  → pista vertical 16 y horizontal 7"
        )

    # ─────────────────────────────────────────────
    # CONSTRUCCIÓN DE GRILLA
    # ─────────────────────────────────────────────

    @staticmethod
    def _construir_grilla(board: KakuroBoard, tokens: List[List[str]]) -> None:
        """Construye la grilla 2D de objetos Celda en el board."""
        for f, fila_tokens in enumerate(tokens):
            fila_celdas = []
            for c, token in enumerate(fila_tokens):
                celda = FileParser._parsear_token(token, f, c)
                fila_celdas.append(celda)
            board.grilla.append(fila_celdas)

    # ─────────────────────────────────────────────
    # EXTRACCIÓN DE SECUENCIAS
    # ─────────────────────────────────────────────

    @staticmethod
    def _extraer_secuencias_h(board: KakuroBoard) -> None:
        """
        Extrae secuencias horizontales.

        Busca celdas PISTA con pista_h definida y recolecta
        todas las celdas JUGABLE consecutivas a su derecha.
        """
        for f in range(board.filas):
            c = 0
            while c < board.cols:
                celda = board.grilla[f][c]

                if celda.tipo == TipoCelda.PISTA and celda.pista_h is not None:
                    jugables: List[str] = []
                    c += 1

                    while c < board.cols and \
                          board.grilla[f][c].tipo == TipoCelda.JUGABLE:
                        jugables.append(KakuroBoard.celda_id(f, c))
                        c += 1

                    if len(jugables) == 0:
                        raise FormatoInvalidoError(
                            f"Pista horizontal en fila {f+1}, col {celda.col+1} "
                            f"(suma {celda.pista_h}) no tiene celdas jugables a su derecha."
                        )

                    board.agregar_secuencia(
                        Secuencia(celda.pista_h, jugables, "H")
                    )
                else:
                    c += 1

    @staticmethod
    def _extraer_secuencias_v(board: KakuroBoard) -> None:
        """
        Extrae secuencias verticales.

        Busca celdas PISTA con pista_v definida y recolecta
        todas las celdas JUGABLE consecutivas hacia abajo.
        """
        for c in range(board.cols):
            f = 0
            while f < board.filas:
                celda = board.grilla[f][c]

                if celda.tipo == TipoCelda.PISTA and celda.pista_v is not None:
                    jugables: List[str] = []
                    f += 1

                    while f < board.filas and \
                          board.grilla[f][c].tipo == TipoCelda.JUGABLE:
                        jugables.append(KakuroBoard.celda_id(f, c))
                        f += 1

                    if len(jugables) == 0:
                        raise FormatoInvalidoError(
                            f"Pista vertical en fila {celda.fila+1}, col {c+1} "
                            f"(suma {celda.pista_v}) no tiene celdas jugables debajo."
                        )

                    board.agregar_secuencia(
                        Secuencia(celda.pista_v, jugables, "V")
                    )
                else:
                    f += 1
