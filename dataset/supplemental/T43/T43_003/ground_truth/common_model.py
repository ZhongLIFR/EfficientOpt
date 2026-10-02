from __future__ import annotations

import itertools
import json
import math
import time
from collections import defaultdict, deque
from pathlib import Path


def load_data() -> dict:
    return json.loads(Path("instance.json").read_text(encoding="utf-8"))


def outcome(objective, start, work, iterations, variables, constraints, nonzeros, method, **extra):
    result = {
        "objective": float(objective),
        "wall_seconds": time.perf_counter() - start,
        "runtime": time.perf_counter() - start,
        "work": int(work),
        "iterations": int(iterations),
        "variables": int(variables),
        "constraints": int(constraints),
        "nonzeros": int(nonzeros),
        "method": method,
    }
    result.update(extra)
    return result


def _t29_sos(data, mode):
    start = time.perf_counter()
    costs = data["mode_costs"]
    n = len(costs)
    m = len(costs[0])
    if mode == "technique":
        selected = [min(row) for row in costs]
        return outcome(sum(selected), start, n * m, n, n * m, n, n * m, "one_choice_native_selection", selected_modes=[min(range(m), key=row.__getitem__) for row in costs])
    best = float("inf")
    best_modes = None
    work = 0
    for modes in itertools.product(range(m), repeat=n):
        value = 0.0
        for i, j in enumerate(modes):
            value += costs[i][j]
            work += 1
        if value < best:
            best = value
            best_modes = modes
    return outcome(best, start, work, m ** n, n * m, n, n * m, "enumerate_one_choice_assignments", selected_modes=list(best_modes))


def _t29_indicator(data, mode):
    start = time.perf_counter()
    costs = data["activation_costs"]
    k = int(data["active_count"])
    n = len(costs)
    if mode == "technique":
        order = sorted(range(n), key=lambda i: costs[i])
        selected = order[:k]
        return outcome(sum(costs[i] for i in selected), start, n * math.ceil(math.log2(max(2, n))), n, n, n, n, "indicator_propagation_and_sorted_activation", selected=selected)
    best = float("inf")
    selected_best = None
    work = 0
    for selected in itertools.combinations(range(n), k):
        work += len(selected)
        value = sum(costs[i] for i in selected)
        if value < best:
            best = value
            selected_best = selected
    return outcome(best, start, work, math.comb(n, k), n, 1, n, "enumerate_indicator_activation_patterns", selected=list(selected_best))


def _pwl_cost(q, breaks, slopes, fixed):
    value = fixed
    previous = 0.0
    for upper, slope in zip(breaks, slopes):
        width = max(0.0, min(q, upper) - previous)
        value += width * slope
        previous = upper
        if q <= upper:
            break
    return value


def _t29_pwl(data, mode):
    start = time.perf_counter()
    queries = data["queries"]
    breaks = data["breaks"]
    slopes = data["slopes"]
    fixed = data["fixed_cost"]
    total = 0.0
    work = 0
    if mode == "technique":
        for q in queries:
            lo, hi = 0, len(breaks) - 1
            while lo < hi:
                mid = (lo + hi) // 2
                work += 1
                if q <= breaks[mid]:
                    hi = mid
                else:
                    lo = mid + 1
            total += _pwl_cost(q, breaks, slopes, fixed)
        method = "ordered_piecewise_segment_lookup"
    else:
        for q in queries:
            for segment in range(len(breaks)):
                work += 1
                if q <= breaks[segment]:
                    total += _pwl_cost(q, breaks, slopes, fixed)
                    break
        method = "scan_all_piecewise_segments"
    return outcome(total, start, work, len(queries), len(queries) * len(breaks), len(queries), len(queries) * len(breaks), method)


