import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T18_20 ordinary (naive): MTZ subtour elimination (TSP)."""
    n = instance["city_count"]
    dist = instance["distances"]
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    m = gp.Model("t18_20_tsp_mtz")
    x = m.addVars(arcs, vtype=GRB.BINARY, name="x")
    u = m.addVars(range(1, n), lb=1, ub=n - 1, name="order")
    m.addConstrs((quicksum(x[i, j] for j in range(n) if i != j) == 1 for i in range(n)), name="out")
    m.addConstrs((quicksum(x[i, j] for i in range(n) if i != j) == 1 for j in range(n)), name="in")
    m.addConstrs(
        (u[i] - u[j] + n * x[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j),
        name="mtz",
    )
    m.setObjective(quicksum(dist[i][j] * x[i, j] for (i, j) in arcs), GRB.MINIMIZE)
    return m
