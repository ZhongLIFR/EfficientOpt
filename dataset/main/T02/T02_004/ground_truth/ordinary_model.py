import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_18 ordinary (naive): explicit absolute deviation vars per observation
    with max via a shared upper-bound var (larger but literal formulation).

    min t  with d_i = |y_i-(a+b x_i)|, d_i <= t for all i (d_i explicit).
    """
    obs = instance["observations"]
    n = len(obs)
    m = gp.Model("t2_18_chebyshev_naive")
    a = m.addVar(lb=-GRB.INFINITY, name="intercept")
    b = m.addVar(lb=-GRB.INFINITY, name="slope")
    d = m.addVars(n, lb=0.0, name="abs_dev")
    t = m.addVar(lb=0.0, name="max_err")
    for i, o in enumerate(obs):
        res = o["observed_value"] - (a + b * o["predictor"])
        m.addConstr(d[i] >= res, name=f"d1[{i}]")
        m.addConstr(d[i] >= -res, name=f"d2[{i}]")
        m.addConstr(d[i] <= t, name=f"cap[{i}]")
    m.setObjective(t, GRB.MINIMIZE)
    return m
