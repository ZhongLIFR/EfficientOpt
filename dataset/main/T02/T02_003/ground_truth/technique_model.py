import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_16 technique (T02 epigraph): worst-segment illumination calibration.

    Same semantics as ordinary.  Instead of per-segment deviation variables
    and a shared cap, the peak is bounded from both sides for every segment
    (two linear rows per segment, no extra variables).
    """
    lamps = instance["num_lamps"]
    ub = instance["power_bounds"]
    segments = instance["segments"]
    m = gp.Model("t2_16_illumination_epigraph")
    p = m.addVars(lamps, lb=0.0, ub=ub, name="power")
    peak = m.addVar(lb=0.0, name="maximum_deviation")
    for i, seg in enumerate(segments):
        actual = quicksum(c * p[l] for l, c in seg["lamp_contributions"])
        res = actual - seg["target_illumination"]
        m.addConstr(peak >= res, name=f"u[{i}]")
        m.addConstr(peak >= -res, name=f"l[{i}]")
    m.setObjective(peak, GRB.MINIMIZE)
    return m
