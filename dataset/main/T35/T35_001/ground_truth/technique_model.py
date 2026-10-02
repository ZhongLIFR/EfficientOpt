from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance: dict) -> gp.Model:
    names = instance["variable_names"]
    blocks = instance["blocks"]
    n, k = len(blocks), len(names)
    eliminated = k - 1
    x = gp.tupledict()
    model = gp.Model("balance_variable_eliminated")
    for i, block in enumerate(blocks):
        for j in range(eliminated):
            x[i, j] = model.addVar(vtype=GRB.INTEGER, lb=block["lower"][j], ub=block["upper"][j], name=f"allocation[{i},{j}]")

    objective = gp.LinExpr()
    for i, block in enumerate(blocks):
        kept_sum = gp.quicksum(x[i, j] for j in range(eliminated))
        removed = block["balance"] - kept_sum
        objective += gp.quicksum(block["cost"][j] * x[i, j] for j in range(eliminated))
        objective += block["cost"][eliminated] * removed
        model.addConstr(removed >= block["lower"][eliminated], name=f"removed_lower[{i}]")
        model.addConstr(removed <= block["upper"][eliminated], name=f"removed_upper[{i}]")
    for quota in instance["coupling_constraints"]:
        j = int(quota["variable_index"])
        lhs = gp.quicksum(x[int(i), j] for i in quota["block_indices"])
        if quota["sense"] == "<=":
            model.addConstr(lhs <= quota["rhs"], name=quota["name"])
        else:
            model.addConstr(lhs >= quota["rhs"], name=quota["name"])
    model.setObjective(objective, GRB.MINIMIZE)
    return model
