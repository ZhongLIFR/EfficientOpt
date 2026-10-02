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

    model = gp.Model()

    # Precompute eligible pairs and reverse mapping for capacity constraints
    eligible_pairs = []
    zones_for_station = [[] for _ in range(station_count)]
    for i in range(zone_count):
        for j in eligibility[i]:
            eligible_pairs.append((i, j))
            zones_for_station[j].append(i)

    # Decision variables
    y = model.addVars(station_count, vtype=GRB.BINARY, name="y")
    x = model.addVars(eligible_pairs, vtype=GRB.BINARY, name="x")

    # Objective function
    model.setObjective(
        gp.quicksum(station_open_cost[j] * y[j] for j in range(station_count)) +
        gp.quicksum(assignment_cost[i][j] * x[i, j] for i, j in eligible_pairs),
        GRB.MINIMIZE
    )

    # Assignment constraints: each zone assigned exactly once
    for i in range(zone_count):
        model.addConstr(
            gp.quicksum(x[i, j] for j in eligibility[i]) == 1,
            name=f"assign_{i}"
        )

    # Capacity constraints: total demand <= capacity * open_status
    for j in range(station_count):
        if zones_for_station[j]:
            model.addConstr(
                gp.quicksum(zone_demand[i] * x[i, j] for i in zones_for_station[j]) <= station_capacity[j] * y[j],
                name=f"cap_{j}"
            )

    return model