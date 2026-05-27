import itertools as it
from collections import defaultdict, deque


cols = "ABCDEFGHI"
rows = range(1, 10)

keys = list(it.product(range(1, 10), cols))
strKeys = [f"{key[1]}{key[0]}" for key in keys]

# dominios iniciales
var_doms = {key: set(range(1, 10)) for key in strKeys}

#---------------------------
# CARGAR TABLERO DESDE TXT:
def cargar_tablero(path):

    tablero = []

    with open(path, "r") as f:

        for line in f:

            line = line.strip()

            if line:
                tablero.append(line)

    if len(tablero) != 9:
        raise ValueError("El tablero debe tener 9 filas.")

    for i in range(9):

        if len(tablero[i]) != 9:
            raise ValueError("Cada fila debe tener 9 números.")

        for j in range(9):

            valor = tablero[i][j]

            celda = f"{cols[j]}{i+1}"

            # 0 significa vacío
            if valor != "0":

                numero = int(valor)

                if numero < 1 or numero > 9:
                    raise ValueError(f"Valor inválido en {celda}")

                var_doms[celda] = {numero}

    print("✅ Tablero cargado correctamente desde Sudoku.txt")


#---------------------------
# FUNCIONES DE CONSTRAINTS:

def DefRowsConstraints(cols, rows):
    return [[f"{id}{i}" for id in cols] for i in rows]


def DefColsConstraints(cols, rows):
    return [[f"{id}{i}" for i in rows] for id in cols]


def DefBoxesConstraints(cols, rows):

    boxes = []

    for i in range(3):
        for j in range(3):

            group = [
                f"{cols[i*3 + x]}{rows[j*3 + y]}"
                for x in range(3)
                for y in range(3)
            ]

            boxes.append(group)

    return boxes


#---------------------------
# REGLA ALL DIFFERENT:

def AllDif(var_doms, vars):

    anyChange = False

    for var in vars:

        if len(var_doms[var]) == 1:

            valor = list(var_doms[var])[0]

            for var2 in vars:

                if var != var2 and valor in var_doms[var2]:

                    var_doms[var2].discard(valor)

                    anyChange = True

                    print(f"   -> Eliminando {valor} de {var2}")

    return anyChange


#---------------------------
# DEFINIR GRUPOS:

varsGroups = (
    DefRowsConstraints(cols, rows)
    + DefColsConstraints(cols, rows)
    + DefBoxesConstraints(cols, rows)
)


#---------------------------
# CONSTRUCCIÓN DE CONSTRAINTS:

class Constraint:

    def __init__(self, name, vars, func):

        self.name = name
        self.vars = list(vars)
        self.func = func

    def apply(self, var_doms):

        # print(f"\nAplicando restricción: {self.name}")

        return self.func(var_doms, self.vars)


constraints = []

for i, group in enumerate(varsGroups):

    constraints.append(
        Constraint(
            f"AllDif_{i}",
            group,
            AllDif
        )
    )


#---------------------------
# MAPEO DE RESTRICCIONES:

var_to_constraints = defaultdict(list)

for cons in constraints:
    for v in cons.vars:
        var_to_constraints[v].append(cons)


# vecinos
neighbours = {v: set() for v in var_doms}

for cons in constraints:

    for v in cons.vars:

        neighbours[v].update(
            [u for u in cons.vars if u != v]
        )


#---------------------------
# FUNCIONES AUXILIARES:

def esta_completo(var_doms):

    return all(len(var_doms[v]) == 1 for v in var_doms)


def hay_conflicto(var_doms):

    return any(len(var_doms[v]) == 0 for v in var_doms)


def copiar_estado(var_doms):

    return {k: set(v) for k, v in var_doms.items()}


def elegir_variable(var_doms):

    sin_asignar = [
        v for v in var_doms
        if len(var_doms[v]) > 1
    ]

    if not sin_asignar:
        return None

    # MRV
    mrv = min(sin_asignar, key=lambda v: len(var_doms[v]))

    # desempate degree heuristic
    candidates = [
        v for v in sin_asignar
        if len(var_doms[v]) == len(var_doms[mrv])
    ]

    best = max(
        candidates,
        key=lambda v:
        sum(
            1 for nb in neighbours[v]
            if len(var_doms[nb]) > 1
        )
    )

    return best


#---------------------------
# PROPAGACIÓN DE RESTRICCIONES:

def aplicar_restricciones(var_doms, constraints, var_to_constraints):

    queue = deque(constraints)

    while queue:

        cons = queue.popleft()

        changed = cons.apply(var_doms)

        if changed:

            if hay_conflicto(var_doms):
                return var_doms

            for v in cons.vars:

                for neigh_cons in var_to_constraints[v]:

                    if neigh_cons is not cons:
                        queue.append(neigh_cons)

    return var_doms


#---------------------------
# BACKTRACKING:

def backtracking(var_doms, constraints, var_to_constraints):

    var_doms = aplicar_restricciones(
        var_doms,
        constraints,
        var_to_constraints
    )

    if esta_completo(var_doms):

        print("\n✅ SOLUCIÓN ENCONTRADA\n")

        return var_doms

    if hay_conflicto(var_doms):

        print("\n❌ Conflicto detectado. Backtracking...\n")

        return None

    var = elegir_variable(var_doms)

    print(f"\n📌 Variable elegida: {var}")
    print(f"   Dominio actual: {var_doms[var]}")

    for valor in list(var_doms[var]):

        print(f"\n➡️ Intentando {var} = {valor}")

        nuevo_estado = copiar_estado(var_doms)

        nuevo_estado[var] = {valor}

        resultado = backtracking(
            nuevo_estado,
            constraints,
            var_to_constraints
        )

        if resultado is not None:
            return resultado

    print(f"\n↩️ Retrocediendo en variable {var}")

    return None


#---------------------------
# IMPRIMIR TABLERO:

def mostrar_tablero(var_doms):

    print("\nTABLERO RESUELTO:\n")

    for r in range(1, 10):

        fila = ""

        for c in cols:

            val = var_doms[f"{c}{r}"]

            if len(val) == 1:
                fila += str(list(val)[0]) + " "
            else:
                fila += ". "

            if c in "CF":
                fila += "| "

        print(fila)

        if r in (3, 6):
            print("- " * 11)

    print()


# ---------------------------
# EJECUCIÓN PRINCIPAL:

print("\n===================================")
print("     RESOLVER SUDOKU CSP")
print("===================================\n")

# cargar tablero
cargar_tablero("Sudoku.txt")

print("\n🔍 Ejecutando solver...\n")

solucion = backtracking(
    var_doms,
    constraints,
    var_to_constraints
)

if solucion:

    print("✅ Sudoku resuelto correctamente")

    mostrar_tablero(solucion)

else:

    print("❌ El Sudoku no tiene solución")