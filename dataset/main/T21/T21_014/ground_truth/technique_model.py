from __future__ import annotations
import itertools
import gurobipy as gp
from gurobipy import GRB

def enumerate_routes(region: dict, capacity: int):
    n=len(region["customer_demand"]); routes=[]
    for size in range(1,capacity+1):
        for subset in itertools.combinations(range(1,n+1),size):
            if sum(region["customer_demand"][i-1] for i in subset)>capacity: continue
            best_cost=None; best_order=None
            for order in itertools.permutations(subset):
                cost=region["distance"][0][order[0]]+sum(region["distance"][order[k]][order[k+1]] for k in range(len(order)-1))+region["distance"][order[-1]][0]
                if best_cost is None or cost<best_cost: best_cost,best_order=cost,order
            routes.append((subset,best_order,int(best_cost)))
    return routes

def build_model(instance: dict) -> gp.Model:
    n=instance["customer_count"]; C=range(1,n+1); Q=instance["vehicle_capacity"]
    route_sets=[enumerate_routes(region,Q) for region in instance["regions"]]
    keys=[(r,k) for r,rows in enumerate(route_sets) for k in range(len(rows))]
    model=gp.Model("regional_cvrp_route_partitioning")
    use=model.addVars(keys,vtype=GRB.BINARY,name="route")
    model.addConstrs((gp.quicksum(use[r,k] for k,row in enumerate(route_sets[r]) if i in row[0])==1 for r in range(len(route_sets)) for i in C),name="customer_cover")
    model.setObjective(gp.quicksum(route_sets[r][k][2]*use[r,k] for r,k in keys),GRB.MINIMIZE)
    model._use=use; model._route_sets=route_sets
    return model
