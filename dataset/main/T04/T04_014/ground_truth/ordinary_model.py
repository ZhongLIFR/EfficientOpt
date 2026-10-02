import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model()
    rows = instance["rows"]
    category_count = len(instance["categories"])
    x = model.addVars(len(rows), category_count, vtype=GRB.INTEGER, lb=0.0, name="x")
    for i, row in enumerate(rows):
        if not (len(row["lb"]) == len(row["ub"]) == len(row["cost"]) == category_count):
            raise ValueError("lb, ub, and cost must align with categories")
        for j in range(category_count):
            x[i, j].LB = row["lb"][j]
            x[i, j].UB = row["ub"][j]
        for group in row["groups"]:
            expression = gp.quicksum(x[i, j] for j in group["indices"])
            sense = group["sense"]
            rhs = group["rhs"]
            if sense == "<=":
                model.addConstr(expression <= rhs)
            elif sense == ">=":
                model.addConstr(expression >= rhs)
            elif sense == "=":
                model.addConstr(expression == rhs)
            else:
                raise ValueError(f"unsupported group sense: {sense}")
    model.setObjective(
        gp.quicksum(rows[i]["cost"][j] * x[i, j] for i in range(len(rows)) for j in range(category_count)),
        GRB.MINIMIZE,
    )
    return model
