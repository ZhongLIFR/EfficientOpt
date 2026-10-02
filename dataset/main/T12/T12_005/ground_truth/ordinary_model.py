import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T12_06 ordinary (naive primal): L1-epigraph straight-line fit.

    min sum_i |y_i - (a + b x_i)|  over free intercept a and slope b.
    """
    x = instance["predictor_values"]
    y = instance["observed_values"]
    n = len(y)
    m = gp.Model("t12_06_l1_epigraph")
    a = m.addVar(lb=-GRB.INFINITY, name="intercept")
    b = m.addVar(lb=-GRB.INFINITY, name="slope")
    dev = m.addVars(n, lb=0.0, name="deviation")
    for i in range(n):
        m.addConstr(dev[i] >= a + b * x[i] - y[i], name=f"p[{i}]")
        m.addConstr(dev[i] >= y[i] - (a + b * x[i]), name=f"n[{i}]")
    m.setObjective(dev.sum(), GRB.MINIMIZE)
    return m
