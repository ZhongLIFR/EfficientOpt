import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 n=len(d["units"]); K=d["options_per_unit"]; m=gp.Model("portfolio_technique")
 y=m.addVars(n,K,vtype=GRB.BINARY,name="choose")
 m.addConstrs((gp.quicksum(y[i,k] for k in range(K))==1 for i in range(n)),name="choose_one")
 m.addConstr(gp.quicksum(d["units"][i]["options"][k]["capacity"]*y[i,k] for i in range(n) for k in range(K))>=d["minimum_total_capacity"],name="minimum_capacity")
 m.addConstr(gp.quicksum(d["units"][i]["options"][k]["risk"]*y[i,k] for i in range(n) for k in range(K))<=d["maximum_total_risk"],name="maximum_risk")
 m.setObjective(gp.quicksum(d["units"][i]["options"][k]["value"]*y[i,k] for i in range(n) for k in range(K)),GRB.MAXIMIZE); return m
