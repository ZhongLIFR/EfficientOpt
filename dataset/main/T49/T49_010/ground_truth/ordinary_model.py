import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict

def build_model(instance):
    programmes = instance['programmes']
    work_packages = instance['work_packages']
    staffing_costs = instance['staffing_costs']

    prog_data = {p['id']: p for p in programmes}
    wp_data = {wp['id']: wp for wp in work_packages}
    
    cost_map = {(sc['work_package'], sc['programme']): sc['cost_per_staff_hour'] for sc in staffing_costs}
    
    wp_to_progs = defaultdict(list)
    prog_to_wps = defaultdict(list)
    for wp_id, p_id in cost_map.keys():
        wp_to_progs[wp_id].append(p_id)
        prog_to_wps[p_id].append(wp_id)
        
    model = gp.Model()
    
    y = model.addVars(prog_data.keys(), vtype=GRB.BINARY, name="y")
    x = model.addVars(cost_map.keys(), lb=0, name="x")
    
    obj = gp.quicksum(prog_data[p_id]['launch_cost'] * y[p_id] for p_id in prog_data) + \
          gp.quicksum(cost_map[wp_id, p_id] * x[wp_id, p_id] for wp_id, p_id in cost_map.keys())
    model.setObjective(obj, GRB.MINIMIZE)
    
    for wp_id, wp in wp_data.items():
        progs = wp_to_progs.get(wp_id, [])
        model.addConstr(gp.quicksum(x[wp_id, p_id] for p_id in progs) == wp['required_staff_hours'], name=f"demand_{wp_id}")
        
    for p_id, wps in prog_to_wps.items():
        prog = prog_data[p_id]
        model.addConstr(gp.quicksum(x[wp_id, p_id] for wp_id in wps) <= prog['staff_hour_capacity'] * y[p_id], name=f"staff_cap_{p_id}")
        model.addConstr(gp.quicksum(wp_data[wp_id]['lab_points_per_hour'] * x[wp_id, p_id] for wp_id in wps) <= prog['lab_point_capacity'] * y[p_id], name=f"lab_cap_{p_id}")
        
    return model