import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """Full McCormick formulation for this fixed-schema assignment QAP."""
    n = int(instance["warehouse_count"])
    m = int(instance["center_count"])
    capacity = instance["center_capacity"]
    fixed = instance["fixed_assignment_cost"]
    benefit = instance["coordination_benefit"]
    pair_cost = instance["network_pair_cost"]

    model = gp.Model("t10_020_ordinary_mccormick")
    x = model.addVars(n, m, vtype=GRB.BINARY, name="assign")
    model.addConstrs((gp.quicksum(x[i, c] for c in range(m)) == 1 for i in range(n)), name="once")
    model.addConstrs((gp.quicksum(x[i, c] for i in range(n)) <= capacity[c] for c in range(m)), name="capacity")

    objective = gp.quicksum((fixed[i][c] - benefit[i]) * x[i, c] for i in range(n) for c in range(m))
    for edge in instance["data_exchange_pairs"]:
        i, j, volume = int(edge["i"]), int(edge["j"]), float(edge["volume"])
        z = model.addVars(m, m, lb=0.0, ub=1.0, name=f"pair_{i}_{j}")
        model.addConstrs((z[c, k] <= x[i, c] for c in range(m) for k in range(m)), name=f"upper_i_{i}_{j}")
        model.addConstrs((z[c, k] <= x[j, k] for c in range(m) for k in range(m)), name=f"upper_j_{i}_{j}")
        model.addConstrs((z[c, k] >= x[i, c] + x[j, k] - 1 for c in range(m) for k in range(m)), name=f"lower_{i}_{j}")
        objective += gp.quicksum(volume * pair_cost[c][k] * z[c, k] for c in range(m) for k in range(m))

    model.setObjective(objective, GRB.MINIMIZE)
    return model

