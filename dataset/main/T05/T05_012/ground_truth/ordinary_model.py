from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


TECHNIQUE = False
MODEL_NAME = 'aquaculture_biosecurity_ordinary'


def build_model(instance):
    d = instance
    projects = {
        row[0]: {"group": row[1], "capital": float(row[2]), "benefit": float(row[3])}
        for row in d["projects"]
    }
    standards = {
        row[0]: {
            "limit": float(row[1]),
            "coefficients": {q[0]: float(q[1]) for q in row[2]},
        }
        for row in d["review_standards"]
    }
    cycles = {
        row[0]: {"cap": float(row[1]), "multiplier": float(row[2]), "group_caps": row[3]}
        for row in d["funding_cycles"]
    }
    ids = sorted(projects)
    standard_ids = sorted(standards)
    cycle_ids = sorted(cycles)
    keys = [(i, c) for i in ids for c in cycle_ids]
    standard_keys = [(q, c) for q in standard_ids for c in cycle_ids]

    model = gp.Model(MODEL_NAME)
    model.Params.OutputFlag = 0
    model.Params.Threads = 1
    model.Params.Seed = 0
    model.Params.TimeLimit = 300
    model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9
    model.Params.IntFeasTol = 1e-9
    implement = model.addVars(keys, vtype=GRB.BINARY, name="implement")
    satisfied = model.addVars(standard_keys, vtype=GRB.BINARY, name="standard_satisfied")

    for i in ids:
        model.addConstr(gp.quicksum(implement[i, c] for c in cycle_ids) <= 1, name=f"once[{i}]")
    for group in sorted({projects[i]["group"] for i in ids}):
        model.addConstr(
            gp.quicksum(implement[i, c] for i, c in keys if projects[i]["group"] == group)
            >= d["minimum_projects_per_group"],
            name=f"group_minimum[{group}]",
        )
    for c, row in cycles.items():
        model.addConstr(
            gp.quicksum(projects[i]["capital"] * implement[i, c] for i in ids)
            <= row["cap"],
            name=f"capital[{c}]",
        )
        for group, cap in row["group_caps"].items():
            model.addConstr(
                gp.quicksum(
                    projects[i]["capital"] * implement[i, c]
                    for i in ids
                    if projects[i]["group"] == group
                )
                <= cap,
                name=f"group[{c},{group}]",
            )
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(implement[a, c] + implement[b, c] <= 1, name=f"conflict[{c},{a},{b}]")
        model.addConstr(
            gp.quicksum(satisfied[q, c] for q in standard_ids)
            >= d["minimum_standards_satisfied"],
            name=f"minimum[{c}]",
        )
        for q, standard in standards.items():
            lhs = gp.quicksum(
                coefficient * implement[i, c]
                for i, coefficient in standard["coefficients"].items()
            )
            if TECHNIQUE:
                model.addGenConstrIndicator(
                    satisfied[q, c], True, lhs <= standard["limit"], name=f"standard[{c},{q}]"
                )
            else:
                model.addConstr(
                    lhs <= standard["limit"] + 1_000_000.0 * (1 - satisfied[q, c]),
                    name=f"standard[{c},{q}]",
                )
    model.setObjective(
        gp.quicksum(cycles[c]["multiplier"] * projects[i]["benefit"] * implement[i, c] for i, c in keys),
        GRB.MAXIMIZE,
    )
    return model
