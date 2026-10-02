from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """Primal minimax absolute-deviation linear regression model."""
    rows = instance["observations"]
    p = len(rows[0]["features"])

    model = gp.Model("t12_002_linf_primal")
    beta = model.addVars(p, lb=-GRB.INFINITY, name="coefficient")
    peak = model.addVar(lb=0.0, name="maximum_deviation")

    for i, row in enumerate(rows):
        prediction = gp.quicksum(
            float(row["features"][j]) * beta[j] for j in range(p)
        )
        residual = prediction - float(row["y"])
        model.addConstr(peak >= residual, name=f"positive_residual[{i}]")
        model.addConstr(peak >= -residual, name=f"negative_residual[{i}]")

    model.setObjective(peak, GRB.MINIMIZE)
    return model
