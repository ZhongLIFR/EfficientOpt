import gurobipy as gp
from gurobipy import GRB, quicksum


def _all_patterns(ws, W):
    """Enumerate every feasible nonempty cutting pattern (count per width)."""
    n = len(ws)
    cnt = [0] * n
    out = []

    def dfs(i, rem, used):
        if i == n:
            if used:
                out.append(tuple(cnt))
            return
        w = ws[i]
        for k in range(rem // w + 1):
            cnt[i] = k
            dfs(i + 1, rem - k * w, used + k)
        cnt[i] = 0

    dfs(0, W, 0)
    return out


def build_model(instance):
    """T24_018 ordinary: full-pattern cutting-stock covering IP.

    z_p = integer rolls cut with pattern p (every admissible nonempty pattern);
    sum_p a_ip z_p >= demand_i (overproduction allowed); minimize sum z_p.
    """
    W = int(instance["stock_width"])
    ws = [int(w) for w in instance["item_widths"]]
    dem = [float(v) for v in instance["demands"]]
    pats = _all_patterns(ws, W)

    m = gp.Model("t24_018_all_patterns")
    z = m.addVars(len(pats), lb=0.0, vtype=GRB.INTEGER, name="z")
    for i, di in enumerate(dem):
        m.addConstr(quicksum(pats[p][i] * z[p] for p in range(len(pats))) >= di, name=f"dem_{i}")
    m.setObjective(quicksum(z), GRB.MINIMIZE)
    m._npat = len(pats)
    return m
