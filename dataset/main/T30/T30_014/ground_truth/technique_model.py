from __future__ import annotations

import gurobipy as gp
from gurobipy import GRB


def _initial_tour(costs: list[list[float]]) -> list[int]:
    n = len(costs)
    tour = [0]
    unvisited = set(range(1, n))
    while unvisited:
        next_site = min(unvisited, key=lambda j: (costs[tour[-1]][j], j))
        tour.append(next_site)
        unvisited.remove(next_site)

    improved = True
    while improved:
        improved = False
        for start in range(1, n - 1):
            for end in range(start + 1, n):
                old = costs[tour[start - 1]][tour[start]] + costs[tour[end]][tour[(end + 1) % n]]
                new = costs[tour[start - 1]][tour[end]] + costs[tour[start]][tour[(end + 1) % n]]
                if new + 1e-9 < old:
                    tour[start : end + 1] = reversed(tour[start : end + 1])
                    improved = True
    return tour


def build_model(instance: dict) -> gp.Model:
    n = len(instance["sites"])
    costs = instance["travel_cost"]
    arcs = [(i, j) for i in range(n) for j in range(n) if i != j]

    model = gp.Model("directed_tsp_warm_start")
    travel = model.addVars(arcs, vtype=GRB.BINARY, name="travel")
    order = model.addVars(range(1, n), lb=1, ub=n - 1, name="visit_order")
    model.addConstrs(
        (gp.quicksum(travel[i, j] for j in range(n) if j != i) == 1 for i in range(n)),
        name="depart_once",
    )
    model.addConstrs(
        (gp.quicksum(travel[j, i] for j in range(n) if j != i) == 1 for i in range(n)),
        name="arrive_once",
    )
    model.addConstrs(
        (
            order[i] - order[j] + n * travel[i, j] <= n - 1
            for i in range(1, n)
            for j in range(1, n)
            if i != j
        ),
        name="order_link",
    )
    model.setObjective(
        gp.quicksum(costs[i][j] * travel[i, j] for i, j in arcs),
        GRB.MINIMIZE,
    )

    tour = _initial_tour(costs)
    selected = {(tour[k], tour[(k + 1) % n]) for k in range(n)}
    for arc in arcs:
        travel[arc].Start = int(arc in selected)
    for position in range(1, n):
        order[tour[position]].Start = position
    return model

