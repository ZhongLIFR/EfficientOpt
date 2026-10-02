from __future__ import annotations

import json
import math
from itertools import product
from pathlib import Path
from time import perf_counter


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def dense_solve(a: list[list[float]], b: list[float]) -> list[float]:
    n = len(b)
    for i in range(n):
        pivot = i
        pivot_abs = abs(a[i][i])
        for r in range(i + 1, n):
            value = abs(a[r][i])
            if value > pivot_abs:
                pivot = r
                pivot_abs = value
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            b[i], b[pivot] = b[pivot], b[i]
        inv = 1.0 / a[i][i]
        row_i = a[i]
        for j in range(i, n):
            row_i[j] *= inv
        b[i] *= inv
        for r in range(n):
            if r == i:
                continue
            factor = a[r][i]
            if factor == 0.0:
                continue
            row_r = a[r]
            for j in range(i, n):
                row_r[j] -= factor * row_i[j]
            b[r] -= factor * b[i]
    return b


def box_arrays(data: dict) -> tuple[list[float], list[float], list[float]]:
    n = int(data["n"])
    seed = int(data["seed"])
    q = [1.0 + ((seed + 13 * i) % 23) / 7.0 for i in range(n)]
    upper = [4.0 + ((seed + 17 * i) % 9) for i in range(n)]
    center = [upper[i] * (-0.15 + ((seed * 3 + 19 * i) % 130) / 100.0) for i in range(n)]
    linear = [q[i] * center[i] for i in range(n)]
    return q, linear, upper


def box_objective(q: list[float], linear: list[float], x: list[float]) -> float:
    return sum(0.5 * q[i] * x[i] * x[i] - linear[i] * x[i] for i in range(len(x)))


def solve_box_qp(data: dict, mode: str) -> dict:
    q, linear, upper = box_arrays(data)
    n = len(q)
    start = perf_counter()
    if mode == "ordinary":
        best_obj = float("inf")
        best_x: list[float] | None = None
        combinations = 3 ** n
        for code in range(combinations):
            state = code
            x = [0.0] * n
            valid = True
            for i in range(n):
                status = state % 3
                state //= 3
                if status == 0:
                    x[i] = 0.0
                elif status == 1:
                    value = linear[i] / q[i]
                    if value < -1e-12 or value > upper[i] + 1e-12:
                        valid = False
                        break
                    x[i] = clamp(value, 0.0, upper[i])
                else:
                    x[i] = upper[i]
            if not valid:
                continue
            obj = box_objective(q, linear, x)
            if obj < best_obj:
                best_obj = obj
                best_x = x
        assert best_x is not None
        runtime = perf_counter() - start
        return {
            "objective": best_obj,
            "solution_checksum": sum((i + 1) * best_x[i] for i in range(n)),
            "wall_seconds": runtime,
            "runtime": runtime,
            "work": combinations * n,
            "iterations": combinations,
            "variables": n,
            "constraints": 2 * n,
            "nonzeros": 2 * n,
            "method": "enumerate_complementarity_active_statuses",
        }
    x = [clamp(linear[i] / q[i], 0.0, upper[i]) for i in range(n)]
    runtime = perf_counter() - start
    return {
        "objective": box_objective(q, linear, x),
        "solution_checksum": sum((i + 1) * x[i] for i in range(n)),
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": n,
        "iterations": 1,
        "variables": n,
        "constraints": 2 * n,
        "nonzeros": 2 * n,
        "method": "closed_form_kkt_complementarity_clipping",
    }


def activation_arrays(data: dict) -> tuple[list[int], list[int], list[int], list[int], list[int]]:
    n = int(data["n"])
    seed = int(data["seed"])
    demand = [35 + ((seed * 11 + i * 17) % 75) for i in range(n)]
    variable = [1 + ((seed + i * 5) % 6) for i in range(n)]
    lower = [4 + ((seed + i * 7) % 11) for i in range(n)]
    upper = [lower[i] + 45 + ((seed * 3 + i * 13) % 50) for i in range(n)]
    fixed = [20 + ((seed * 5 + i * 19) % 65) for i in range(n)]
    return demand, variable, lower, upper, fixed


