import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    chains = instance["chains"]
    chain_count = len(chains)
    task_count = len(instance["tasks"])
    model = gp.Model("technique_integer_start_time")
    start = model.addVars(chain_count, task_count, vtype=GRB.INTEGER, name="start")
    for i, chain in enumerate(chains):
        for task in range(task_count):
            start[i, task].LB = chain["release"][task]
            start[i, task].UB = chain["latest"][task]
    model.setObjective(
        gp.quicksum(chains[i]["weights"][task] * start[i, task] for i in range(chain_count) for task in range(task_count)),
        GRB.MINIMIZE,
    )
    model.addConstrs(
        (start[i, task + 1] - start[i, task] >= chains[i]["lags"][task] for i in range(chain_count) for task in range(task_count - 1)),
        name="precedence",
    )
    return model
