import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 n=len(d["units"]); K=d["options_per_unit"]; m=gp.Model("portfolio_ordinary")
 y=m.addVars(n,K,vtype=GRB.BINARY,name="choose"); cap=m.addVars(n,lb=0,ub=d["capacity_attribute_upper_bound"],name="capacity"); risk=m.addVars(n,lb=0,ub=d["risk_attribute_upper_bound"],name="risk")
 m.addConstrs((gp.quicksum(y[i,k] for k in range(K))==1 for i in range(n)),name="choose_one")
 for i,u in enumerate(d["units"]):
  for k,o in enumerate(u["options"]):
   m.addConstr(cap[i]<=o["capacity"]+d["capacity_attribute_upper_bound"]*(1-y[i,k]))
   m.addConstr(cap[i]>=o["capacity"]-d["capacity_attribute_upper_bound"]*(1-y[i,k]))
   m.addConstr(risk[i]<=o["risk"]+d["risk_attribute_upper_bound"]*(1-y[i,k]))
   m.addConstr(risk[i]>=o["risk"]-d["risk_attribute_upper_bound"]*(1-y[i,k]))
 m.addConstr(gp.quicksum(cap.values())>=d["minimum_total_capacity"],name="minimum_capacity"); m.addConstr(gp.quicksum(risk.values())<=d["maximum_total_risk"],name="maximum_risk")
 m.setObjective(gp.quicksum(d["units"][i]["options"][k]["value"]*y[i,k] for i in range(n) for k in range(K)),GRB.MAXIMIZE); return m
