import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    activities = instance["activities"]
    groups = instance["groups"]
    resources = instance["resources"]
    model = gp.Model("cold_chain_dispatch")
    quantity = model.addVars(
        range(len(activities)),
        lb=0.0,
        ub={i: float(activity["max_hours"]) for i, activity in enumerate(activities)},
        vtype=GRB.CONTINUOUS,
        name="service_hours",
    )
    active = model.addVars(range(len(activities)), vtype=GRB.BINARY, name="selected_block")
    for i, activity in enumerate(activities):
        model.addConstr(
            quantity[i] >= float(activity["min_hours"]) * active[i],
            name=f"minimum_block_{i}",
        )
        model.addConstr(
            quantity[i] <= float(activity["max_hours"]) * active[i],
            name=f"maximum_block_{i}",
        )
    for group in groups:
        indices = [i for i, activity in enumerate(activities) if activity["group"] == group["group"]]
        model.addConstr(
            gp.quicksum(quantity[i] for i in indices) >= float(group["minimum_hours"]),
            name=f"group_floor_{group['group']}",
        )
    for resource_id, resource in enumerate(resources):
        model.addConstr(
            gp.quicksum(
                float(activity["resource_use"][resource_id]) * quantity[i]
                for i, activity in enumerate(activities)
            ) <= float(resource["capacity"]),
            name=f"resource_cap_{resource_id}",
        )
    model.setObjective(
        gp.quicksum(float(activity["value_per_hour"]) * quantity[i] for i, activity in enumerate(activities)),
        GRB.MAXIMIZE,
    )
    return model
