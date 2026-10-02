import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    chains = instance["chains"]
    task_count = len(instance["tasks"])
    model = gp.Model("ordinary_time_indexed_start")
    starts_at = {
        (i, task, period): model.addVar(vtype=GRB.BINARY, name=f"starts_at[{i},{task},{period}]")
        for i, chain in enumerate(chains)
        for task in range(task_count)
        for period in range(chain["release"][task], chain["latest"][task] + 1)
    }
    model.setObjective(
        gp.quicksum(
            chains[i]["weights"][task] * period * starts_at[i, task, period]
            for i, chain in enumerate(chains)
            for task in range(task_count)
            for period in range(chain["release"][task], chain["latest"][task] + 1)
        ),
        GRB.MINIMIZE,
    )
    for i, chain in enumerate(chains):
        for task in range(task_count):
            model.addConstr(
                gp.quicksum(
                    starts_at[i, task, period]
                    for period in range(chain["release"][task], chain["latest"][task] + 1)
                )
                == 1,
                name=f"one_start[{i},{task}]",
            )
    for i, chain in enumerate(chains):
        for task in range(task_count - 1):
            next_start = gp.quicksum(
                period * starts_at[i, task + 1, period]
                for period in range(chain["release"][task + 1], chain["latest"][task + 1] + 1)
            )
            current_start = gp.quicksum(
                period * starts_at[i, task, period]
                for period in range(chain["release"][task], chain["latest"][task] + 1)
            )
            model.addConstr(next_start - current_start >= chain["lags"][task], name=f"precedence[{i},{task}]")
    return model
