from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """Exact LP dual of least-absolute-deviation regression."""
    rows = instance["observations"]
    n = len(rows)
    p = len(rows[0]["features"])

    model = gp.Model("t12_004_l1_dual")
    weight = model.addVars(n, lb=-1.0, ub=1.0, name="dual_residual_weight")

    for j in range(p):
        model.addConstr(
            gp.quicksum(
                float(rows[i]["features"][j]) * weight[i] for i in range(n)
            )
            == 0.0,
            name=f"orthogonality[{j}]",
        )
    model.setObjective(
        gp.quicksum(float(rows[i]["y"]) * weight[i] for i in range(n)),
        GRB.MAXIMIZE,
    )
    return model
