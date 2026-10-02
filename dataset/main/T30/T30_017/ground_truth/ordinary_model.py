from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    model = gp.Model("regional_tsp_ordinary")
    objective = gp.LinExpr()
    for r, region in enumerate(instance["regions"]):
        n = len(region["sites"])
        costs = region["travel_cost"]
        arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
        travel = model.addVars(arcs, vtype=GRB.BINARY, name=f"travel_{r}")
        order = model.addVars(range(1, n), lb=1, ub=n - 1, name=f"visit_order_{r}")
        model.addConstrs((gp.quicksum(travel[i, j] for j in range(n) if j != i) == 1 for i in range(n)), name=f"depart_once_{r}")
        model.addConstrs((gp.quicksum(travel[j, i] for j in range(n) if j != i) == 1 for i in range(n)), name=f"arrive_once_{r}")
        model.addConstrs((order[i] - order[j] + n * travel[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j), name=f"order_link_{r}")
        objective += gp.quicksum(costs[i][j] * travel[i, j] for i, j in arcs)
    model.setObjective(objective, GRB.MINIMIZE)
    return model
