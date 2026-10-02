from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    groups = instance["groups"]
    capacities = instance["resource_capacities"]
    keys = [(g, k) for g, group in enumerate(groups) for k in range(len(group["options"]))]

    model = gp.Model("regional_package_selection_ordinary")
    select = model.addVars(keys, vtype=GRB.BINARY, name="select")
    model.addConstrs(
        (gp.quicksum(select[g, k] for k in range(len(groups[g]["options"]))) == 1
         for g in range(len(groups))),
        name="choose_one",
    )
    model.addConstrs(
        (gp.quicksum(
            groups[g]["options"][k]["resource_use"][r] * select[g, k]
            for g in range(len(groups))
            for k in range(len(groups[g]["options"]))
        ) <= capacities[r] for r in range(len(capacities))),
        name="resource",
    )
    model.setObjective(
        gp.quicksum(
            groups[g]["options"][k]["value"] * select[g, k]
            for g in range(len(groups))
            for k in range(len(groups[g]["options"]))
        ),
        GRB.MAXIMIZE,
    )
    return model
