"""Route-set-partitioning builder derived only from primitive cost matrices."""

from __future__ import annotations

from itertools import combinations

import gurobipy as gp


CUSTOMERS = tuple(range(1, 11))
SUBSETS_BY_SIZE = {
    size: tuple(combinations(CUSTOMERS, size))
    for size in range(1, 6)
}
ROUTE_SUBSETS = SUBSETS_BY_SIZE[5]


def _optimal_five_city_route_costs(cost):
    """Return the optimal depot tour cost for every five-city subset."""
    dp = {}
    for city in CUSTOMERS:
        dp[(1 << (city - 1), city)] = float(cost[0][city])

    for size in range(2, 6):
        for subset in SUBSETS_BY_SIZE[size]:
            mask = sum(1 << (city - 1) for city in subset)
            for last in subset:
                previous_mask = mask ^ (1 << (last - 1))
                dp[(mask, last)] = min(
                    dp[(previous_mask, previous)] + float(cost[previous][last])
                    for previous in subset
                    if previous != last
                )

    route_costs = []
    for subset in ROUTE_SUBSETS:
        mask = sum(1 << (city - 1) for city in subset)
        best = min(dp[(mask, last)] + float(cost[last][0]) for last in subset)
        route_costs.append(round(best, 4))
    return route_costs


def build_model(instance):
    model = gp.Model("t21_route_set_partitioning")
    objective = gp.LinExpr()
    for block_index, block in enumerate(instance["blocks"]):
        route_costs = _optimal_five_city_route_costs(block["cost"])
        use = model.addVars(
            len(ROUTE_SUBSETS),
            vtype=gp.GRB.BINARY,
            name=f"route[{block_index}]",
        )
        for customer in CUSTOMERS:
            model.addConstr(
                gp.quicksum(
                    use[route_index]
                    for route_index, subset in enumerate(ROUTE_SUBSETS)
                    if customer in subset
                )
                == 1,
                name=f"cover[{block_index},{customer}]",
            )
        model.addConstr(
            gp.quicksum(use.values()) == 2,
            name=f"two_routes[{block_index}]",
        )
        objective += gp.quicksum(
            route_costs[route_index] * use[route_index]
            for route_index in range(len(ROUTE_SUBSETS))
        )
    model.setObjective(objective, gp.GRB.MINIMIZE)
    return model
