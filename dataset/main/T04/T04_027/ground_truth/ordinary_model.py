import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """Ordinary formulation with binary prefix-state variables. The model is semantically identical to the technique formulation but retains the redundant integrality declaration on the auxiliary state."""
    S = int(instance["sources"]); D = int(instance["sinks"]); P = int(instance["periods"])
    K = int(instance["max_open_per_period"])
    supply = [float(v) for v in instance["supply"]]
    demand = [[float(v) for v in row] for row in instance["demand"]]
    cost = [[float(v) for v in row] for row in instance["cost"]]
    fixed = [[float(v) for v in row] for row in instance["fixed"]]
    cap = [[float(v) for v in row] for row in instance["capacity"]]

    m = gp.Model("t44_reauth_binary_exact_closure")
    idx = [(s, d) for s in range(S) for d in range(D)]
    ship = m.addVars(S, D, P, lb=0.0, name="ship")
    use = m.addVars(S, D, P, vtype=GRB.BINARY, name="use")
    open_ = m.addVars(S, D, P, vtype=GRB.BINARY, name="open")

    for t in range(P):
        m.addConstr(quicksum(use[s, d, t] for (s, d) in idx) <= K, name=f"cap[{t}]")
    for s in range(S):
        for t in range(P):
            m.addConstr(quicksum(ship[s, d, t] for d in range(D)) <= supply[s],
                        name=f"supply[{s},{t}]")
    for d in range(D):
        for t in range(P):
            m.addConstr(quicksum(ship[s, d, t] for s in range(S)) == demand[d][t],
                        name=f"demand[{d},{t}]")
    for (s, d) in idx:
        for t in range(P):
            m.addConstr(ship[s, d, t] <= cap[s][d] * use[s, d, t], name=f"shipif[{s},{d},{t}]")
            m.addConstr(use[s, d, t] <= open_[s, d, t], name=f"useif[{s},{d},{t}]")
        for t in range(P - 1):
            m.addConstr(open_[s, d, t] >= open_[s, d, t + 1], name=f"prefix[{s},{d},{t}]")
            m.addConstr(open_[s, d, t] <= use[s, d, t] + open_[s, d, t + 1],
                        name=f"exact_prefix[{s},{d},{t}]")
        m.addConstr(open_[s, d, P - 1] <= use[s, d, P - 1],
                    name=f"exact_last[{s},{d}]")

    m.setObjective(quicksum(cost[s][d] * ship[s, d, t] for s in range(S) for d in range(D) for t in range(P))
                   + quicksum(fixed[s][d] * open_[s, d, t] for s in range(S) for d in range(D) for t in range(P)),
                   GRB.MINIMIZE)
    return m
