from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    parks = {x["id"]: x for x in data["electrolyser_parks"]}
    buyers = {x["id"]: x for x in data["industrial_buyers"]}
    costs = {(x["industrial_buyer"], x["electrolyser_park"]): float(x["production_cost_per_unit"]) for x in data["production_costs"]}
    arcs = sorted(costs)
    model = gp.Model("green_hydrogen_supply")
    active = model.addVars(sorted(parks), vtype=GRB.BINARY, name="started")
    hydrogen = model.addVars(arcs, lb=0.0, name="hydrogen")
    for i, buyer in buyers.items():
        model.addConstr(gp.quicksum(hydrogen[i, j] for j in buyer["eligible_parks"]) == buyer["required_hydrogen_units"], name=f"buyer[{i}]")
    for j, park in parks.items():
        model.addConstr(gp.quicksum(hydrogen[i, k] for i, k in arcs if k == j) <= park["production_capacity_units"] * active[j], name=f"production[{j}]")
        model.addConstr(gp.quicksum(buyers[i]["electricity_points_per_unit"] * hydrogen[i, k] for i, k in arcs if k == j) <= park["electricity_capacity_points"] * active[j], name=f"electricity[{j}]")
    for i, j in arcs:
        model.addConstr(hydrogen[i, j] <= buyers[i]["required_hydrogen_units"] * active[j], name=f"buyer_park[{{i}},{{j}}]")
    model.setObjective(gp.quicksum(parks[j]["startup_cost"] * active[j] for j in parks) + gp.quicksum(costs[a] * hydrogen[a] for a in arcs), GRB.MINIMIZE)
    return model
