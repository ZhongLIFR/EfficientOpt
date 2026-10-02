import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T2_16 ordinary (naive literal): worst-segment illumination calibration.

    Each road segment s has lamps (lamp_idx, contribution) + target.  Power
    p in [0, power_bounds]; achieved = sum contribution*p.  Minimize the
    largest |achieved - target| over segments.

    Naive: per-segment absolute-deviation variable d_s, two linear rows
    (d >= res, d >= -res) and a shared peak cap d_s <= peak — the direct
    reading of "largest absolute deviation".
    """
    lamps = instance["num_lamps"]
    ub = instance["power_bounds"]
    segments = instance["segments"]
    m = gp.Model("t2_16_illumination_naive")
    p = m.addVars(lamps, lb=0.0, ub=ub, name="power")
    peak = m.addVar(lb=0.0, name="maximum_deviation")
    for i, seg in enumerate(segments):
        actual = quicksum(c * p[l] for l, c in seg["lamp_contributions"])
        res = actual - seg["target_illumination"]
        d = m.addVar(lb=0.0, name=f"dev[{i}]")
        m.addConstr(d >= res, name=f"d1[{i}]")
        m.addConstr(d >= -res, name=f"d2[{i}]")
        m.addConstr(d <= peak, name=f"cap[{i}]")
    m.setObjective(peak, GRB.MINIMIZE)
    return m
