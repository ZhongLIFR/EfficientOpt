import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("layout_optimization")
    
    min_total_anchor_dev = instance["minimum_total_anchor_deviation"]
    anchor_dev_weight = instance["anchor_deviation_weight"]
    
    entities = instance["layout_entities"]
    non_overlap = instance["non_overlap_requirements"]
    relationships = instance["relationships"]
    calibrations = instance["connector_axis_calibration"]
    
    ent_dict = {e[0]: e for e in entities}
    
    r = {}
    c = {}
    diff_r = {}
    diff_c = {}
    dr = {}
    dc = {}
    
    for e in entities:
        eid = e[0]
        r_min, r_max = e[2], e[3]
        c_min, c_max = e[4], e[5]
        a_row, a_col = e[6], e[7]
        
        r[eid] = model.addVar(lb=r_min, ub=r_max, vtype=GRB.INTEGER, name=f"r_{eid}")
        c[eid] = model.addVar(lb=c_min, ub=c_max, vtype=GRB.INTEGER, name=f"c_{eid}")
        
        diff_r[eid] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name=f"diff_r_{eid}")
        diff_c[eid] = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name=f"diff_c_{eid}")
        
        dr[eid] = model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name=f"dr_{eid}")
        dc[eid] = model.addVar(lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS, name=f"dc_{eid}")
        
        model.addConstr(diff_r[eid] == r[eid] - a_row, name=f"eq_diff_r_{eid}")
        model.addConstr(diff_c[eid] == c[eid] - a_col, name=f"eq_diff_c_{eid}")
        
        model.addGenConstrAbs(dr[eid], diff_r[eid], name=f"abs_r_{eid}")
        model.addGenConstrAbs(dc[eid], diff_c[eid], name=f"abs_c_{eid}")
        
    model.addConstr(gp.quicksum(dr[eid] + dc[eid] for eid in r) >= min_total_anchor_dev, name="min_anchor_dev")
    
    z_r1 = {}
    z_r2 = {}
    z_c1 = {}
    z_c2 = {}
    
    pair_dict = {}
    
    for req in non_overlap:
        pid = req[0]
        u = req[1]
        v = req[2]
        g_r1 = req[3]
        g_r2 = req[4]
        g_c1 = req[5]
        g_c2 = req[6]
        
        pair_dict[(u, v)] = pid
        pair_dict[(v, u)] = pid
        
        z_r1[pid] = model.addVar(vtype=GRB.BINARY, name=f"z_r1_{pid}")
        z_r2[pid] = model.addVar(vtype=GRB.BINARY, name=f"z_r2_{pid}")
        z_c1[pid] = model.addVar(vtype=GRB.BINARY, name=f"z_c1_{pid}")
        z_c2[pid] = model.addVar(vtype=GRB.BINARY, name=f"z_c2_{pid}")
        
        model.addConstr(z_r1[pid] + z_r2[pid] + z_c1[pid] + z_c2[pid] == 1, name=f"cert_{pid}")
        
        u_rmin, u_rmax = ent_dict[u][2], ent_dict[u][3]
        u_cmin, u_cmax = ent_dict[u][4], ent_dict[u][5]
        v_rmin, v_rmax = ent_dict[v][2], ent_dict[v][3]
        v_cmin, v_cmax = ent_dict[v][4], ent_dict[v][5]
        
        M_r1 = max(0, g_r1 - v_rmin + u_rmax)
        M_r2 = max(0, g_r2 - u_rmin + v_rmax)
        M_c1 = max(0, g_c1 - v_cmin + u_cmax)
        M_c2 = max(0, g_c2 - u_cmin + v_cmax)
        
        model.addConstr(r[v] - r[u] >= g_r1 - M_r1 * (1 - z_r1[pid]), name=f"gap_r1_{pid}")
        model.addConstr(r[u] - r[v] >= g_r2 - M_r2 * (1 - z_r2[pid]), name=f"gap_r2_{pid}")
        model.addConstr(c[v] - c[u] >= g_c1 - M_c1 * (1 - z_c1[pid]), name=f"gap_c1_{pid}")
        model.addConstr(c[u] - c[v] >= g_c2 - M_c2 * (1 - z_c2[pid]), name=f"gap_c2_{pid}")
        
    calib_dict = {}
    for cal in calibrations:
        rid = cal[0]
        axis = cal[1]
        axis_key = "row" if str(axis).lower().startswith("r") else "col"
        calib_dict[(rid, axis_key)] = cal
        
    span_r = {}
    span_c = {}
    
    obj_expr = anchor_dev_weight * gp.quicksum(dr[eid] + dc[eid] for eid in r)
    
    for rel in relationships:
        rid = rel[0]
        u = rel[1]
        v = rel[2]
        weight = rel[3]
        min_total_span = rel[4]
        
        pid = pair_dict[(u, v)]
        
        cal_r = calib_dict[(rid, "row")]
        adj1_r = cal_r[2]
        adj2_r = cal_r[3]
        min_sep_r = cal_r[4]
        max_span_r = cal_r[5]
        
        span_r[rid] = model.addVar(lb=0, ub=max_span_r, vtype=GRB.CONTINUOUS, name=f"span_r_{rid}")
        
        model.addConstr(span_r[rid] >= r[u] - r[v] + adj1_r, name=f"span_r1_{rid}")
        model.addConstr(span_r[rid] >= r[v] - r[u] + adj2_r, name=f"span_r2_{rid}")
        model.addConstr(span_r[rid] >= min_sep_r * (z_r1[pid] + z_r2[pid]), name=f"span_r_sep_{rid}")
        
        cal_c = calib_dict[(rid, "col")]
        adj1_c = cal_c[2]
        adj2_c = cal_c[3]
        min_sep_c = cal_c[4]
        max_span_c = cal_c[5]
        
        span_c[rid] = model.addVar(lb=0, ub=max_span_c, vtype=GRB.CONTINUOUS, name=f"span_c_{rid}")
        
        model.addConstr(span_c[rid] >= c[u] - c[v] + adj1_c, name=f"span_c1_{rid}")
        model.addConstr(span_c[rid] >= c[v] - c[u] + adj2_c, name=f"span_c2_{rid}")
        model.addConstr(span_c[rid] >= min_sep_c * (z_c1[pid] + z_c2[pid]), name=f"span_c_sep_{rid}")
        
        model.addConstr(span_r[rid] + span_c[rid] >= min_total_span, name=f"min_total_span_{rid}")
        
        obj_expr += weight * (span_r[rid] + span_c[rid])
        
    model.setObjective(obj_expr, GRB.MINIMIZE)
    
    return model
