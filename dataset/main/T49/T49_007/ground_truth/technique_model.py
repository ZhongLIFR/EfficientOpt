from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    hubs = {x["id"]: x for x in data["hubs"]}
    zones = {x["id"]: x for x in data["zones"]}
    costs = {(x["zone"], x["hub"]): float(x["cost_per_unit"]) for x in data["delivery_costs"]}
    arcs = sorted(costs)
    model = gp.Model("emergency_relief_hubs")
    open_hub = model.addVars(sorted(hubs), vtype=GRB.BINARY, name="open")
    shipment = model.addVars(arcs, lb=0.0, name="shipment")
    for zone, row in zones.items():
        model.addConstr(gp.quicksum(shipment[zone, j] for j in row["eligible_hubs"]) == row["required_units"], name=f"zone[{zone}]")
    for hub, row in hubs.items():
        model.addConstr(gp.quicksum(shipment[i, hub] for i, j in arcs if j == hub) <= row["daily_throughput_units"] * open_hub[hub], name=f"hub[{hub}]")
    for zone, hub in arcs:
        model.addConstr(shipment[zone, hub] <= zones[zone]["required_units"] * open_hub[hub], name=f"zone_hub[{{zone}},{{hub}}]")
    model.setObjective(gp.quicksum(hubs[h]["opening_cost"] * open_hub[h] for h in hubs) + gp.quicksum(costs[a] * shipment[a] for a in arcs), GRB.MINIMIZE)
    return model