def activation_cost(x: float, y: int, demand: int, variable: int, fixed: int) -> float:
    return 0.5 * (x - demand) ** 2 + y * fixed + variable * x


def solve_activation(data: dict, mode: str) -> dict:
    demand, variable, lower, upper, fixed = activation_arrays(data)
    n = len(demand)
    start = perf_counter()
    total = 0.0
    checksum = 0.0
    if mode == "ordinary":
        for i in range(n):
            best = activation_cost(0.0, 0, demand[i], variable[i], fixed[i])
            best_x = 0.0
            for x in range(lower[i], upper[i] + 1):
                obj = activation_cost(float(x), 1, demand[i], variable[i], fixed[i])
                if obj < best:
                    best = obj
                    best_x = float(x)
            total += best
            checksum += (i + 1) * best_x
        runtime = perf_counter() - start
        return {
            "objective": total,
            "solution_checksum": checksum,
            "wall_seconds": runtime,
            "runtime": runtime,
            "work": sum(upper[i] - lower[i] + 2 for i in range(n)),
            "iterations": n,
            "variables": 2 * n,
            "constraints": 4 * n,
            "nonzeros": 8 * n,
            "method": "loose_activation_grid_scan",
        }
    for i in range(n):
        off_cost = activation_cost(0.0, 0, demand[i], variable[i], fixed[i])
        x_on = round(clamp(demand[i] - variable[i], lower[i], upper[i]))
        on_cost = activation_cost(float(x_on), 1, demand[i], variable[i], fixed[i])
        if on_cost < off_cost:
            total += on_cost
            checksum += (i + 1) * x_on
        else:
            total += off_cost
    runtime = perf_counter() - start
    return {
        "objective": total,
        "solution_checksum": checksum,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": n,
        "iterations": 1,
        "variables": n,
        "constraints": 2 * n,
        "nonzeros": 3 * n,
        "method": "tight_linking_activation_closed_form",
    }


def soc_vector(data: dict) -> tuple[list[float], float]:
    n = int(data["n"])
    seed = int(data["seed"])
    v = [
        math.sin((i + 1) * (seed + 3) * 0.013)
        + 0.7 * math.cos((i + 5) * (seed + 1) * 0.007)
        + 0.01 * (i % 9)
        for i in range(n)
    ]
    norm = math.sqrt(sum(x * x for x in v))
    radius = float(data["radius_fraction"]) * norm
    return v, radius


def solve_soc(data: dict, mode: str) -> dict:
    v, radius = soc_vector(data)
    n = len(v)
    norm = math.sqrt(sum(x * x for x in v))
    start = perf_counter()
    if mode == "ordinary":
        low = 0.0
        high = 1.0
        while norm / (1.0 + high) > radius:
            high *= 2.0
        for _ in range(int(data["iterations"])):
            mid = 0.5 * (low + high)
            if norm / (1.0 + mid) > radius:
                low = mid
            else:
                high = mid
        lam = 0.5 * (low + high)
        scale = 1.0 / (1.0 + lam)
        method = "generic_soc_lagrange_bisection"
        work = int(data["iterations"]) * n
    else:
        scale = 1.0 if norm <= radius else radius / norm
        method = "direct_second_order_cone_projection"
        work = n
    objective = 0.5 * (1.0 - scale) ** 2 * norm * norm
    runtime = perf_counter() - start
    return {
        "objective": objective,
        "solution_checksum": scale * sum((i + 1) * v[i] for i in range(n)),
        "max_feasibility_error": max(0.0, scale * norm - radius),
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": int(data["iterations"]) if mode == "ordinary" else 1,
        "variables": n + 1,
        "constraints": 1,
        "nonzeros": n,
        "method": method,
    }


def exp_arrays(data: dict) -> tuple[list[float], float, float]:
    n = int(data["n"])
    seed = int(data["seed"])
    a = [0.25 + ((seed * 7 + i * 13) % 480) / 50.0 for i in range(n)]
    return a, float(data["lower"]), float(data["upper"])


