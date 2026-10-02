from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective_from_consensus


def solve() -> dict:
    data = load_data()
    q, p = build_arrays(data)
    regions = int(data["regions"])
    periods = int(data["time_periods"])
    rho = float(data["rho"])
    tol = float(data["absolute_tolerance"])
    max_iter = int(data["max_admm_iterations"])
    z = [0.0] * periods
    u = [[0.0] * periods for _ in range(regions)]
    x = [[0.0] * periods for _ in range(regions)]
    start = perf_counter()
    for iteration in range(1, max_iter + 1):
        for k in range(regions):
            qk = q[k]
            pk = p[k]
            uk = u[k]
            xk = x[k]
            for h in range(periods):
                xk[h] = (qk[h] * pk[h] + rho * (z[h] - uk[h])) / (qk[h] + rho)
        old_z = z[:]
        for h in range(periods):
            z[h] = sum(x[k][h] + u[k][h] for k in range(regions)) / regions
        primal_residual = 0.0
        for k in range(regions):
            uk = u[k]
            xk = x[k]
            for h in range(periods):
                residual = xk[h] - z[h]
                uk[h] += residual
                if abs(residual) > primal_residual:
                    primal_residual = abs(residual)
        dual_residual = max(rho * abs(z[h] - old_z[h]) for h in range(periods))
        if primal_residual <= tol and dual_residual <= tol:
            break
    wall_seconds = perf_counter() - start
    objective = objective_from_consensus(q, p, z)
    return {
        "objective": objective,
        "consensus_profile": z,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": iteration * regions * periods,
        "iterations": iteration,
        "variables": regions * periods + periods,
        "constraints": regions * periods,
        "nonzeros": 2 * regions * periods,
        "method": "consensus_admm_closed_form",
        "rho": rho,
        "primal_residual": primal_residual,
        "dual_residual": dual_residual,
    }


if __name__ == "__main__":
    result = solve()
    result.pop("consensus_profile")
    print(json.dumps(result, indent=2))
