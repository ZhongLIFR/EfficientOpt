from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    capacity = instance["capacity"]
    bins = instance["candidate_disk_count"]
    model = gp.Model("repeated_file_packing_load_order")
    for g, group in enumerate(instance["groups"]):
        sizes = group["file_sizes"]
        n = len(sizes)
        assign = model.addVars([(g, i, b) for i in range(n) for b in range(bins)], vtype=GRB.BINARY, name="assign")
        used = model.addVars([(g, b) for b in range(bins)], vtype=GRB.BINARY, obj=1.0, name="used")
        load = model.addVars([(g, b) for b in range(bins)], lb=0.0, ub=capacity, name="load")
        model.addConstrs((gp.quicksum(assign[g, i, b] for b in range(bins)) == 1 for i in range(n)), name=f"once_{g}")
        model.addConstrs(
            (load[g, b] == gp.quicksum(sizes[i] * assign[g, i, b] for i in range(n)) for b in range(bins)),
            name=f"load_definition_{g}",
        )
        model.addConstrs((load[g, b] <= capacity * used[g, b] for b in range(bins)), name=f"capacity_{g}")
        model.addConstrs((assign[g, i, b] <= used[g, b] for i in range(n) for b in range(bins)), name=f"activate_{g}")
        model.addConstrs((load[g, b] >= load[g, b + 1] for b in range(bins - 1)), name=f"load_order_{g}")
    model.ModelSense = GRB.MINIMIZE
    return model
