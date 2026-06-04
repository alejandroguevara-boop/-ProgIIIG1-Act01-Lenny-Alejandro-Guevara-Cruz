"""
Heuristics.py
=============
Heurísticas de selección de variable para el backtracking.

Reutilizadas y desacopladas del solver de Sudoku:
  - MRV (Minimum Remaining Values)
  - Degree Heuristic (desempate)

En Sudoku estas funciones estaban mezcladas en el archivo principal.
Aquí se aíslan para mayor claridad y testabilidad.

La combinación MRV + Degree es una estrategia clásica en CSP que
reduce significativamente el tamaño del árbol de búsqueda.
"""

from typing import Dict, List, Optional, Set


Dominios = Dict[str, Set[int]]
Vecinos  = Dict[str, Set[str]]


def elegir_variable(
    var_doms: Dominios,
    neighbours: Vecinos
) -> Optional[str]:
    """
    Selecciona la próxima variable a asignar usando MRV + Degree.

    ESTRATEGIA MRV (Minimum Remaining Values):
        Elige la variable con el menor número de valores posibles
        en su dominio. Intuitivamente: atacar primero las celdas
        más restringidas reduce el factor de ramificación.

    DESEMPATE: DEGREE HEURISTIC:
        Entre las variables con igual MRV, elige la que tiene más
        vecinos no asignados. Esto maximiza el impacto de la
        asignación sobre las restricciones futuras.

    Reutilizado del solver de Sudoku (función elegir_variable).
    Desacoplado: recibe neighbours como parámetro en lugar de
    usar una variable global.

    Args:
        var_doms:   Diccionario variable -> dominio actual.
        neighbours: Grafo de vecinos (variable -> set de vecinos).

    Returns:
        Nombre de la variable seleccionada, o None si todas
        las variables están asignadas (dominio de tamaño 1).
    """
    # Variables no asignadas: dominio de tamaño > 1.
    sin_asignar: List[str] = [
        v for v in var_doms
        if len(var_doms[v]) > 1
    ]

    if not sin_asignar:
        return None

    # ── MRV: variable con menor dominio ──────────────────────────
    min_dom = min(len(var_doms[v]) for v in sin_asignar)

    candidatos = [
        v for v in sin_asignar
        if len(var_doms[v]) == min_dom
    ]

    if len(candidatos) == 1:
        return candidatos[0]

    # ── Degree Heuristic: más vecinos no asignados ────────────────
    mejor = max(
        candidatos,
        key=lambda v: sum(
            1 for nb in neighbours[v]
            if len(var_doms[nb]) > 1
        )
    )

    return mejor
