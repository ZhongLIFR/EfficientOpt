from __future__ import annotations
import json,time
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
 data=instance
 projects={r[0]:{"zone":r[1],"capital":float(r[2]),"benefit":float(r[3])} for r in data["projects"]}
 standards={r[0]:{"limit":float(r[1]),"coefficients":{t[0]:float(t[1]) for t in r[2]}} for r in data["review_standards"]}
 waves={r[0]:{"cap":float(r[1]),"multiplier":float(r[2]),"zone_caps":r[3]} for r in data["funding_cycles"]}
 pids,sids,wids=sorted(projects),sorted(standards),sorted(waves);xkeys=[(p,w) for p in pids for w in wids];mkeys=[(s,w) for s in sids for w in wids]
 model=gp.Model("bus_depot_upgrades_ordinary")
 model.Params.OutputFlag=0;model.Params.Threads=1;model.Params.Seed=0;model.Params.TimeLimit=300;model.Params.MIPGap=0;model.Params.FeasibilityTol=1e-9;model.Params.IntFeasTol=1e-9
 x=model.addVars(xkeys,vtype=GRB.BINARY,name="install");met=model.addVars(mkeys,vtype=GRB.BINARY,name="standard_satisfied")
 for p in pids:model.addConstr(gp.quicksum(x[p,w] for w in wids)<=1,name=f"once[{p}]")
 for w,row in waves.items():
  model.addConstr(gp.quicksum(projects[p]["capital"]*x[p,w] for p in pids)<=row["cap"],name=f"capital[{w}]")
  for zone,cap in row["zone_caps"].items():model.addConstr(gp.quicksum(projects[p]["capital"]*x[p,w] for p in pids if projects[p]["zone"]==zone)<=cap,name=f"zone[{w},{zone}]")
  for a,b in data["incompatible_project_pairs"]:model.addConstr(x[a,w]+x[b,w]<=1,name=f"conflict[{w},{a},{b}]")
  model.addConstr(gp.quicksum(met[s,w] for s in sids)>=data["minimum_standards_satisfied"],name=f"minimum[{w}]")
  for s,z in standards.items():
   model.addConstr(gp.quicksum(co*x[p,w] for p,co in z["coefficients"].items())<=z["limit"]+1_000_000.0*(1-met[s,w]),name=f"standard[{w},{s}]")
 model.setObjective(gp.quicksum(waves[w]["multiplier"]*projects[p]["benefit"]*x[p,w] for p,w in xkeys),GRB.MAXIMIZE)
 return model
