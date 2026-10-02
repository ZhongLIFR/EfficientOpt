import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_eliminated_variable")
    blocks = instance["blocks"]
    names = instance["variables"]
    eliminated = names[-1]
    kept = names[:-1]
    count = len(blocks)
    quantity = {name: model.addVars(count, vtype=GRB.INTEGER, lb=0, name=name) for name in kept}

    def substitute(block, i):
        equality = block["equality"]
        coefficient = equality["coefficients"][eliminated]
        if coefficient not in (-1, 1):
            raise ValueError("selected equality coefficient must be +1 or -1 for exact integer elimination")
        return (equality["rhs"] - gp.quicksum(equality["coefficients"][name] * quantity[name][i] for name in kept)) / coefficient

    model.setObjective(
        gp.quicksum(
            block["costs"][eliminated] * substitute(block, i)
            + gp.quicksum(block["costs"][name] * quantity[name][i] for name in kept)
            for i, block in enumerate(blocks)
        ),
        GRB.MINIMIZE,
    )
    for i, block in enumerate(blocks):
        eliminated_value = substitute(block, i)
        model.addConstr(eliminated_value >= 0)
        for constraint in block["constraints"]:
            expression = constraint["coefficients"].get(eliminated, 0) * eliminated_value + gp.quicksum(
                constraint["coefficients"].get(name, 0) * quantity[name][i] for name in kept
            )
            if constraint["sense"] == "<=":
                model.addConstr(expression <= constraint["rhs"])
            elif constraint["sense"] == ">=":
                model.addConstr(expression >= constraint["rhs"])
            else:
                raise ValueError("unsupported constraint sense")
    return model
