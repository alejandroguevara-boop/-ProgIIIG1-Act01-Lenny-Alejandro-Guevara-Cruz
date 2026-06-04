"""
CSPModel.py
===========
Construye el modelo CSP completo a partir de un KakuroBoard.

Responsabilidades:
  - Crear variables (una por celda jugable).
  - Inicializar dominios {1..9} y reducirlos con combinaciones de suma.
  - Crear objetos Constraint para AllDif y SumConstraint por secuencia.
  - Construir el mapa var_to_constraints (variable -> lista de constraints).
  - Construir el grafo de vecinos (variable -> set de variables en misma secuencia).

Relación con el Sudoku:
  - La clase Constraint es idéntica a la del Sudoku.
  - La construcción del mapa var_to_constraints y neighbours es idéntica.
  - La diferencia está en CÓMO se generan los grupos y las funciones de restricción.
"""

from collections import defaultdict
from functools import partial
from typing import Callable, Dict, List, Set

from Constraints import allDif, combinaciones_validas, sum_constraint
from KakuroBoard import KakuroBoard, Secuencia


Dominios = Dict[str, Set[int]]


# ─────────────────────────────────────────────
# CLASE CONSTRAINT
# ─────────────────────────────────────────────

class Constraint:
    """
    Restricción CSP genérica.

    Reutilizada del solver de Sudoku con mínimas modificaciones:
      - Se agrega el atributo 'variables' como alias de 'vars'
        para claridad semántica.
      - La función puede recibir parámetros adicionales vía partial().

    Attributes:
        nombre:    Nombre descriptivo de la restricción.
        variables: Lista de variables afectadas.
        func:      Función de propagación (var_doms, variables) -> bool.
    """

    def __init__(
        self,
        nombre: str,
        variables: List[str],
        func: Callable[[Dominios, List[str]], bool]
    ):
        self.nombre    = nombre
        self.variables = list(variables)
        self.func      = func

    def aplicar(self, var_doms: Dominios) -> bool:
        """
        Ejecuta la función de propagación sobre los dominios.

        Args:
            var_doms: Dominios actuales (modificados in-place).

        Returns:
            True si algún dominio cambió.
        """
        return self.func(var_doms, self.variables)


# ─────────────────────────────────────────────
# MODELO CSP
# ─────────────────────────────────────────────

class CSPModel:
    """
    Modelo CSP completo para un tablero de Kakuro.

    Attributes:
        var_doms:           Dominios de todas las variables.
        constraints:        Lista de todos los objetos Constraint.
        var_to_constraints: Mapa variable -> lista de constraints que la involucran.
        neighbours:         Grafo de vecinos (variable -> set de variables relacionadas).
    """

    def __init__(self, board: KakuroBoard):
        """
        Construye el modelo CSP a partir de un KakuroBoard.

        Args:
            board: Tablero de Kakuro parseado por FileParser.
        """
        # 1. Inicializar dominios con {1..9} para cada celda jugable.
        self.var_doms: Dominios = {
            cid: set(range(1, 10))
            for cid in board.jugables
        }

        self.constraints: List[Constraint] = []

        # 2. Por cada secuencia, crear restricciones AllDif + SumConstraint.
        for seq in board.secuencias:
            self._agregar_restricciones_secuencia(seq)

        # 3. Construir mapa variable -> constraints que la involucran.
        self.var_to_constraints: Dict[str, List[Constraint]] = defaultdict(list)
        for cons in self.constraints:
            for v in cons.variables:
                self.var_to_constraints[v].append(cons)

        # 4. Construir grafo de vecinos.
        self.neighbours: Dict[str, Set[str]] = {
            v: set() for v in self.var_doms
        }
        for cons in self.constraints:
            for v in cons.variables:
                self.neighbours[v].update(
                    u for u in cons.variables if u != v
                )

        # 5. Preprocesamiento: reducir dominios con combinaciones de suma.
        self._preprocesar_dominios(board)

    # ─────────────────────────────────────────────
    # MÉTODOS PRIVADOS
    # ─────────────────────────────────────────────

    def _agregar_restricciones_secuencia(self, seq: Secuencia) -> None:
        """
        Crea y registra las restricciones AllDif y SumConstraint
        para una secuencia dada.

        Se usan dos restricciones separadas por secuencia:
          1. AllDif: todos los valores deben ser distintos.
          2. SumConstraint: los valores deben sumar exactamente seq.suma.

        La SumConstraint se crea con partial() para inyectar suma_objetivo
        en la firma de sum_constraint(var_doms, variables, suma_objetivo).

        Args:
            seq: Secuencia con suma objetivo y lista de celdas.
        """
        etiqueta = f"{seq.direccion}_suma{seq.suma}_{seq.celdas[0]}"

        # Restricción de unicidad (AllDifferent).
        self.constraints.append(
            Constraint(
                nombre    = f"AllDif_{etiqueta}",
                variables = seq.celdas,
                func      = allDif
            )
        )

        # Restricción de suma exacta con propagación por combinaciones.
        # Usamos partial para fijar suma_objetivo en la función.
        func_suma = partial(sum_constraint, suma_objetivo=seq.suma)
        self.constraints.append(
            Constraint(
                nombre    = f"Sum_{etiqueta}",
                variables = seq.celdas,
                func      = func_suma
            )
        )

    def _preprocesar_dominios(self, board: KakuroBoard) -> None:
        """
        Reducción inicial de dominios antes de la búsqueda.

        Para cada secuencia, calcula los valores que aparecen en AL MENOS
        UNA combinación válida y los intersecta con el dominio actual.

        Esta es la propagación más potente en Kakuro: en muchos tableros
        elimina el 50-80% de los valores imposibles antes de hacer
        ninguna asignación. Tableros 'muy difíciles' se benefician
        especialmente porque las secuencias largas tienen pocas combinaciones.

        Ejemplo:
            Secuencia de 2 celdas, suma = 17.
            combinaciones_validas(17, 2) = [(8,9), (9,8)] -> valores {8, 9}
            => Ambas celdas solo pueden ser 8 o 9.
            => Dominio de {1..9} se reduce a {8, 9} antes de buscar.

        Args:
            board: Tablero con las secuencias definidas.
        """
        for seq in board.secuencias:
            combos = combinaciones_validas(seq.suma, len(seq.celdas))

            if not combos:
                # Secuencia imposible: el tablero no tiene solución.
                # Vaciamos el dominio de la primera celda para que
                # el solver lo detecte en hay_conflicto().
                if seq.celdas:
                    self.var_doms[seq.celdas[0]] = set()
                continue

            # Unión de todos los valores que aparecen en alguna combinación.
            valores_posibles: Set[int] = set()
            for combo in combos:
                valores_posibles.update(combo)

            # Intersectar con el dominio actual de cada celda.
            for cid in seq.celdas:
                self.var_doms[cid] &= valores_posibles
