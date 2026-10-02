import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    depots = instance["depots"]
    bases = instance["maintenance_bases"]
    costs = instance["replenishment_costs"]
    
    depot_ids = [d["id"] for d in depots]
    base_ids = [b["id"] for b in bases]
    
    depot_info = {d["id"]: d for d in depots}
    base_info = {b["id"]: b for b in bases}
    
    bases_per_depot = {d_id: [] for d_id in depot_ids}
    depots_per_base = {b_id: [] for b_id in base_ids}
    cost_map = {}
    
    for c in costs:
        b_id = c["maintenance_base"]
        d_id = c["depot"]
        cost_map[(b_id, d_id)] = c["replenishment_cost_per_unit"]
        bases_per_depot[d_id].append(b_id)
        depots_per_base[b_id].append(d_id)
        
    model = gp.Model()
    
    y = model.addVars(depot_ids, vtype=GRB.BINARY, name="y")
    x = model.addVars(cost_map.keys(), vtype=GRB.CONTINUOUS, lb=0, name="x")
    
    obj_fixed = gp.quicksum(depot_info[d]["opening_cost"] * y[d] for d in depot_ids)
    obj_var = gp.quicksum(cost_map[(b, d)] * x[b, d] for (b, d) in cost_map)
    model.setObjective(obj_fixed + obj_var, GRB.MINIMIZE)
    
    for b_id in base_ids:
        req = base_info[b_id]["required_part_units"]
        model.addConstr(
            gp.quicksum(x[b_id, d] for d in depots_per_base[b_id]) == req,
            name=f"demand_{b_id}"
        )
        
    for d_id in depot_ids:
        cap_t = depot_info[d_id]["throughput_capacity_units"]
        model.addConstr(
            gp.quicksum(x[b, d_id] for b in bases_per_depot[d_id]) <= cap_t * y[d_id],
            name=f"throughput_{d_id}"
        )
        
    for d_id in depot_ids:
        cap_h = depot_info[d_id]["handling_capacity_points"]
        model.addConstr(
            gp.quicksum(base_info[b]["handling_points_per_unit"] * x[b, d_id] for b in bases_per_depot[d_id]) <= cap_h * y[d_id],
            name=f"handling_{d_id}"
        )
        
    return model