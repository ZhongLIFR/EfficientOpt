import gurobipy as gp
from gurobipy import GRB, quicksum


def iter_models(instance):
    """Yield one exact integer transportation model per independent block."""
    for block_index, block in enumerate(instance["blocks"]):
        source_count = len(block["supplies"])
        destination_count = len(block["demands"])
        model = gp.Model(f"t15_block_{block_index}")
        flow = model.addVars(
            source_count,
            destination_count,
            lb=0.0,
            vtype=GRB.INTEGER,
            name="flow",
        )
        for source in range(source_count):
            model.addConstr(
                quicksum(flow[source, destination] for destination in range(destination_count))
                == block["supplies"][source]
            )
        for destination in range(destination_count):
            model.addConstr(
                quicksum(flow[source, destination] for source in range(source_count))
                == block["demands"][destination]
            )
        model.setObjective(
            quicksum(
                block["costs"][source][destination] * flow[source, destination]
                for source in range(source_count)
                for destination in range(destination_count)
            ),
            GRB.MINIMIZE,
        )
        yield model


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

