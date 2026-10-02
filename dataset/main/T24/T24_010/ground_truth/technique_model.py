import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["rows"];n=len(a);x3=m.addVars(n,vtype=GRB.INTEGER,lb=[r["d3"] for r in a],name="x3");x4=m.addVars(n,vtype=GRB.INTEGER,lb=[r["d4"] for r in a],name="x4");m.setObjective(gp.quicksum(a[i]["c3"]*x3[i]+a[i]["c4"]*x4[i] for i in range(n)),GRB.MINIMIZE);m.addConstrs((x3[i]+x4[i]<=a[i]["cap34"] for i in range(n)));m._x=(x3,x4);m._n=n;return m
def extract_technique_solution(m):
 x3,x4=m._x;return {"x1":[0.]*m._n,"x2":[0.]*m._n,"x3":[x3[i].X for i in range(m._n)],"x4":[x4[i].X for i in range(m._n)]}
