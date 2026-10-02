import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("bulk_vessel_loading")
    
    holds_data = instance["holds"]
    cargo_lots_data = instance["cargo_lots"]
    handling_costs_data = instance["handling_costs"]
    
    # Build lookup dictionaries for efficient access
    hold_info = {h["id"]: h for h in holds_data}
    lot_info = {l["id"]: l for l in cargo_lots_data}
    
    # Build sparse handling cost lookup
    handling_cost_map = {}
    for rec in handling_costs_data:
        handling_cost_map[(rec["cargo_lot"], rec["hold"])] = rec["handling_cost_per_tonne"]
    
    # Get all hold IDs and cargo lot IDs
    hold_ids = [h["id"] for h in holds_data]
    lot_ids = [l["id"] for l in cargo_lots_data]
    
    # Decision variables
    # Binary: is hold h prepared?
    y = model.addVars(hold_ids, vtype=GRB.BINARY, name="prepare")
    
    # Continuous: tonnes of lot l loaded in hold h (only for valid pairs)
    valid_pairs = list(handling_cost_map.keys())
    x = model.addVars(valid_pairs, vtype=GRB.CONTINUOUS, lb=0.0, name="load")
    
    # Objective: minimize total cost
    prep_cost = gp.quicksum(hold_info[h]["preparation_cost"] * y[h] for h in hold_ids)
    handling_cost = gp.quicksum(handling_cost_map[pair] * x[pair] for pair in valid_pairs)
    model.setObjective(prep_cost + handling_cost, GRB.MINIMIZE)
    
    # Constraint 1: Demand satisfaction for each cargo lot
    for lot_id in lot_ids:
        # Find all valid holds for this lot
        lot_pairs = [(l, h) for (l, h) in valid_pairs if l == lot_id]
        model.addConstr(
            gp.quicksum(x[pair] for pair in lot_pairs) == lot_info[lot_id]["required_tonnes"],
            name=f"demand_{lot_id}"
        )
    
    # Constraint 2: Weight capacity for each hold
    for hold_id in hold_ids:
        # Find all lots that can go in this hold
        hold_pairs = [(l, h) for (l, h) in valid_pairs if h == hold_id]
        if hold_pairs:
            model.addConstr(
                gp.quicksum(x[pair] for pair in hold_pairs) <= hold_info[hold_id]["weight_capacity_tonnes"],
                name=f"weight_{hold_id}"
            )
    
    # Constraint 3: Volume capacity for each hold
    for hold_id in hold_ids:
        # Find all lots that can go in this hold
        hold_pairs = [(l, h) for (l, h) in valid_pairs if h == hold_id]
        if hold_pairs:
            model.addConstr(
                gp.quicksum(lot_info[l]["volume_per_tonne_m3"] * x[(l, h)] for (l, h) in hold_pairs) <= hold_info[hold_id]["volume_capacity_m3"],
                name=f"volume_{hold_id}"
            )
    
    # Constraint 4: Preparation linking (cargo can only be loaded if hold is prepared)
    for (lot_id, hold_id) in valid_pairs:
        # Use the lot's required tonnes as big-M
        model.addConstr(
            x[(lot_id, hold_id)] <= lot_info[lot_id]["required_tonnes"] * y[hold_id],
            name=f"prep_{lot_id}_{hold_id}"
        )
    
    return model