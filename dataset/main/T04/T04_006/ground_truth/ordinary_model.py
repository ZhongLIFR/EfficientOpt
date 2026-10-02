import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Direct integer transportation formulation."""
    supplies = [int(v) for v in instance["supplies"]]
    demands = [int(v) for v in instance["demands"]]
    costs = instance["costs"]
    origins = range(len(supplies))
    destinations = range(len(demands))
    model = gp.Model("integer_transportation")
    shipment = model.addVars(origins, destinations, vtype=GRB.INTEGER, lb=0.0, name="shipment")
    for i in origins:
        model.addConstr(quicksum(shipment[i, j] for j in destinations) == supplies[i])
    for j in destinations:
        model.addConstr(quicksum(shipment[i, j] for i in origins) == demands[j])
    model.setObjective(
        quicksum(float(costs[i][j]) * shipment[i, j] for i in origins for j in destinations),
        GRB.MINIMIZE,
    )
    return model
