import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("equipment_mobilization")
    
    # Parse instance data
    pools_data = {p['id']: p for p in instance['equipment_pools']}
    sites_data = {s['id']: s for s in instance['construction_sites']}
    
    # Build sparse structure from operating_costs
    valid_pairs = set()
    op_cost = {}
    for record in instance['operating_costs']:
        site_id = record['site']
        pool_id = record['equipment_pool']
        valid_pairs.add((site_id, pool_id))
        op_cost[(site_id, pool_id)] = record['cost_per_machine_hour']
    
    # Create mobilization variables for pools
    pool_ids = list(pools_data.keys())
    y = model.addVars(pool_ids, vtype=GRB.BINARY, name="mobilize")
    
    # Create assignment variables only for valid pairs
    x = model.addVars(valid_pairs, vtype=GRB.CONTINUOUS, lb=0.0, name="assign")
    
    # Objective: mobilization costs + operating costs
    mob_cost = gp.quicksum(pools_data[p]['mobilization_cost'] * y[p] for p in pool_ids)
    operating_cost = gp.quicksum(op_cost[s, p] * x[s, p] for (s, p) in valid_pairs)
    model.setObjective(mob_cost + operating_cost, GRB.MINIMIZE)
    
    # Constraint 1: Demand satisfaction for each site
    for site_id, site in sites_data.items():
        eligible = [(site_id, p) for p in site['eligible_pools'] if (site_id, p) in valid_pairs]
        if eligible:
            model.addConstr(
                gp.quicksum(x[s, p] for (s, p) in eligible) == site['required_machine_hours'],
                name=f"demand_{site_id}"
            )
    
    # Build reverse index: pool -> sites that can use it
    pool_to_sites = {p: [] for p in pool_ids}
    for (s, p) in valid_pairs:
        pool_to_sites[p].append(s)
    
    # Constraint 2: Machine hour capacity for each pool
    for pool_id in pool_ids:
        sites_using = pool_to_sites[pool_id]
        if sites_using:
            model.addConstr(
                gp.quicksum(x[s, pool_id] for s in sites_using) <= pools_data[pool_id]['machine_hour_capacity'],
                name=f"capacity_{pool_id}"
            )
    
    # Constraint 3: Fuel capacity for each pool
    for pool_id in pool_ids:
        sites_using = pool_to_sites[pool_id]
        if sites_using:
            model.addConstr(
                gp.quicksum(sites_data[s]['fuel_points_per_hour'] * x[s, pool_id] for s in sites_using) 
                <= pools_data[pool_id]['fuel_support_points'],
                name=f"fuel_{pool_id}"
            )
    
    # Constraint 4: Mobilization linkage (x can be positive only if pool is mobilized)
    for (site_id, pool_id) in valid_pairs:
        # Use site's demand as big-M (tightest bound)
        M = sites_data[site_id]['required_machine_hours']
        model.addConstr(
            x[site_id, pool_id] <= M * y[pool_id],
            name=f"link_{site_id}_{pool_id}"
        )
    
    return model