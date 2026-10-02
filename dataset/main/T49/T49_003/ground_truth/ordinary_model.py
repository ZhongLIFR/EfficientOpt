import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    clinics = instance['clinics']
    patients = instance['patients']
    assign_data = instance['assignment_costs']
    
    n_c = len(clinics)
    n_p = len(patients)
    
    c_ids = [c['id'] for c in clinics]
    p_ids = [p['id'] for p in patients]
    c_map = {cid: i for i, cid in enumerate(c_ids)}
    p_map = {pid: i for i, pid in enumerate(p_ids)}
    
    cap = [c['capacity_minutes'] for c in clinics]
    open_cost = [c['opening_cost'] for c in clinics]
    treat = [p['treatment_minutes'] for p in patients]
    
    p_to_c = [[] for _ in range(n_p)]
    c_to_p = [[] for _ in range(n_c)]
    pairs = []
    costs = []
    
    for rec in assign_data:
        pi = p_map[rec['patient']]
        ci = c_map[rec['clinic']]
        pairs.append((pi, ci))
        costs.append(rec['cost'])
        p_to_c[pi].append(ci)
        c_to_p[ci].append(pi)
        
    m = gp.Model()
    
    x = m.addVars(pairs, vtype=GRB.BINARY, name="x")
    y = m.addVars(range(n_c), vtype=GRB.BINARY, name="y")
    
    obj = gp.quicksum(open_cost[c] * y[c] for c in range(n_c)) + \
          gp.quicksum(costs[i] * x[pairs[i]] for i in range(len(pairs)))
    m.setObjective(obj, GRB.MINIMIZE)
    
    m.addConstrs(
        (gp.quicksum(x[p, c] for c in p_to_c[p]) == 1 for p in range(n_p)),
        name="assign"
    )
    
    m.addConstrs(
        (gp.quicksum(treat[p] * x[p, c] for p in c_to_p[c]) <= cap[c] * y[c] for c in range(n_c)),
        name="cap"
    )
    
    return m