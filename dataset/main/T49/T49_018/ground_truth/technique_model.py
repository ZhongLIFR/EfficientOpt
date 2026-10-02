import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("water_treatment_commissioning")
    
    # Parse instance data
    modules = instance["treatment_modules"]
    sectors = instance["demand_sectors"]
    treatment_costs = instance["treatment_costs"]
    incompatible_pairs = instance["incompatible_module_pairs"]
    
    # Build lookup dictionaries
    module_dict = {m["id"]: m for m in modules}
    sector_dict = {s["id"]: s for s in sectors}
    
    # Build sparse treatment cost dictionary for valid (sector, module) pairs
    cost_dict = {}
    for tc in treatment_costs:
        cost_dict[(tc["demand_sector"], tc["treatment_module"])] = tc["treatment_cost_per_unit"]
    
    # Valid (sector, module) pairs - use treatment_costs as the sparse structure
    valid_pairs = list(cost_dict.keys())
    
    # Decision variables
    # Binary: commission module m
    y = model.addVars(
        (m["id"] for m in modules),
        vtype=GRB.BINARY,
        name="commission"
    )
    
    # Continuous: water units from module m to sector s (only for valid pairs)
    x = model.addVars(
        valid_pairs,
        lb=0.0,
        vtype=GRB.CONTINUOUS,
        name="flow"
    )
    
    # Objective: minimize commissioning + treatment costs
    commission_cost = gp.quicksum(
        module_dict[m["id"]]["commissioning_cost"] * y[m["id"]]
        for m in modules
    )
    
    treatment_cost = gp.quicksum(
        cost_dict[s_id, m_id] * x[s_id, m_id]
        for s_id, m_id in valid_pairs
    )
    
    model.setObjective(commission_cost + treatment_cost, GRB.MINIMIZE)
    
    # Constraint 1: Demand satisfaction
    # Each sector must receive its full required water units
    for s in sectors:
        s_id = s["id"]
        # Find all modules that can supply this sector (from valid_pairs)
        supply_modules = [m_id for (sec_id, m_id) in valid_pairs if sec_id == s_id]
        model.addConstr(
            gp.quicksum(x[s_id, m_id] for m_id in supply_modules) == s["required_water_units"],
            name=f"demand_{s_id}"
        )
    
    # Constraint 2: Treatment capacity
    # Total water supplied by module m cannot exceed its treatment capacity
    for m in modules:
        m_id = m["id"]
        # Find all sectors that this module supplies (from valid_pairs)
        supplied_sectors = [s_id for (s_id, mod_id) in valid_pairs if mod_id == m_id]
        if supplied_sectors:  # Only add constraint if module has potential flows
            model.addConstr(
                gp.quicksum(x[s_id, m_id] for s_id in supplied_sectors) <= m["treatment_capacity_units"],
                name=f"treat_cap_{m_id}"
            )
    
    # Constraint 3: Chemical capacity
    # Total chemical points used by module m cannot exceed its chemical capacity
    for m in modules:
        m_id = m["id"]
        # Find all sectors that this module supplies
        supplied_sectors = [s_id for (s_id, mod_id) in valid_pairs if mod_id == m_id]
        if supplied_sectors:
            model.addConstr(
                gp.quicksum(
                    sector_dict[s_id]["chemical_points_per_unit"] * x[s_id, m_id]
                    for s_id in supplied_sectors
                ) <= m["chemical_capacity_points"],
                name=f"chem_cap_{m_id}"
            )
    
    # Constraint 4: Incompatibility
    # At most one module from each incompatible pair can be commissioned
    for pair in incompatible_pairs:
        m1_id = pair[0]
        m2_id = pair[1]
        model.addConstr(
            y[m1_id] + y[m2_id] <= 1,
            name=f"incompat_{m1_id}_{m2_id}"
        )
    
    # Constraint 5: Linking
    # Module must be commissioned to supply water
    # x[s,m] <= required_water_units[s] * y[m]
    for s_id, m_id in valid_pairs:
        model.addConstr(
            x[s_id, m_id] <= sector_dict[s_id]["required_water_units"] * y[m_id],
            name=f"link_{s_id}_{m_id}"
        )
    
    return model
