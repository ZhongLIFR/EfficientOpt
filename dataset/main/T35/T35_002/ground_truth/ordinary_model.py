import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t35_full_variables")
    blocks = instance["blocks"]
    names = instance["variables"]
    count = len(blocks)
    quantity = {name: model.addVars(count, vtype=GRB.INTEGER, lb=0, name=name) for name in names}
    model.setObjective(
        gp.quicksum(block["costs"][name] * quantity[name][i] for i, block in enumerate(blocks) for name in names),
        GRB.MINIMIZE,
    )
    for i, block in enumerate(blocks):
        equality = block["equality"]
        model.addConstr(gp.quicksum(equality["coefficients"][name] * quantity[name][i] for name in names) == equality["rhs"])
        for constraint in block["constraints"]:
            expression = gp.quicksum(constraint["coefficients"].get(name, 0) * quantity[name][i] for name in names)
            if constraint["sense"] == "<=":
                model.addConstr(expression <= constraint["rhs"])
            elif constraint["sense"] == ">=":
                model.addConstr(expression >= constraint["rhs"])
            else:
                raise ValueError("unsupported constraint sense")
    return model
