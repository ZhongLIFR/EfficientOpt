from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    plants = {x["id"]: x for x in data["plants"]}
    districts = {x["id"]: x for x in data["districts"]}
    costs = {(x["district"], x["plant"]): float(x["cost_per_tonne"]) for x in data["treatment_costs"]}
    arcs = sorted(costs)
    model = gp.Model("municipal_waste_treatment")
    commissioned = model.addVars(sorted(plants), vtype=GRB.BINARY, name="commissioned")
    tonnes = model.addVars(arcs, lb=0.0, name="tonnes")
    for district, row in districts.items():
        model.addConstr(gp.quicksum(tonnes[district, p] for p in row["eligible_plants"]) == row["annual_tonnes"], name=f"district[{district}]")
    for plant, row in plants.items():
        model.addConstr(gp.quicksum(tonnes[d, plant] for d, p in arcs if p == plant) <= row["annual_capacity_tonnes"] * commissioned[plant], name=f"plant_capacity[{plant}]")
    for did, plant in arcs:
        model.addConstr(tonnes[did, plant] <= districts[did]["annual_tonnes"] * commissioned[plant], name=f"district_plant[{{did}},{{plant}}]")
    model.setObjective(gp.quicksum(plants[p]["commissioning_cost"] * commissioned[p] for p in plants) + gp.quicksum(costs[a] * tonnes[a] for a in arcs), GRB.MINIMIZE)
    return model