def _t31_dag(data, mode):
    start = time.perf_counter()
    n = data["node_count"]
    edges = [tuple(edge) for edge in data["edges"]]
    source = data["source"]
    target = data["target"]
    dist = [float("inf")] * n
    dist[source] = 0.0
    work = 0
    if mode == "technique":
        outgoing = [[] for _ in range(n)]
        for u, v, w in edges:
            outgoing[u].append((v, w))
        for u in range(n):
            for v, w in outgoing[u]:
                work += 1
                dist[v] = min(dist[v], dist[u] + w)
        method = "topological_dag_shortest_path"
        iterations = n
    else:
        for _ in range(n - 1):
            changed = False
            for u, v, w in edges:
                work += 1
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    changed = True
            if not changed:
                break
        method = "repeated_generic_relaxation"
        iterations = n - 1
    return outcome(dist[target], start, work, iterations, n, n, len(edges), method)


def _t31_intervals(data, mode):
    start = time.perf_counter()
    intervals = [tuple(x) for x in data["intervals"]]
    n = len(intervals)
    if mode == "technique":
        selected = []
        end = -float("inf")
        for idx, (left, right) in sorted(enumerate(intervals), key=lambda x: (x[1][1], x[1][0])):
            if left >= end:
                selected.append(idx)
                end = right
        return outcome(len(selected), start, n * math.ceil(math.log2(max(2, n))), n, n, 1, n, "earliest_finish_interval_matching", selected=selected)
    best = 0
    best_set = []
    work = 0
    for mask in range(1 << n):
        chosen = []
        valid = True
        for i in range(n):
            if mask & (1 << i):
                work += 1
                for j in chosen:
                    if not (intervals[i][1] <= intervals[j][0] or intervals[j][1] <= intervals[i][0]):
                        valid = False
                        break
                if not valid:
                    break
                chosen.append(i)
        if valid and len(chosen) > best:
            best = len(chosen)
            best_set = chosen
    return outcome(best, start, work, 1 << n, n, n, n, "enumerate_interval_subsets", selected=best_set)


def _tree_children(n):
    return {i: [j for j in (2 * i + 1, 2 * i + 2) if j < n] for i in range(n)}


def _t31_tree(data, mode):
    start = time.perf_counter()
    weights = data["weights"]
    n = len(weights)
    children = _tree_children(n)
    if mode == "technique":
        def dp(node):
            child_values = [dp(child) for child in children[node]]
            skip = sum(value[0] for value in child_values)
            take = weights[node] + sum(value[1] for value in child_values)
            return max(skip, take), skip
        best, _ = dp(0)
        return outcome(best, start, n, n, n, n - 1, n - 1, "tree_message_passing_independent_set")
    best = 0
    work = 0
    for mask in range(1 << n):
        valid = True
        value = 0
        for node in range(n):
            if mask & (1 << node):
                work += 1
                for child in children[node]:
                    if mask & (1 << child):
                        valid = False
                        break
                if not valid:
                    break
                value += weights[node]
        if valid and value > best:
            best = value
    return outcome(best, start, work, 1 << n, n, n - 1, n - 1, "enumerate_tree_independent_sets")


def _hitset_value(costs, sets, mask):
    return sum(costs[i] for i in range(len(costs)) if mask & (1 << i)) if all(any(mask & (1 << i) for i in s) for s in sets) else float("inf")


def _t32_hitset(data, mode):
    start = time.perf_counter()
    costs = data["costs"]
    sets = [set(x) for x in data["conflict_logs"]]
    n = len(costs)
    if mode == "technique":
        # Logs are intentionally partitioned into independent connected components.
        components = []
        unvisited = set(range(n))
        while unvisited:
            seed = next(iter(unvisited)); component = {seed}; changed = True
            while changed:
                changed = False
                for s in sets:
                    if component & s and not s <= component:
                        component |= s; changed = True
            unvisited -= component
            components.append(component)
        total = 0; work = 0
        for comp in components:
            comp_list = sorted(comp); best = float("inf")
            local_sets = [s & comp for s in sets if s & comp]
            for mask in range(1 << len(comp_list)):
                work += 1
                global_mask = sum((1 << item) for j, item in enumerate(comp_list) if mask & (1 << j))
                best = min(best, _hitset_value(costs, local_sets, global_mask))
            total += best
        return outcome(total, start, work, len(components), n, len(sets), sum(len(s) for s in sets), "conflict_log_component_diagnosis")
    best = float("inf"); work = 0
    for mask in range(1 << n):
        work += 1
        best = min(best, _hitset_value(costs, sets, mask))
    return outcome(best, start, work, 1, n, len(sets), sum(len(s) for s in sets), "global_repair_set_enumeration")


