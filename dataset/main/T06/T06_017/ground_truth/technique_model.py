from __future__ import annotations
import json
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB

def load_instance() -> dict:
    return json.loads((Path(__file__).resolve().parents[1] / "public" / "instance.json").read_text())

def build_model(instance: dict) -> gp.Model:
    F, P, T = range(len(instance["sites"])), range(len(instance["products"])), range(len(instance["periods"]))
    keys = [(f,p,t) for f in F for p in P for t in T]
    model = gp.Model(instance["problem_id"] + "_technique")
    lower = {(f,p,t): instance["site_data"][f]["minimum_batch"][p][t] for f,p,t in keys}
    upper = {(f,p,t): instance["site_data"][f]["maximum_batch"][p][t] for f,p,t in keys}
    production = model.addVars(keys, lb=lower, ub=upper, vtype=GRB.SEMICONT, name="production")
    inventory = model.addVars(keys, lb=0, name="inventory")
    model.addConstrs((production[f,p,0] - inventory[f,p,0] == instance["site_data"][f]["demand"][p][0] for f in F for p in P), name="initial_balance")
    model.addConstrs((inventory[f,p,t-1] + production[f,p,t] - inventory[f,p,t] == instance["site_data"][f]["demand"][p][t] for f in F for p in P for t in range(1,len(instance["periods"]))), name="balance")
    model.addConstrs((gp.quicksum(production[f,p,t] for p in P) <= instance["site_data"][f]["line_capacity"][t] for f in F for t in T), name="site_capacity")
    model.setObjective(gp.quicksum(instance["site_data"][f]["operating_cost"][p][t]*production[f,p,t] + instance["site_data"][f]["holding_cost"][p][t]*inventory[f,p,t] for f,p,t in keys), GRB.MINIMIZE)
    return model
