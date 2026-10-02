import gurobipy as gp

def build_model(instance):
    # Parse input data
    fleet_groups = instance['fleet_groups']
    route_programmes = instance['route_programmes']
    operating_costs = instance['operating_costs']

    # Index mappings
    fg_id_to_idx = {fg['id']: i for i, fg in enumerate(fleet_groups)}
    route_id_to_idx = {rp['id']: i for i, rp in enumerate(route_programmes)}

    n_fg = len(fleet_groups)
    n_routes = len(route_programmes)

    # Fleet group data arrays
    flight_hour_capacity = [0] * n_fg
    maintenance_point_capacity = [0] * n_fg
    readiness_cost = [0] * n_fg
    for fg in fleet_groups:
        idx = fg_id_to_idx[fg['id']]
        flight_hour_capacity[idx] = fg['flight_hour_capacity']
        maintenance_point_capacity[idx] = fg['maintenance_point_capacity']
        readiness_cost[idx] = fg['readiness_cost']

    # Route data arrays
    required_flight_hours = [0] * n_routes
    maintenance_points_per_hour = [0] * n_routes
    for rp in route_programmes:
        idx = route_id_to_idx[rp['id']]
        required_flight_hours[idx] = rp['required_flight_hours']
        maintenance_points_per_hour[idx] = rp['maintenance_points_per_hour']

    # Allowed (route, fleet) pairs with operating cost
    allowed = {}  # (r_idx, g_idx) -> operating_cost_per_hour
    for oc in operating_costs:
        r = route_id_to_idx[oc['route']]
        g = fg_id_to_idx[oc['fleet_group']]
        allowed[(r, g)] = oc['operating_cost_per_hour']

    # Build adjacency lists for efficient constraint construction
    route_to_fleet = {r: [] for r in range(n_routes)}
    fleet_to_route = {g: [] for g in range(n_fg)}
    for (r, g) in allowed.keys():
        route_to_fleet[r].append(g)
        fleet_to_route[g].append(r)

    # Create model
    model = gp.Model()

    # Decision variables
    y = model.addVars(n_fg, vtype=gp.GRB.BINARY, name='y')
    x = model.addVars(allowed.keys(), vtype=gp.GRB.CONTINUOUS, lb=0, name='x')

    # Objective
    obj = gp.quicksum(readiness_cost[i] * y[i] for i in range(n_fg))
    obj += gp.quicksum(allowed[(r, g)] * x[(r, g)] for (r, g) in allowed.keys())
    model.setObjective(obj, gp.GRB.MINIMIZE)

    # Route hour requirement constraints
    for r in range(n_routes):
        expr = gp.quicksum(x[(r, g)] for g in route_to_fleet[r])
        model.addConstr(expr == required_flight_hours[r], name=f'route_hours_{r}')

    # Fleet flight-hour capacity constraints
    for g in range(n_fg):
        expr = gp.quicksum(x[(r, g)] for r in fleet_to_route[g])
        model.addConstr(expr <= flight_hour_capacity[g] * y[g], name=f'fleet_capacity_{g}')

    # Fleet maintenance-point capacity constraints
    for g in range(n_fg):
        expr = gp.quicksum(x[(r, g)] * maintenance_points_per_hour[r] for r in fleet_to_route[g])
        model.addConstr(expr <= maintenance_point_capacity[g] * y[g], name=f'maint_capacity_{g}')

    model.update()
    return model
