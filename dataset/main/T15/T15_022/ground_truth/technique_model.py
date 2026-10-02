import gurobipy as gp
from gurobipy import GRB


def build_program_model(block, block_index):
    model = gp.Model(f"t15_program_{block_index}")
    selected = model.addVars(len(block["options"]), vtype=GRB.BINARY, name="select")
    model.setObjective(gp.quicksum(option["cost"] * selected[j] for j, option in enumerate(block["options"])), GRB.MINIMIZE)
    for r, requirement in enumerate(block["requirements"]):
        model.addConstr(
            gp.quicksum(selected[j] for j in requirement["eligible_options"]) >= requirement["required"],
            name=f"requirement_{r}",
        )
    return model


def solve_algorithm(instance, context):
    total_objective = 0.0
    solved = 0
    for b, block in enumerate(instance["programs"]):
        model = build_program_model(block, b)
        try:
            status = context.optimize(model)
            if status != "OPTIMAL":
                return {"solver_status": status, "objective_value": None, "solution_summary": f"completed_programs={solved}"}
            total_objective += float(model.ObjVal)
            solved += 1
        finally:
            model.dispose()
    return {"solver_status": "OPTIMAL", "objective_value": total_objective, "solution_summary": f"independent_programs={solved}"}
