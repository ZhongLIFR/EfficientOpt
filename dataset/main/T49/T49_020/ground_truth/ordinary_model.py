import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    shelters = instance["shelters"]
    zones = instance["evacuation_zones"]
    costs_data = instance["provision_costs"]
    
    shelter_ids = [s["id"] for s in shelters]
    zone_ids = [z["id"] for z in zones]
    
    shelter_idx = {sid: i for i, sid in enumerate(shelter_ids)}
    zone_idx = {zid: i for i, zid in enumerate(zone_ids)}
    
    num_shelters = len(shelters)
    num_zones = len(zones)
    
    open_cost = [s["opening_cost"] for s in shelters]
    prov_cap = [s["provision_capacity_units"] for s in shelters]
    med_cap = [s["medical_capacity_points"] for s in shelters]
    
    demand = [z["required_provision_units"] for z in zones]
    med_pts = [z["medical_points_per_unit"] for z in zones]
    
    cost_dict = {}
    shelters_by_zone = [[] for _ in range(num_zones)]
    zones_by_shelter = [[] for _ in range(num_shelters)]
    
    for pc in costs_data:
        z = zone_idx[pc["evacuation_zone"]]
        s = shelter_idx[pc["shelter"]]
        c = pc["provision_cost_per_unit"]
        cost_dict[(z, s)] = c
        shelters_by_zone[z].append(s)
        zones_by_shelter[s].append(z)
        
    model = gp.Model("disaster_shelter")
    
    y = model.addVars(num_shelters, vtype=GRB.BINARY, name="y")
    valid_pairs = list(cost_dict.keys())
    x = model.addVars(valid_pairs, lb=0, vtype=GRB.CONTINUOUS, name="x")
    
    obj = gp.quicksum(open_cost[s] * y[s] for s in range(num_shelters)) + gp.quicksum(cost_dict[p] * x[p] for p in valid_pairs)
    model.setObjective(obj, GRB.MINIMIZE)
    
    for z in range(num_zones):
        model.addConstr(gp.quicksum(x[z, s] for s in shelters_by_zone[z]) == demand[z], name=f"demand_{z}")
        
    for s in range(num_shelters):
        model.addConstr(gp.quicksum(x[z, s] for z in zones_by_shelter[s]) <= prov_cap[s] * y[s], name=f"prov_cap_{s}")
        model.addConstr(gp.quicksum(med_pts[z] * x[z, s] for z in zones_by_shelter[s]) <= med_cap[s] * y[s], name=f"med_cap_{s}")
        
    return model