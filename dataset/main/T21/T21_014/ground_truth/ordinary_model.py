from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance: dict) -> gp.Model:
    n=instance["customer_count"]; Q=instance["vehicle_capacity"]; N=range(n+1); C=range(1,n+1)
    model=gp.Model("regional_cvrp_ordinary")
    keys=[(region["index"],i,j) for region in instance["regions"] for i in N for j in N if i!=j]
    arc=model.addVars(keys,vtype=GRB.BINARY,name="arc")
    flow=model.addVars(keys,lb=0,ub=Q,name="commodity_flow")
    by_index={region["index"]:region for region in instance["regions"]}
    R=list(by_index)
    model.addConstrs((gp.quicksum(arc[r,i,j] for j in N if j!=i)==1 for r in R for i in C),name="customer_depart")
    model.addConstrs((gp.quicksum(arc[r,j,i] for j in N if j!=i)==1 for r in R for i in C),name="customer_arrive")
    model.addConstrs((gp.quicksum(arc[r,0,j] for j in C)==gp.quicksum(arc[r,i,0] for i in C) for r in R),name="depot_balance")
    model.addConstrs((gp.quicksum(flow[r,i,j] for i in N if i!=j)-gp.quicksum(flow[r,j,k] for k in N if k!=j)==by_index[r]["customer_demand"][j-1] for r in R for j in C),name="flow_balance")
    model.addConstrs((flow[r,i,j]<=(Q if i==0 else Q-by_index[r]["customer_demand"][i-1])*arc[r,i,j] for r,i,j in keys),name="flow_upper")
    model.addConstrs((flow[r,i,j]>=by_index[r]["customer_demand"][j-1]*arc[r,i,j] for r,i,j in keys if j!=0),name="flow_lower")
    model.setObjective(gp.quicksum(by_index[r]["distance"][i][j]*arc[r,i,j] for r,i,j in keys),GRB.MINIMIZE)
    model._arc=arc
    return model
