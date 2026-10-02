import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """Build the exact monolithic multi-program set-multicover model."""
    model = gp.Model("t15_cover_monolithic")
    x = {}
    for b, block in enumerate(instance["blocks"]):
        for j in range(len(block["options"])):
            x[b, j] = model.addVar(vtype=GRB.BINARY, name=f"x_{b}_{j}")
    model.setObjective(
        gp.quicksum(
            option["cost"] * x[b, j]
            for b, block in enumerate(instance["blocks"])
            for j, option in enumerate(block["options"])
        ),
        GRB.MINIMIZE,
    )
    for b, block in enumerate(instance["blocks"]):
        for r_idx, requirement in enumerate(block["requirements"]):
            model.addConstr(
                gp.quicksum(x[b, j] for j in requirement["eligible_options"])
                >= requirement["required"],
                name=f"cover_{b}_{r_idx}",
            )
    return model
