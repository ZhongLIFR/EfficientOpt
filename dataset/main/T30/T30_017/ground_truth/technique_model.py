from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _improve(tour: list[int], costs: list[list[float]]) -> list[int]:
    n = len(tour)
    improved = True
    while improved:
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                old = costs[tour[i]][tour[(i + 1) % n]] + costs[tour[j]][tour[(j + 1) % n]]
                new = costs[tour[i]][tour[j]] + costs[tour[(i + 1) % n]][tour[(j + 1) % n]]
                if new + 1e-9 < old:
                    tour[i + 1:j + 1] = reversed(tour[i + 1:j + 1])
                    improved = True
    return tour


def _initial_tour(costs: list[list[float]]) -> list[int]:
    n = len(costs)
    best_tour = None
    best_cost = None
    for first in range(n):
        tour = [first]
        unvisited = set(range(n)) - {first}
        while unvisited:
            nxt = min(unvisited, key=lambda j: (costs[tour[-1]][j], j))
            tour.append(nxt)
            unvisited.remove(nxt)
        tour = _improve(tour, costs)
        zero = tour.index(0)
        tour = tour[zero:] + tour[:zero]
        value = sum(costs[tour[k]][tour[(k + 1) % n]] for k in range(n))
        if best_cost is None or value < best_cost:
            best_cost, best_tour = value, tour
    assert best_tour is not None
    return best_tour


def build_model(instance: dict) -> gp.Model:
    model = gp.Model("regional_tsp_warm_start")
    objective = gp.LinExpr()
    for r, region in enumerate(instance["regions"]):
        n = len(region["sites"])
        costs = region["travel_cost"]
        arcs = [(i, j) for i in range(n) for j in range(n) if i != j]
        travel = model.addVars(arcs, vtype=GRB.BINARY, name=f"travel_{r}")
        order = model.addVars(range(1, n), lb=1, ub=n - 1, name=f"visit_order_{r}")
        model.addConstrs((gp.quicksum(travel[i, j] for j in range(n) if j != i) == 1 for i in range(n)), name=f"depart_once_{r}")
        model.addConstrs((gp.quicksum(travel[j, i] for j in range(n) if j != i) == 1 for i in range(n)), name=f"arrive_once_{r}")
        model.addConstrs((order[i] - order[j] + n * travel[i, j] <= n - 1 for i in range(1, n) for j in range(1, n) if i != j), name=f"order_link_{r}")
        objective += gp.quicksum(costs[i][j] * travel[i, j] for i, j in arcs)
        tour = _initial_tour(costs)
        selected = {(tour[k], tour[(k + 1) % n]) for k in range(n)}
        for arc in arcs:
            travel[arc].Start = int(arc in selected)
        for position in range(1, n):
            order[tour[position]].Start = position
    model.setObjective(objective, GRB.MINIMIZE)
    return model
