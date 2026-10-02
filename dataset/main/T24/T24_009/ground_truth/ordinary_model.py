import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["rows"];n=len(a);x=m.addVars(n,vtype=GRB.INTEGER,lb=0,ub=[r["ux"] for r in a],name="x");y=m.addVars(n,vtype=GRB.INTEGER,lb=0,ub=[r["uy"] for r in a],name="y");z=m.addVars(n,vtype=GRB.INTEGER,lb=0,ub=[r["uz"] for r in a],name="z");m.setObjective(gp.quicksum(r["cx"]*x[i]+r["cy"]*y[i]+r["cz"]*z[i] for i,r in enumerate(a)),GRB.MINIMIZE);m.addConstrs((x[i]+y[i]+z[i]<=a[i]["cap"] for i in range(n)));m.addConstrs((x[i]-y[i]>=a[i]["dxy"] for i in range(n)));m.addConstrs((y[i]-z[i]>=a[i]["dyz"] for i in range(n)));m._v=(x,y,z);m._n=n;return m
def extract_ordinary_solution(m):
 x,y,z=m._v;return {"x":[x[i].X for i in range(m._n)],"y":[y[i].X for i in range(m._n)],"z":[z[i].X for i in range(m._n)]}
