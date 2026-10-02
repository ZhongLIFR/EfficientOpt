import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    model = gp.Model("t15_monolithic_program_portfolio")
    selected = {}
    for b, block in enumerate(instance["programs"]):
        for j in range(len(block["options"])):
            selected[b, j] = model.addVar(vtype=GRB.BINARY, name=f"select_{b}_{j}")
    model.setObjective(
        gp.quicksum(option["cost"] * selected[b, j]
                    for b, block in enumerate(instance["programs"])
                    for j, option in enumerate(block["options"])),
        GRB.MINIMIZE,
    )
    for b, block in enumerate(instance["programs"]):
        for r, requirement in enumerate(block["requirements"]):
            model.addConstr(
                gp.quicksum(selected[b, j] for j in requirement["eligible_options"])
                >= requirement["required"],
                name=f"requirement_{b}_{r}",
            )
    return model
