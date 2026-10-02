from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    n = instance["item_count"]
    bins = instance["candidate_pallet_count"]
    sizes = instance["item_volumes"]
    capacity = instance["pallet_capacity"]
    model = gp.Model("pallet_packing_ordinary")
    assign = model.addVars(n, bins, vtype=GRB.BINARY, name="assign")
    used = model.addVars(bins, vtype=GRB.BINARY, name="used")
    model.setObjective(used.sum(), GRB.MINIMIZE)
    model.addConstrs((assign.sum(i, "*") == 1 for i in range(n)), name="once")
    model.addConstrs(
        (gp.quicksum(sizes[i] * assign[i, b] for i in range(n)) <= capacity * used[b]
         for b in range(bins)),
        name="capacity",
    )
    model.addConstrs((used[b] <= assign.sum("*", b) for b in range(bins)), name="nonempty_if_used")
    return model
