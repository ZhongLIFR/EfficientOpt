import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20_18 technique: compact sliding-window shift-start model.

    Only the start[s] variables remain; coverage[t] sums starts in the window
    [t-length+1, t]. The duplicated activity variables and their == link rows
    are gone (exact same feasible region in start).
    """
    demand = [int(v) for v in instance["demand"]]
    length = int(instance["shift_length"])
    costs = [float(v) for v in instance["start_cost"]]
    n = len(demand)
    m = gp.Model("t20_18_compact")
    start = m.addVars(n, lb=0.0, vtype=GRB.INTEGER, name="start")
    for t in range(n):
        m.addConstr(quicksum(start[s] for s in range(max(0, t - length + 1), t + 1)) >= demand[t],
                    name=f"cov[{t}]")
    m.setObjective(quicksum(costs[s] * start[s] for s in range(n)), GRB.MINIMIZE)
    return m
