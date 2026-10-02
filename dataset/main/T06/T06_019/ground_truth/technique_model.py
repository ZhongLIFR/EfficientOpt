import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    activities = instance["activities"]
    groups = instance["groups"]
    resources = instance["resources"]
    model = gp.Model("cold_chain_dispatch_native_domain")
    quantity = model.addVars(
        range(len(activities)),
        vtype=GRB.CONTINUOUS,
        name="service_hours",
    )
    for i, activity in enumerate(activities):
        quantity[i].VType = GRB.SEMICONT
        quantity[i].LB = float(activity["min_hours"])
        quantity[i].UB = float(activity["max_hours"])
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
