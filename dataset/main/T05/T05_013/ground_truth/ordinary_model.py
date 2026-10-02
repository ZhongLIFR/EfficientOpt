from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

TECHNIQUE = False

def build_model(instance):
    d = instance
    projects = {r[0]: {"group": r[1], "capital": float(r[2]), "benefit": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coefficients": {q[0]: float(q[1]) for q in r[2]}} for r in d["review_standards"]}
    cycles = {r[0]: {"cap": float(r[1]), "multiplier": float(r[2]), "group_caps": r[3]} for r in d["funding_cycles"]}
    ids, sids, cids = sorted(projects), sorted(standards), sorted(cycles)
    keys = [(i, c) for i in ids for c in cids]
    skeys = [(q, c) for q in sids for c in cids]
    model = gp.Model('spaceport_modernization_ordinary')
    model.Params.OutputFlag = 0; model.Params.Threads = 1; model.Params.Seed = 0; model.Params.TimeLimit = 300; model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9; model.Params.IntFeasTol = 1e-9
    implement = model.addVars(keys, vtype=GRB.BINARY, name="implement")
    satisfied = model.addVars(skeys, vtype=GRB.BINARY, name="standard_satisfied")
    for i in ids:
        model.addConstr(gp.quicksum(implement[i, c] for c in cids) <= 1, name=f"once[{i}]")
    for group in sorted({projects[i]["group"] for i in ids}):
        model.addConstr(gp.quicksum(implement[i, c] for i, c in keys if projects[i]["group"] == group) >= d["minimum_projects_per_group"], name=f"group_minimum[{group}]")
    for c, row in cycles.items():
        model.addConstr(gp.quicksum(projects[i]["capital"] * implement[i, c] for i in ids) <= row["cap"], name=f"capital[{c}]")
        for group, cap in row["group_caps"].items():
            model.addConstr(gp.quicksum(projects[i]["capital"] * implement[i, c] for i in ids if projects[i]["group"] == group) <= cap, name=f"group[{c},{group}]")
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(implement[a, c] + implement[b, c] <= 1, name=f"conflict[{c},{a},{b}]")
        model.addConstr(gp.quicksum(satisfied[q, c] for q in sids) >= d["minimum_standards_satisfied"], name=f"minimum[{c}]")
        for q, standard in standards.items():
            lhs = gp.quicksum(co * implement[i, c] for i, co in standard["coefficients"].items())
            model.addConstr(lhs <= standard["limit"] + 1_000_000.0 * (1 - satisfied[q, c]), name=f"standard[{c},{q}]")
    model.setObjective(gp.quicksum(cycles[c]["multiplier"] * projects[i]["benefit"] * implement[i, c] for i, c in keys), GRB.MAXIMIZE)
    return model
