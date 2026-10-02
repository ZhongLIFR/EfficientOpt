import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T48_04 ordinary: MTZ subtour elimination + forbidden arcs."""
    n = instance["node_count"]
    cost = instance["cost"]
    forbidden = {tuple(a) for a in instance["forbidden_arcs"]}
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j and (i, j) not in forbidden]
    m = gp.Model("t48_04_ordinary_mtz")
    x = m.addVars(arcs, vtype=GRB.BINARY, name="x")
    u = m.addVars(range(1, n), lb=1, ub=n - 1, name="u")
    m.addConstrs((quicksum(x[i, j] for j in range(n) if (i, j) in arcs) == 1 for i in range(n)), name="out")
    m.addConstrs((quicksum(x[i, j] for i in range(n) if (i, j) in arcs) == 1 for j in range(n)), name="in")
    m.addConstrs(
        (u[i] - u[j] + n * x[i, j] <= n - 1 for (i, j) in arcs if i != 0 and j != 0),
        name="mtz",
    )
    m.setObjective(quicksum(cost[i][j] * x[i, j] for (i, j) in arcs), GRB.MINIMIZE)
    return m
