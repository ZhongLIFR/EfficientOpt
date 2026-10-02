from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    records = instance["regions"]
    capacity = instance["container_capacity"]
    model = gp.Model("independent_bin_packing_ordinary")
    objective_terms = []

    for record in records:
        g = record["index"]
        sizes = [item["size"] for item in record["items"]]
        n = len(sizes)

        bins_by_item = {i: range(n) for i in range(n)}

        assign_keys = [(g, i, b) for i in range(n) for b in bins_by_item[i]]
        used_keys = [(g, b) for b in range(n)]
        assign = model.addVars(assign_keys, vtype=GRB.BINARY, name="assign")
        used = model.addVars(used_keys, vtype=GRB.BINARY, name="used")

        model.addConstrs(
            (gp.quicksum(assign[g, i, b] for b in bins_by_item[i]) == 1 for i in range(n)),
            name=f"item_once_{g}",
        )
        model.addConstrs(
            (gp.quicksum(
                sizes[i] * assign[g, i, b]
                for i in range(n) if b in bins_by_item[i]
            ) <= capacity * used[g, b] for b in range(n)),
            name=f"capacity_{g}",
        )
        model.addConstrs(
            (assign[g, i, b] <= used[g, b] for _, i, b in assign_keys),
            name=f"activation_{g}",
        )

        objective_terms.extend(used.values())

    model.setObjective(gp.quicksum(objective_terms), GRB.MINIMIZE)
    return model
