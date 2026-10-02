def build_model(instance):
    import gurobipy as gp
    from gurobipy import GRB

    # Parse modules
    treatment_modules = instance["treatment_modules"]
    M = len(treatment_modules)
    module_ids = [m["id"] for m in treatment_modules]
    module_id_to_idx = {mid: idx for idx, mid in enumerate(module_ids)}
    module_cap = [m["treatment_capacity_units"] for m in treatment_modules]
    module_chem_cap = [m["chemical_capacity_points"] for m in treatment_modules]
    module_comm_cost = [m["commissioning_cost"] for m in treatment_modules]

    # Parse sectors
    demand_sectors = instance["demand_sectors"]
    S = len(demand_sectors)
    sector_ids = [s["id"] for s in demand_sectors]
    sector_id_to_idx = {sid: idx for idx, sid in enumerate(sector_ids)}
    sector_demand = [s["required_water_units"] for s in demand_sectors]
    sector_chem_per_unit = [s["chemical_points_per_unit"] for s in demand_sectors]

    # Parse allowed pairs (treatment_costs)
    treatment_costs = instance["treatment_costs"]
    allowed_pairs = []
    sector_to_modules = [[] for _ in range(S)]
    module_to_sectors = [[] for _ in range(M)]
    for record in treatment_costs:
        sector_id = record["demand_sector"]
        module_id = record["treatment_module"]
        cost = record["treatment_cost_per_unit"]
        i = module_id_to_idx[module_id]
        j = sector_id_to_idx[sector_id]
        allowed_pairs.append((i, j, cost))
        sector_to_modules[j].append((i, cost))
        module_to_sectors[i].append((j, cost))

    # Parse incompatible pairs
    incompatible_pairs = instance["incompatible_module_pairs"]
    incompatible_pairs_idx = []
    for pair in incompatible_pairs:
        i1_id = pair[0]
        i2_id = pair[1]
        i1 = module_id_to_idx[i1_id]
        i2 = module_id_to_idx[i2_id]
        incompatible_pairs_idx.append((i1, i2))

    # Create model
    model = gp.Model()

    # Add binary commissioning variables
    y = model.addVars(M, vtype=GRB.BINARY, obj=module_comm_cost, name="y")

    # Add continuous flow variables
    x = {}
    for (i, j, cost) in allowed_pairs:
        x[i, j] = model.addVar(obj=cost, lb=0, vtype=GRB.CONTINUOUS, name=f"x_{i}_{j}")

    # Add demand constraints
    for j in range(S):
        vars_list = [x[i, j] for (i, cost) in sector_to_modules[j]]
        demand = sector_demand[j]
        model.addConstr(gp.quicksum(vars_list) == demand, name=f"demand_{j}")

    # Add module treatment capacity constraints
    for i in range(M):
        vars_list = [x[i, j] for (j, cost) in module_to_sectors[i]]
        cap = module_cap[i]
        y_i = y[i]
        model.addConstr(gp.quicksum(vars_list) <= cap * y_i, name=f"capacity_{i}")

    # Add module chemical capacity constraints
    for i in range(M):
        expr = gp.quicksum(sector_chem_per_unit[j] * x[i, j] for (j, cost) in module_to_sectors[i])
        chem_cap = module_chem_cap[i]
        y_i = y[i]
        model.addConstr(expr <= chem_cap * y_i, name=f"chem_capacity_{i}")

    # Add incompatibility constraints
    for (i1, i2) in incompatible_pairs_idx:
        model.addConstr(y[i1] + y[i2] <= 1, name=f"incompatible_{i1}_{i2}")

    # Set objective sense
    model.setAttr(GRB.Attr.ModelSense, GRB.MINIMIZE)

    # Update model
    model.update()

    return model