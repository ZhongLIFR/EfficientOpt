from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
 d=instance;W=d["workload_count"];D=d["datacenter_count"];edges=d["data_exchange_pairs"]
 m=gp.Model("workload_assignment_ordinary")
 x=m.addVars(W,D,vtype=GRB.BINARY,name="located")
 m.addConstrs((gp.quicksum(x[i,c] for c in range(D))==1 for i in range(W)),name="once")
 m.addConstrs((gp.quicksum(x[i,c] for i in range(W))<=d["datacenter_capacity"][c] for c in range(D)),name="capacity")
 obj=gp.quicksum((d["fixed_assignment_cost"][i][c]-d["coordination_benefit"][i])*x[i,c] for i in range(W) for c in range(D))
 for e in edges:
  i,j,vol=e["i"],e["j"],e["volume"];z=m.addVars(D,D,lb=0.0,ub=1.0,name=f"pair_{i}_{j}")
  m.addConstrs((z[c,k] <= x[i,c] for c in range(D) for k in range(D)), name=f"ub_i_{i}_{j}")
  m.addConstrs((z[c,k] <= x[j,k] for c in range(D) for k in range(D)), name=f"ub_j_{i}_{j}")
  m.addConstrs((z[c,k] >= x[i,c]+x[j,k]-1 for c in range(D) for k in range(D)), name=f"lb_{i}_{j}")
  obj += gp.quicksum(vol*d["network_pair_cost"][c][k]*z[c,k] for c in range(D) for k in range(D))
 m.setObjective(obj,GRB.MINIMIZE)
 return m
