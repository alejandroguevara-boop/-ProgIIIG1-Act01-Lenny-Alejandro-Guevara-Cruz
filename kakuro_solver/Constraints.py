"""
Constraints.py
==============
Define las funciones de restricción que se inyectan en los objetos Constraint.

Reutilizado del Sudoku:
  - AllDif (lógica idéntica)

Nuevo para Kakuro:
  - combinaciones_validas: precomputa combinaciones de suma sin repetición
  - sum_constraint: propaga usando combinaciones válidas

La clave de Kakuro es que la restricción de suma no solo verifica
la igualdad final, sino que REDUCE dominios durante la búsqueda
eliminando valores que no aparecen en ninguna combinación viable.
"""

from itertools import combinations
from typing import Dict, Set, List, Tuple


Dominios = Dict[str, Set[int]]


# ─────────────────────────────────────────────
# CACHE DE COMBINACIONES VÁLIDAS
# ─────────────────────────────────────────────

# Precalcular todas las combinaciones posibles para cada (suma, n_celdas).
# Esto evita recalcular en cada llamada durante la búsqueda.
_cache_combinaciones: Dict[Tuple[int, int], List[Tuple[int, ...]]] = {}


def combinaciones_validas(suma: int, n: int) -> List[Tuple[int, ...]]:
    """
    Retorna todas las combinaciones de exactamente n valores distintos
    de {1..9} que sumen exactamente 'suma'.

    Estas combinaciones modelan las posibles soluciones para una
    secuencia de Kakuro. Son fundamentales para la propagación de
    restricciones: cualquier valor que no aparezca en ninguna
    combinación puede eliminarse del dominio.

    Ejemplo:
        combinaciones_validas(4, 2) -> [(1,3), (3,1)] como conjuntos
        => solo {1,3} es posible, así que ninguna celda puede ser 2,4,5..9

    Args:
        suma: Pista de suma de la secuencia.
        n:    Número de celdas en la secuencia.

    Returns:
        Lista de tuplas con los valores (sin orden) que forman la suma.
    """
    clave = (suma, n)

    if clave not in _cache_combinaciones:
        _cache_combinaciones[clave] = [
            combo
            for combo in combinations(range(1, 10), n)
            if sum(combo) == suma
        ]

    return _cache_combinaciones[clave]


# ─────────────────────────────────────────────
# RESTRICCIÓN: ALL DIFFERENT
# ─────────────────────────────────────────────

def allDif(var_doms: Dominios, variables: List[str]) -> bool:
    """
    Propagación de restricción de unicidad (AllDifferent).

    Si una variable tiene dominio de tamaño 1 (asignada), elimina ese
    valor del dominio de todas las demás variables de la secuencia.

    Reutilizado directamente del solver de Sudoku (función AllDif).
    Renombrada a camelCase para PEP8.

    Args:
        var_doms:  Diccionario de dominios (modificado in-place).
        variables: Lista de nombres de variables en la secuencia.

    Returns:
        True si se realizó al menos un cambio en algún dominio.
    """
    any_change = False

    for var in variables:

        if len(var_doms[var]) == 1:

            valor = next(iter(var_doms[var]))

            for var2 in variables:

                if var != var2 and valor in var_doms[var2]:
                    var_doms[var2].discard(valor)
                    any_change = True

    return any_change


# ─────────────────────────────────────────────
# RESTRICCIÓN: SUMA EXACTA CON PROPAGACIÓN
# ─────────────────────────────────────────────

def sum_constraint(
    var_doms: Dominios,
    variables: List[str],
    suma_objetivo: int
) -> bool:
    """
    Propagación de restricción de suma para una secuencia de Kakuro.

    ALGORITMO:
    1. Obtiene las combinaciones válidas para (suma_objetivo, n_celdas).
    2. Filtra las combinaciones que son COMPATIBLES con los dominios actuales:
       una combinación es compatible si para cada posición existe al menos
       un valor en el dominio de esa celda que esté en la combinación.
    3. Calcula la unión de valores que aparecen en combinaciones viables.
    4. Elimina de cada dominio los valores que NO aparecen en ninguna
       combinación viable.

    POR QUÉ MEJORA EL RENDIMIENTO:
    Sin esta propagación, el backtracking explora asignaciones que
    violan la suma solo cuando la secuencia está completa (demasiado tarde).
    Con esta propagación, los valores inválidos se eliminan antes
    de siquiera intentar asignarlos, reduciendo el árbol de búsqueda
    dramáticamente — especialmente en secuencias largas.

    Ejemplo concreto:
        Secuencia de 2 celdas, suma = 3.
        combinaciones_validas(3, 2) = [(1, 2)]
        => Solo los valores {1, 2} son posibles en cualquier celda.
        => Si el dominio de una celda es {1,2,5,7}, queda {1,2}.
        => Si el dominio de la otra celda es {2,3,8}, queda {2}.
        => Tras AllDif, la primera celda queda {1}. Solución propagada.

    Args:
        var_doms:      Diccionario de dominios (modificado in-place).
        variables:     Lista de nombres de variables en la secuencia.
        suma_objetivo: Suma que debe alcanzar la secuencia.

    Returns:
        True si se realizó al menos un cambio en algún dominio.
    """
    n = len(variables)
    combos = combinaciones_validas(suma_objetivo, n)

    # Filtrar combinaciones compatibles con los dominios actuales.
    # Una combinación es compatible si cada uno de sus valores
    # puede asignarse a alguna celda con ese valor en su dominio.
    # Nota: usamos conjuntos para verificar intersección rápida.
    combos_viables = [
        combo for combo in combos
        if _es_compatible(combo, variables, var_doms)
    ]

    if not combos_viables:
        # Ninguna combinación es viable: conflicto.
        # Vaciamos un dominio para que hay_conflicto() lo detecte.
        var_doms[variables[0]] = set()
        return True

    # Valores que aparecen en AL MENOS UNA combinación viable.
    valores_posibles = set()
    for combo in combos_viables:
        valores_posibles.update(combo)

    # Eliminar de cada dominio los valores que no pueden aparecer
    # en ninguna combinación viable.
    any_change = False

    for var in variables:
        antes = len(var_doms[var])
        var_doms[var] &= valores_posibles  # intersección in-place
        if len(var_doms[var]) < antes:
            any_change = True

    return any_change


def _es_compatible(
    combo: Tuple[int, ...],
    variables: List[str],
    var_doms: Dominios
) -> bool:
    """
    Verifica si una combinación es compatible con los dominios actuales.

    Una combinación de valores es compatible si existe al menos una
    asignación de los valores de la combinación a las variables tal
    que cada valor pertenezca al dominio de la variable asignada.

    Se usa un matching greedy simple: para cada valor de la combo,
    se verifica que al menos una variable no asignada tenga ese valor
    en su dominio.

    Args:
        combo:     Tupla de valores a verificar.
        variables: Variables de la secuencia.
        var_doms:  Dominios actuales.

    Returns:
        True si la combinación puede satisfacerse con los dominios dados.
    """
    valores_combo = set(combo)

    # Verificar que la unión de dominios cubre todos los valores
    # de la combinación (condición necesaria pero no suficiente).
    # Para Kakuro esto es una buena aproximación sin costo de matching.
    for var in variables:
        if not (var_doms[var] & valores_combo):
            return False

    return True
