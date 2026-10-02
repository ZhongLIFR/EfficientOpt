import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["rows"];n=len(a);x=[m.addVars(n,vtype=GRB.INTEGER,lb=0,name=f"x{k}") for k in range(4)];m.setObjective(gp.quicksum(a[i][f"c{k+1}"]*x[k][i] for i in range(n) for k in range(4)),GRB.MINIMIZE);m.addConstrs((x[0][i]+x[1][i]<=a[i]["cap12"] for i in range(n)));m.addConstrs((x[2][i]+x[3][i]<=a[i]["cap34"] for i in range(n)));m.addConstrs((x[2][i]-x[0][i]>=a[i]["d3"] for i in range(n)));m.addConstrs((x[3][i]-x[1][i]>=a[i]["d4"] for i in range(n)));m._x=x;m._n=n;return m
def extract_ordinary_solution(m):return {f"x{k+1}":[m._x[k][i].X for i in range(m._n)] for k in range(4)}
