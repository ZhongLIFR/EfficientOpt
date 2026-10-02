import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    activities = instance["activities"]
    groups = instance["groups"]
    resources = instance["resources"]
    model = gp.Model("neighborhood_repair_packages_sos")
    selected = model.addVars(range(len(activities)), vtype=GRB.BINARY, name="package_selected")
    for group in groups:
        indices = [i for i, activity in enumerate(activities) if activity["district"] == group["district"]]
        model.addConstr(gp.quicksum(selected[i] for i in indices) >= group["minimum_selected"], name=f"district_min_{group['district']}")
        model.addSOS(GRB.SOS_TYPE1, [selected[i] for i in indices], list(range(len(indices))))
    for resource_id, resource in enumerate(resources):
        model.addConstr(
            gp.quicksum(float(activity["crew_load"][resource_id]) * selected[i] for i, activity in enumerate(activities)) <= resource["capacity"],
            name=f"crew_resource_{resource_id}",
        )
    model.setObjective(gp.quicksum(float(activity["priority_score"]) * selected[i] for i, activity in enumerate(activities)), GRB.MAXIMIZE)
    return model
