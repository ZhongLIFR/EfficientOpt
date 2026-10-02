import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 a=d['units']; n=len(a); S=4; m=gp.Model('allocation_ordinary')
 seg=m.addVars(n,S,lb=0,ub={(i,k):a[i]['breakpoints'][k+1]-a[i]['breakpoints'][k] for i in range(n) for k in range(S)},name='segment'); fill=m.addVars(n,S-1,vtype=GRB.BINARY,name='filled')
 x={i:gp.quicksum(seg[i,k] for k in range(S)) for i in range(n)}
 for i in range(n):
  for k in range(S-1): m.addConstr(seg[i,k]>=(a[i]['breakpoints'][k+1]-a[i]['breakpoints'][k])*fill[i,k]); m.addConstr(seg[i,k+1]<=(a[i]['breakpoints'][k+2]-a[i]['breakpoints'][k+1])*fill[i,k])
 m.addConstrs((gp.quicksum(x[i] for i in range(n) if a[i]['group']==g)>=d['group_minimum_quantity'][g] for g in range(d['group_count'])),name='group_minimum')
 m.addConstrs((gp.quicksum(a[i]['resource_use_per_quantity'][r]*x[i] for i in range(n))<=d['resource_capacities'][r] for r in range(len(d['resource_capacities']))),name='shared_resource')
 m.setObjective(gp.quicksum(a[i]['slopes'][k]*seg[i,k] for i in range(n) for k in range(S)),GRB.MINIMIZE); return m
