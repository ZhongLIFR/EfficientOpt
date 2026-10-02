import gurobipy as gp

def build_model(instance):
    clinic_count = instance['clinic_count']
    hub_count = instance['hub_count']
    clinic_demand = instance['clinic_demand']
    hub_capacity = instance['hub_capacity']
    hub_open_cost = instance['hub_open_cost']
    eligibility = instance['eligibility']
    assignment_cost = instance['assignment_cost']
    
    model = gp.Model("Vaccine_Cold_Chain")
    
    # Precompute valid assignments to exploit sparsity
    x_indices = []
    clinics_for_hub = {j: [] for j in range(hub_count)}
    for i in range(clinic_count):
        for j in eligibility[i]:
            x_indices.append((i, j))
            clinics_for_hub[j].append(i)
            
    # Decision variables
    y = model.addVars(hub_count, vtype=gp.GRB.BINARY, name="y")
    x = model.addVars(x_indices, vtype=gp.GRB.BINARY, name="x")
    
    # Objective: Minimize hub opening costs + assignment costs
    obj = gp.quicksum(hub_open_cost[j] * y[j] for j in range(hub_count)) + \
          gp.quicksum(assignment_cost[i][j] * x[i, j] for i, j in x_indices)
    model.setObjective(obj, gp.GRB.MINIMIZE)
    
    # Constraints
    # 1. Each clinic must be assigned to exactly one eligible hub
    model.addConstrs(
        (gp.quicksum(x[i, j] for j in eligibility[i]) == 1 for i in range(clinic_count)),
        name="assign"
    )
        
    # 2. Hub capacity constraints
    for j in range(hub_count):
        if clinics_for_hub[j]:
            model.addConstr(
                gp.quicksum(clinic_demand[i] * x[i, j] for i in clinics_for_hub[j]) <= hub_capacity[j] * y[j],
                name=f"cap_{j}"
            )
        else:
            # If no clinics can be assigned to this hub, force it closed to avoid trivial LP values
            model.addConstr(y[j] == 0, name=f"cap_{j}_empty")
            
    # 3. Strong formulation constraints: clinic can only be assigned to an open hub
    model.addConstrs(
        (x[i, j] <= y[j] for i, j in x_indices),
        name="strong"
    )
        
    return model
