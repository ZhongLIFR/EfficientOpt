from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    d = instance
    projects = {r[0]: {"basin": r[1], "capital": float(r[2]), "benefit": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coefficients": {q[0]: float(q[1]) for q in r[2]}} for r in d["review_standards"]}
    cycles = {r[0]: {"cap": float(r[1]), "multiplier": float(r[2]), "basin_caps": r[3]} for r in d["funding_cycles"]}
    ids, sids, cids = sorted(projects), sorted(standards), sorted(cycles)
    keys = [(i, c) for i in ids for c in cids]
    skeys = [(q, c) for q in sids for c in cids]
    model = gp.Model('habitat_restoration_ordinary')
    model.Params.OutputFlag = 0; model.Params.Threads = 1; model.Params.Seed = 0; model.Params.TimeLimit = 300; model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9; model.Params.IntFeasTol = 1e-9
    restore = model.addVars(keys, vtype=GRB.BINARY, name="restore")
    met = model.addVars(skeys, vtype=GRB.BINARY, name="standard_satisfied")
    for i in ids:
        model.addConstr(gp.quicksum(restore[i, c] for c in cids) <= 1, name=f"once[{i}]")
    for c, row in cycles.items():
        model.addConstr(gp.quicksum(projects[i]["capital"] * restore[i, c] for i in ids) <= row["cap"], name=f"capital[{c}]")
        for basin, cap in row["basin_caps"].items():
            model.addConstr(gp.quicksum(projects[i]["capital"] * restore[i, c] for i in ids if projects[i]["basin"] == basin) <= cap, name=f"basin[{c},{basin}]")
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(restore[a, c] + restore[b, c] <= 1, name=f"conflict[{c},{a},{b}]")
        model.addConstr(gp.quicksum(met[q, c] for q in sids) >= d["minimum_standards_satisfied"], name=f"minimum[{c}]")
        for q, row_s in standards.items():
            burden = gp.quicksum(co * restore[i, c] for i, co in row_s["coefficients"].items())
            model.addConstr(burden <= row_s["limit"] + 1_000_000.0 * (1 - met[q, c]), name=f"standard[{c},{q}]")
    model.setObjective(gp.quicksum(cycles[c]["multiplier"] * projects[i]["benefit"] * restore[i, c] for i, c in keys), GRB.MAXIMIZE)
    return model
