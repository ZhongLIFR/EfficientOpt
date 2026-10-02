"""Reference extensive-form builder for T16, used for objective checks."""

from __future__ import annotations

import gurobipy as gp


def build_model(instance):
    f = int(instance["facility_count"])
    s_count = int(instance["scenario_count"])
    hire = [float(v) for v in instance["hire_cost"]]
    capacity = [float(v) for v in instance["capacity"]]
    demand = [float(v) for v in instance["demand"]]
    availability = instance["availability"]
    service_cost = instance["service_cost"]
    penalty = float(instance["shortage_penalty"])
    if len(hire) != f or len(capacity) != f:
        raise ValueError("facility arrays do not match facility_count")
    if len(demand) != s_count or len(availability) != s_count or len(service_cost) != s_count:
        raise ValueError("scenario arrays do not match scenario_count")
    if any(len(row) != f for row in availability) or any(len(row) != f for row in service_cost):
        raise ValueError("scenario matrices do not match facility_count")

    model = gp.Model("t16_reference_extensive_form")
    open_facility = model.addVars(f, vtype=gp.GRB.BINARY, name="open")
    flow = model.addVars(s_count, f, lb=0.0, name="flow")
    shortage = model.addVars(s_count, lb=0.0, name="shortage")
    for scen in range(s_count):
        served = gp.LinExpr()
        for fac in range(f):
            served += flow[scen, fac]
            model.addConstr(
                flow[scen, fac]
                <= float(availability[scen][fac]) * capacity[fac] * open_facility[fac],
                name=f"capacity[{scen},{fac}]",
            )
        model.addConstr(served + shortage[scen] >= demand[scen], name=f"demand[{scen}]")
    probability = 1.0 / s_count
    expr = gp.quicksum(hire[fac] * open_facility[fac] for fac in range(f))
    for scen in range(s_count):
        expr += probability * penalty * shortage[scen]
        for fac in range(f):
            expr += probability * float(service_cost[scen][fac]) * flow[scen, fac]
    model.setObjective(expr, gp.GRB.MINIMIZE)
    return model
