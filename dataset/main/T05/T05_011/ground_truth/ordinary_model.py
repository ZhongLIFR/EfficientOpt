from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    d = instance
    projects = {r[0]: {"zone": r[1], "investment": float(r[2]), "value": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coefficients": {p[0]: float(p[1]) for p in r[2]}} for r in d["review_standards"]}
    cycles = {r[0]: {"budget": float(r[1]), "multiplier": float(r[2]), "zone_caps": r[3]} for r in d["funding_cycles"]}
    project_ids = sorted(projects)
    standard_ids = sorted(standards)
    cycle_ids = sorted(cycles)

    model = gp.Model('funding_cycles_loose_big_m')
    choose = model.addVars([(i, c) for i in project_ids for c in cycle_ids], vtype=GRB.BINARY, name="choose")
    met = model.addVars([(q, c) for q in standard_ids for c in cycle_ids], vtype=GRB.BINARY, name="satisfied")

    for i in project_ids:
        model.addConstr(gp.quicksum(choose[i, c] for c in cycle_ids) <= 1, name=f"once[{i}]")

    minimum_per_group = d.get("minimum_projects_per_group", d.get("minimum_projects_per_base"))
    if minimum_per_group is not None:
        for zone in sorted({projects[i]["zone"] for i in project_ids}):
            model.addConstr(
                gp.quicksum(
                    choose[i, c]
                    for i in project_ids
                    if projects[i]["zone"] == zone
                    for c in cycle_ids
                ) >= int(minimum_per_group),
                name=f"minimum_projects[{zone}]",
            )

    for c, cycle in cycles.items():
        model.addConstr(
            gp.quicksum(projects[i]["investment"] * choose[i, c] for i in project_ids) <= cycle["budget"],
            name=f"budget[{c}]",
        )
        for zone, cap in cycle["zone_caps"].items():
            model.addConstr(
                gp.quicksum(
                    projects[i]["investment"] * choose[i, c]
                    for i in project_ids
                    if projects[i]["zone"] == zone
                ) <= float(cap),
                name=f"zone_cap[{c},{zone}]",
            )
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(choose[a, c] + choose[b, c] <= 1, name=f"incompatible[{c},{a},{b}]")
        model.addConstr(
            gp.quicksum(met[q, c] for q in standard_ids) >= int(d["minimum_standards_satisfied"]),
            name=f"minimum_standards[{c}]",
        )
        for q, z in standards.items():
            lhs = gp.quicksum(coef * choose[i, c] for i, coef in z["coefficients"].items())
            model.addConstr(lhs <= z["limit"] + 1_000_000.0 * (1 - met[q, c]), name=f"standard[{c},{q}]")

    model.setObjective(
        gp.quicksum(
            cycles[c]["multiplier"] * projects[i]["value"] * choose[i, c]
            for i in project_ids
            for c in cycle_ids
        ),
        GRB.MAXIMIZE,
    )
    return model
