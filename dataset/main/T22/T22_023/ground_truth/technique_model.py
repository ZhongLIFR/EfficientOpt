from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    limits = instance["limits"]
    product_count = len(instance["profit"])
    gamma = float(instance["uncertainty_budget"])
    rhs = instance["limit_value"]
    max_support = max(len(record["support"]) for record in limits)
    model = gp.Model("robust_compact_counterpart")
    production = model.addVars(product_count, lb=0.0, name="production_level")
    budget_price = model.addVars(len(limits), lb=0.0, name="budget_price")
    deviation_price = model.addVars(len(limits), max_support, lb=0.0, name="deviation_price")
    for k, record in enumerate(limits):
        support = record["support"]
        nominal = record["nominal"]
        deviation = record["deviation"]
        model.addConstr(
            gp.quicksum(nominal[i] * production[support[i]] for i in range(len(support)))
            + gamma * budget_price[k]
            + gp.quicksum(deviation_price[k, i] for i in range(len(support)))
            <= rhs[k],
            name=f"robust_{k}",
        )
        for i in range(len(support)):
            model.addConstr(
                budget_price[k] + deviation_price[k, i] >= deviation[i] * production[support[i]],
                name=f"price_{k}_{i}",
            )
    model.setObjective(gp.quicksum(instance["profit"][j] * production[j] for j in range(product_count)), GRB.MAXIMIZE)
    return model
