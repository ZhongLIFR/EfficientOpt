import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 a=d['units']; n=len(a); m=gp.Model('allocation_technique'); x=m.addVars(n,lb=0,ub={i:a[i]['breakpoints'][-1] for i in range(n)},name='quantity'); cost=m.addVars(n,lb=0,name='cost')
 for i in range(n):
  value=0
  for k,slope in enumerate(a[i]['slopes']): m.addConstr(cost[i]>=slope*x[i]+value-slope*a[i]['breakpoints'][k]); value+=slope*(a[i]['breakpoints'][k+1]-a[i]['breakpoints'][k])
 m.addConstrs((gp.quicksum(x[i] for i in range(n) if a[i]['group']==g)>=d['group_minimum_quantity'][g] for g in range(d['group_count'])),name='group_minimum')
 m.addConstrs((gp.quicksum(a[i]['resource_use_per_quantity'][r]*x[i] for i in range(n))<=d['resource_capacities'][r] for r in range(len(d['resource_capacities']))),name='shared_resource')
 m.setObjective(gp.quicksum(cost.values()),GRB.MINIMIZE); return m
