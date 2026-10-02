import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    workshops = instance["workshops"]
    capacities = instance["boiler_capacity"]
    budgets = instance["workshop_carbon_budget"]
    n = len(workshops)
    q = len(workshops[0]["recipes"])

    model = gp.Model("recipe_mix_lagrangian_dual")
    boiler_price = model.addVars(len(capacities), lb=0.0, name="boiler_price")
    carbon_price = model.addVars(n, lb=0.0, name="carbon_price")
    workshop_value = model.addVars(n, lb=-GRB.INFINITY, name="workshop_value")

    for b in range(n):
        for j in range(q):
            recipe = workshops[b]["recipes"][j]
            model.addConstr(
                workshop_value[b]
                + float(recipe["carbon"]) * carbon_price[b]
                + float(recipe["steam"]) * boiler_price[int(recipe["boiler"])]
                >= float(recipe["output"]),
                name=f"recipe_bound[{b},{j}]",
            )

    model.setObjective(
        gp.quicksum(
            workshop_value[b] + float(budgets[b]) * carbon_price[b]
            for b in range(n)
        )
        + gp.quicksum(
            float(capacities[k]) * boiler_price[k]
            for k in range(len(capacities))
        ),
        GRB.MINIMIZE,
    )
    return model
