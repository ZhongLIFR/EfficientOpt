import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    records = instance["records"]
    resources = instance["resources"]
    model = gp.Model("dual_feature_packages_linear")
    first = model.addVars(range(len(records)), vtype=GRB.BINARY, name="feature_a")
    second = model.addVars(range(len(records)), vtype=GRB.BINARY, name="feature_b")
    joint = model.addVars(range(len(records)), vtype=GRB.BINARY, name="joint_feature")
    for i in range(len(records)):
        model.addConstr(joint[i] <= first[i], name=f"product_upper_a_{i}")
        model.addConstr(joint[i] <= second[i], name=f"product_upper_b_{i}")
        model.addConstr(joint[i] >= first[i] + second[i] - 1, name=f"product_lower_{i}")
    for resource_id, resource in enumerate(resources):
        model.addConstr(
            gp.quicksum(float(row["load_a"][resource_id]) * first[i] + float(row["load_b"][resource_id]) * second[i] for i, row in enumerate(records))
            <= float(resource["capacity"]),
            name=f"capacity_{resource_id}",
        )
    for group in instance["groups"]:
        indices = [i for i, row in enumerate(records) if row["group"] == group["group"]]
        model.addConstr(gp.quicksum(first[i] for i in indices) <= group["max_a"], name=f"group_a_{group['group']}")
        model.addConstr(gp.quicksum(second[i] for i in indices) <= group["max_b"], name=f"group_b_{group['group']}")
    model.setObjective(
        gp.quicksum(
            float(row["joint_value"]) * joint[i]
            - float(row["cost_a"]) * first[i]
            - float(row["cost_b"]) * second[i]
            for i, row in enumerate(records)
        ),
        GRB.MAXIMIZE,
    )
    return model
