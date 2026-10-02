import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    W = instance['workload_count']
    C = instance['datacenter_count']
    capacity = instance['datacenter_capacity']
    fixed_cost = instance['fixed_assignment_cost']
    coord_benefit = instance['coordination_benefit']
    network_cost = instance['network_pair_cost']

    pairs_raw = instance['data_exchange_pairs']
    if pairs_raw and isinstance(pairs_raw[0], dict):
        pairs = [(p['i'], p['j'], p['volume']) for p in pairs_raw]
    else:
        pairs = [(p[0], p[1], p[2]) for p in pairs_raw]

    model = gp.Model()
    model.Params.NonConvex = 2

    x = model.addVars(W, C, vtype=GRB.BINARY, name='x')

    # Precompute non-zero off-diagonal network cost coefficients
    net_coeffs = []
    for c in range(C):
        row = network_cost[c]
        for k in range(C):
            if c != k:
                cost = row[k]
                if cost != 0.0:
                    net_coeffs.append((c, k, cost))

    # Linear part: fixed assignment costs
    lin_coeffs = []
    lin_vars = []
    for i in range(W):
        row = fixed_cost[i]
        for c in range(C):
            lin_coeffs.append(row[c])
            lin_vars.append(x[i, c])
    obj = gp.QuadExpr()
    obj.add(gp.LinExpr(lin_coeffs, lin_vars))
    obj.addConstant(-sum(coord_benefit))

    # Quadratic part: network exchange costs
    if net_coeffs:
        q_coeffs = []
        q_vars1 = []
        q_vars2 = []
        for i, j, volume in pairs:
            if volume == 0:
                continue
            for c, k, base in net_coeffs:
                q_coeffs.append(base * volume)
                q_vars1.append(x[i, c])
                q_vars2.append(x[j, k])
        if q_coeffs:
            obj.addTerms(q_coeffs, q_vars1, q_vars2)

    model.setObjective(obj, GRB.MINIMIZE)

    # Assignment constraints
    model.addConstrs(
        (gp.quicksum(x[i, c] for c in range(C)) == 1 for i in range(W)),
        name='assign'
    )
    # Capacity constraints
    model.addConstrs(
        (gp.quicksum(x[i, c] for i in range(W)) <= capacity[c] for c in range(C)),
        name='cap'
    )

    return model