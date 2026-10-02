import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("farm_technology_adoption")
    
    # Precompute lookup dictionaries for O(1) access
    packages = {pkg['id']: pkg for pkg in instance['technology_packages']}
    zones = {zone['id']: zone for zone in instance['crop_zones']}
    
    # Build sparse operating cost dictionary: (zone_id, pkg_id) -> cost
    operating_cost = {}
    valid_pairs = set()
    for rec in instance['operating_costs']:
        z, p = rec['crop_zone'], rec['technology_package']
        operating_cost[(z, p)] = rec['operating_cost_per_hectare']
        valid_pairs.add((z, p))
    
    # Decision variables
    # adopt[p]: binary, whether package p is adopted
    adopt = model.addVars(packages.keys(), vtype=GRB.BINARY, name="adopt")
    
    # assign[z,p]: continuous non-negative, hectares from zone z to package p
    assign = model.addVars(valid_pairs, lb=0.0, vtype=GRB.CONTINUOUS, name="assign")
    
    # Objective: adoption costs + operating costs
    adoption_cost_expr = gp.quicksum(
        packages[p]['adoption_cost'] * adopt[p] for p in packages
    )
    operating_cost_expr = gp.quicksum(
        operating_cost[(z, p)] * assign[z, p] for z, p in valid_pairs
    )
    model.setObjective(adoption_cost_expr + operating_cost_expr, GRB.MINIMIZE)
    
    # Constraint 1: Coverage - each zone must assign exactly its required hectares
    for zone_id, zone_data in zones.items():
        eligible = [(zone_id, p) for p in zone_data['eligible_technology_packages'] 
                   if (zone_id, p) in valid_pairs]
        if eligible:
            model.addConstr(
                gp.quicksum(assign[z, p] for z, p in eligible) == zone_data['required_hectares'],
                name=f"coverage_{zone_id}"
            )
    
    # Precompute which zones can be served by each package (for capacity constraints)
    pkg_to_zones = {p: [] for p in packages}
    for z, p in valid_pairs:
        pkg_to_zones[p].append(z)
    
    # Constraint 2: Area capacity for each package
    for pkg_id, pkg_data in packages.items():
        if pkg_to_zones[pkg_id]:
            model.addConstr(
                gp.quicksum(assign[z, pkg_id] for z in pkg_to_zones[pkg_id]) 
                <= pkg_data['area_capacity_hectares'],
                name=f"area_cap_{pkg_id}"
            )
    
    # Constraint 3: Support capacity for each package
    for pkg_id, pkg_data in packages.items():
        if pkg_to_zones[pkg_id]:
            model.addConstr(
                gp.quicksum(
                    zones[z]['support_points_per_hectare'] * assign[z, pkg_id] 
                    for z in pkg_to_zones[pkg_id]
                ) <= pkg_data['support_capacity_points'],
                name=f"support_cap_{pkg_id}"
            )
    
    # Constraint 4: Adoption linking - can only assign to adopted packages
    # assign[z,p] <= required_hectares[z] * adopt[p]
    for z, p in valid_pairs:
        model.addConstr(
            assign[z, p] <= zones[z]['required_hectares'] * adopt[p],
            name=f"link_{z}_{p}"
        )
    
    return model