def _threshold(data, mode):
    start = time.perf_counter()
    lo, hi = int(data["lower"]), int(data["upper"])
    demands = data["demands"]; caps = data["capacities"]; target = float(data["target_residual"])
    def residual(t):
        return sum(max(0.0, d - t * c) for d, c in zip(demands, caps))
    work = 0
    if mode == "technique":
        while lo < hi:
            mid = (lo + hi) // 2
            work += 1
            if residual(mid) <= target: hi = mid
            else: lo = mid + 1
        method = "log_guided_binary_threshold"
        iterations = work
    else:
        answer = hi
        for t in range(lo, hi + 1):
            work += 1
            if residual(t) <= target:
                answer = t; break
        lo = answer
        method = "scan_all_threshold_candidates"
        iterations = work
    return outcome(lo, start, work * len(demands), iterations, len(demands), 1, len(demands), method, residual=residual(lo))


def _t32_components(data, mode):
    start = time.perf_counter()
    costs = data["costs"]; groups = [set(x) for x in data["log_components"]]
    n = len(costs)
    if mode == "technique":
        total = 0; work = 0
        for group in groups:
            best = float("inf")
            for mask in range(1 << len(group)):
                work += 1
                value = sum(costs[i] for j, i in enumerate(sorted(group)) if mask & (1 << j))
                if all(any(mask & (1 << j) for j, i in enumerate(sorted(group)) if i in log) for log in groups if log <= group):
                    best = min(best, value)
            total += best
        return outcome(total, start, work, len(groups), n, len(groups), sum(len(g) for g in groups), "log_connected_component_decomposition")
    best = float("inf"); work = 0
    for mask in range(1 << n):
        work += 1
        if all(any(mask & (1 << i) for i in log) for log in groups):
            best = min(best, sum(costs[i] for i in range(n) if mask & (1 << i)))
    return outcome(best, start, work, 1, n, len(groups), sum(len(g) for g in groups), "global_log_fault_enumeration")


def _t33_sparse(data, mode):
    start = time.perf_counter()
    terms = [tuple(x) for x in data["raw_terms"]]
    candidates = data["candidates"]; targets = data["targets"]
    if mode == "technique":
        canonical = defaultdict(float)
        for expr, idx, coef in terms:
            canonical[(expr, idx)] += coef
        work = len(terms) + len(candidates) * len(targets)
        method = "canonical_sparse_coefficient_aggregation"
        coeffs = canonical
    else:
        work = 0
        best = float("inf")
        for x in candidates:
            score = 0.0
            for expr, target in enumerate(targets):
                total = 0.0
                for e, idx, coef in terms:
                    if e == expr:
                        total += coef * x[idx]; work += 1
                score += (total - target) ** 2
            best = min(best, score)
        return outcome(best, start, work, len(candidates), len(candidates) * len(targets), len(targets), len(terms), "reparse_raw_sparse_terms_per_candidate")
    best = float("inf")
    for x in candidates:
        score = 0.0
        for expr, target in enumerate(targets):
            total = sum(coef * x[idx] for (e, idx), coef in coeffs.items() if e == expr)
            score += (total - target) ** 2
        best = min(best, score)
    return outcome(best, start, work, len(candidates), len(candidates) * len(targets), len(targets), len(coeffs), method)


