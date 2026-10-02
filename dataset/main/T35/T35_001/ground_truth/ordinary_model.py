from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    names = instance["variable_names"]
    blocks = instance["blocks"]
    n, k = len(blocks), len(names)
    model = gp.Model("dense_bound_encoding_ordinary")
    x = model.addVars(n, k, vtype=GRB.INTEGER, lb=0, name="allocation")
    model.setObjective(gp.quicksum(blocks[i]["cost"][j] * x[i, j] for i in range(n) for j in range(k)), GRB.MINIMIZE)
    for i, block in enumerate(blocks):
        total = gp.quicksum(x[i, j] for j in range(k))
        model.addConstr(total == block["balance"], name=f"balance[{i}]")
        for j in range(k):
            model.addConstr(x[i, j] <= block["upper"][j], name=f"upper[{i},{j}]")
            # Given total == balance, this dense row is exactly x[i,j] >= lower[i,j].
            model.addConstr(total - x[i, j] <= block["balance"] - block["lower"][j], name=f"lower_dense[{i},{j}]")
    for quota in instance["coupling_constraints"]:
        j = int(quota["variable_index"])
        lhs = gp.quicksum(x[int(i), j] for i in quota["block_indices"])
        if quota["sense"] == "<=":
            model.addConstr(lhs <= quota["rhs"], name=quota["name"])
        else:
            model.addConstr(lhs >= quota["rhs"], name=quota["name"])
    return model
