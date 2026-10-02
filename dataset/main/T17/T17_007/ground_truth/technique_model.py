"""Technique formulation: Dantzig-Wolfe column generation.

Restricted master keeps a handful of routes; the pricing subproblem is a cardinality-constrained
independent-set MIP over the conflict graph, solved by Gurobi.  Columns with negative reduced cost
are added until none remain, at which point the restricted master equals the full covering LP.
Runtime = sum of all Gurobi optimize() runtimes.
"""
from __future__ import annotations

import json
import time

import gurobipy as gp
from gurobipy import GRB

from common import configure, load_instance, rss_mb

MAX_ITER = 400
TOL = 1e-7


def solve(technique: bool = True) -> dict:
    if not technique:
        raise RuntimeError("technique_model.py implements the technique formulation only")
    rss0 = rss_mb()
    d = load_instance()
    n = d["site_count"]; K = d["max_sites_per_route"]; J = d["max_open_routes"]
    cm = [0] * n
    for a, b in d["incompatible_pairs"]:
        cm[a] |= 1 << b
        cm[b] |= 1 << a
    t_build = time.perf_counter()

    master = gp.Model("restricted_master"); configure(master)
    cover = master.addConstrs((gp.LinExpr() >= 1.0 for _ in range(n)), name="cover")
    fleet = master.addConstr(gp.LinExpr() <= float(J), name="fleet_limit")
    xvars = []
    route_list = []
    known = set()

    def add_route(mask):
        c = d["fixed_route_charge"] + sum(d["site_service_cost"][i] for i in range(n)
                                          if mask >> i & 1)
        v = master.addVar(lb=0.0, ub=1.0, obj=float(c), name=f"route_use[{len(xvars)}]")
        master.update()
        for i in range(n):
            if mask >> i & 1:
                master.chgCoeff(cover[i], v, 1.0)
        master.chgCoeff(fleet, v, 1.0)
        xvars.append(v)
        route_list.append(mask)
        known.add(mask)
        master.update()

    # feasible initial columns: greedy packing that respects conflicts, route size, shift length
    # and the fleet limit (an initial column violating the shift limit would relax the master and
    # break equivalence with the ordinary model)
    remaining = set(range(n))
    dur = d["site_duration"]; shift = d["shift_length"]
    wgt = d["site_weight"]; wlim = d["route_weight_limit"]
    vol = d["site_volume"]; vlim = d["route_volume_limit"]
    for _ in range(J):
        route = []
        used = used_w = used_v = 0
        for i in sorted(remaining):
            if len(route) >= K:
                break
            if used + dur[i] > shift or used_w + wgt[i] > wlim or used_v + vol[i] > vlim:
                continue
            if all(not (cm[i] >> j & 1) for j in route):
                route.append(i)
                used += dur[i]; used_w += wgt[i]; used_v += vol[i]
        if not route:
            break
        mask = 0
        for i in route:
            mask |= 1 << i
        add_route(mask)
        remaining -= set(route)
    for i in sorted(remaining):      # only if the instance itself is very tight
        add_route(1 << i)

    pr = gp.Model("pricing"); configure(pr)
    z = pr.addVars(n, vtype=GRB.BINARY, name="visit")
    pr.addConstr(gp.quicksum(z[i] for i in range(n)) <= K, name="cardinality")
    pr.addConstr(gp.quicksum(d["site_duration"][i] * z[i] for i in range(n))
                 <= d["shift_length"], name="shift_length")
    pr.addConstr(gp.quicksum(d["site_weight"][i] * z[i] for i in range(n))
                 <= d["route_weight_limit"], name="route_weight")
    pr.addConstr(gp.quicksum(d["site_volume"][i] * z[i] for i in range(n))
                 <= d["route_volume_limit"], name="route_volume")
    for a, b in d["incompatible_pairs"]:
        pr.addConstr(z[a] + z[b] <= 1, name="conflict")

    rt_total = 0.0
    work_total = 0.0
    iters = 0
    master_obj = None
    build_s = time.perf_counter() - t_build
    rss1 = rss_mb()
    for it in range(MAX_ITER):
        master.optimize()
        rt_total += master.Runtime
        work_total += master.Work
        if master.Status != GRB.OPTIMAL:
            raise RuntimeError(f"master status {master.Status}")
        duals = [cover[i].Pi for i in range(n)]
        nu = fleet.Pi
        master_obj = master.ObjVal
        # A new route has reduced cost c_r - sum_i u_i a_ir - nu, where
        # nu <= 0 is the dual of the fleet-limit row.  Hence the pricing
        # improvement is sum_i (u_i-s_i) z_i + nu - fixed_charge.
        pr.setObjective(gp.quicksum((duals[i] - d["site_service_cost"][i]) * z[i]
                                    for i in range(n)) + nu - d["fixed_route_charge"], GRB.MAXIMIZE)
        pr.optimize()
        rt_total += pr.Runtime
        work_total += pr.Work
        if pr.Status != GRB.OPTIMAL:
            raise RuntimeError(f"pricing status {pr.Status}")
        iters = it + 1
        if pr.ObjVal <= TOL:
            break
        mask = 0
        for i in range(n):
            if z[i].X > 0.5:
                mask |= 1 << i
        if mask in known or mask == 0:
            break
        add_route(mask)
    rss2 = rss_mb()
    # feasibility re-check on the generated master solution
    usage = [0.0] * n
    for p, m in enumerate(route_list):
        val = xvars[p].X
        for i in range(n):
            if m >> i & 1:
                usage[i] += val
    viol = max(0.0, sum(xvars[p].X for p in range(len(xvars))) - J)
    for i in range(n):
        viol = max(viol, 1.0 - usage[i])
    return {
        "objective": master_obj, "runtime_s": rt_total, "work": work_total,
        "num_variables": master.NumVars, "num_constraints": master.NumConstrs,
        "num_nonzeros": master.NumNZs, "build_time_s": round(build_s, 4),
        "node_count": int(getattr(master, "NodeCount", 0) or 0),
        "simplex_iterations": int(getattr(master, "IterCount", 0) or 0),
        "gurobi_mem_used_mb": float(getattr(master, "MemUsed", 0.0) or 0.0),
        "max_mem_used_mb": float(getattr(master, "MaxMemUsed", 0.0) or 0.0),
        "rss_after_load_mb": rss0, "rss_after_build_mb": rss1, "rss_after_solve_mb": rss2,
        "constraint_violation": viol, "bound_violation": 0.0,
        "checksum": round(sum((p + 1) * xvars[p].X for p in range(len(xvars))), 6),
        "pricing_iterations": iters, "generated_columns": len(xvars),
    }


if __name__ == "__main__":
    print(json.dumps(solve(True)))