def solve_exp_dcp(data: dict, mode: str) -> dict:
    a, lower, upper = exp_arrays(data)
    n = len(a)
    start = perf_counter()
    objective = 0.0
    checksum = 0.0
    if mode == "ordinary":
        iterations = int(data["iterations"])
        for i, ai in enumerate(a):
            lo = lower
            hi = upper
            for _ in range(iterations):
                m1 = lo + (hi - lo) / 3.0
                m2 = hi - (hi - lo) / 3.0
                f1 = math.exp(m1) - ai * m1
                f2 = math.exp(m2) - ai * m2
                if f1 < f2:
                    hi = m2
                else:
                    lo = m1
            x = 0.5 * (lo + hi)
            objective += math.exp(x) - ai * x
            checksum += (i + 1) * x
        work = iterations * n
        method = "black_box_univariate_convex_search"
        iterations_out = iterations
    else:
        for i, ai in enumerate(a):
            x = clamp(math.log(ai), lower, upper)
            objective += math.exp(x) - ai * x
            checksum += (i + 1) * x
        work = n
        method = "dcp_stationarity_exp_cone_closed_form"
        iterations_out = 1
    runtime = perf_counter() - start
    return {
        "objective": objective,
        "solution_checksum": checksum,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": iterations_out,
        "variables": n,
        "constraints": 2 * n,
        "nonzeros": 2 * n,
        "method": method,
    }


def l1_arrays(data: dict) -> tuple[list[float], float, float]:
    n = int(data["n"])
    seed = int(data["seed"])
    v = [
        2.5 * math.sin((i + 1) * (seed + 2) * 0.011)
        + 1.2 * math.cos((i + 4) * (seed + 5) * 0.017)
        + 0.02 * ((i % 11) - 5)
        for i in range(n)
    ]
    return v, float(data["l1_lambda"]), float(data["ridge"])


def l1_objective(x: float, v: float, l1_lambda: float, ridge: float) -> float:
    return 0.5 * (x - v) ** 2 + l1_lambda * abs(x) + 0.5 * ridge * x * x


def solve_l1(data: dict, mode: str) -> dict:
    v, l1_lambda, ridge = l1_arrays(data)
    n = len(v)
    start = perf_counter()
    objective = 0.0
    checksum = 0.0
    if mode == "ordinary":
        iterations = int(data["iterations"])
        for i, vi in enumerate(v):
            lo = min(0.0, vi) - l1_lambda - 1.0
            hi = max(0.0, vi) + l1_lambda + 1.0
            for _ in range(iterations):
                m1 = lo + (hi - lo) / 3.0
                m2 = hi - (hi - lo) / 3.0
                if l1_objective(m1, vi, l1_lambda, ridge) < l1_objective(m2, vi, l1_lambda, ridge):
                    hi = m2
                else:
                    lo = m1
            x = 0.5 * (lo + hi)
            objective += l1_objective(x, vi, l1_lambda, ridge)
            checksum += (i + 1) * x
        work = iterations * n
        method = "generic_composite_convex_search"
        iterations_out = iterations
    else:
        denom = 1.0 + ridge
        for i, vi in enumerate(v):
            x = math.copysign(max(abs(vi) - l1_lambda, 0.0), vi) / denom
            objective += l1_objective(x, vi, l1_lambda, ridge)
            checksum += (i + 1) * x
        work = n
        method = "soft_thresholding_proximal_operator"
        iterations_out = 1
    runtime = perf_counter() - start
    return {
        "objective": objective,
        "solution_checksum": checksum,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": iterations_out,
        "variables": n,
        "constraints": 0,
        "nonzeros": n,
        "method": method,
    }


def median_arrays(data: dict) -> tuple[list[float], list[float]]:
    n = int(data["n"])
    seed = int(data["seed"])
    points = [float(((seed * 37 + i * 29) % 2001) - 1000) / 10.0 for i in range(n)]
    weights = [1.0 + ((seed * 11 + i * 17) % 19) for i in range(n)]
    return points, weights


