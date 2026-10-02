import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    workshops = instance["workshops"]
    capacities = instance["boiler_capacity"]
    budgets = instance["workshop_carbon_budget"]
    n = len(workshops)
    q = len(workshops[0]["recipes"])

    model = gp.Model("recipe_mix_primal")
    weight = model.addVars(n, q, lb=0.0, ub=1.0, name="recipe_weight")
    model.addConstrs((weight.sum(b, "*") == 1.0 for b in range(n)), name="mix")
    model.addConstrs(
        (
            gp.quicksum(
                float(workshops[b]["recipes"][j]["carbon"]) * weight[b, j]
                for j in range(q)
            )
            <= float(budgets[b])
            for b in range(n)
        ),
        name="carbon_budget",
    )
    for k, capacity in enumerate(capacities):
        model.addConstr(
            gp.quicksum(
                float(workshops[b]["recipes"][j]["steam"]) * weight[b, j]
                for b in range(n)
                for j in range(q)
                if int(workshops[b]["recipes"][j]["boiler"]) == k
            )
            <= float(capacity),
            name=f"boiler_capacity[{k}]",
        )
    model.setObjective(
        gp.quicksum(
            float(workshops[b]["recipes"][j]["output"]) * weight[b, j]
            for b in range(n)
            for j in range(q)
        ),
        GRB.MAXIMIZE,
    )
    return model
