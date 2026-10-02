import gurobipy as gp
from gurobipy import GRB, quicksum


def build_model(instance):
    """T20_024 re-authored technique: compact feature-selection Chebyshev fit.

    min sum_t tmax[t] + sum_j fixed[j]*z[j,t]
    s.t. |y[t][i] - sum_j beta[j,t]*F[t][i][j]| <= tmax[t]     (epigraph rows)
         |beta[j,t]| <= coefficient_bounds[j]*z[j,t]                        (feature enabled)
         sum_j z[j,t] <= K
         z[j,t] >= z[j,t+1]                                   (adjacent prefix)
    """
    P = int(instance["periods"]); n = int(instance["obs_per_period"])
    p = int(instance["features"]); K = int(instance["max_features"])
    y = instance["y"]; F = instance["F"]
    coefficient_bounds = [float(v) for v in instance["coefficient_bounds"]]
    fixed = [float(v) for v in instance["fixed"]]
    loss = instance.get("loss", "cheb")

    m = gp.Model("t20_rebuild_allpairs")
    beta = m.addVars(p, P, lb=-GRB.INFINITY, name="beta")
    z = m.addVars(p, P, vtype=GRB.BINARY, name="z")
    tmax = m.addVars(P, lb=0.0, name="tmax")
    dev = m.addVars(P, n, lb=0.0, name="dev") if loss == "l1" else None

    for t in range(P):
        m.addConstr(quicksum(z[j, t] for j in range(p)) <= K, name=f"card[{t}]")
        for i in range(n):
            res = quicksum(beta[j, t] * float(F[t][i][j]) for j in range(p)) - float(y[t][i])
            if loss == "l1":
                m.addConstr(dev[t, i] >= res, name=f"u[{t},{i}]")
                m.addConstr(dev[t, i] >= -res, name=f"l[{t},{i}]")
            else:
                m.addConstr(res <= tmax[t], name=f"u[{t},{i}]")
                m.addConstr(-res <= tmax[t], name=f"l[{t},{i}]")
    for j in range(p):
        for t in range(P):
            m.addConstr(beta[j, t] <= coefficient_bounds[j] * z[j, t], name=f"zp[{j},{t}]")
            m.addConstr(-beta[j, t] <= coefficient_bounds[j] * z[j, t], name=f"zn[{j},{t}]")
        for t in range(P):
            for tau in range(t + 1, P):
                m.addConstr(z[j, t] >= z[j, tau], name=f"persist[{j},{t},{tau}]")

    fit = (quicksum(dev[t, i] for t in range(P) for i in range(n)) if loss == "l1"
           else quicksum(tmax[t] for t in range(P)))
    m.setObjective(fit + quicksum(fixed[j] * z[j, t] for j in range(p) for t in range(P)),
                   GRB.MINIMIZE)
    return m
