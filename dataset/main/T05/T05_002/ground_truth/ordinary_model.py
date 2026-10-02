import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    m = gp.Model()
    
    projects = instance['projects']
    district_caps = instance.get('district_intensity_caps', {})
    total_cap = instance['total_intensity_cap']
    agreements = instance['community_agreements']
    min_agreements = instance['minimum_agreements_honoured']
    
    # Precompute effective maximum intensities for tighter Big-M
    eff_max_int = {}
    for p in projects:
        pid = p['id']
        d = p['district']
        cap_d = district_caps.get(d, float('inf'))
        eff_max_int[pid] = min(p['maximum_intensity'], total_cap, cap_d)
        
    # Variables
    x = {}
    for p in projects:
        x[p['id']] = m.addVar(
            lb=0, 
            ub=p['maximum_intensity'], 
            vtype=GRB.CONTINUOUS, 
            name=f"x_{p['id']}"
        )
        
    y = {}
    for a in agreements:
        y[a['id']] = m.addVar(vtype=GRB.BINARY, name=f"y_{a['id']}")
        
    # Objective
    m.setObjective(
        gp.quicksum(p['public_value_per_unit'] * x[p['id']] for p in projects), 
        GRB.MAXIMIZE
    )
    
    # Total cap
    m.addConstr(gp.quicksum(x.values()) <= total_cap, name="total_cap")
    
    # District caps
    district_projects = {}
    for p in projects:
        d = p['district']
        if d not in district_projects:
            district_projects[d] = []
        district_projects[d].append(p['id'])
        
    for d, cap in district_caps.items():
        if d in district_projects:
            m.addConstr(
                gp.quicksum(x[pid] for pid in district_projects[d]) <= cap, 
                name=f"dist_cap_{d}"
            )
            
    # Agreements
    for a in agreements:
        aid = a['id']
        limit = a['disruption_limit']
        coeffs = a['disruption_coefficients']
        
        max_disruption = 0
        for pid, coef in coeffs.items():
            if coef > 0 and pid in eff_max_int:
                max_disruption += coef * eff_max_int[pid]
                
        if max_disruption <= limit:
            m.addConstr(y[aid] == 1, name=f"always_honoured_{aid}")
        else:
            M = max_disruption - limit
            expr = gp.quicksum(coef * x[pid] for pid, coef in coeffs.items() if pid in x)
            m.addConstr(expr <= limit + M * (1 - y[aid]), name=f"agreement_{aid}")
            
    # Min agreements honoured
    m.addConstr(gp.quicksum(y.values()) >= min_agreements, name="min_agreements")
    
    return m
