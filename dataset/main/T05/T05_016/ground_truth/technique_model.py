from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    projects = {row[0]: {"arena": row[1], "capital": float(row[2]), "benefit": float(row[3])} for row in data["projects"]}
    standards = {row[0]: {"limit": float(row[1]), "coefficients": {entry[0]: float(entry[1]) for entry in row[2]}} for row in data["review_standards"]}
    cycles = {row[0]: {"cap": float(row[1]), "multiplier": float(row[2]), "arena_caps": row[3]} for row in data["funding_cycles"]}
    project_ids, standard_ids, cycle_ids = sorted(projects), sorted(standards), sorted(cycles)
    assignment_keys = [(i, c) for i in project_ids for c in cycle_ids]
    standard_keys = [(q, c) for q in standard_ids for c in cycle_ids]
    model = gp.Model('ice_rink_native_conditions')
    model.Params.OutputFlag = 0; model.Params.Threads = 1; model.Params.Seed = 0; model.Params.TimeLimit = 300; model.Params.MIPGap = 0
    model.Params.FeasibilityTol = 1e-9; model.Params.IntFeasTol = 1e-9
    implement = model.addVars(assignment_keys, vtype=GRB.BINARY, name="implement")
    satisfied = model.addVars(standard_keys, vtype=GRB.BINARY, name="standard_satisfied")
    for i in project_ids:
        model.addConstr(gp.quicksum(implement[i, c] for c in cycle_ids) <= 1, name=f"once[{i}]")
    for c, cycle in cycles.items():
        model.addConstr(gp.quicksum(projects[i]["capital"] * implement[i, c] for i in project_ids) <= cycle["cap"], name=f"capital[{c}]")
        for arena, cap in cycle["arena_caps"].items():
            model.addConstr(gp.quicksum(projects[i]["capital"] * implement[i, c] for i in project_ids if projects[i]["arena"] == arena) <= cap, name=f"arena_cap[{c},{arena}]")
        for a, b in data["incompatible_project_pairs"]:
            model.addConstr(implement[a, c] + implement[b, c] <= 1, name=f"conflict[{c},{a},{b}]")
        model.addConstr(gp.quicksum(satisfied[q, c] for q in standard_ids) >= data["minimum_standards_satisfied"], name=f"minimum_standards[{c}]")
        for q, standard in standards.items():
            burden = gp.quicksum(coefficient * implement[i, c] for i, coefficient in standard["coefficients"].items())
            model.addGenConstrIndicator(satisfied[q, c], True, burden <= standard["limit"], name=f"conditional_standard[{c},{q}]")
    model.setObjective(gp.quicksum(cycles[c]["multiplier"] * projects[i]["benefit"] * implement[i, c] for i, c in assignment_keys), GRB.MAXIMIZE)
    return model
