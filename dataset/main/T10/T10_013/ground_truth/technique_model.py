import gurobipy as gp
from gurobipy import GRB


TECHNIQUE = True
FULL_MCCORMICK = False


def build_model(instance):
    departments = range(len(instance["departments"]))
    cities = range(len(instance["cities"]))
    model = gp.Model("joint_marginal_convex_hull" if TECHNIQUE else "local_product_envelopes")
    located = model.addVars(departments, cities, vtype=GRB.BINARY, name="located")
    model.addConstrs(
        (gp.quicksum(located[i, city] for city in cities) == 1 for i in departments),
        name="assign",
    )
    model.addConstrs(
        (
            gp.quicksum(located[i, city] for i in departments)
            <= int(instance["city_capacity"][city])
            for city in cities
        ),
        name="capacity",
    )

    objective = gp.quicksum(
        (
            float(instance["fixed_assignment_cost"][i][city])
            - float(instance["relocation_benefit"][i])
        )
        * located[i, city]
        for i in departments
        for city in cities
    )
    for edge, raw_edge in enumerate(instance["communication_edges"]):
        i, j, volume = int(raw_edge[0]), int(raw_edge[1]), float(raw_edge[2])
        joint = model.addVars(cities, cities, lb=0.0, ub=1.0, name=f"pair[{edge}]")
        if TECHNIQUE:
            model.addConstrs(
                (
                    gp.quicksum(joint[city, other] for other in cities) == located[i, city]
                    for city in cities
                ),
                name=f"row_marginal[{edge}]",
            )
            model.addConstrs(
                (
                    gp.quicksum(joint[other, city] for other in cities) == located[j, city]
                    for city in cities
                ),
                name=f"column_marginal[{edge}]",
            )
        else:
            model.addConstrs(
                (
                    joint[city, other] >= located[i, city] + located[j, other] - 1.0
                    for city in cities
                    for other in cities
                ),
                name=f"product_lower_envelope[{edge}]",
            )
            if FULL_MCCORMICK:
                model.addConstrs(
                    (
                        joint[city, other] <= located[i, city]
                        for city in cities
                        for other in cities
                    ),
                    name=f"product_upper_i[{edge}]",
                )
                model.addConstrs(
                    (
                        joint[city, other] <= located[j, other]
                        for city in cities
                        for other in cities
                    ),
                    name=f"product_upper_j[{edge}]",
                )
        objective += gp.quicksum(
            volume
            * float(instance["city_pair_cost"][city][other])
            * joint[city, other]
            for city in cities
            for other in cities
        )

    model.setObjective(objective, GRB.MINIMIZE)
    return model
