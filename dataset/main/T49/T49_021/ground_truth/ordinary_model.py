import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    plants = instance["heat_plants"]
    districts = instance["customer_districts"]
    costs = instance["supply_costs"]

    n_plants = len(plants)
    n_districts = len(districts)

    plant_to_idx = {p["id"]: i for i, p in enumerate(plants)}
    district_to_idx = {d["id"]: i for i, d in enumerate(districts)}

    startup_cost = [p["startup_cost"] for p in plants]
    heat_cap = [p["heat_capacity_units"] for p in plants]
    pump_cap = [p["pumping_capacity_points"] for p in plants]

    req_units = [d["required_heat_units"] for d in districts]
    pump_per_unit = [d["pumping_points_per_unit"] for d in districts]

    valid_pairs = []
    supply_cost = {}
    pairs_by_district = [[] for _ in range(n_districts)]
    pairs_by_plant = [[] for _ in range(n_plants)]

    for sc in costs:
        d = district_to_idx[sc["customer_district"]]
        p = plant_to_idx[sc["heat_plant"]]
        valid_pairs.append((d, p))
        supply_cost[(d, p)] = sc["supply_cost_per_unit"]
        pairs_by_district[d].append(p)
        pairs_by_plant[p].append(d)

    model = gp.Model()

    y = model.addVars(n_plants, vtype=GRB.BINARY, name="y")
    x = model.addVars(valid_pairs, vtype=GRB.CONTINUOUS, lb=0.0, name="x")

    obj_startup = gp.quicksum(startup_cost[p] * y[p] for p in range(n_plants))
    obj_supply = gp.quicksum(supply_cost[(d, p)] * x[d, p] for d, p in valid_pairs)
    model.setObjective(obj_startup + obj_supply, GRB.MINIMIZE)

    model.addConstrs(
        (gp.quicksum(x[d, p] for p in pairs_by_district[d]) == req_units[d]
         for d in range(n_districts)),
        name="demand"
    )

    model.addConstrs(
        (gp.quicksum(x[d, p] for d in pairs_by_plant[p]) <= heat_cap[p] * y[p]
         for p in range(n_plants)),
        name="heat_cap"
    )

    model.addConstrs(
        (gp.quicksum(pump_per_unit[d] * x[d, p] for d in pairs_by_plant[p]) <= pump_cap[p] * y[p]
         for p in range(n_plants)),
        name="pump_cap"
    )

    return model