from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    capacity = float(instance["capacity"])
    bin_count = int(instance["candidate_disk_count"])
    model = gp.Model("bin_packing_warm_start")
    objective_terms = []

    for group_index, group in enumerate(instance["groups"]):
        sizes = group["sizes"]
        n = len(sizes)
        assign = model.addVars(n, bin_count, vtype=GRB.BINARY, name=f"assign_{group_index}")
        used = model.addVars(bin_count, vtype=GRB.BINARY, name=f"used_{group_index}")

        loads = [0.0] * bin_count
        placement = {}
        for i in sorted(range(n), key=lambda index: (-float(sizes[index]), index)):
            selected = next(b for b in range(bin_count) if loads[b] + float(sizes[i]) <= capacity)
            placement[i] = selected
            loads[selected] += float(sizes[i])

        model.addConstrs(
            (gp.quicksum(assign[i, b] for b in range(bin_count)) == 1 for i in range(n)),
            name=f"item_once_{group_index}",
        )

        for i in range(n):
            for b in range(bin_count):
                assign[i, b].Start = int(placement[i] == b)

        model.addConstrs(
            (gp.quicksum(float(sizes[i]) * assign[i, b] for i in range(n)) <= capacity * used[b]
             for b in range(bin_count)),
            name=f"capacity_{group_index}",
        )
        model.addConstrs(
            (assign[i, b] <= used[b] for i in range(n) for b in range(bin_count)),
            name=f"activation_{group_index}",
        )

        for b in range(bin_count):
            used[b].Start = int(loads[b] > 0)

        objective_terms.extend(used.values())

    model.setObjective(gp.quicksum(objective_terms), GRB.MINIMIZE)
    return model
