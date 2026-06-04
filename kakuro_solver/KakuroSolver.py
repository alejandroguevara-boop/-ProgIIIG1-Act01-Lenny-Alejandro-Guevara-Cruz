"""
KakuroSolver.py
===============
Motor principal del solver de Kakuro.

Orquesta:
  1. Propagación de restricciones (AC-3 like, reutilizado del Sudoku).
  2. Backtracking cronológico con Forward Checking.
  3. Selección de variable por MRV + Degree.
  4. Extracción y display de la solución.

La lógica de propagar_restricciones y backtracking es directamente
derivada del solver de Sudoku, adaptada para:
  - Recibir parámetros en lugar de usar estado global.
  - Usar deque con deduplicación para evitar re-encolado innecesario.
  - Mostrar estadísticas de ejecución.
"""

import time
from collections import deque
from typing import Dict, List, Optional, Set

from CSPModel import Constraint, CSPModel
from Heuristics import elegir_variable
from KakuroBoard import KakuroBoard
from Utils import copiar_estado, esta_completo, hay_conflicto


Dominios = Dict[str, Set[int]]


# ─────────────────────────────────────────────
# PROPAGACIÓN DE RESTRICCIONES
# ─────────────────────────────────────────────

def propagar_restricciones(
    var_doms:           Dominios,
    constraints:        List[Constraint],
    var_to_constraints: Dict[str, List[Constraint]]
) -> Dominios:
    """
    Propaga restricciones mediante una cola (estilo AC-3).

    Algoritmo (reutilizado del Sudoku con mejora de deduplicación):
      1. Inicializar la cola con todas las constraints.
      2. Sacar una constraint de la cola y aplicarla.
      3. Si el dominio de alguna variable cambió:
           a. Verificar conflicto (dominio vacío).
           b. Encolar las constraints vecinas que aún no están en cola.
      4. Repetir hasta que la cola esté vacía.

    Mejora respecto al Sudoku original:
      - Se usa un set 'en_cola' para evitar encolar la misma constraint
        múltiples veces, reduciendo trabajo redundante.

    Args:
        var_doms:           Dominios actuales (modificados in-place).
        constraints:        Lista de todos los objetos Constraint.
        var_to_constraints: Mapa variable -> constraints que la involucran.

    Returns:
        var_doms modificados (el mismo objeto, in-place).
    """
    cola:    deque   = deque(constraints)
    en_cola: set     = set(id(c) for c in constraints)

    while cola:
        cons = cola.popleft()
        en_cola.discard(id(cons))

        cambio = cons.aplicar(var_doms)

        if cambio:
            if hay_conflicto(var_doms):
                return var_doms  # Conflicto detectado: salir rápido.

            # Encolar constraints vecinas no presentes aún en la cola.
            for v in cons.variables:
                for cons_vecina in var_to_constraints[v]:
                    if id(cons_vecina) not in en_cola:
                        cola.append(cons_vecina)
                        en_cola.add(id(cons_vecina))

    return var_doms


# ─────────────────────────────────────────────
# BACKTRACKING CON FORWARD CHECKING
# ─────────────────────────────────────────────

