"""Shared T38 regression models: l1 (sum abs residual) or linf (max abs residual),
with ridge 0.5*qw*||x||^2, features n x p, target n.

Mother semantics vary per item (T38_02/03/04/05), so the builder takes a family
flag from the module name or a 'family' field. This module provides two factory
functions; each item's mother model files import the right one.
"""
import gurobipy as gp
from gurobipy import GRB, quicksum


def build_primal(instance, norm):
    rows = instance["features"]
    y = instance["target"]
    qw = instance["quadratic_weight"]
    n = len(y)
    p = len(rows[0])
    m = gp.Model("t38_primal")
    x = m.addVars(p, lb=-GRB.INFINITY, name="coef")
    if norm == "l1":
        r = m.addVars(n, lb=0.0, name="abs_residual")
        for i in range(n):
            res = quicksum(rows[i][j] * x[j] for j in range(p)) - y[i]
            m.addConstr(r[i] >= res, name=f"r1[{i}]")
            m.addConstr(r[i] >= -res, name=f"r2[{i}]")
        penalty = r.sum()
    else:  # linf
        t = m.addVar(lb=0.0, name="max_residual")
        for i in range(n):
            res = quicksum(rows[i][j] * x[j] for j in range(p)) - y[i]
            m.addConstr(res <= t, name=f"u[{i}]")
            m.addConstr(-res <= t, name=f"l[{i}]")
        penalty = t
    m.setObjective(0.5 * qw * quicksum(x[j] * x[j] for j in range(p)) + penalty, GRB.MINIMIZE)
    return m


def build_dual(instance, norm):
    rows = instance["features"]
    y = instance["target"]
    qw = instance["quadratic_weight"]
    n = len(y)
    p = len(rows[0])
    m = gp.Model("t38_fenchel_dual")
    if norm == "l1":
        u = m.addVars(n, lb=-1.0, ub=1.0, name="dual")
    else:
        u = m.addVars(n, lb=-GRB.INFINITY, name="dual")
        a = m.addVars(n, lb=0.0, name="abs_dual")
        for i in range(n):
            m.addConstr(a[i] >= u[i], name=f"a1[{i}]")
            m.addConstr(a[i] >= -u[i], name=f"a2[{i}]")
        m.addConstr(a.sum() <= 1.0, name="l1_ball")
    at = m.addVars(p, lb=-GRB.INFINITY, name="at_dual")
    for j in range(p):
        m.addConstr(at[j] == quicksum(rows[i][j] * u[i] for i in range(n)), name=f"at[{j}]")
    m.setObjective(
        -(0.5 / qw * quicksum(at[j] * at[j] for j in range(p))
          + quicksum(y[i] * u[i] for i in range(n))),
        GRB.MAXIMIZE,
    )
    return m


def build_model(instance):
    return build_primal(instance, 'l1')
