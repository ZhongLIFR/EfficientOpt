from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    """Exact LP dual of minimax absolute-deviation regression."""
    rows = instance["observations"]
    n = len(rows)
    p = len(rows[0]["features"])

    model = gp.Model("t12_002_linf_dual")
    positive = model.addVars(n, lb=0.0, name="positive_weight")
    negative = model.addVars(n, lb=0.0, name="negative_weight")

    for j in range(p):
        model.addConstr(
            gp.quicksum(
                float(rows[i]["features"][j])
                * (positive[i] - negative[i])
                for i in range(n)
            )
            == 0.0,
            name=f"orthogonality[{j}]",
        )
    model.addConstr(
        gp.quicksum(positive[i] + negative[i] for i in range(n)) <= 1.0,
        name="l1_norm_bound",
    )
    model.setObjective(
        gp.quicksum(
            float(rows[i]["y"]) * (positive[i] - negative[i])
            for i in range(n)
        ),
        GRB.MAXIMIZE,
    )
    return model