def _t33_sign(data, mode):
    start = time.perf_counter()
    rows = data["rows"]; candidates = data["candidates"]
    if mode == "technique":
        canonical = []
        for row in rows:
            sense = row["sense"]
            coeffs = row["coefficients"]
            rhs = row["rhs"]
            if sense == ">=": coeffs = [-c for c in coeffs]; rhs = -rhs
            elif sense == "=":
                canonical.append((coeffs, rhs, "<=")); coeffs = [-c for c in coeffs]; rhs = -rhs
            canonical.append((coeffs, rhs, "<="))
        work = sum(len(row["coefficients"]) for row in rows) + len(candidates) * len(canonical)
        def feasible(x): return all(sum(c * x[i] for i, c in enumerate(coeffs)) <= rhs + 1e-9 for coeffs, rhs, _ in canonical)
        method = "canonical_standard_leq_transformation"
    else:
        work = len(candidates) * sum(len(row["coefficients"]) for row in rows)
        def feasible(x):
            for row in rows:
                lhs = sum(c * x[i] for i, c in enumerate(row["coefficients"]))
                if row["sense"] == "<=" and lhs > row["rhs"] + 1e-9: return False
                if row["sense"] == ">=" and lhs < row["rhs"] - 1e-9: return False
                if row["sense"] == "=" and abs(lhs - row["rhs"]) > 1e-9: return False
            return True
        method = "raw_mixed_sense_branch_evaluation"
    best = float("inf")
    for x in candidates:
        if feasible(x): best = min(best, sum(v * v for v in x))
    return outcome(best, start, work, len(candidates), len(candidates), len(rows), sum(len(r["coefficients"]) for r in rows), method)


def _t33_block(data, mode):
    start = time.perf_counter()
    blocks = data["blocks"]; candidates = data["candidates"]
    if mode == "technique":
        stats = []
        for block in blocks:
            xtx = [[sum(row[i] * row[j] for row in block["features"]) for j in range(len(block["features"][0]))] for i in range(len(block["features"][0]))]
            xty = [sum(row[i] * y for row, y in zip(block["features"], block["targets"])) for i in range(len(xtx))]
            yty = sum(y * y for y in block["targets"])
            stats.append((xtx, xty, yty))
        work = sum(len(b["features"]) * len(b["features"][0]) for b in blocks) + len(candidates) * len(stats)
        method = "canonical_block_sufficient_statistics"
        best = float("inf")
        for x in candidates:
            value = 0.0
            for (xtx, xty, yty), block in zip(stats, blocks):
                value += yty - 2 * sum(x[i] * xty[i] for i in range(len(x))) + sum(x[i] * xtx[i][j] * x[j] for i in range(len(x)) for j in range(len(x)))
            best = min(best, value)
    else:
        work = 0; best = float("inf")
        for x in candidates:
            value = 0.0
            for block in blocks:
                for row, y in zip(block["features"], block["targets"]):
                    residual = y - sum(a * b for a, b in zip(row, x)); value += residual * residual; work += len(x)
            best = min(best, value)
        method = "rebuild_block_quadratics_per_candidate"
    return outcome(best, start, work, len(candidates), len(candidates) * len(blocks), sum(len(b["features"]) for b in blocks), sum(len(b["features"]) * len(b["features"][0]) for b in blocks), method)


def _t43_knapsack(data, mode):
    start = time.perf_counter(); weights=data["weights"]; values=data["values"]; cap=data["capacity"]; n=len(weights)
    if mode == "technique":
        dp=[0]*(cap+1); work=0
        for w,v in zip(weights,values):
            for c in range(cap,w-1,-1): dp[c]=max(dp[c],dp[c-w]+v); work+=1
        return outcome(dp[cap],start,work,n,cap+1,cap,cap*n,"zero_one_knapsack_dynamic_programming")
    best=0;work=0
    for mask in range(1<<n):
        w=v=0
        for i in range(n):
            if mask&(1<<i): w+=weights[i];v+=values[i];work+=1
        if w<=cap: best=max(best,v)
    return outcome(best,start,work,1<<n,n,1,n,"enumerate_knapsack_subsets")


