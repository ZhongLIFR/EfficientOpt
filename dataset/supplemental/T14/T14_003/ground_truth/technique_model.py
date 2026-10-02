from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective_from_shared


def solve() -> dict:
    data = load_data()
    a, b = build_arrays(data)
    sites = int(data["sites"])
    features = int(data["features"])
    rho = float(data["rho"])
    tol = float(data["absolute_tolerance"])
    max_iter = int(data["max_admm_iterations"])
    z = [0.0] * features
    x = [[0.0] * features for _ in range(sites)]
    u = [[0.0] * features for _ in range(sites)]
    start = perf_counter()
    for iteration in range(1, max_iter + 1):
        for k in range(sites):
            ak = a[k]
            bk = b[k]
            uk = u[k]
            xk = x[k]
            for j in range(features):
                xk[j] = (ak[j] * bk[j] + rho * (z[j] - uk[j])) / (ak[j] + rho)
        old_z = z[:]
        for j in range(features):
            z[j] = sum(x[k][j] + u[k][j] for k in range(sites)) / sites
        primal_residual = 0.0
        for k in range(sites):
            uk = u[k]
            xk = x[k]
            for j in range(features):
                residual = xk[j] - z[j]
                uk[j] += residual
                if abs(residual) > primal_residual:
                    primal_residual = abs(residual)
        dual_residual = max(rho * abs(z[j] - old_z[j]) for j in range(features))
        if primal_residual <= tol and dual_residual <= tol:
            break
    wall_seconds = perf_counter() - start
    objective = objective_from_shared(a, b, z)
    return {
        "objective": objective,
        "shared_coefficients": z,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": iteration * sites * features,
        "iterations": iteration,
        "variables": sites * features + features,
        "constraints": sites * features,
        "nonzeros": 2 * sites * features,
        "method": "consensus_admm_closed_form",
        "rho": rho,
        "primal_residual": primal_residual,
        "dual_residual": dual_residual,
    }


if __name__ == "__main__":
    result = solve()
    result.pop("shared_coefficients")
    print(json.dumps(result, indent=2))
