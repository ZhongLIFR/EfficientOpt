def build_model(instance):
    import gurobipy as gp
    from gurobipy import GRB

    shelters = instance.get('shelters', [])
    zones = instance.get('evacuation_zones', [])
    cost_rows = instance.get('provision_costs', [])

    shelter_ids = [s['id'] for s in shelters]
    zone_ids = [z['id'] for z in zones]

    shelter_data = {s['id']: s for s in shelters}
    zone_data = {z['id']: z for z in zones}

    demand = {z['id']: float(z['required_provision_units']) for z in zones}
    med_per_unit = {z['id']: float(z['medical_points_per_unit']) for z in zones}
    prov_cap = {s['id']: float(s['provision_capacity_units']) for s in shelters}
    med_cap = {s['id']: float(s['medical_capacity_points']) for s in shelters}
    open_cost = {s['id']: float(s['opening_cost']) for s in shelters}

    # Respect the explicit eligibility lists while using provision_costs as the sparse arc/cost table.
    eligible = {z['id']: set(z.get('eligible_shelters', [])) for z in zones}
    valid_shelters = set(shelter_ids)
    valid_zones = set(zone_ids)

    cost = {}
    arcs_by_zone = {z: [] for z in zone_ids}
    arcs_by_shelter = {s: [] for s in shelter_ids}

    for r in cost_rows:
        z = r['evacuation_zone']
        s = r['shelter']
        if z not in valid_zones or s not in valid_shelters:
            continue
        if s not in eligible.get(z, ()):
            continue
        a = (z, s)
        if a in cost:
            # The schema states one record per allowed pair; if duplicates appear, keep the last cost.
            cost[a] = float(r['provision_cost_per_unit'])
        else:
            cost[a] = float(r['provision_cost_per_unit'])
            arcs_by_zone[z].append(a)
            arcs_by_shelter[s].append(a)

    arcs = list(cost.keys())

    m = gp.Model('disaster_shelter_opening_and_provisioning')

    y = m.addVars(shelter_ids, vtype=GRB.BINARY, obj=open_cost, name='open')

    ub = {a: demand[a[0]] for a in arcs}
    x = m.addVars(arcs, lb=0.0, ub=ub, vtype=GRB.CONTINUOUS, obj=cost, name='alloc')

    m.ModelSense = GRB.MINIMIZE

    # Every evacuation zone receives exactly its required provision units.
    for z in zone_ids:
        m.addConstr(
            gp.quicksum(x[a] for a in arcs_by_zone[z]) == demand[z],
            name='demand[%s]' % z
        )

    # Shelter provision and medical capacities, active only when opened.
    for s in shelter_ids:
        inc = arcs_by_shelter[s]
        if inc:
            m.addConstr(
                gp.quicksum(x[a] for a in inc) <= prov_cap[s] * y[s],
                name='provision_capacity[%s]' % s
            )
            m.addConstr(
                gp.quicksum(med_per_unit[a[0]] * x[a] for a in inc) <= med_cap[s] * y[s],
                name='medical_capacity[%s]' % s
            )
        else:
            # If a shelter has no allowed assignments, keep the binary for complete reporting.
            # Positive opening costs will naturally leave it closed; negative costs, if any, remain modelled correctly.
            pass

    # Pair-level linking strengthens the LP relaxation and explicitly forbids service from closed shelters.
    m.addConstrs(
        (x[a] <= demand[a[0]] * y[a[1]] for a in arcs),
        name='open_link'
    )

    # Attach useful handles for downstream reporting by the executor.
    m._open_vars = y
    m._allocation_vars = x
    m._shelter_ids = shelter_ids
    m._zone_ids = zone_ids
    m._arcs = arcs
    m._arcs_by_zone = arcs_by_zone
    m._arcs_by_shelter = arcs_by_shelter

    return m
