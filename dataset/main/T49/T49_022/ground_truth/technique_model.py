import gurobipy as gp

def build_model(instance):
    commodities = instance['commodities']
    network_arcs = instance['network_arcs']
    network_nodes = instance['network_nodes']

    num_arcs = len(network_arcs)
    num_commodities = len(commodities)
    capacity = 1500

    # Precompute arc data as flat lists
    sources = [a['source'] for a in network_arcs]
    targets = [a['target'] for a in network_arcs]
    fixed_costs = [a['fixed_cost'] for a in network_arcs]
    var_costs = [a['var_cost'] for a in network_arcs]

    # Precompute adjacency lists: node_id -> list of arc indices
    outgoing = {}
    incoming = {}
    for n in network_nodes:
        nid = n['node_id']
        outgoing[nid] = []
        incoming[nid] = []

    for i in range(num_arcs):
        outgoing[sources[i]].append(i)
        incoming[targets[i]].append(i)

    # Commodity data as flat lists
    origins = [c['origin'] for c in commodities]
    dests = [c['destination'] for c in commodities]
    demands = [c['demand'] for c in commodities]

    model = gp.Model()

    # Binary variables: y[i] = 1 if arc i is opened
    y = model.addVars(num_arcs, vtype=gp.GRB.BINARY, name="y")

    # Continuous flow variables: f[i,k] = flow of commodity k on arc i
    f = model.addVars(num_arcs, num_commodities, lb=0.0, name="f")

    # Objective: minimize fixed opening costs + variable flow costs
    model.setObjective(
        gp.quicksum(fixed_costs[i] * y[i] for i in range(num_arcs))
        + gp.quicksum(var_costs[i] * f[i, k]
                       for i in range(num_arcs)
                       for k in range(num_commodities)),
        gp.GRB.MINIMIZE
    )

    # Flow conservation for each commodity k at each node
    for k in range(num_commodities):
        o, d, dem = origins[k], dests[k], demands[k]
        for n in network_nodes:
            nid = n['node_id']
            if nid == o and nid == d:
                rhs = 0
            elif nid == o:
                rhs = dem
            elif nid == d:
                rhs = -dem
            else:
                rhs = 0

            out_arcs = outgoing[nid]
            in_arcs = incoming[nid]

            # Skip trivially satisfied constraints
            if not out_arcs and not in_arcs and rhs == 0:
                continue

            model.addConstr(
                gp.quicksum(f[i, k] for i in out_arcs)
                - gp.quicksum(f[i, k] for i in in_arcs)
                == rhs
            )

    # Shared capacity: total flow on arc i cannot exceed capacity * y[i]
    for i in range(num_arcs):
        model.addConstr(
            gp.quicksum(f[i, k] for k in range(num_commodities))
            <= capacity * y[i]
        )

    # Variable upper bounds: f[i,k] <= demand[k] * y[i]
    # Strengthens LP relaxation by linking each commodity flow to arc opening
    model.addConstrs(
        (f[i, k] <= demands[k] * y[i]
         for i in range(num_arcs)
         for k in range(num_commodities)),
        name="vub"
    )

    return model