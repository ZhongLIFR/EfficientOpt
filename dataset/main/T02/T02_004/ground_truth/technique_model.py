import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_18 technique (T02 epigraph): Chebyshev line fit, min max |y-(a+b x)|.

    min t  s.t. |y_i - (a + b x_i)| <= t for all i.
    """
    obs = instance["observations"]
    n = len(obs)
    m = gp.Model("t2_18_chebyshev")
    a = m.addVar(lb=-GRB.INFINITY, name="intercept")
    b = m.addVar(lb=-GRB.INFINITY, name="slope")
    t = m.addVar(lb=0.0, name="max_err")
    for i, o in enumerate(obs):
        m.addConstr(o["observed_value"] - (a + b * o["predictor"]) <= t, name=f"u[{i}]")
        m.addConstr((a + b * o["predictor"]) - o["observed_value"] <= t, name=f"l[{i}]")
    m.setObjective(t, GRB.MINIMIZE)
    return m
