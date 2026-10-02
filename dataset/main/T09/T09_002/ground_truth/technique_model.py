import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    records = instance["records"]
    model = gp.Model("tiered_service_cost_native_pwl")
    quantity = model.addVars(
        range(len(records)),
        lb=0.0,
        ub={i: records[i]["breakpoints"][-1] for i in range(len(records))},
        name="quantity",
    )
    cost = model.addVars(range(len(records)), lb=-GRB.INFINITY, name="cost")
    for i, row in enumerate(records):
        model.addGenConstrPWL(quantity[i], cost[i], row["breakpoints"], row["values"], name=f"native_curve_{i}")
    for group in instance["groups"]:
        indices = [i for i, row in enumerate(records) if row["group"] == group["group"]]
        model.addConstr(gp.quicksum(quantity[i] for i in indices) >= group["minimum_quantity"], name=f"group_min_{group['group']}")
    for resource_id, resource in enumerate(instance["resources"]):
        model.addConstr(gp.quicksum(row["resource_use"][resource_id] * quantity[i] for i, row in enumerate(records)) <= resource["capacity"], name=f"resource_{resource_id}")
    model.addConstr(gp.quicksum(quantity[i] for i in range(len(records))) >= instance["total_required"], name="total_requirement")
    model.setObjective(gp.quicksum(cost[i] for i in range(len(records))), GRB.MINIMIZE)
    return model
