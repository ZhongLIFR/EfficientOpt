from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    d = instance
    projects = {r[0]: {"region": r[1], "funding": float(r[2]), "value": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coefficients": {q[0]: float(q[1]) for q in r[2]}} for r in d["review_standards"]}
    cycles = {r[0]: {"cap": float(r[1]), "multiplier": float(r[2]), "regional": r[3]} for r in d["funding_cycles"]}
    ids, sids, cids = sorted(projects), sorted(standards), sorted(cycles)
    keys = [(i, c) for i in ids for c in cids]
    mkeys = [(q, c) for q in sids for c in cids]
    model = gp.Model('coastal_flood_tight_big_m')
    model.Params.OutputFlag = 0; model.Params.Threads = 1; model.Params.Seed = 0; model.Params.TimeLimit = 300; model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9; model.Params.IntFeasTol = 1e-9
    construct = model.addVars(keys, vtype=GRB.BINARY, name="construct")
    met = model.addVars(mkeys, vtype=GRB.BINARY, name="satisfied")
    for i in ids:
        model.addConstr(gp.quicksum(construct[i, c] for c in cids) <= 1, name=f"once[{i}]")
    for c, row in cycles.items():
        model.addConstr(gp.quicksum(projects[i]["funding"] * construct[i, c] for i in ids) <= row["cap"], name=f"capital[{c}]")
        for region, cap in row["regional"].items():
            model.addConstr(gp.quicksum(projects[i]["funding"] * construct[i, c] for i in ids if projects[i]["region"] == region) <= cap, name=f"sector[{c},{region}]")
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(construct[a, c] + construct[b, c] <= 1, name=f"conflict[{c},{a},{b}]")
        model.addConstr(gp.quicksum(met[q, c] for q in sids) >= d["minimum_standards_satisfied"], name=f"minimum[{c}]")
        for q, z in standards.items():
            lhs = gp.quicksum(co * construct[i, c] for i, co in z["coefficients"].items())
            model.addConstr(lhs <= z["limit"] + max(0.0, sum(z["coefficients"].values()) - z["limit"]) * (1 - met[q, c]), name=f"permit[{c},{q}]")
    model.setObjective(gp.quicksum(cycles[c]["multiplier"] * projects[i]["value"] * construct[i, c] for i, c in keys), GRB.MAXIMIZE)
    return model
