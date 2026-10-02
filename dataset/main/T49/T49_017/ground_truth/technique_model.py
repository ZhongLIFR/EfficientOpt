import gurobipy as gp

def build_model(instance):
    depots = instance['depots']
    maintenance_bases = instance['maintenance_bases']
    replenishment_costs = instance['replenishment_costs']

    # Precompute depot data
    depot_ids = [d['id'] for d in depots]
    depot_opening_cost = {d['id']: d['opening_cost'] for d in depots}
    depot_throughput = {d['id']: d['throughput_capacity_units'] for d in depots}
    depot_handling_cap = {d['id']: d['handling_capacity_points'] for d in depots}

    # Precompute base data
    base_ids = [b['id'] for b in maintenance_bases]
    base_demand = {b['id']: b['required_part_units'] for b in maintenance_bases}
    base_handling_ppu = {b['id']: b['handling_points_per_unit'] for b in maintenance_bases}
    base_eligible = {b['id']: b['eligible_depots'] for b in maintenance_bases}

    # Build replenishment cost lookup and eligible pair list
    replen_cost = {}
    for r in replenishment_costs:
        replen_cost[(r['maintenance_base'], r['depot'])] = r['replenishment_cost_per_unit']

    # Build eligible pairs list and reverse index: depot -> list of bases
    eligible_pairs = []
    depot_to_bases = {d_id: [] for d_id in depot_ids}
    for b_id in base_ids:
        for d_id in base_eligible[b_id]:
            eligible_pairs.append((b_id, d_id))
            depot_to_bases[d_id].append(b_id)

    # Create model
    model = gp.Model()

    # Binary variables for depot opening
    y = model.addVars(depot_ids, vtype=gp.GRB.BINARY, name="y")

    # Continuous variables for shipments with upper bounds
    x = model.addVars(
        eligible_pairs,
        vtype=gp.GRB.CONTINUOUS,
        lb=0,
        ub={pair: base_demand[pair[0]] for pair in eligible_pairs},
        name="x"
    )

    # Objective: opening costs + replenishment costs
    model.setObjective(
        gp.quicksum(depot_opening_cost[d_id] * y[d_id] for d_id in depot_ids)
        + gp.quicksum(replen_cost[pair] * x[pair] for pair in eligible_pairs),
        gp.GRB.MINIMIZE
    )

    # Demand satisfaction: each base receives its full required units
    for b_id in base_ids:
        model.addConstr(
            gp.quicksum(x[b_id, d_id] for d_id in base_eligible[b_id])
            == base_demand[b_id],
            name=f"demand_{b_id}"
        )

    # Linking constraints: depot must be open to ship to any base
    for b_id, d_id in eligible_pairs:
        model.addConstr(
            x[b_id, d_id] <= base_demand[b_id] * y[d_id],
            name=f"link_{b_id}_{d_id}"
        )

    # Throughput capacity: total units shipped from depot <= capacity
    for d_id in depot_ids:
        bases = depot_to_bases[d_id]
        if bases:
            model.addConstr(
                gp.quicksum(x[b_id, d_id] for b_id in bases)
                <= depot_throughput[d_id],
                name=f"throughput_{d_id}"
            )

    # Handling capacity: total handling points from depot <= capacity
    for d_id in depot_ids:
        bases = depot_to_bases[d_id]
        if bases:
            model.addConstr(
                gp.quicksum(base_handling_ppu[b_id] * x[b_id, d_id] for b_id in bases)
                <= depot_handling_cap[d_id],
                name=f"handling_{d_id}"
            )

    return model