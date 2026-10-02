import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T15_21 technique: equality-tightened continuous LP relaxation.

    Two exact reformulation steps keep the optimum identical to the naive
    integer model:
    1. Balance tightening: per grade the total neighborhood supply equals the
       total school capacity (N*supply == S*cap), so in every feasible solution
       each school is exactly at capacity -> the "at most" rows become
       equalities without changing the feasible set.
    2. TU: a transportation polytope with integral RHS has an integral
       optimum, so the continuous relaxation solves the integer problem.
    """
    m = gp.Model("t15_21_grades_lp_eq")
    cost = instance["assignment_cost"]
    supply = float(instance["students_per_neighborhood_grade"])
    cap = float(instance["school_capacity_per_grade"])
    G = len(instance["grades"])
    N = len(instance["neighborhoods"])
    S = len(instance["schools"])
    obj = gp.LinExpr()
    for g in range(G):
        x = m.addVars(N, S, lb=0.0, name=f"x_{g}")
        for n in range(N):
            m.addConstr(quicksum(x[n, s] for s in range(S)) == supply, name=f"sup_{g}_{n}")
        for s in range(S):
            m.addConstr(quicksum(x[n, s] for n in range(N)) == cap, name=f"cap_{g}_{s}")
        obj += quicksum(cost[g][n][s] * x[n, s] for n in range(N) for s in range(S))
    m.setObjective(obj, GRB.MINIMIZE)
    return m
