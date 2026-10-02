import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Ordinary formulation: integer transportation flows in every block."""
    model = gp.Model("t15_block_transportation_integer")
    objective = gp.LinExpr()
    for block_index, block in enumerate(instance["blocks"]):
        source_count = len(block["supplies"])
        destination_count = len(block["demands"])
        flow = model.addVars(
            source_count,
            destination_count,
            lb=0.0,
            vtype=GRB.INTEGER,
            name=f"flow_{block_index}",
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
        objective += quicksum(
            block["costs"][source][destination] * flow[source, destination]
            for source in range(source_count)
            for destination in range(destination_count)
        )
    model.setObjective(objective, GRB.MINIMIZE)
    return model
