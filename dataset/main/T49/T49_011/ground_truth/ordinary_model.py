def build_model(instance):
    import gurobipy as gp

    # Extract data
    holds = instance["holds"]
    cargo_lots = instance["cargo_lots"]
    handling_costs = instance["handling_costs"]

    # Index mappings
    hold_ids = [h["id"] for h in holds]
    lot_ids = [c["id"] for c in cargo_lots]
    hold_index = {hid: i for i, hid in enumerate(hold_ids)}
    lot_index = {lid: i for i, lid in enumerate(lot_ids)}

    # Hold parameters
    weight_cap = {h["id"]: h["weight_capacity_tonnes"] for h in holds}
    volume_cap = {h["id"]: h["volume_capacity_m3"] for h in holds}
    prep_cost = {h["id"]: h["preparation_cost"] for h in holds}

    # Lot parameters
    required = {c["id"]: c["required_tonnes"] for c in cargo_lots}
    vol_per_tonne = {c["id"]: c["volume_per_tonne_m3"] for c in cargo_lots}

    # Allowed lot‑hold pairs and handling costs
    allowed = {}
    lot_to_holds = {}
    hold_to_lots = {}
    for rec in handling_costs:
        lid = rec["cargo_lot"]
        hid = rec["hold"]
        cost = rec["handling_cost_per_tonne"]
        allowed[(lid, hid)] = cost
        lot_to_holds.setdefault(lid, []).append(hid)
        hold_to_lots.setdefault(hid, []).append(lid)

    # Build model
    model = gp.Model()

    # Decision variables
    x = model.addVars(hold_ids, vtype=gp.GRB.BINARY, name="prepare")
    y = model.addVars(allowed.keys(), vtype=gp.GRB.CONTINUOUS, lb=0.0, name="load")

    # Objective
    model.setObjective(
        gp.quicksum(prep_cost[h] * x[h] for h in hold_ids) +
        gp.quicksum(cost * y[key] for key, cost in allowed.items()),
        sense=gp.GRB.MINIMIZE
    )

    # Lot demand constraints
    for lid in lot_ids:
        holds_list = lot_to_holds.get(lid, [])
        model.addConstr(
            gp.quicksum(y[(lid, h)] for h in holds_list) == required[lid],
            name=f"demand_{lid}"
        )

    # Hold weight capacity constraints
    for hid in hold_ids:
        lots_list = hold_to_lots.get(hid, [])
        model.addConstr(
            gp.quicksum(y[(l, hid)] for l in lots_list) <= weight_cap[hid] * x[hid],
            name=f"weight_{hid}"
        )

    # Hold volume capacity constraints
    for hid in hold_ids:
        lots_list = hold_to_lots.get(hid, [])
        if lots_list:
            expr = gp.quicksum(y[(l, hid)] * vol_per_tonne[l] for l in lots_list)
        else:
            expr = 0
        model.addConstr(expr <= volume_cap[hid] * x[hid], name=f"volume_{hid}")

    model.update()
    return model