def median_objective(x: float, points: list[float], weights: list[float]) -> float:
    return sum(weights[i] * abs(x - points[i]) for i in range(len(points)))


def weighted_median(points: list[float], weights: list[float]) -> float:
    pairs = sorted(zip(points, weights), key=lambda item: item[0])
    half = 0.5 * sum(weights)
    cumulative = 0.0
    for point, weight in pairs:
        cumulative += weight
        if cumulative >= half:
            return point
    return pairs[-1][0]


def solve_weighted_median(data: dict, mode: str) -> dict:
    points, weights = median_arrays(data)
    n = len(points)
    start = perf_counter()
    if mode == "ordinary":
        best_x = points[0]
        best_obj = float("inf")
        for candidate in points:
            obj = median_objective(candidate, points, weights)
            if obj < best_obj:
                best_obj = obj
                best_x = candidate
        work = n * n
        method = "all_candidate_absolute_loss_scan"
    else:
        best_x = weighted_median(points, weights)
        best_obj = median_objective(best_x, points, weights)
        work = n * int(math.ceil(math.log2(max(2, n))))
        method = "subgradient_weighted_median_condition"
    runtime = perf_counter() - start
    return {
        "objective": best_obj,
        "solution_checksum": best_x,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": n if mode == "ordinary" else 1,
        "variables": 1,
        "constraints": 0,
        "nonzeros": n,
        "method": method,
    }


def simplex_vector(data: dict) -> tuple[list[float], float]:
    n = int(data["n"])
    seed = int(data["seed"])
    v = [
        1.4 * math.sin((i + 1) * (seed + 3) * 0.009)
        + 0.9 * math.cos((i + 2) * (seed + 7) * 0.015)
        + 0.003 * (i % 17)
        for i in range(n)
    ]
    positives = sum(max(value, 0.0) for value in v)
    budget = float(data["budget_fraction"]) * positives
    return v, budget


def simplex_objective(x: list[float], v: list[float]) -> float:
    return 0.5 * sum((x[i] - v[i]) ** 2 for i in range(len(v)))


def simplex_projection_sort(v: list[float], budget: float) -> list[float]:
    u = sorted(v, reverse=True)
    cssv = 0.0
    theta = 0.0
    for idx, value in enumerate(u, start=1):
        cssv += value
        candidate = (cssv - budget) / idx
        if idx == len(u) or u[idx] <= candidate:
            theta = candidate
            break
    return [max(value - theta, 0.0) for value in v]


def solve_simplex(data: dict, mode: str) -> dict:
    v, budget = simplex_vector(data)
    n = len(v)
    start = perf_counter()
    if mode == "ordinary":
        low = min(v) - budget - 1.0
        high = max(v) + 1.0
        iterations = int(data["iterations"])
        for _ in range(iterations):
            mid = 0.5 * (low + high)
            total = sum(max(value - mid, 0.0) for value in v)
            if total > budget:
                low = mid
            else:
                high = mid
        theta = 0.5 * (low + high)
        x = [max(value - theta, 0.0) for value in v]
        work = iterations * n
        method = "generic_projection_dual_bisection"
        iterations_out = iterations
    else:
        x = simplex_projection_sort(v, budget)
        work = n * int(math.ceil(math.log2(max(2, n))))
        method = "simplex_projection_sort_threshold"
        iterations_out = 1
    runtime = perf_counter() - start
    return {
        "objective": simplex_objective(x, v),
        "solution_checksum": sum((i + 1) * x[i] for i in range(n)),
        "max_feasibility_error": abs(sum(x) - budget),
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": iterations_out,
        "variables": n,
        "constraints": n + 1,
        "nonzeros": 2 * n,
        "method": method,
    }


def vi_arrays(data: dict) -> tuple[list[float], list[float], float]:
    n = int(data["n"])
    seed = int(data["seed"])
    h = [1.0 + ((seed + 7 * i) % 31) / 10.0 for i in range(n)]
    a = [65.0 + ((seed * 5 + 11 * i) % 70) / 2.0 for i in range(n)]
    beta = float(data["beta"])
    return h, a, beta


