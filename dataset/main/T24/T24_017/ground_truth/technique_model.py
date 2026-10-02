from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _dominates(first, second):
    return (
        first["value"] >= second["value"]
        and all(a <= b for a, b in zip(first["resource_use"], second["resource_use"]))
        and (first["value"] > second["value"] or first["resource_use"] != second["resource_use"])
    )


def _kept_indices(group):
    options = group["options"]
    return [
        k for k, candidate in enumerate(options)
        if not any(j != k and _dominates(other, candidate) for j, other in enumerate(options))
    ]


def build_model(instance):
    groups = instance["groups"]
    capacities = instance["resource_capacities"]
    kept = [_kept_indices(group) for group in groups]
    keys = [(g, k) for g in range(len(groups)) for k in kept[g]]

    model = gp.Model("regional_package_selection_technique")
    select = model.addVars(keys, vtype=GRB.BINARY, name="select")
    model.addConstrs(
        (gp.quicksum(select[g, k] for k in kept[g]) == 1 for g in range(len(groups))),
        name="choose_one",
    )
    model.addConstrs(
        (gp.quicksum(
            groups[g]["options"][k]["resource_use"][r] * select[g, k]
            for g in range(len(groups)) for k in kept[g]
        ) <= capacities[r] for r in range(len(capacities))),
        name="resource",
    )
    model.setObjective(
        gp.quicksum(
            groups[g]["options"][k]["value"] * select[g, k]
            for g in range(len(groups)) for k in kept[g]
        ),
        GRB.MAXIMIZE,
    )
    return model
