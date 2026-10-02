import gurobipy as gp
from gurobipy import GRB


def _costs(instance):
    route_cost = instance["route_cost"]
    n = len(route_cost)
    return {(i, j): float(route_cost[i][j]) for i in range(n) for j in range(n) if i != j}


def build_model(instance):
    """Single-commodity-flow formulation for one directed Hamiltonian tour."""
    n = len(instance["city_names"])
    depot = int(instance["depot_city"])
    costs = _costs(instance)
    model = gp.Model("t21_022_scf")
    x = model.addVars(costs.keys(), vtype=GRB.BINARY, name="x")
    flow = model.addVars(costs.keys(), lb=0.0, ub=n - 1, name="flow")

    for i in range(n):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n) if i != j) == 1, name=f"out[{i}]")
        model.addConstr(gp.quicksum(x[j, i] for j in range(n) if i != j) == 1, name=f"in[{i}]")
    for i, j in costs:
        model.addConstr(flow[i, j] <= (n - 1) * x[i, j], name=f"link[{i},{j}]")
    for v in range(n):
        if v == depot:
            continue
        model.addConstr(
            gp.quicksum(flow[i, v] for i in range(n) if i != v)
            - gp.quicksum(flow[v, j] for j in range(n) if j != v) == 1,
            name=f"flow_balance[{v}]",
        )

    model.setObjective(gp.quicksum(costs[i, j] * x[i, j] for i, j in costs), GRB.MINIMIZE)
    return model