def vi_solution_formula(h: list[float], a: list[float], beta: float) -> list[float]:
    inv_sum = sum(1.0 / value for value in h)
    rhs_sum = sum(a[i] / h[i] for i in range(len(h)))
    total = rhs_sum / (1.0 + beta * inv_sum)
    return [(a[i] - beta * total) / h[i] for i in range(len(h))]


def vi_objective(q: list[float], h: list[float], a: list[float], beta: float) -> float:
    total = sum(q)
    return 0.5 * sum(h[i] * q[i] * q[i] for i in range(len(q))) + 0.5 * beta * total * total - sum(a[i] * q[i] for i in range(len(q)))


def solve_vi(data: dict, mode: str) -> dict:
    h, a, beta = vi_arrays(data)
    n = len(h)
    start = perf_counter()
    if mode == "ordinary":
        matrix = [[beta for _ in range(n)] for _ in range(n)]
        for i in range(n):
            matrix[i][i] += h[i]
        q = dense_solve(matrix, a[:])
        work = n ** 3
        method = "dense_affine_vi_linear_system"
    else:
        q = vi_solution_formula(h, a, beta)
        work = n
        method = "monotone_vi_aggregate_closed_form"
    residual = max(abs(h[i] * q[i] + beta * sum(q) - a[i]) for i in range(n))
    runtime = perf_counter() - start
    return {
        "objective": vi_objective(q, h, a, beta),
        "solution_checksum": sum((i + 1) * q[i] for i in range(n)),
        "max_vi_residual": residual,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": 1,
        "variables": n,
        "constraints": n,
        "nonzeros": n * n,
        "method": method,
    }


def parametric_arrays(data: dict) -> tuple[list[float], list[float], list[float]]:
    n = int(data["n"])
    scenarios = int(data["scenarios"])
    seed = int(data["seed"])
    d = [1.0 + ((seed + 13 * i) % 29) / 8.0 for i in range(n)]
    p = [0.4 + ((seed * 3 + 17 * i) % 101) / 20.0 for i in range(n)]
    base = sum(p)
    budgets = [base * (0.55 + ((seed + 7 * s) % 70) / 200.0) for s in range(scenarios)]
    return d, p, budgets


def parametric_objective_for_budget(d: list[float], p: list[float], budget: float) -> tuple[float, float]:
    inv_sum = sum(1.0 / value for value in d)
    lam = (sum(p) - budget) / inv_sum
    objective = 0.5 * lam * lam * inv_sum
    checksum = sum((i + 1) * (p[i] - lam / d[i]) for i in range(len(d)))
    return objective, checksum


def solve_parametric(data: dict, mode: str) -> dict:
    d, p, budgets = parametric_arrays(data)
    n = len(d)
    start = perf_counter()
    total_objective = 0.0
    checksum = 0.0
    if mode == "ordinary":
        for s, budget in enumerate(budgets):
            size = n + 1
            matrix = [[0.0] * size for _ in range(size)]
            rhs = [0.0] * size
            for i in range(n):
                matrix[i][i] = d[i]
                matrix[i][n] = 1.0
                matrix[n][i] = 1.0
                rhs[i] = d[i] * p[i]
            rhs[n] = budget
            sol = dense_solve(matrix, rhs)
            obj = 0.5 * sum(d[i] * (sol[i] - p[i]) ** 2 for i in range(n))
            total_objective += (1.0 + 0.001 * s) * obj
            checksum += sum((i + 1) * sol[i] for i in range(n))
        work = len(budgets) * (n + 1) ** 3
        method = "independent_dense_kkt_for_each_parameter"
    else:
        for s, budget in enumerate(budgets):
            obj, chk = parametric_objective_for_budget(d, p, budget)
            total_objective += (1.0 + 0.001 * s) * obj
            checksum += chk
        work = len(budgets) * n
        method = "sensitivity_formula_reused_across_parameters"
    runtime = perf_counter() - start
    return {
        "objective": total_objective,
        "solution_checksum": checksum,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": len(budgets),
        "variables": len(budgets) * (n + 1) if mode == "ordinary" else n + len(budgets),
        "constraints": len(budgets),
        "nonzeros": len(budgets) * 3 * n if mode == "ordinary" else len(budgets) + n,
        "method": method,
    }


