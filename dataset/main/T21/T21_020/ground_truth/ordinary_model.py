from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    n = int(instance["node_count"])
    costs = instance["cost"]
    nodes = range(n)
    arcs = [(i, j) for i in nodes for j in nodes if i != j]

    model = gp.Model("directed_tsp_mtz")
    travel = model.addVars(arcs, vtype=GRB.BINARY, name="travel")
    order = model.addVars(range(1, n), lb=0.0, ub=n - 1, name="order")
    model.addConstrs(
        (gp.quicksum(travel[i, j] for j in nodes if j != i) == 1 for i in nodes),
        name="out_degree",
    )
    model.addConstrs(
        (gp.quicksum(travel[j, i] for j in nodes if j != i) == 1 for i in nodes),
        name="in_degree",
    )
    model.addConstrs(
        (order[i] - order[j] + (n - 1) * travel[i, j] <= n - 2
         for i in range(1, n) for j in range(1, n) if i != j),
        name="mtz",
    )
    model.setObjective(
        gp.quicksum(float(costs[i][j]) * travel[i, j] for i, j in arcs),
        GRB.MINIMIZE,
    )
    return model
