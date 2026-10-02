from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    n = len(instance["sites"])
    costs = instance["travel_cost"]
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
    model = gp.Model("tsp_ordinary")
    travel = model.addVars(arcs, vtype=GRB.BINARY, name="travel")
    order = model.addVars(range(1, n), lb=1, ub=n - 1, name="visit_order")
    model.addConstrs((gp.quicksum(travel[i, j] for j in range(n) if j != i) == 1 for i in range(n)), name="depart_once")
    model.addConstrs((gp.quicksum(travel[j, i] for j in range(n) if j != i) == 1 for i in range(n)), name="arrive_once")
    model.addConstrs((order[i] - order[j] + n * travel[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j), name="order_link")
    model.setObjective(gp.quicksum(costs[i][j] * travel[i, j] for i, j in arcs), GRB.MINIMIZE)
    return model
