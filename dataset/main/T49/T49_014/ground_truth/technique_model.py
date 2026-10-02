import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    fleet_groups = instance["fleet_groups"]
    route_programmes = instance["route_programmes"]
    operating_costs = instance["operating_costs"]

    fleet_ids = [g["id"] for g in fleet_groups]
    route_ids = [r["id"] for r in route_programmes]

    fleet_data = {g["id"]: g for g in fleet_groups}
    route_data = {r["id"]: r for r in route_programmes}

    required_hours = {r["id"]: float(r["required_flight_hours"]) for r in route_programmes}
    maint_per_hour = {r["id"]: float(r["maintenance_points_per_hour"]) for r in route_programmes}
    eligible = {r["id"]: set(r.get("eligible_fleet_groups", ())) for r in route_programmes}

    # Build the sparse arc set from the explicitly supplied cost table, retaining only valid eligible pairs.
    # If duplicate cost rows were ever supplied, keep the last value; the schema states one row per allowed pair.
    cost = {}
    route_to_arcs = {r: [] for r in route_ids}
    fleet_to_arcs = {g: [] for g in fleet_ids}
    fleet_id_set = set(fleet_ids)
    route_id_set = set(route_ids)

    for rec in operating_costs:
        r = rec["route"]
        g = rec["fleet_group"]
        if r in route_id_set and g in fleet_id_set and g in eligible[r]:
            arc = (r, g)
            if arc not in cost:
                route_to_arcs[r].append(arc)
                fleet_to_arcs[g].append(arc)
            cost[arc] = float(rec["operating_cost_per_hour"])

    arcs = list(cost.keys())

    m = gp.Model("airline_fleet_readiness_route_hours")

    y_obj = {g: float(fleet_data[g]["readiness_cost"]) for g in fleet_ids}
    y = m.addVars(fleet_ids, vtype=GRB.BINARY, obj=y_obj, name="ready")
    x = m.addVars(arcs, lb=0.0, vtype=GRB.CONTINUOUS, obj=cost, name="hours")

    # Every route programme receives exactly its required flight-hours.
    for r in route_ids:
        m.addConstr(
            gp.quicksum(x[arc] for arc in route_to_arcs[r]) == required_hours[r],
            name="route_hours[%s]" % r,
        )

    # Fleet-group readiness-linked flight-hour and maintenance capacities.
    for g in fleet_ids:
        arcs_g = fleet_to_arcs[g]
        flight_cap = float(fleet_data[g]["flight_hour_capacity"])
        maint_cap = float(fleet_data[g]["maintenance_point_capacity"])

        m.addConstr(
            gp.quicksum(x[arc] for arc in arcs_g) <= flight_cap * y[g],
            name="flight_capacity[%s]" % g,
        )
        m.addConstr(
            gp.quicksum(maint_per_hour[arc[0]] * x[arc] for arc in arcs_g) <= maint_cap * y[g],
            name="maintenance_capacity[%s]" % g,
        )

    # Strengthening: no route can assign more than its demand to a non-ready/fractionally-ready group.
    for r, g in arcs:
        m.addConstr(
            x[r, g] <= required_hours[r] * y[g],
            name="link[%s,%s]" % (r, g),
        )

    m.ModelSense = GRB.MINIMIZE

    # Attach useful handles for downstream solution reporting by the executor, without affecting optimization.
    m._ready_vars = y
    m._hour_vars = x
    m._fleet_ids = fleet_ids
    m._route_ids = route_ids
    m._arcs = arcs

    return m
