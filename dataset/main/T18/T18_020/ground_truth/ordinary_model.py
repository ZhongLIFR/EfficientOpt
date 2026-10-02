import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    n = instance["origin_count"]
    model = gp.Model("service_assignment_binary")
    assign = model.addVars(range(n), range(n), vtype=GRB.BINARY, name="assign")
    for i in range(n):
        model.addConstr(gp.quicksum(assign[i, j] for j in range(n)) == 1, name=f"assign_once_{i}")
    for j in range(n):
        model.addConstr(gp.quicksum(assign[i, j] for i in range(n)) <= 1, name=f"destination_capacity_{j}")
    model.setObjective(gp.quicksum(instance["costs"][i][j] * assign[i, j] for i in range(n) for j in range(n)), GRB.MINIMIZE)
    return model
