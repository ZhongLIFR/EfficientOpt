import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T15_21 ordinary: per-grade integer student flow (neighborhood -> school).

    Naive reading: aggregated student counts per (grade, neighborhood, school),
    each neighborhood fully placed (== supply), each school at most capacity.
    """
    m = gp.Model("t15_21_grades_mip")
    cost = instance["assignment_cost"]
    supply = float(instance["students_per_neighborhood_grade"])
    cap = float(instance["school_capacity_per_grade"])
    G = len(instance["grades"])
    N = len(instance["neighborhoods"])
    S = len(instance["schools"])
    obj = gp.LinExpr()
    for g in range(G):
        x = m.addVars(N, S, lb=0.0, vtype=GRB.INTEGER, name=f"x_{g}")
        for n in range(N):
            m.addConstr(quicksum(x[n, s] for s in range(S)) == supply, name=f"sup_{g}_{n}")
        for s in range(S):
            m.addConstr(quicksum(x[n, s] for n in range(N)) <= cap, name=f"cap_{g}_{s}")
        obj += quicksum(cost[g][n][s] * x[n, s] for n in range(N) for s in range(S))
    m.setObjective(obj, GRB.MINIMIZE)
    return m
