import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["rows"];n=len(a);x=m.addVars(n,vtype=GRB.INTEGER,lb=0,ub=[r["ux"] for r in a],name="x");y=m.addVars(n,vtype=GRB.INTEGER,lb=0,ub=[r["uy"] for r in a],name="y");m.setObjective(gp.quicksum(r["cx"]*x[i]+r["cy"]*y[i] for i,r in enumerate(a)),GRB.MINIMIZE);m.addConstrs((10*x[i]+15*y[i]==a[i]["rhs"] for i in range(n)));m.addConstrs((x[i]-y[i]>=a[i]["gap"] for i in range(n)));m._v=(x,y);m._n=n;return m
def extract_technique_solution(m):
 x,y=m._v;return {"x":[x[i].X for i in range(m._n)],"y":[y[i].X for i in range(m._n)]}
