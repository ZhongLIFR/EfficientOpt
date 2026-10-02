from __future__ import annotations

from itertools import combinations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    limits = instance["limits"]
    product_count = len(instance["profit"])
    gamma = int(instance["uncertainty_budget"])
    rhs = instance["limit_value"]
    model = gp.Model("robust_scenario_enumeration")
    production = model.addVars(product_count, lb=0.0, name="production_level")
    for k, record in enumerate(limits):
        support = record["support"]
        nominal = record["nominal"]
        deviation = record["deviation"]
        size = len(support)
        for cardinality in range(min(gamma, size) + 1):
            for subset in combinations(range(size), cardinality):
                adverse = set(subset)
                model.addConstr(
                    gp.quicksum(
                        (nominal[i] + (deviation[i] if i in adverse else 0.0)) * production[support[i]]
                        for i in range(size)
                    ) <= rhs[k]
                )
    model.setObjective(gp.quicksum(instance["profit"][j] * production[j] for j in range(product_count)), GRB.MAXIMIZE)
    return model
