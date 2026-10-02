from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("regional_oven_packing_technique")
    objective_terms = []
    for region in instance["regions"]:
        g = region["index"]
        sizes = [item["size"] for item in region["items"]]
        n = len(sizes)
        position = {item: p for p, item in enumerate(sorted(range(n), key=lambda i: (-sizes[i], i)))}
        keys = [(g, i, b) for i in range(n) for b in range(n) if b <= position[i]]
        assign = model.addVars(keys, vtype=GRB.BINARY, name="assign")
        used = model.addVars([(g, b) for b in range(n)], vtype=GRB.BINARY, name="used")
        model.addConstrs((gp.quicksum(assign[g, i, b] for b in range(n) if (g, i, b) in assign) == 1 for i in range(n)), name=f"once_{g}")
        model.addConstrs(
            (gp.quicksum(sizes[i] * assign[g, i, b] for i in range(n) if (g, i, b) in assign)
             <= instance["container_capacity"] * used[g, b] for b in range(n)),
            name=f"capacity_{g}",
        )
        model.addConstrs((assign[g, i, b] <= used[g, b] for _, i, b in keys), name=f"activate_{g}")
        model.addConstrs((used[g, b] >= used[g, b + 1] for b in range(n - 1)), name=f"used_order_{g}")
        objective_terms.extend(used.values())
    model.setObjective(gp.quicksum(objective_terms), GRB.MINIMIZE)
    return model
