import gurobipy as gp
from gurobipy import GRB, quicksum


def _maximal_patterns(ws, W):
    """Enumerate only maximal patterns: leftover < every item width.

    A non-maximal pattern still fits at least one more item; appending it
    cannot increase the roll count and keeps feasibility (overproduction is
    allowed), so some optimum uses maximal patterns only. Exact reduction.
    """
    n = len(ws)
    cnt = [0] * n
    out = []
    wmin = min(ws)

    def dfs(i, rem, used):
        if i == n:
            if used and rem < wmin:
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
    """T24_018 technique: maximal-pattern (dominance-reduced) covering IP.

    Same cutting-stock optimum as the full-pattern model, but with only the
    maximal (Pareto) patterns as columns -> strictly fewer integer variables.
    """
    W = int(instance["stock_width"])
    ws = [int(w) for w in instance["item_widths"]]
    dem = [float(v) for v in instance["demands"]]
    pats = _maximal_patterns(ws, W)

    m = gp.Model("t24_018_maximal_patterns")
    z = m.addVars(len(pats), lb=0.0, vtype=GRB.INTEGER, name="z")
    for i, di in enumerate(dem):
        m.addConstr(quicksum(pats[p][i] * z[p] for p in range(len(pats))) >= di, name=f"dem_{i}")
    m.setObjective(quicksum(z), GRB.MINIMIZE)
    m._npat = len(pats)
    return m
