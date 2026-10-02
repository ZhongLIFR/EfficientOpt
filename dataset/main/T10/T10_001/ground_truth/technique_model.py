import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    W = instance["workload_count"]
    D = instance["datacenter_count"]
    cap = instance["datacenter_capacity"]
    fac = instance["fixed_assignment_cost"]
    cb = instance["coordination_benefit"]
    npc = instance["network_pair_cost"]
    deps = instance["data_exchange_pairs"]
    
    model = gp.Model("cross_datacenter_workload_assignment")
    
    # Variables
    # x[i, c] = 1 if workload i is assigned to datacenter c
    x = model.addVars(W, D, vtype=GRB.BINARY, name="x")
    
    # Constraints
    # 1. Each workload must be assigned to exactly one datacenter
    model.addConstrs((x.sum(i, '*') == 1 for i in range(W)), name="assign")
    
    # 2. Datacenter capacity cannot be exceeded
    model.addConstrs((x.sum('*', c) <= cap[c] for c in range(D)), name="cap")
    
    obj = gp.LinExpr()
    
    # Hosting cost minus coordination credit
    for i in range(W):
        for c in range(D):
            # Handle potential 1D or 2D array formats for fixed_assignment_cost
            cost = fac[i][c] if isinstance(fac[i], (list, tuple)) else fac[i]
            obj += (cost - cb[i]) * x[i, c]
            
    # Network cost
    for p_idx, pair in enumerate(deps):
        i = pair["i"]
        j = pair["j"]
        vol = pair["volume"]
        
        # Skip if workloads are the same or volume is zero
        if i == j or vol == 0:
            continue
            
        # z_p[c, k] = 1 if workload i is at c and workload j is at k
        z_p = model.addVars(D, D, vtype=GRB.CONTINUOUS, lb=0, ub=1, name=f"z_{p_idx}")
        
        # Linearization constraints for the quadratic assignment
        model.addConstrs((z_p.sum(c, '*') == x[i, c] for c in range(D)), name=f"z_sum_k_{p_idx}")
        model.addConstrs((z_p.sum('*', k) == x[j, k] for k in range(D)), name=f"z_sum_c_{p_idx}")
        
        # Add to objective (cost is zero if c == k)
        for c in range(D):
            for k in range(D):
                if c != k:
                    obj += vol * npc[c][k] * z_p[c, k]
                    
    model.setObjective(obj, GRB.MINIMIZE)
    
    return model
