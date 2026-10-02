from __future__ import annotations

import json
from time import perf_counter

from common_model import build_arrays, load_data, objective


def solve() -> dict:
    data = load_data()
    q, p, demand = build_arrays(data)
    warehouses = int(data["warehouses"])
    periods = int(data["periods"])
    rho = float(data["rho"])
    tol = float(data["absolute_tolerance"])
    max_iter = int(data["max_admm_iterations"])
    x = [[p[k][h] for h in range(periods)] for k in range(warehouses)]
    y = [row[:] for row in x]
    u = [[0.0] * periods for _ in range(warehouses)]
    for h in range(periods):
        shift = (demand[h] - sum(y[k][h] for k in range(warehouses))) / warehouses
        for k in range(warehouses):
            y[k][h] += shift
    start = perf_counter()
    for iteration in range(1, max_iter + 1):
        for k in range(warehouses):
            qk = q[k]
            pk = p[k]
            yk = y[k]
            uk = u[k]
            xk = x[k]
            for h in range(periods):
                xk[h] = (qk[h] * pk[h] + rho * (yk[h] - uk[h])) / (qk[h] + rho)
        old_y = [row[:] for row in y]
        for h in range(periods):
            total = sum(x[k][h] + u[k][h] for k in range(warehouses))
            shift = (demand[h] - total) / warehouses
            for k in range(warehouses):
                y[k][h] = x[k][h] + u[k][h] + shift
        primal_residual = 0.0
        dual_residual = 0.0
        for k in range(warehouses):
            uk = u[k]
            xk = x[k]
            yk = y[k]
            old_yk = old_y[k]
            for h in range(periods):
                residual = xk[h] - yk[h]
                uk[h] += residual
                if abs(residual) > primal_residual:
                    primal_residual = abs(residual)
                dual = rho * abs(yk[h] - old_yk[h])
                if dual > dual_residual:
                    dual_residual = dual
        if primal_residual <= tol and dual_residual <= tol:
            break
    wall_seconds = perf_counter() - start
    return {
        "objective": objective(q, p, y),
        "shipments": y,
        "wall_seconds": wall_seconds,
        "runtime": wall_seconds,
        "work": iteration * warehouses * periods,
        "iterations": iteration,
        "variables": 2 * warehouses * periods,
        "constraints": warehouses * periods + periods,
        "nonzeros": 2 * warehouses * periods,
        "method": "exchange_admm_projection",
        "rho": rho,
        "primal_residual": primal_residual,
        "dual_residual": dual_residual,
    }


if __name__ == "__main__":
    result = solve()
    result.pop("shipments")
    print(json.dumps(result, indent=2))
