import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T12_011 technique (T12 dual transformation): L1 dual straight-line fit.

    max sum_i y_i w_i  s.t. |w_i| <= 1, sum w_i = 0, sum x_i w_i = 0.
    """
    x = instance["predictor_values"]
    y = instance["observed_values"]
    n = len(y)
    m = gp.Model("t12_06_l1_dual")
    w = m.addVars(n, lb=-1.0, ub=1.0, name="w")
    m.addConstr(w.sum() == 0.0, name="orth_intercept")
    m.addConstr(quicksum(x[i] * w[i] for i in range(n)) == 0.0, name="orth_slope")
    m.setObjective(quicksum(y[i] * w[i] for i in range(n)), GRB.MAXIMIZE)
    return m
