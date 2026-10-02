from __future__ import annotations

import math
import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    n = instance["item_count"]
    bins = instance["candidate_pallet_count"]
    sizes = instance["item_volumes"]
    capacity = instance["pallet_capacity"]
    total_volume = sum(sizes)
    volume_lower_bound = math.ceil(total_volume / capacity)

    model = gp.Model("pallet_packing_technique")
    used = model.addVars(bins, vtype=GRB.BINARY, name="used")
    assign = model.addVars(n, bins, vtype=GRB.BINARY, name="assign")
    load = model.addVars(bins, lb=0.0, ub=capacity, name="load")
    model.setObjective(used.sum(), GRB.MINIMIZE)
    model.addConstrs((assign.sum(i, "*") == 1 for i in range(n)), name="once")
    model.addConstrs(
        (load[b] == gp.quicksum(sizes[i] * assign[i, b] for i in range(n)) for b in range(bins)),
        name="load_definition",
    )
    model.addConstrs((load[b] <= capacity * used[b] for b in range(bins)), name="capacity")
    model.addConstrs((used[b] >= used[b + 1] for b in range(bins - 1)), name="used_order")
    model.addConstr(used.sum() >= volume_lower_bound, name="volume_lower_bound")
    model.addConstr(load.sum() == total_volume, name="total_volume")
    return model
