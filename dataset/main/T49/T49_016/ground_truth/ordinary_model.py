import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    pkg_data = {p['id']: p for p in instance['technology_packages']}
    zone_data = {z['id']: z for z in instance['crop_zones']}
    
    op_costs = {}
    zone_to_pkgs = {}
    pkg_to_zones = {}
    for oc in instance['operating_costs']:
        z, p = oc['crop_zone'], oc['technology_package']
        op_costs[(z, p)] = oc['operating_cost_per_hectare']
        zone_to_pkgs.setdefault(z, []).append(p)
        pkg_to_zones.setdefault(p, []).append(z)
        
    model = gp.Model()
    
    y = model.addVars(pkg_data.keys(), vtype=GRB.BINARY, name="adopt")
    x = model.addVars(op_costs.keys(), vtype=GRB.CONTINUOUS, lb=0, name="assign")
    
    model.addConstrs(
        (gp.quicksum(x[z, p] for p in zone_to_pkgs.get(z, [])) == zone_data[z]['required_hectares'] for z in zone_data.keys()),
        name="demand"
    )
    
    model.addConstrs(
        (gp.quicksum(x[z, p] for z in pkg_to_zones.get(p, [])) <= pkg_data[p]['area_capacity_hectares'] * y[p] for p in pkg_data.keys()),
        name="area_cap"
    )
    
    zone_support = {z: zone_data[z]['support_points_per_hectare'] for z in zone_data.keys()}
    model.addConstrs(
        (gp.quicksum(zone_support[z] * x[z, p] for z in pkg_to_zones.get(p, [])) 
         <= pkg_data[p]['support_capacity_points'] * y[p] for p in pkg_data.keys()),
        name="support_cap"
    )
    
    obj = gp.quicksum(pkg_data[p]['adoption_cost'] * y[p] for p in pkg_data.keys()) + \
          gp.quicksum(c * x[z, p] for (z, p), c in op_costs.items())
    model.setObjective(obj, GRB.MINIMIZE)
    
    return model