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
    model = gp.Model(instance["problem_id"] + "_ordinary")
    upper = {(f,p,t): instance["site_data"][f]["maximum_batch"][p][t] for f,p,t in keys}
    lower = {(f,p,t): instance["site_data"][f]["minimum_batch"][p][t] for f,p,t in keys}
    production = model.addVars(keys, lb=0, ub=upper, name="production")
    active = model.addVars(keys, vtype=GRB.BINARY, name="active")
    model.addConstrs((production[k] >= lower[k] * active[k] for k in keys), name="minimum_batch")
    model.addConstrs((production[k] <= upper[k] * active[k] for k in keys), name="maximum_batch")
    inventory = model.addVars(keys, lb=0, name="inventory")
    model.addConstrs((production[f,p,0] - inventory[f,p,0] == instance["site_data"][f]["demand"][p][0] for f in F for p in P), name="initial_balance")
    model.addConstrs((inventory[f,p,t-1] + production[f,p,t] - inventory[f,p,t] == instance["site_data"][f]["demand"][p][t] for f in F for p in P for t in range(1,len(instance["periods"]))), name="balance")
    model.addConstrs((gp.quicksum(production[f,p,t] for p in P) <= instance["site_data"][f]["line_capacity"][t] for f in F for t in T), name="site_capacity")
    model.setObjective(gp.quicksum(instance["site_data"][f]["operating_cost"][p][t]*production[f,p,t] + instance["site_data"][f]["holding_cost"][p][t]*inventory[f,p,t] for f,p,t in keys), GRB.MINIMIZE)
    return model
