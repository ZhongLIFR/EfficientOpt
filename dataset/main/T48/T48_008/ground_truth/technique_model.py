import gurobipy as gp
from gurobipy import GRB


def _arcs(instance):
    n = int(instance["node_count"])
    cost = instance["cost"]
    forbidden = {(int(i), int(j)) for i, j in instance.get("forbidden_arcs", [])}
    arcs = {
        (i, j): float(cost[i][j])
        for i in range(n)
        for j in range(n)
        if i != j and (i, j) not in forbidden
    }
    return n, arcs


def build_model(instance):
    """Directed-tour formulation with single-commodity-flow connectivity."""
    n, arcs = _arcs(instance)
    model = gp.Model("t48_09_scf")
    x = model.addVars(arcs.keys(), vtype=GRB.BINARY, name="x")
    flow = model.addVars(arcs.keys(), lb=0.0, ub=n - 1, name="flow")
    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if (i, j) in arcs) == 1)
        model.addConstr(gp.quicksum(x[j, i] for j in range(n) if (j, i) in arcs) == 1)
    for i, j in arcs:
        model.addConstr(flow[i, j] <= (n - 1) * x[i, j])
    for city in range(1, n):
        model.addConstr(
            gp.quicksum(flow[i, city] for i in range(n) if (i, city) in arcs)
            - gp.quicksum(flow[city, j] for j in range(n) if (city, j) in arcs)
            == 1
        )
    model.setObjective(gp.quicksum(arcs[i, j] * x[i, j] for i, j in arcs), GRB.MINIMIZE)
    return model
