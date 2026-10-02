from __future__ import annotations
import gurobipy as gp
from gurobipy import GRB

def standard_bound(q,plots,caps):
 total=0.0
 for reg,cap in caps.items():
  pairs=sorted(((q["water_risk_coefficients"].get(i,0.0),a["maximum_hectares"]) for i,a in plots.items() if a["region"]==reg),reverse=True);left=cap
  for coef,ub in pairs:
   take=min(left,ub);total+=coef*take;left-=take
   if left<=1e-9:break
 return total

def build_model(instance):
 d=instance;p={x["id"]:x for x in d["plots"]};s={x["id"]:x for x in d["water_standards"]};ids=sorted(p);sids=sorted(s)
 m=gp.Model("agricultural_land_allocation_tight_m");m.Params.OutputFlag=0;m.Params.Threads=1;m.Params.Seed=0;m.Params.TimeLimit=300;m.Params.MIPGap=0;m.Params.FeasibilityTol=1e-9;m.Params.IntFeasTol=1e-9
 x=m.addVars(ids,lb=0.0,ub={i:p[i]["maximum_hectares"] for i in ids},name="hectares");met=m.addVars(sids,vtype=GRB.BINARY,name="met")
 m.addConstr(gp.quicksum(x[i] for i in ids)<=d["total_area_cap"],name="total_area")
 for r,cap in d["region_area_caps"].items():m.addConstr(gp.quicksum(x[i] for i in ids if p[i]["region"]==r)<=cap,name=f"region[{r}]")
 m.addConstr(gp.quicksum(met[q] for q in sids)>=d["minimum_standards_met"],name="minimum_standards")
 for sid,q in s.items():
  M=max(0.0,standard_bound(q,p,d["region_area_caps"])-q["risk_limit"])
  m.addConstr(gp.quicksum(co*x[i] for i,co in q["water_risk_coefficients"].items())<=q["risk_limit"]+M*(1-met[sid]),name=f"standard[{sid}]")
 m.setObjective(gp.quicksum(p[i]["profit_per_hectare"]*x[i] for i in ids),GRB.MAXIMIZE)
 return m
