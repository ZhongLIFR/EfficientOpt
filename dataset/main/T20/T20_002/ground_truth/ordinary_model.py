"""Reference fixed-runner builder for T20 inventory recurrences."""

from __future__ import annotations

import gurobipy as gp


def build_model(instance):
    demand = [float(v) for v in instance["demand"]]
    capacity = [float(v) for v in instance["capacity"]]
    costs = [float(v) for v in instance["production_cost"]]
    holding = float(instance["holding_cost"])
    n = len(demand)
    if len(capacity) != n or len(costs) != n:
        raise ValueError("period arrays must have equal length")
    model = gp.Model("t20_inventory_reference")
    produce = model.addVars(n, lb=0.0, ub=capacity, name="produce")
    stock = model.addVars(n, lb=0.0, name="stock")
    objective = gp.LinExpr()
    for t in range(n):
        previous = stock[t - 1] if t else 0.0
        model.addConstr(previous + produce[t] == demand[t] + stock[t], name=f"balance[{t}]")
        objective += costs[t] * produce[t] + holding * stock[t]
    model.setObjective(objective, gp.GRB.MINIMIZE)
    return model
