import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    orders = instance["work_orders"]
    resource_capacities = instance["resource_capacities"]
    minimum_service_scores = instance["minimum_service_scores"]
    segments = {row["segment"]: row for row in instance["segment_limits"]}

    model = gp.Model("two_plan_portfolio_eliminated")
    choose_b = {i: model.addVar(vtype=GRB.BINARY, name=f"choose_b[{i}]") for i in range(len(orders))}

    for r, capacity in enumerate(resource_capacities):
        base = sum(row["resource_a"][r] for row in orders)
        model.addConstr(
            gp.quicksum(
                (row["resource_b"][r] - row["resource_a"][r]) * choose_b[i]
                for i, row in enumerate(orders)
            ) <= capacity - base,
            name=f"resource[{r}]",
        )

    for s, minimum in enumerate(minimum_service_scores):
        base = sum(row["service_a"][s] for row in orders)
        model.addConstr(
            gp.quicksum(
                (row["service_b"][s] - row["service_a"][s]) * choose_b[i]
                for i, row in enumerate(orders)
            ) >= minimum - base,
            name=f"service[{s}]",
        )

    by_segment = {segment: [] for segment in segments}
    for i, row in enumerate(orders):
        by_segment[row["segment"]].append(i)
    for segment, indices in by_segment.items():
        limits = segments[segment]
        total_b = gp.quicksum(choose_b[i] for i in indices)
        model.addConstr(total_b >= limits["minimum_plan_b"], name=f"segment_min[{segment}]")
        model.addConstr(total_b <= limits["maximum_plan_b"], name=f"segment_max[{segment}]")

    base_cost = sum(row["cost_a"] for row in orders)
    model.setObjective(
        base_cost + gp.quicksum(
            (row["cost_b"] - row["cost_a"]) * choose_b[i]
            for i, row in enumerate(orders)
        ),
        GRB.MINIMIZE,
    )
    return model
