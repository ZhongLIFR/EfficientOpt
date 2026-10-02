import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    records = instance["records"]
    model = gp.Model("quality_controlled_field_tests_linear")
    approved = model.addVars(range(len(records)), vtype=GRB.BINARY, name="quality_gate")
    effort = model.addVars(range(len(records)), lb=0.0, ub={i: row["max_output"] for i, row in enumerate(records)}, name="planned_tests")
    effective = model.addVars(range(len(records)), lb=0.0, ub={i: row["max_output"] for i, row in enumerate(records)}, name="accepted_tests")
    for i, row in enumerate(records):
        upper = float(row["max_output"])
        model.addConstr(effective[i] <= upper * approved[i], name=f"product_upper_gate_{i}")
        model.addConstr(effective[i] <= effort[i], name=f"product_upper_effort_{i}")
        model.addConstr(effective[i] >= effort[i] - upper * (1 - approved[i]), name=f"product_lower_{i}")
    for resource_id, resource in enumerate(instance["resources"]):
        model.addConstr(gp.quicksum(row["effort_use"][resource_id] * effort[i] for i, row in enumerate(records)) <= resource["capacity"], name=f"resource_{resource_id}")
    for group in instance["groups"]:
        indices = [i for i, row in enumerate(records) if row["group"] == group["group"]]
        model.addConstr(gp.quicksum(effective[i] for i in indices) >= group["minimum_accepted"], name=f"minimum_group_{group['group']}")
    model.setObjective(gp.quicksum(row["yield_value"] * effective[i] - row["effort_cost"] * effort[i] - row["activation_fee"] * approved[i] for i, row in enumerate(records)), GRB.MAXIMIZE)
    return model
