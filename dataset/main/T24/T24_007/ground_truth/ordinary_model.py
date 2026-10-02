import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 m=gp.Model();a=d["farms"];n=len(a);c=m.addVars(n,vtype=GRB.INTEGER,lb=0,name="corn");w=m.addVars(n,vtype=GRB.INTEGER,lb=0,name="wheat");s=m.addVars(n,vtype=GRB.INTEGER,lb=0,name="soy");m.setObjective(gp.quicksum(r["corn_cost"]*c[i]+r["wheat_cost"]*w[i]+r["soy_cost"]*s[i] for i,r in enumerate(a)),GRB.MINIMIZE);m.addConstrs((2*c[i]+w[i]>=a[i]["food_requirement"] for i in range(n)));m.addConstrs((w[i]+s[i]<=a[i]["soil_capacity"] for i in range(n)));m.addConstrs((c[i]-s[i]>=a[i]["corn_over_soy"] for i in range(n)));m._v=(c,w,s);m._n=n;return m
def extract_ordinary_solution(m):
 c,w,s=m._v;return {"corn":[c[i].X for i in range(m._n)],"wheat":[w[i].X for i in range(m._n)],"soy":[s[i].X for i in range(m._n)]}
