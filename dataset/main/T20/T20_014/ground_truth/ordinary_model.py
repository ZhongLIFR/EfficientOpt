import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    periods = instance["periods"]
    horizon = len(periods)
    model = gp.Model("ordinary_explicit_activity_links")
    starts = model.addVars(horizon, vtype=GRB.INTEGER, lb=0.0, name="starts")
    active = {}
    covering = [[] for _ in range(horizon)]
    for s, period in enumerate(periods):
        end = min(horizon, s + period["duration"])
        for t in range(s, end):
            active[s, t] = model.addVar(lb=0.0, name=f"active[{s},{t}]")
            model.addConstr(active[s, t] == starts[s], name=f"link[{s},{t}]")
            covering[t].append(s)
    for t, period in enumerate(periods):
        model.addConstr(
            gp.quicksum(active[s, t] for s in covering[t]) >= period["demand"],
            name=f"demand[{t}]",
        )
    model.setObjective(
        gp.quicksum(periods[s]["start_cost"] * starts[s] for s in range(horizon)),
        GRB.MINIMIZE,
    )
    return model
