from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
 d=instance;I=len(d["fixed_assignment_cost"]);J=len(d["fixed_assignment_cost"][0]);edges=d["data_exchange_pairs"]
 m=gp.Model("assignment_mccormick")
 x=m.addVars(I,J,vtype=GRB.BINARY,name="located")
 m.addConstrs((gp.quicksum(x[i,j] for j in range(J))==1 for i in range(I)),name="once")
 m.addConstrs((gp.quicksum(x[i,j] for i in range(I))<=d["campus_capacity"][j] for j in range(J)),name="capacity")
 obj=gp.quicksum((d["fixed_assignment_cost"][i][j]-d["coordination_benefit"][i])*x[i,j] for i in range(I) for j in range(J))
 for e in edges:
  i,jj,vol=e["i"],e["j"],e["volume"];z=m.addVars(J,J,lb=0.0,ub=1.0,name=f"pair_{i}_{jj}")
  m.addConstrs((z[j,k]<=x[i,j] for j in range(J) for k in range(J)),name=f"ub_i_{i}_{jj}")
  m.addConstrs((z[j,k]<=x[jj,k] for j in range(J) for k in range(J)),name=f"ub_j_{i}_{jj}")
  m.addConstrs((z[j,k]>=x[i,j]+x[jj,k]-1 for j in range(J) for k in range(J)),name=f"lb_{i}_{jj}")
  obj += gp.quicksum(vol*d["network_pair_cost"][j][k]*z[j,k] for j in range(J) for k in range(J))
 m.setObjective(obj,GRB.MINIMIZE)
 return m