def cq_arrays(data: dict) -> tuple[list[int], list[float], list[float]]:
    n = int(data["n"])
    seed = int(data["seed"])
    anchors = [((seed + 7 * i) % 41) - 20 for i in range(n)]
    target = [anchors[i] + (((seed * 5 + 11 * i) % 101) - 50) / 17.0 for i in range(n)]
    weights = [1.0 + ((seed + 13 * i) % 17) / 5.0 for i in range(n)]
    return anchors, target, weights


def solve_cq(data: dict, mode: str) -> dict:
    anchors, target, weights = cq_arrays(data)
    n = len(anchors)
    start = perf_counter()
    objective = 0.0
    checksum = 0.0
    if mode == "ordinary":
        window = int(data["scan_window"])
        for i in range(n):
            best = float("inf")
            best_x = anchors[i]
            for candidate in range(anchors[i] - window, anchors[i] + window + 1):
                if (candidate - anchors[i]) ** 2 <= 0:
                    obj = 0.5 * weights[i] * (candidate - target[i]) ** 2
                    if obj < best:
                        best = obj
                        best_x = candidate
            objective += best
            checksum += (i + 1) * best_x
        work = n * (2 * window + 1)
        method = "generic_kkt_search_despite_failed_cq"
        variables = n
        constraints = n
        nonzeros = n
    else:
        for i in range(n):
            objective += 0.5 * weights[i] * (anchors[i] - target[i]) ** 2
            checksum += (i + 1) * anchors[i]
        work = n
        method = "constraint_qualification_audit_reduce_zero_gradient_constraints"
        variables = 0
        constraints = 0
        nonzeros = 0
    runtime = perf_counter() - start
    return {
        "objective": objective,
        "solution_checksum": checksum,
        "cq_valid": False,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": 1,
        "variables": variables,
        "constraints": constraints,
        "nonzeros": nonzeros,
        "method": method,
    }


def newsvendor_arrays(data: dict) -> tuple[list[list[int]], float, float, int]:
    products = int(data["products"])
    scenarios = int(data["scenarios"])
    max_q = int(data["max_q"])
    seed = int(data["seed"])
    demands = []
    for p in range(products):
        row = []
        for s in range(scenarios):
            value = 10 + ((seed * 17 + p * 31 + s * 19 + (p + 3) * (s % 23)) % (max_q - 9))
            row.append(value)
        demands.append(row)
    return demands, float(data["holding_cost"]), float(data["shortage_cost"]), max_q


def newsvendor_cost(q: int, demands: list[int], holding: float, shortage: float) -> float:
    return sum(holding * max(q - d, 0) + shortage * max(d - q, 0) for d in demands) / len(demands)


def solve_newsvendor(data: dict, mode: str) -> dict:
    demands_by_product, holding, shortage, max_q = newsvendor_arrays(data)
    products_count = len(demands_by_product)
    scenarios = len(demands_by_product[0])
    start = perf_counter()
    objective = 0.0
    checksum = 0.0
    if mode == "ordinary":
        for p, demands in enumerate(demands_by_product):
            best_q = 0
            best_obj = float("inf")
            for q in range(max_q + 1):
                obj = newsvendor_cost(q, demands, holding, shortage)
                if obj < best_obj:
                    best_obj = obj
                    best_q = q
            objective += best_obj
            checksum += (p + 1) * best_q
        work = products_count * (max_q + 1) * scenarios
        method = "full_scenario_grid_scan"
    else:
        alpha = shortage / (shortage + holding)
        for p, demands in enumerate(demands_by_product):
            sorted_demands = sorted(demands)
            index = min(len(sorted_demands) - 1, max(0, math.ceil(alpha * len(sorted_demands)) - 1))
            q = sorted_demands[index]
            objective += newsvendor_cost(q, demands, holding, shortage)
            checksum += (p + 1) * q
        work = products_count * scenarios * int(math.ceil(math.log2(max(2, scenarios))))
        method = "scenario_decomposition_quantile_rule"
    runtime = perf_counter() - start
    return {
        "objective": objective,
        "solution_checksum": checksum,
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": products_count,
        "variables": products_count * scenarios if mode == "ordinary" else products_count,
        "constraints": products_count * scenarios if mode == "ordinary" else products_count,
        "nonzeros": products_count * scenarios,
        "method": method,
    }


