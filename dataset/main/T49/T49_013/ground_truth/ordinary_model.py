import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict

def build_model(instance):
    m = gp.Model()

    pools = {p['id']: p for p in instance['equipment_pools']}
    sites = {s['id']: s for s in instance['construction_sites']}
    op_costs = {(oc['site'], oc['equipment_pool']): oc['cost_per_machine_hour'] for oc in instance['operating_costs']}

    # Precompute sparse adjacency structures
    site_to_pools = {s_id: s['eligible_pools'] for s_id, s in sites.items()}
    pool_to_sites = defaultdict(list)
    for s_id, p_list in site_to_pools.items():
        for p_id in p_list:
            pool_to_sites[p_id].append(s_id)

    # Decision variables
    y = m.addVars(pools.keys(), vtype=GRB.BINARY, name="y")
    x = m.addVars([(s, p) for s in site_to_pools for p in site_to_pools[s]], lb=0, name="x")

    # Objective: mobilization + operating costs
    obj = gp.quicksum(pools[p]['mobilization_cost'] * y[p] for p in pools)
    obj += gp.quicksum(c * x[s, p] for (s, p), c in op_costs.items())
    m.setObjective(obj, GRB.MINIMIZE)

    # Demand satisfaction constraints
    m.addConstrs(
        (gp.quicksum(x[s, p] for p in site_to_pools[s]) == sites[s]['required_machine_hours'] for s in sites),
        name="demand"
    )

    # Machine-hour capacity constraints
    m.addConstrs(
        (gp.quicksum(x[s, p] for s in pool_to_sites[p]) <= pools[p]['machine_hour_capacity'] * y[p] for p in pools),
        name="machine_cap"
    )

    # Fuel-support capacity constraints
    m.addConstrs(
        (gp.quicksum(sites[s]['fuel_points_per_hour'] * x[s, p] for s in pool_to_sites[p]) <= pools[p]['fuel_support_points'] * y[p] for p in pools),
        name="fuel_cap"
    )

    return m