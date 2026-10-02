from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    d = instance
    projects = {r[0]: {"area": r[1], "capital": float(r[2]), "benefit": float(r[3])} for r in d["projects"]}
    standards = {r[0]: {"limit": float(r[1]), "coefficients": {t[0]: float(t[1]) for t in r[2]}} for r in d["review_standards"]}
    phases = {r[0]: {"cap": float(r[1]), "multiplier": float(r[2]), "area_caps": r[3]} for r in d["funding_cycles"]}
    pids, sids, hids = sorted(projects), sorted(standards), sorted(phases)
    xkeys = [(i, h) for i in pids for h in hids]
    mkeys = [(q, h) for q in sids for h in hids]
    model = gp.Model('substation_hardening_ordinary')
    model.Params.OutputFlag = 0; model.Params.Threads = 1; model.Params.Seed = 0; model.Params.TimeLimit = 300; model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9; model.Params.IntFeasTol = 1e-9
    harden = model.addVars(xkeys, vtype=GRB.BINARY, name="harden")
    satisfied = model.addVars(mkeys, vtype=GRB.BINARY, name="standard_satisfied")
    for i in pids:
        model.addConstr(gp.quicksum(harden[i, h] for h in hids) <= 1, name=f"once[{i}]")
    for h, row in phases.items():
        model.addConstr(gp.quicksum(projects[i]["capital"] * harden[i, h] for i in pids) <= row["cap"], name=f"capital[{h}]")
        for area, cap in row["area_caps"].items():
            model.addConstr(gp.quicksum(projects[i]["capital"] * harden[i, h] for i in pids if projects[i]["area"] == area) <= cap, name=f"area[{h},{area}]")
        for a, b in d["incompatible_project_pairs"]:
            model.addConstr(harden[a, h] + harden[b, h] <= 1, name=f"conflict[{h},{a},{b}]")
        model.addConstr(gp.quicksum(satisfied[q, h] for q in sids) >= d["minimum_standards_satisfied"], name=f"minimum[{h}]")
        for q, row_s in standards.items():
            lhs = gp.quicksum(co * harden[i, h] for i, co in row_s["coefficients"].items())
            model.addConstr(lhs <= row_s["limit"] + 1_000_000.0 * (1 - satisfied[q, h]), name=f"standard[{h},{q}]")
    model.setObjective(gp.quicksum(phases[h]["multiplier"] * projects[i]["benefit"] * harden[i, h] for i, h in xkeys), GRB.MAXIMIZE)
    return model
