"""Technique formulation: support-function separation (cutting planes).

max_{v in C_k} v^T (A_k x) is the support function of the polytope C_k evaluated at A_k x.
Only the generated supporting vertices are kept as cuts (eta_k >= v^T A_k x); each round the
separation LP over C_k's facets certifies whether any vertex is still violated.  Converges to the
exact value of the semi-infinite constraint, because a linear function attains its maximum over a
polytope at a vertex.
"""
from __future__ import annotations

import json
import time
from itertools import product

import numpy as np
import gurobipy as gp
from gurobipy import GRB

from common import configure, load_instance, rss_mb

MAX_ROUNDS = 200
TOL = 1e-7


def solve(technique: bool = True) -> dict:
    if not technique:
        raise RuntimeError("technique_model.py implements the technique formulation only")
    rss0 = rss_mb()
    d_ = load_instance()
    gates = d_["gates"]; K = len(gates); J = len(d_["profit"])
    b = d_["gate_limit"]
    t_build = time.perf_counter()

    master = gp.Model("master"); configure(master)
    x = master.addVars(J, lb=0.0, name="plan_level")
    xlist = [x[j] for j in range(J)]
    eta = master.addVars(K, lb=0.0, name="support_value")
    for k in range(K):
        master.addConstr(gp.quicksum(gates[k]["nominal_load"][j] * x[j] for j in range(J))
                         + eta[k] <= b[k], name=f"gate_{k}")
    master.setObjective(gp.quicksum(d_["profit"][j] * x[j] for j in range(J)), GRB.MAXIMIZE)

    # ONE reusable separation model (holding K separate models costs gigabytes at scale)
    dmax = max(np.asarray(g["facet_normals"]).shape[0] for g in gates)
    ddim = max(np.asarray(g["facet_normals"]).shape[1] for g in gates)
    sep = gp.Model("separation"); configure(sep)
    v = sep.addVars(ddim, lb=-GRB.INFINITY, name="v")
    sep_con = sep.addConstrs((gp.LinExpr() <= 0.0 for _ in range(dmax)), name="facet")
    sep_active = dmax

    def set_separation(k):
        """load gate k's facet description into the shared separation model"""
        nonlocal sep_active
        F = np.asarray(gates[k]["facet_normals"], dtype=float)
        r = np.asarray(gates[k]["facet_rhs"], dtype=float)
        for f in range(dmax):
            con = sep_con[f]
            if f < F.shape[0]:
                for i in range(ddim):
                    sep.chgCoeff(con, v[i], float(F[f, i]))
                con.RHS = float(r[f])
            else:
                for i in range(ddim):
                    sep.chgCoeff(con, v[i], 0.0)
                con.RHS = 0.0
        sep.update()

    def add_cut(k, vvec):
        row = np.asarray(vvec, dtype=float) @ np.asarray(gates[k]["kpi_matrix"], dtype=float)
        master.addConstr(eta[k] >= gp.quicksum(float(row[j]) * x[j] for j in range(J)),
                         name=f"cut_{k}_{master.NumConstrs}")

    # warm start: the corner that is worst for a balanced plan
    for k in range(K):
        A = np.asarray(gates[k]["kpi_matrix"], dtype=float)
        z = A @ np.ones(J)
        corner = np.sign(z)
        corner[corner == 0] = 1.0
        add_cut(k, corner)
    build_s = time.perf_counter() - t_build
    rss1 = rss_mb()

    rt_total = 0.0
    work_total = 0.0
    rounds = 0
    for rnd in range(MAX_ROUNDS):
        master.optimize()
        rt_total += master.Runtime
        work_total += master.Work
        if master.Status != GRB.OPTIMAL:
            raise RuntimeError(f"master status {master.Status}")
        xv = np.array([x[j].X for j in range(J)])
        added = 0
        for k in range(K):
            A = np.asarray(gates[k]["kpi_matrix"], dtype=float)
            z = A @ xv
            set_separation(k)
            sep.setObjective(gp.quicksum(float(z[i]) * v[i] for i in range(len(z))), GRB.MAXIMIZE)
            sep.optimize()
            rt_total += sep.Runtime
            work_total += sep.Work
            if sep.Status != GRB.OPTIMAL:
                raise RuntimeError(f"separation status {sep.Status}")
            val = sep.ObjVal
            if val > eta[k].X + TOL * max(1.0, abs(val)):
                add_cut(k, np.array([v[i].X for i in range(len(z))]))
                added += 1
        rounds = rnd + 1
        if added == 0:
            break
    rss2 = rss_mb()

    viol = 0.0
    for k in range(K):
        load = gates[k]["nominal_load"]
        A = np.asarray(gates[k]["kpi_matrix"], dtype=float)
        V = np.array(list(product((1.0, -1.0), repeat=A.shape[0])))
        xv2 = np.array([x[j].X for j in range(J)])
        worst = float(np.max(V @ (A @ xv2)))
        viol = max(viol, float(np.asarray(load) @ xv2) + worst - b[k])
    return {
        "objective": master.ObjVal, "runtime_s": rt_total, "work": work_total,
        "num_variables": master.NumVars, "num_constraints": master.NumConstrs,
        "num_nonzeros": master.NumNZs, "build_time_s": round(build_s, 4),
        "node_count": int(getattr(master, "NodeCount", 0) or 0),
        "simplex_iterations": int(getattr(master, "IterCount", 0) or 0),
        "gurobi_mem_used_mb": round(float(getattr(master, "MemUsed", 0.0) or 0.0), 2),
        "max_mem_used_mb": round(float(getattr(master, "MaxMemUsed", 0.0) or 0.0), 2),
        "rss_after_load_mb": rss0, "rss_after_build_mb": rss1, "rss_after_solve_mb": rss2,
        "constraint_violation": max(0.0, viol), "bound_violation": 0.0,
        "checksum": round(sum((j + 1) * x[j].X for j in range(J)), 6),
        "cutting_plane_rounds": rounds,
    }


if __name__ == "__main__":
    print(json.dumps(solve(True)))
