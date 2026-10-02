import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """T2_14 ordinary (naive literal): rocket minimum-peak-thrust control.

    Discrete dynamics: x_{t+1}=x_t+v_t, v_{t+1}=v_t+a_t with |a_t|<=ab and
    fixed boundaries.  Objective: minimize max_t |a_t|.

    Naive literal transcription: per-period absolute acceleration via a
    dedicated nonnegative variable and an explicit maximum (genConstrAbs +
    genConstrMax) over the whole plan — the direct reading of "minimize the
    largest absolute acceleration".
    """
    n = instance["periods"]
    x0, v0 = instance["initial_position"], instance["initial_velocity"]
    xf, vf = instance["final_position"], instance["final_velocity"]
    ab = instance["acceleration_bound"]

    m = gp.Model("t2_14_rocket_naive")
    x = m.addVars(n + 1, lb=-GRB.INFINITY, name="position")
    v = m.addVars(n + 1, lb=-GRB.INFINITY, name="velocity")
    a = m.addVars(n, lb=-ab, ub=ab, name="acceleration")
    aa = m.addVars(n, lb=0.0, name="absolute_acceleration")
    peak = m.addVar(lb=0.0, name="peak_thrust")

    m.addConstr(x[0] == x0, name="x0")
    m.addConstr(v[0] == v0, name="v0")
    for t in range(n):
        m.addConstr(x[t + 1] == x[t] + v[t], name=f"dx[{t}]")
        m.addConstr(v[t + 1] == v[t] + a[t], name=f"dv[{t}]")
    m.addConstr(x[n] == xf, name="x_end")
    m.addConstr(v[n] == vf, name="v_end")
    for t in range(n):
        m.addGenConstrAbs(aa[t], a[t], name=f"abs[{t}]")
    m.addGenConstrMax(peak, list(aa.values()), name="peak_max")

    m.setObjective(peak, GRB.MINIMIZE)
    return m
