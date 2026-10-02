import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["rows"];n=len(a);x1=m.addVars(n,vtype=GRB.INTEGER,lb=[r["d1"] for r in a],name="x1");x2=m.addVars(n,vtype=GRB.INTEGER,lb=[r["d2"] for r in a],name="x2");m.setObjective(gp.quicksum(a[i]["c1"]*x1[i]+a[i]["c2"]*x2[i] for i in range(n)),GRB.MINIMIZE);m.addConstrs((x1[i]+x2[i]<=a[i]["cap12"] for i in range(n)));m._x=(x1,x2);m._n=n;return m
def extract_technique_solution(m):
 x1,x2=m._x;return {"x1":[x1[i].X for i in range(m._n)],"x2":[x2[i].X for i in range(m._n)],"x3":[0.]*m._n,"x4":[0.]*m._n}
