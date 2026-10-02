import gurobipy as gp
from gurobipy import GRB
def build_model(d):
 T=d['period_count']; I=len(d['activities']); a=d['activities']; m=gp.Model('campaign_technique'); q=m.addVars(T,I,lb=0,ub={(t,i):a[i]['maximum_quantity'] for t in range(T) for i in range(I)},name='quantity'); b=m.addVars(T,vtype=GRB.BINARY,name='bonus'); credit=m.addVars(T,lb=0,name='credited_spend')
 eligible={t:gp.quicksum(a[i]['eligible_spend_per_unit']*q[t,i] for i in range(I)) for t in range(T)}
 for t,p in enumerate(d['periods']):
  m.addConstr(gp.quicksum(a[i]['resource_a_use']*q[t,i] for i in range(I))<=p['resource_a_capacity']); m.addConstr(gp.quicksum(a[i]['resource_b_use']*q[t,i] for i in range(I))<=p['resource_b_capacity']); m.addConstr(eligible[t]>=p['bonus_threshold']*b[t]); m.addConstr(eligible[t]<=p['bonus_threshold']+(p['eligible_spend_upper_bound']-p['bonus_threshold'])*b[t]); m.addConstr(credit[t]<=eligible[t]); m.addConstr(credit[t]<=p['eligible_spend_upper_bound']*b[t]); m.addConstr(credit[t]>=eligible[t]-p['eligible_spend_upper_bound']*(1-b[t]))
 m.addConstrs((gp.quicksum(q[t,i] for t in range(T))<=d['activity_total_limits'][i] for i in range(I)),name='activity_total')
 m.addConstrs((gp.quicksum(d['periods'][t]['campaign_resource_coeffs'][r]*q[t,i] for t in range(T) for i in range(I))<=d['campaign_resource_limits'][r] for r in range(len(d['campaign_resource_limits']))),name='campaign_resource')
 m.setObjective(gp.quicksum(a[i]['base_margin_per_unit']*q[t,i] for t in range(T) for i in range(I))+d['bonus_rate']*gp.quicksum(credit.values()),GRB.MAXIMIZE); return m
