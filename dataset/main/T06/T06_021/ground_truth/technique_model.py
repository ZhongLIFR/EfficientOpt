import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    activities = instance["activities"]
    groups = instance["groups"]
    resources = instance["resources"]
    model = gp.Model("telemetry_inspection_shifts_native_domain")
    shift = model.addVars(range(len(activities)), vtype=GRB.CONTINUOUS, name="inspection_shift")
    for i, activity in enumerate(activities):
        shift[i].VType = GRB.SEMICONT
        shift[i].LB = float(activity["minimum_shift"])
        shift[i].UB = float(activity["maximum_shift"])
    for group in groups:
        indices = [i for i, activity in enumerate(activities) if activity["zone"] == group["zone"]]
        model.addConstr(gp.quicksum(shift[i] for i in indices) >= group["minimum_service"], name=f"zone_{group['zone']}")
    for resource_id, resource in enumerate(resources):
        model.addConstr(
            gp.quicksum(float(activity["resource_demand"][resource_id]) * shift[i] for i, activity in enumerate(activities)) <= resource["capacity"],
            name=f"sensor_resource_{resource_id}",
        )
    model.setObjective(gp.quicksum(float(activity["service_value"]) * shift[i] for i, activity in enumerate(activities)), GRB.MAXIMIZE)
    return model
