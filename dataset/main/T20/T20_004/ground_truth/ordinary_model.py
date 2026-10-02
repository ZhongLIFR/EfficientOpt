import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20_18 ordinary (naive): expanded shift-activity formulation.

    Integer starts start[s]; for every covered (s,t) pair a duplicated
    activity variable active[s,t] == start[s], plus sliding-window coverage
    rows summing active over starts covering t.
    """
    demand = [int(v) for v in instance["demand"]]
    length = int(instance["shift_length"])
    costs = [float(v) for v in instance["start_cost"]]
    n = len(demand)
    m = gp.Model("t20_18_expanded")
    start = m.addVars(n, lb=0.0, vtype=GRB.INTEGER, name="start")
    active = {}
    for s in range(n):
        for t in range(s, min(n, s + length)):
            active[s, t] = m.addVar(lb=0.0, name=f"act[{s},{t}]")
            m.addConstr(active[s, t] == start[s], name=f"link[{s},{t}]")
    for t in range(n):
        m.addConstr(quicksum(active[s, t] for s in range(max(0, t - length + 1), t + 1)) >= demand[t],
                    name=f"cov[{t}]")
    m.setObjective(quicksum(costs[s] * start[s] for s in range(n)), GRB.MINIMIZE)
    return m
