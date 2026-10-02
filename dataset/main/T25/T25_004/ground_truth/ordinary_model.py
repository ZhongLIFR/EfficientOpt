from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("regional_oven_packing_ordinary")
    objective_terms = []
    for region in instance["regions"]:
        g = region["index"]
        sizes = [item["size"] for item in region["items"]]
        n = len(sizes)
        assign = model.addVars([(g, i, b) for i in range(n) for b in range(n)], vtype=GRB.BINARY, name="assign")
        used = model.addVars([(g, b) for b in range(n)], vtype=GRB.BINARY, name="used")
        model.addConstrs((gp.quicksum(assign[g, i, b] for b in range(n)) == 1 for i in range(n)), name=f"once_{g}")
        model.addConstrs(
            (gp.quicksum(sizes[i] * assign[g, i, b] for i in range(n))
             <= instance["container_capacity"] * used[g, b] for b in range(n)),
            name=f"capacity_{g}",
        )
        model.addConstrs((assign[g, i, b] <= used[g, b] for i in range(n) for b in range(n)), name=f"activate_{g}")
        objective_terms.extend(used.values())
    model.setObjective(gp.quicksum(objective_terms), GRB.MINIMIZE)
    return model
