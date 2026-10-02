import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("research_staffing")
    
    # Parse instance
    programmes = {p['id']: p for p in instance['programmes']}
    work_packages = {w['id']: w for w in instance['work_packages']}
    
    # Build sparse cost structure and reverse index
    # staffing_costs gives us the valid (wp, prog) pairs
    staffing_cost = {}  # (wp_id, prog_id) -> cost_per_staff_hour
    prog_to_wps = {p_id: [] for p_id in programmes}  # programme -> list of work packages it can serve
    
    for sc in instance['staffing_costs']:
        wp_id = sc['work_package']
        prog_id = sc['programme']
        cost = sc['cost_per_staff_hour']
        staffing_cost[(wp_id, prog_id)] = cost
        prog_to_wps[prog_id].append(wp_id)
    
    # Decision variables
    # Binary: programme launched
    y = model.addVars(programmes.keys(), vtype=GRB.BINARY, name="launch")
    
    # Continuous: staff hours assigned (only for valid pairs)
    x = model.addVars(staffing_cost.keys(), lb=0.0, vtype=GRB.CONTINUOUS, name="hours")
    
    # Objective: total launch cost + total staffing cost
    launch_cost_expr = gp.quicksum(programmes[p_id]['launch_cost'] * y[p_id] 
                                     for p_id in programmes)
    staffing_cost_expr = gp.quicksum(staffing_cost[key] * x[key] 
                                      for key in staffing_cost)
    model.setObjective(launch_cost_expr + staffing_cost_expr, GRB.MINIMIZE)
    
    # Constraint 1: Each work package must receive exactly its required staff hours
    for wp_id, wp in work_packages.items():
        # Find all programmes that can serve this work package
        valid_progs = [p_id for p_id in programmes if (wp_id, p_id) in staffing_cost]
        if valid_progs:
            model.addConstr(
                gp.quicksum(x[wp_id, p_id] for p_id in valid_progs) == wp['required_staff_hours'],
                name=f"demand_{wp_id}"
            )
    
    # Constraint 2: Staff hour capacity for each programme
    for p_id in programmes:
        wp_list = prog_to_wps[p_id]
        if wp_list:
            model.addConstr(
                gp.quicksum(x[wp_id, p_id] for wp_id in wp_list) <= programmes[p_id]['staff_hour_capacity'],
                name=f"staff_cap_{p_id}"
            )
    
    # Constraint 3: Lab point capacity for each programme
    for p_id in programmes:
        wp_list = prog_to_wps[p_id]
        if wp_list:
            model.addConstr(
                gp.quicksum(work_packages[wp_id]['lab_points_per_hour'] * x[wp_id, p_id] 
                           for wp_id in wp_list) <= programmes[p_id]['lab_point_capacity'],
                name=f"lab_cap_{p_id}"
            )
    
    # Constraint 4: Linking constraints - can only assign hours if programme is launched
    # x[w,p] <= required_staff_hours[w] * y[p]
    for (wp_id, p_id) in staffing_cost:
        model.addConstr(
            x[wp_id, p_id] <= work_packages[wp_id]['required_staff_hours'] * y[p_id],
            name=f"link_{wp_id}_{p_id}"
        )
    
    return model