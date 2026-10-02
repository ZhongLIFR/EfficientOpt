def build_model(instance):
    import gurobipy as gp
    from gurobipy import GRB

    dist = instance['distance']
    n = len(dist)
    customers = range(1, n)
    m_customers = n - 1

    model = gp.Model('single_vehicle_delivery_tour')

    # Directed arcs excluding self-loops.
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]

    # Flow is needed only on arcs whose head is a customer; no flow returns to depot.
    flow_arcs = [(i, j) for i in range(n) for j in range(1, n) if i != j]

    x = model.addVars(arcs, vtype=GRB.BINARY, name='x')

    # Arc-specific upper bounds tighten the single-commodity flow formulation.
    # At most m_customers units can leave the depot; after visiting at least one
    # customer, at most m_customers - 1 units remain on customer-to-customer arcs.
    f_ub = {}
    for i, j in flow_arcs:
        f_ub[(i, j)] = float(m_customers if i == 0 else max(m_customers - 1, 0))
    f = model.addVars(flow_arcs, lb=0.0, ub=f_ub, vtype=GRB.CONTINUOUS, name='f')

    # Objective: total travel cost.
    model.setObjective(
        gp.quicksum(float(dist[i][j]) * x[i, j] for i, j in arcs),
        GRB.MINIMIZE
    )

    # Precompute sparse adjacency lists for efficient constraint construction.
    out_x = [[] for _ in range(n)]
    in_x = [[] for _ in range(n)]
    for i, j in arcs:
        out_x[i].append((i, j))
        in_x[j].append((i, j))

    out_f = [[] for _ in range(n)]
    in_f = [[] for _ in range(n)]
    for i, j in flow_arcs:
        out_f[i].append((i, j))
        in_f[j].append((i, j))

    # Degree constraints: every node has exactly one successor and one predecessor.
    model.addConstrs(
        (gp.quicksum(x[a] for a in out_x[i]) == 1 for i in range(n)),
        name='out_degree'
    )
    model.addConstrs(
        (gp.quicksum(x[a] for a in in_x[j]) == 1 for j in range(n)),
        name='in_degree'
    )

    # Flow conservation: depot-originated commodity supplies one unit to each customer.
    model.addConstrs(
        (
            gp.quicksum(f[a] for a in in_f[k]) - gp.quicksum(f[a] for a in out_f[k]) == 1
            for k in customers
        ),
        name='flow_conservation'
    )

    # Flow can occur only on selected travel arcs.
    model.addConstrs(
        (f[i, j] <= f_ub[(i, j)] * x[i, j] for i, j in flow_arcs),
        name='flow_link'
    )

    # Deterministic greedy MIP start for a feasible tour; does not change the model.
    if n > 1:
        unvisited = set(range(1, n))
        tour = [0]
        cur = 0
        while unvisited:
            nxt = min(unvisited, key=lambda j: (float(dist[cur][j]), j))
            tour.append(nxt)
            unvisited.remove(nxt)
            cur = nxt
        tour.append(0)
        selected = set(zip(tour[:-1], tour[1:]))
        for a in arcs:
            x[a].Start = 1.0 if a in selected else 0.0

    # Attach useful handles for external solution extraction.
    model._x = x
    model._flow = f
    model._nodes = list(range(n))
    model._arcs = arcs

    model.update()
    return model
