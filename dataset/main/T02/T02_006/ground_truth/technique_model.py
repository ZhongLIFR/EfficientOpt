import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """T2_14 technique (T02 epigraph): rocket minimum-peak-thrust control.

    Same semantics as ordinary.  Instead of per-period absolute variables and
    a general max, the peak is bounded from below by both +a_t and -a_t for
    every period (two linear rows per period, no general constraints).
    """
    n = instance["periods"]
    x0, v0 = instance["initial_position"], instance["initial_velocity"]
    xf, vf = instance["final_position"], instance["final_velocity"]
    ab = instance["acceleration_bound"]

    m = gp.Model("t2_14_rocket_epigraph")
    x = m.addVars(n + 1, lb=-GRB.INFINITY, name="position")
    v = m.addVars(n + 1, lb=-GRB.INFINITY, name="velocity")
    a = m.addVars(n, lb=-ab, ub=ab, name="acceleration")
    peak = m.addVar(lb=0.0, name="peak_thrust")

    m.addConstr(x[0] == x0, name="x0")
    m.addConstr(v[0] == v0, name="v0")
    for t in range(n):
        m.addConstr(x[t + 1] == x[t] + v[t], name=f"dx[{t}]")
        m.addConstr(v[t + 1] == v[t] + a[t], name=f"dv[{t}]")
    m.addConstr(x[n] == xf, name="x_end")
    m.addConstr(v[n] == vf, name="v_end")
    for t in range(n):
        m.addConstr(peak >= a[t], name=f"peak_u[{t}]")
        m.addConstr(peak >= -a[t], name=f"peak_l[{t}]")

    m.setObjective(peak, GRB.MINIMIZE)
    return m
