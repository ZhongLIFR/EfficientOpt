import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    items = instance["items"]
    count = int(instance["container_count"])
    capacity = float(instance["container_capacity"])
    keys = [(i, b) for i in range(len(items)) for b in range(i + 1)]
    model = gp.Model("canonical_container_assignment")
    assign = model.addVars(keys, vtype=GRB.BINARY, name="assign")
    used = model.addVars(range(count), vtype=GRB.BINARY, name="used")
    for i in range(len(items)):
        model.addConstr(gp.quicksum(assign[i, b] for b in range(min(count, i + 1))) == 1, name=f"item_once_{i}")
    for b in range(count):
        model.addConstr(gp.quicksum(items[i]["size"] * assign[i, b] for i in range(b, len(items))) <= capacity * used[b], name=f"capacity_{b}")
        for i in range(b, len(items)):
            model.addConstr(assign[i, b] <= used[b], name=f"activate_{i}_{b}")
    for b in range(count - 1):
        model.addConstr(used[b] >= used[b + 1], name=f"prefix_{b}")
    model.setObjective(gp.quicksum(used[b] for b in range(count)), GRB.MINIMIZE)
    return model
