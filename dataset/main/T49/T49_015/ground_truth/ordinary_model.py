import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    suites = {s['id']: s for s in instance['instrument_suites']}
    batches = {b['id']: b for b in instance['assay_batches']}
    
    proc_costs = {}
    for pc in instance['processing_costs']:
        proc_costs[(pc['assay_batch'], pc['instrument_suite'])] = pc['processing_cost_per_hour']
        
    suite_to_batches = {s_id: [] for s_id in suites}
    for b_id, b_data in batches.items():
        for s_id in b_data['eligible_instrument_suites']:
            if (b_id, s_id) in proc_costs and s_id in suite_to_batches:
                suite_to_batches[s_id].append(b_id)
                
    m = gp.Model()
    
    y = m.addVars(suites.keys(), vtype=GRB.BINARY, name="calibrate")
    x = m.addVars(proc_costs.keys(), lb=0, name="assign")
    
    obj_cal = gp.quicksum(suites[s_id]['calibration_cost'] * y[s_id] for s_id in suites)
    obj_proc = gp.quicksum(proc_costs[(b_id, s_id)] * x[b_id, s_id] for (b_id, s_id) in proc_costs)
    m.setObjective(obj_cal + obj_proc, GRB.MINIMIZE)
    
    for b_id, b_data in batches.items():
        m.addConstr(
            gp.quicksum(x[b_id, s_id] for s_id in b_data['eligible_instrument_suites'] if (b_id, s_id) in proc_costs) == b_data['required_runtime_hours'],
            name=f"batch_rt_{b_id}"
        )
        
    for s_id, s_data in suites.items():
        m.addConstr(
            gp.quicksum(x[b_id, s_id] for b_id in suite_to_batches[s_id]) <= s_data['runtime_capacity_hours'] * y[s_id],
            name=f"suite_rt_{s_id}"
        )
        
    for s_id, s_data in suites.items():
        m.addConstr(
            gp.quicksum(batches[b_id]['calibration_points_per_hour'] * x[b_id, s_id] for b_id in suite_to_batches[s_id]) <= s_data['calibration_capacity_points'] * y[s_id],
            name=f"suite_cal_{s_id}"
        )
        
    for pair in instance['incompatible_suite_pairs']:
        if isinstance(pair, dict):
            s1, s2 = list(pair.values())
        else:
            s1, s2 = pair[0], pair[1]
        m.addConstr(y[s1] + y[s2] <= 1, name=f"incomp_{s1}_{s2}")
        
    return m