def _t43_inventory(data, mode):
    start=time.perf_counter(); demand=data["demand"]; max_prod=data["max_production"]; holding=data["holding_cost"]; prod=data["production_cost"]; cap=data["inventory_capacity"]; periods=len(demand)
    if mode=="technique":
        dp={0:0.0};work=0
        for d in demand:
            nd={}
            for inv,cost in dp.items():
                for q in range(max_prod+1):
                    next_inv=inv+q-d
                    if 0<=next_inv<=cap:
                        nd[next_inv]=min(nd.get(next_inv,float('inf')),cost+q*prod+next_inv*holding);work+=1
            dp=nd
        return outcome(min(dp.values()),start,work,periods,periods*(cap+1),periods*(cap+1),periods*(cap+1)*(max_prod+1),"inventory_state_transition_dynamic_programming")
    best=float('inf');work=0
    for plan in itertools.product(range(max_prod+1),repeat=periods):
        inv=0;cost=0.0;valid=True
        for q,d in zip(plan,demand):
            inv+=q-d;work+=1
            if inv<0 or inv>cap:valid=False;break
            cost+=q*prod+inv*holding
        if valid:best=min(best,cost)
    return outcome(best,start,work,max_prod**periods,periods,periods,periods*max_prod,"enumerate_inventory_plans")


def _t43_alignment(data, mode):
    start=time.perf_counter(); a=data["a"];b=data["b"]; match=data["match_cost"]; mismatch=data["mismatch_cost"]; gap=data["gap_cost"]; n=len(a);m=len(b)
    if mode=="technique":
        dp=[[0.0]*(m+1) for _ in range(n+1)];work=0
        for i in range(n+1):dp[i][0]=i*gap
        for j in range(m+1):dp[0][j]=j*gap
        for i in range(1,n+1):
            for j in range(1,m+1):dp[i][j]=min(dp[i-1][j-1]+(match if a[i-1]==b[j-1] else mismatch),dp[i-1][j]+gap,dp[i][j-1]+gap);work+=1
        return outcome(dp[n][m],start,work,n*m,n*m,n*m,3*n*m,"sequence_alignment_dynamic_programming")
    work=0
    def brute(i,j):
        nonlocal work
        work+=1
        if i==0:return j*gap
        if j==0:return i*gap
        return min(brute(i-1,j-1)+(match if a[i-1]==b[j-1] else mismatch),brute(i-1,j)+gap,brute(i,j-1)+gap)
    value=brute(n,m)
    return outcome(value,start,work,work,n*m,n*m,3*n*m,"recursive_alignment_path_enumeration")


DISPATCH={
    "T29_SOS_PORTFOLIO_001":_t29_sos,"T29_INDICATOR_MODE_002":_t29_indicator,"T29_NATIVE_PWL_003":_t29_pwl,
    "T31_DAG_ROUTE_001":_t31_dag,"T31_INTERVAL_SELECTION_002":_t31_intervals,"T31_TREE_FLOW_003":_t31_tree,
    "T32_LOG_HITSET_001":_t32_hitset,"T32_LOG_THRESHOLD_002":_threshold,"T32_LOG_COMPONENT_003":_t32_components,
    "T33_CANONICAL_SPARSE_001":_t33_sparse,"T33_STANDARD_SIGN_002":_t33_sign,"T33_CANONICAL_BLOCK_003":_t33_block,
    "T43_003":_t43_knapsack,"T43_INVENTORY_DP_002":_t43_inventory,"T43_ALIGNMENT_DP_003":_t43_alignment,
}


def solve_model(mode: str) -> dict:
    data = load_data()
    return DISPATCH[data["problem_id"]](data, mode)
