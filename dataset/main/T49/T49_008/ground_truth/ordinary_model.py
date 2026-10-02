from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    data = instance
    warehouses = {x["id"]: x for x in data["warehouses"]}
    products = {x["id"]: x for x in data["products"]}
    costs = {(x["product"], x["warehouse"]): float(x["cost_per_pallet"]) for x in data["storage_costs"]}
    arcs = sorted(costs)
    model = gp.Model("cold_storage")
    leased = model.addVars(sorted(warehouses), vtype=GRB.BINARY, name="leased")
    pallets = model.addVars(arcs, lb=0.0, name="pallets")
    for product, row in products.items():
        model.addConstr(gp.quicksum(pallets[product, j] for j in row["eligible_warehouses"]) == row["required_pallets"], name=f"product[{product}]")
    for warehouse, row in warehouses.items():
        model.addConstr(gp.quicksum(pallets[i, warehouse] for i, k in arcs if k == warehouse) <= row["pallet_capacity"] * leased[warehouse], name=f"pallet_capacity[{warehouse}]")
        model.addConstr(gp.quicksum(products[i]["volume_per_pallet_m3"] * pallets[i, warehouse] for i, k in arcs if k == warehouse) <= row["volume_capacity_m3"] * leased[warehouse], name=f"volume_capacity[{warehouse}]")
    model.setObjective(gp.quicksum(warehouses[j]["lease_cost"] * leased[j] for j in warehouses) + gp.quicksum(costs[a] * pallets[a] for a in arcs), GRB.MINIMIZE)
    return model
