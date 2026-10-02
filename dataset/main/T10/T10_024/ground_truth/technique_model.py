import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """Row-column marginal convex-hull formulation for this fixed-schema assignment QAP."""
    n = int(len(instance["departments"]))
    m = int(len(instance["cities"]))
    capacity = instance["city_capacity"]
    fixed = instance["fixed_assignment_cost"]
    benefit = instance["relocation_benefit"]
    pair_cost = instance["city_pair_cost"]

    model = gp.Model("t10_024_technique_convex_hull")
    x = model.addVars(n, m, vtype=GRB.BINARY, name="assign")
    model.addConstrs((gp.quicksum(x[i, c] for c in range(m)) == 1 for i in range(n)), name="once")
    model.addConstrs((gp.quicksum(x[i, c] for i in range(n)) <= capacity[c] for c in range(m)), name="capacity")

    objective = gp.quicksum((fixed[i][c] - benefit[i]) * x[i, c] for i in range(n) for c in range(m))
    for edge in instance["communication_edges"]:
        i, j, volume = int(edge["i"]), int(edge["j"]), float(edge["volume"])
        z = model.addVars(m, m, lb=0.0, ub=1.0, name=f"pair_{i}_{j}")
        model.addConstrs((gp.quicksum(z[c, k] for k in range(m)) == x[i, c] for c in range(m)), name=f"row_{i}_{j}")
        model.addConstrs((gp.quicksum(z[c, k] for c in range(m)) == x[j, k] for k in range(m)), name=f"column_{i}_{j}")
        objective += gp.quicksum(volume * pair_cost[c][k] * z[c, k] for c in range(m) for k in range(m))

    model.setObjective(objective, GRB.MINIMIZE)
    return model

