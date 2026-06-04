"""
Utils.py
========
Funciones auxiliares puras sin dependencias externas.

Reutilizadas directamente del solver de Sudoku:
  - esta_completo
  - hay_conflicto
  - copiar_estado

Se separaron del archivo monolítico para permitir
importación limpia en cualquier módulo.
"""

from typing import Dict, Set


# Tipo alias para dominios (reutilizado en todos los módulos)
Dominios = Dict[str, Set[int]]


def esta_completo(var_doms: Dominios) -> bool:
    """
    Verifica si todas las variables tienen exactamente un valor asignado.

    Una variable está 'asignada' cuando su dominio tiene exactamente 1 elemento.
    Esta función es idéntica a la del solver de Sudoku.

    Args:
        var_doms: Diccionario variable -> conjunto de valores posibles.

    Returns:
        True si cada variable tiene dominio de tamaño 1.
    """
    return all(len(var_doms[v]) == 1 for v in var_doms)


def hay_conflicto(var_doms: Dominios) -> bool:
    """
    Detecta si alguna variable tiene dominio vacío (conflicto).

    Un dominio vacío significa que no hay ningún valor válido para
    esa variable: la rama actual del árbol de búsqueda es inviable.
    Esta función es idéntica a la del solver de Sudoku.

    Args:
        var_doms: Diccionario variable -> conjunto de valores posibles.

    Returns:
        True si alguna variable tiene dominio vacío.
    """
    return any(len(var_doms[v]) == 0 for v in var_doms)


def copiar_estado(var_doms: Dominios) -> Dominios:
    """
    Crea una copia profunda del diccionario de dominios.

    Necesario para el backtracking: cada rama del árbol de búsqueda
    debe trabajar sobre su propio estado sin modificar el del padre.
    Esta función es idéntica a la del solver de Sudoku.

    Args:
        var_doms: Diccionario variable -> conjunto de valores posibles.

    Returns:
        Nueva copia del diccionario con conjuntos independientes.
    """
    return {k: set(v) for k, v in var_doms.items()}
