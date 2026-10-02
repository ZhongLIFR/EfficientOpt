import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    records = instance["records"]
    model = gp.Model("tiered_service_cost_explicit")
    quantity = model.addVars(
        range(len(records)),
        lb=0.0,
        ub={i: records[i]["breakpoints"][-1] for i in range(len(records))},
        name="quantity",
    )
    cost = model.addVars(range(len(records)), lb=-GRB.INFINITY, name="cost")
    for i, row in enumerate(records):
        points = row["breakpoints"]
        values = row["values"]
        widths = [points[k + 1] - points[k] for k in range(len(points) - 1)]
        slopes = [(values[k + 1] - values[k]) / widths[k] for k in range(len(widths))]
        segment = model.addVars(range(len(widths)), vtype=GRB.BINARY, name=f"segment_{i}")
        theta = model.addVars(range(len(widths)), lb=0.0, ub={k: widths[k] for k in range(len(widths))}, name=f"within_segment_{i}")
        model.addConstr(gp.quicksum(segment[k] for k in range(len(widths))) == 1, name=f"one_segment_{i}")
        for k, width in enumerate(widths):
            model.addConstr(theta[k] <= width * segment[k], name=f"segment_bound_{i}_{k}")
        model.addConstr(quantity[i] == gp.quicksum(points[k] * segment[k] + theta[k] for k in range(len(widths))), name=f"quantity_link_{i}")
        model.addConstr(cost[i] == gp.quicksum(values[k] * segment[k] + slopes[k] * theta[k] for k in range(len(widths))), name=f"cost_link_{i}")
    for group in instance["groups"]:
        indices = [i for i, row in enumerate(records) if row["group"] == group["group"]]
        model.addConstr(gp.quicksum(quantity[i] for i in indices) >= group["minimum_quantity"], name=f"group_min_{group['group']}")
    for resource_id, resource in enumerate(instance["resources"]):
        model.addConstr(gp.quicksum(row["resource_use"][resource_id] * quantity[i] for i, row in enumerate(records)) <= resource["capacity"], name=f"resource_{resource_id}")
    model.addConstr(gp.quicksum(quantity[i] for i in range(len(records))) >= instance["total_required"], name="total_requirement")
    model.setObjective(gp.quicksum(cost[i] for i in range(len(records))), GRB.MINIMIZE)
    return model
