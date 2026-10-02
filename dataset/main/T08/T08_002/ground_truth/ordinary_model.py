import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    records = instance["records"]
    model = gp.Model("adaptive_processing_options")
    enabled = model.addVars(range(len(records)), vtype=GRB.BINARY, name="enabled")
    amount = model.addVars(range(len(records)), lb=0.0, ub={i: row["max_units"] for i, row in enumerate(records)}, name="base_units")
    saleable = model.addVars(range(len(records)), lb=0.0, ub={i: row["max_units"] for i, row in enumerate(records)}, name="saleable_units")
    for i, row in enumerate(records):
        model.addQConstr(saleable[i] == enabled[i] * amount[i], name=f"activation_product_{i}")
    for resource_id, resource in enumerate(instance["resources"]):
        model.addConstr(gp.quicksum(row["resource_use"][resource_id] * amount[i] for i, row in enumerate(records)) <= resource["capacity"], name=f"resource_{resource_id}")
    for group in instance["groups"]:
        indices = [i for i, row in enumerate(records) if row["group"] == group["group"]]
        model.addConstr(gp.quicksum(saleable[i] for i in indices) >= group["minimum_sale"], name=f"minimum_sale_{group['group']}")
    model.setObjective(gp.quicksum(row["unit_value"] * saleable[i] - row["unit_cost"] * amount[i] - row["fixed_cost"] * enabled[i] for i, row in enumerate(records)), GRB.MAXIMIZE)
    model.Params.NonConvex = 2
    return model