def lex_options(data: dict) -> list[list[tuple[int, int, int]]]:
    groups = int(data["groups"])
    options = int(data["options"])
    seed = int(data["seed"])
    all_options = []
    for g in range(groups):
        group = []
        for o in range(options):
            primary = (seed * (g + 3) + 17 * o + 5 * g * o) % 47
            secondary = (seed * (o + 5) + 13 * g + 7 * o * o) % 89
            tertiary = (seed + 19 * g + 23 * o + 3 * g * o) % 101
            group.append((primary, secondary, tertiary))
        all_options.append(group)
    return all_options


def lex_score(metrics: tuple[int, int, int]) -> float:
    return metrics[0] * 1_000_000.0 + metrics[1] * 1_000.0 + metrics[2]


def solve_lex(data: dict, mode: str) -> dict:
    options = lex_options(data)
    groups = len(options)
    start = perf_counter()
    if mode == "ordinary":
        best_tuple: tuple[int, int, int] | None = None
        best_choice: tuple[int, ...] | None = None
        for choice in product(range(len(options[0])), repeat=groups):
            primary = secondary = tertiary = 0
            for g, option_index in enumerate(choice):
                p, s, t = options[g][option_index]
                primary += p
                secondary += s
                tertiary += t
            candidate = (primary, secondary, tertiary)
            if best_tuple is None or candidate < best_tuple:
                best_tuple = candidate
                best_choice = choice
        assert best_tuple is not None and best_choice is not None
        work = (len(options[0]) ** groups) * groups
        method = "cartesian_product_weighted_sum_search"
        checksum = sum((g + 1) * best_choice[g] for g in range(groups))
    else:
        best_tuple = (0, 0, 0)
        checksum = 0
        for g, group in enumerate(options):
            best_option_index, best_metrics = min(enumerate(group), key=lambda item: item[1])
            best_tuple = tuple(best_tuple[i] + best_metrics[i] for i in range(3))  # type: ignore[assignment]
            checksum += (g + 1) * best_option_index
        work = groups * len(options[0])
        method = "staged_lexicographic_filtering"
    runtime = perf_counter() - start
    return {
        "objective": lex_score(best_tuple),
        "lex_tuple": list(best_tuple),
        "solution_checksum": float(checksum),
        "wall_seconds": runtime,
        "runtime": runtime,
        "work": work,
        "iterations": groups,
        "variables": groups,
        "constraints": 3 * groups,
        "nonzeros": groups * len(options[0]),
        "method": method,
    }


def solve_model(mode: str) -> dict:
    data = load_data()
    model_type = data["model_type"]
    if model_type == "box_qp":
        return solve_box_qp(data, mode)
    if model_type == "activation":
        return solve_activation(data, mode)
    if model_type == "soc":
        return solve_soc(data, mode)
    if model_type == "exp_dcp":
        return solve_exp_dcp(data, mode)
    if model_type == "l1_composite":
        return solve_l1(data, mode)
    if model_type == "weighted_median":
        return solve_weighted_median(data, mode)
    if model_type == "simplex_projection":
        return solve_simplex(data, mode)
    if model_type == "vi_affine":
        return solve_vi(data, mode)
    if model_type == "parametric_qp":
        return solve_parametric(data, mode)
    if model_type == "cq_degenerate":
        return solve_cq(data, mode)
    if model_type == "newsvendor":
        return solve_newsvendor(data, mode)
    if model_type == "lexicographic":
        return solve_lex(data, mode)
    raise ValueError(f"unknown model_type: {model_type}")
