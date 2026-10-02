import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    origins = instance["origin_count"]
    destinations = instance["destination_count"]
    model = gp.Model("integer_distribution_flow")
    flow = model.addVars(range(origins), range(destinations), lb=0.0, vtype=GRB.INTEGER, name="flow")
    for i in range(origins):
        model.addConstr(gp.quicksum(flow[i, j] for j in range(destinations)) == instance["supply"][i], name=f"supply_balance_{i}")
    for j in range(destinations):
        model.addConstr(gp.quicksum(flow[i, j] for i in range(origins)) == instance["demand"][j], name=f"demand_balance_{j}")
    model.setObjective(gp.quicksum(instance["costs"][i][j] * flow[i, j] for i in range(origins) for j in range(destinations)), GRB.MINIMIZE)
    return model
