from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    sizes = instance["file_sizes"]
    n = len(sizes)
    bins = instance["candidate_disk_count"]
    model = gp.Model("file_packing_ordinary")
    assign = model.addVars(n, bins, vtype=GRB.BINARY, name="assign")
    used = model.addVars(bins, vtype=GRB.BINARY, name="used")
    model.addConstrs((assign.sum(i, "*") == 1 for i in range(n)), name="once")
    model.addConstrs(
        (gp.quicksum(sizes[i] * assign[i, b] for i in range(n))
         <= instance["capacity"] * used[b] for b in range(bins)),
        name="capacity",
    )
    model.addConstrs((assign[i, b] <= used[b] for i in range(n) for b in range(bins)), name="activate")
    model.setObjective(used.sum(), GRB.MINIMIZE)
    return model
