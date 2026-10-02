import gurobipy as gp
from gurobipy import GRB


def _costs(instance):
    route_cost = instance["route_cost"]
    n = len(route_cost)
    return {(i, j): float(route_cost[i][j]) for i in range(n) for j in range(n) if i != j}


def build_model(instance):
    """MTZ order-variable formulation for one directed Hamiltonian tour."""
    n = len(instance["city_names"])
    depot = int(instance["depot_city"])
    costs = _costs(instance)
    model = gp.Model("t21_022_mtz")
    x = model.addVars(costs.keys(), vtype=GRB.BINARY, name="x")
    order = {i: model.addVar(lb=0.0, ub=n - 1, name=f"order[{i}]") for i in range(n) if i != depot}

    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if i != j) == 1, name=f"out[{i}]")
        model.addConstr(gp.quicksum(x[j, i] for j in range(n) if i != j) == 1, name=f"in[{i}]")
    for i in range(n):
        if i == depot:
            continue
        for j in range(n):
            if j != depot and i != j:
                model.addConstr(order[i] - order[j] + (n - 1) * x[i, j] <= n - 2,
                                name=f"mtz[{i},{j}]")

    model.setObjective(gp.quicksum(costs[i, j] * x[i, j] for i, j in costs), GRB.MINIMIZE)
    return model
