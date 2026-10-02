import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Exact LP relaxation using transportation total unimodularity."""
    supplies = [int(v) for v in instance["supplies"]]
    demands = [int(v) for v in instance["demands"]]
    costs = instance["costs"]
    origins = range(len(supplies))
    destinations = range(len(demands))
    model = gp.Model("transportation_tu_relaxation")
    shipment = model.addVars(origins, destinations, lb=0.0, name="shipment")
    for i in origins:
        model.addConstr(quicksum(shipment[i, j] for j in destinations) == supplies[i])
    # The final demand equation is implied by total supply equaling total demand.
    for j in range(len(demands) - 1):
        model.addConstr(quicksum(shipment[i, j] for i in origins) == demands[j])
    model.setObjective(
        quicksum(float(costs[i][j]) * shipment[i, j] for i in origins for j in destinations),
        GRB.MINIMIZE,
    )
    return model