def backtracking(
    var_doms:           Dominios,
    constraints:        List[Constraint],
    var_to_constraints: Dict[str, List[Constraint]],
    neighbours:         Dict[str, Set[str]],
    stats:              Dict
) -> Optional[Dominios]:
    """
    Backtracking cronológico con propagación y Forward Checking.

    Algoritmo (directamente derivado del solver de Sudoku):
      1. Propagar restricciones sobre el estado actual.
      2. Si completo -> retornar solución.
      3. Si conflicto -> retornar None (backtrack).
      4. Elegir variable con MRV + Degree.
      5. Para cada valor en su dominio:
           a. Crear copia del estado.
           b. Asignar el valor (dominio = {valor}).
           c. Forward Checking: propagar solo las constraints de esta variable.
           d. Si no hay conflicto -> llamar recursivamente.
           e. Si recursión exitosa -> retornar resultado.
      6. Si ningún valor funcionó -> retornar None (backtrack).

    Forward Checking (mejora sobre el Sudoku original):
      Después de asignar un valor, propagar SOLO las constraints
      que involucran la variable asignada antes de la recursión completa.
      Esto detecta conflictos locales más rápido.

    Args:
        var_doms:           Dominios del estado actual.
        constraints:        Lista completa de constraints.
        var_to_constraints: Mapa variable -> constraints.
        neighbours:         Grafo de vecinos.
        stats:              Diccionario para conteo de nodos y backtracks.

    Returns:
        Dominios con la solución, o None si no hay solución en esta rama.
    """
    # Paso 1: Propagar restricciones globalmente.
    var_doms = propagar_restricciones(var_doms, constraints, var_to_constraints)

    # Paso 2: Verificar completitud.
    if esta_completo(var_doms):
        return var_doms

    # Paso 3: Verificar conflicto.
    if hay_conflicto(var_doms):
        stats["backtracks"] += 1
        return None

    # Paso 4: Elegir variable (MRV + Degree).
    var = elegir_variable(var_doms, neighbours)
    if var is None:
        return var_doms

    stats["nodos"] += 1

    # Paso 5: Probar cada valor del dominio.
    for valor in sorted(var_doms[var]):  # sorted para determinismo

        nuevo_estado = copiar_estado(var_doms)
        nuevo_estado[var] = {valor}

        # Forward Checking: propagar solo constraints locales.
        cons_locales = var_to_constraints[var]
        propagar_restricciones(nuevo_estado, cons_locales, var_to_constraints)

        if hay_conflicto(nuevo_estado):
            stats["backtracks"] += 1
            continue  # Valor inválido: probar siguiente.

        # Llamada recursiva.
        resultado = backtracking(
            nuevo_estado,
            constraints,
            var_to_constraints,
            neighbours,
            stats
        )

        if resultado is not None:
            return resultado

    # Paso 6: Ningún valor funcionó -> backtrack.
    stats["backtracks"] += 1
    return None


# ─────────────────────────────────────────────
# EXTRACCIÓN DE SOLUCIÓN
# ─────────────────────────────────────────────

def extraer_solucion(var_doms: Dominios) -> Dict[str, int]:
    """
    Convierte dominios singleton a un diccionario de solución.

    Args:
        var_doms: Dominios con exactamente un valor por variable.

    Returns:
        Diccionario variable -> valor asignado.
    """
    return {v: next(iter(dom)) for v, dom in var_doms.items()}


# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL DE RESOLUCIÓN
# ─────────────────────────────────────────────

def resolver(board: KakuroBoard, verbose: bool = True) -> Optional[Dict[str, int]]:
    """
    Función principal: construye el CSP y ejecuta el solver.

    Args:
        board:   Tablero de Kakuro parseado.
        verbose: Si True, muestra progreso y estadísticas.

    Returns:
        Diccionario con la solución, o None si no tiene solución.
    """
    if verbose:
        print("\n🔧 Construyendo modelo CSP...")

    modelo = CSPModel(board)

    if verbose:
        print(f"   Variables:    {len(modelo.var_doms)}")
        print(f"   Constraints:  {len(modelo.constraints)}")
        print(f"   Secuencias:   {len(board.secuencias)}")
        _mostrar_dominios_iniciales(modelo.var_doms)

    stats = {"nodos": 0, "backtracks": 0}

    if verbose:
        print("\n🔍 Ejecutando solver...\n")

    t_inicio = time.time()

    resultado = backtracking(
        var_doms           = modelo.var_doms,
        constraints        = modelo.constraints,
        var_to_constraints = modelo.var_to_constraints,
        neighbours         = modelo.neighbours,
        stats              = stats
    )

    t_fin = time.time()

    if verbose:
        print(f"\n⏱  Tiempo: {t_fin - t_inicio:.4f}s")
        print(f"   Nodos explorados: {stats['nodos']}")
        print(f"   Backtracks:       {stats['backtracks']}")

    if resultado is None:
        if verbose:
            print("\n❌ El tablero no tiene solución.")
        return None

    if verbose:
        print("\n✅ SOLUCIÓN ENCONTRADA\n")

    return extraer_solucion(resultado)


def _mostrar_dominios_iniciales(var_doms: Dominios) -> None:
    """Muestra el tamaño promedio de dominios tras preprocesamiento."""
    total = sum(len(d) for d in var_doms.values())
    promedio = total / len(var_doms) if var_doms else 0
    print(f"   Tamaño promedio de dominio tras preprocesamiento: {promedio:.2f}/9")
