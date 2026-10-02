from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """Primal least-absolute-deviation quadratic-feature regression LP."""
    rows = instance["observations"]
    p = len(rows[0]["features"])

    model = gp.Model("t12_004_l1_primal")
    beta = model.addVars(p, lb=-GRB.INFINITY, name="coefficient")
    deviation = model.addVars(len(rows), lb=0.0, name="absolute_deviation")

    for i, row in enumerate(rows):
        prediction = gp.quicksum(
            float(row["features"][j]) * beta[j] for j in range(p)
        )
        residual = prediction - float(row["y"])
        model.addConstr(deviation[i] >= residual, name=f"positive_residual[{i}]")
        model.addConstr(deviation[i] >= -residual, name=f"negative_residual[{i}]")

    model.setObjective(deviation.sum(), GRB.MINIMIZE)
    return model
