import gurobipy as gp
from gurobipy import GRB


def iter_models(instance):
    """Yield one exact set-multicover model for each separable program."""
    models = []
    for b, block in enumerate(instance["blocks"]):
        model = gp.Model(f"t15_cover_block_{b}")
        x = model.addVars(len(block["options"]), vtype=GRB.BINARY, name="x")
        model.setObjective(
            gp.quicksum(option["cost"] * x[j] for j, option in enumerate(block["options"])),
            GRB.MINIMIZE,
        )
        for r_idx, requirement in enumerate(block["requirements"]):
            model.addConstr(
                gp.quicksum(x[j] for j in requirement["eligible_options"])
                >= requirement["required"],
                name=f"cover_{r_idx}",
            )
        models.append(model)
    return models


def solve_algorithm(instance, context):
    """Solve independent blocks sequentially through the runner-owned context."""
    objective = 0.0
    solved = 0
    for model in iter_models(instance):
        status = context.optimize(model)
        if status != "OPTIMAL":
            try:
                model.dispose()
            finally:
                return {
                    "solver_status": status,
                    "objective_value": None,
                    "solution_summary": f"completed_blocks={solved}",
                }
        objective += float(model.ObjVal)
        solved += 1
        model.dispose()
    if solved == 0:
        raise ValueError("iter_models(instance) produced no submodels")
    return {
        "solver_status": "OPTIMAL",
        "objective_value": objective,
        "solution_summary": f"independent_blocks={solved}",
    }

