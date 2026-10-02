from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    sizes = instance["file_sizes"]
    n = len(sizes)
    pairs = [(r, i) for i in range(n) for r in range(i + 1)]
    model = gp.Model("file_packing_representatives")
    assign = model.addVars(pairs, vtype=GRB.BINARY, name="assign_to_representative")
    model.addConstrs(
        (gp.quicksum(assign[r, i] for r in range(i + 1)) == 1 for i in range(n)),
        name="once",
    )
    model.addConstrs(
        (gp.quicksum(sizes[i] * assign[r, i] for i in range(r, n))
         <= instance["capacity"] * assign[r, r] for r in range(n)),
        name="capacity_and_activation",
    )
    model.addConstr(
        gp.quicksum(assign[r, r] for r in range(n)) <= instance["candidate_disk_count"],
        name="available_disks",
    )
    model.setObjective(gp.quicksum(assign[r, r] for r in range(n)), GRB.MINIMIZE)
    return model
