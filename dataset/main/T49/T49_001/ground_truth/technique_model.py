import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    zone_count = instance['zone_count']
    station_count = instance['station_count']
    zone_demand = instance['zone_demand']
    station_capacity = instance['station_capacity']
    station_open_cost = instance['station_open_cost']
    eligibility = instance['eligibility']
    assignment_cost = instance['assignment_cost']
    
    model = gp.Model("ChargingStationNetwork")
    
    # Decision variables
    # y[j] = 1 if station j is built, 0 otherwise
    y = model.addVars(station_count, vtype=GRB.BINARY, name="build_station")
    
    # x[i, j] = 1 if zone i is assigned to station j, 0 otherwise
    # Only create variables for eligible (zone, station) pairs to exploit sparsity
    x_indices = [(i, j) for i in range(zone_count) for j in eligibility[i]]
    x = model.addVars(x_indices, vtype=GRB.BINARY, name="assign_zone")
    
    # Objective: Minimize total station opening costs + total assignment costs
    obj = gp.quicksum(station_open_cost[j] * y[j] for j in range(station_count)) + \
          gp.quicksum(assignment_cost[i][j] * x[i, j] for i, j in x_indices)
    model.setObjective(obj, GRB.MINIMIZE)
    
    # Constraints
    
    # 1. Every zone must be assigned exactly once
    for i in range(zone_count):
        model.addConstr(gp.quicksum(x[i, j] for j in eligibility[i]) == 1, name=f"assign_{i}")
        
    # Precompute the list of zones that can be assigned to each station for efficient constraint building
    assigned_to_j = [[] for _ in range(station_count)]
    for i, j in x_indices:
        assigned_to_j[j].append(i)
        
    # 2. Station capacity: sum of demands of assigned zones cannot exceed station capacity
    for j in range(station_count):
        if assigned_to_j[j]:
            model.addConstr(
                gp.quicksum(zone_demand[i] * x[i, j] for i in assigned_to_j[j]) <= station_capacity[j] * y[j],
                name=f"cap_{j}"
            )
            
    # 3. Strong formulation: a zone can only be assigned to a built station
    # This tightens the LP relaxation and helps the solver significantly
    for i, j in x_indices:
        model.addConstr(x[i, j] <= y[j], name=f"strong_{i}_{j}")
        
    return model
