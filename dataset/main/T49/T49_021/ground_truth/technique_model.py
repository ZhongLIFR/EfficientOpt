import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("district_heating")
    
    # Build lookup dictionaries
    plants = {p['id']: p for p in instance['heat_plants']}
    districts = {d['id']: d for d in instance['customer_districts']}
    
    # Build sparse supply cost structure and eligible pairs
    supply_cost = {}
    eligible_pairs = set()
    for rec in instance['supply_costs']:
        d_id = rec['customer_district']
        p_id = rec['heat_plant']
        supply_cost[(d_id, p_id)] = rec['supply_cost_per_unit']
        eligible_pairs.add((d_id, p_id))
    
    # Build reverse mapping: for each plant, which districts can use it
    districts_per_plant = {p_id: [] for p_id in plants}
    for d_id, p_id in eligible_pairs:
        districts_per_plant[p_id].append(d_id)
    
    # Decision variables
    start = model.addVars(plants.keys(), vtype=GRB.BINARY, name="start")
    supply = model.addVars(eligible_pairs, lb=0, vtype=GRB.CONTINUOUS, name="supply")
    
    # Objective: minimize startup costs + supply costs
    startup_cost_expr = gp.quicksum(
        plants[p_id]['startup_cost'] * start[p_id] for p_id in plants
    )
    supply_cost_expr = gp.quicksum(
        supply_cost[(d_id, p_id)] * supply[(d_id, p_id)] for d_id, p_id in eligible_pairs
    )
    model.setObjective(startup_cost_expr + supply_cost_expr, GRB.MINIMIZE)
    
    # Demand satisfaction constraints
    for d_id, district in districts.items():
        eligible_plants = [(d_id, p_id) for p_id in district['eligible_heat_plants'] if (d_id, p_id) in eligible_pairs]
        model.addConstr(
            gp.quicksum(supply[pair] for pair in eligible_plants) == district['required_heat_units'],
            name=f"demand_{d_id}"
        )
    
    # Heat capacity constraints
    for p_id, plant in plants.items():
        eligible_districts = [(d_id, p_id) for d_id in districts_per_plant[p_id]]
        if eligible_districts:
            model.addConstr(
                gp.quicksum(supply[pair] for pair in eligible_districts) <= plant['heat_capacity_units'],
                name=f"heat_cap_{p_id}"
            )
    
    # Pumping capacity constraints
    for p_id, plant in plants.items():
        eligible_districts = [(d_id, p_id) for d_id in districts_per_plant[p_id]]
        if eligible_districts:
            model.addConstr(
                gp.quicksum(
                    districts[d_id]['pumping_points_per_unit'] * supply[(d_id, p_id)]
                    for d_id, _ in eligible_districts
                ) <= plant['pumping_capacity_points'],
                name=f"pump_cap_{p_id}"
            )
    
    # Startup linking constraints (big-M formulation)
    for d_id, p_id in eligible_pairs:
        # Big-M: minimum of district demand and plant capacity
        big_m = min(districts[d_id]['required_heat_units'], plants[p_id]['heat_capacity_units'])
        model.addConstr(
            supply[(d_id, p_id)] <= big_m * start[p_id],
            name=f"link_{d_id}_{p_id}"
        )
    
    return model