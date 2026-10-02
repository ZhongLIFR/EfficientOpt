import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("lab_calibration")
    
    # Extract data
    suites_data = {s['id']: s for s in instance['instrument_suites']}
    batches_data = {b['id']: b for b in instance['assay_batches']}
    
    # Build processing cost lookup
    proc_cost = {}
    for rec in instance['processing_costs']:
        proc_cost[(rec['assay_batch'], rec['instrument_suite'])] = rec['processing_cost_per_hour']
    
    # Decision variables
    # y[s]: binary, 1 if suite s is calibrated
    y = model.addVars(suites_data.keys(), vtype=GRB.BINARY, name="calibrated")
    
    # x[b,s]: hours of batch b on suite s (only for eligible pairs)
    x = {}
    for batch_id, batch in batches_data.items():
        for suite_id in batch['eligible_instrument_suites']:
            x[batch_id, suite_id] = model.addVar(
                lb=0.0,
                ub=batch['required_runtime_hours'],
                vtype=GRB.CONTINUOUS,
                name=f"hours_{batch_id}_{suite_id}"
            )
    
    # Objective: calibration cost + processing cost
    calibration_cost_expr = gp.quicksum(
        suites_data[s]['calibration_cost'] * y[s] for s in suites_data
    )
    processing_cost_expr = gp.quicksum(
        proc_cost.get((b, s), 0) * x[b, s] for (b, s) in x
    )
    model.setObjective(calibration_cost_expr + processing_cost_expr, GRB.MINIMIZE)
    
    # Constraint 1: Each batch receives its required runtime
    for batch_id, batch in batches_data.items():
        eligible_suites = batch['eligible_instrument_suites']
        model.addConstr(
            gp.quicksum(x.get((batch_id, s), 0) for s in eligible_suites) == batch['required_runtime_hours'],
            name=f"batch_runtime_{batch_id}"
        )
    
    # Constraint 2: Runtime capacity per suite
    for suite_id, suite in suites_data.items():
        # Find all batches that can use this suite
        batch_hours = [x[b, suite_id] for b in batches_data if (b, suite_id) in x]
        if batch_hours:
            model.addConstr(
                gp.quicksum(batch_hours) <= suite['runtime_capacity_hours'],
                name=f"runtime_cap_{suite_id}"
            )
    
    # Constraint 3: Calibration capacity per suite
    for suite_id, suite in suites_data.items():
        # Sum of (hours * calibration_points_per_hour) for each batch
        calib_points_terms = [
            batches_data[b]['calibration_points_per_hour'] * x[b, suite_id]
            for b in batches_data if (b, suite_id) in x
        ]
        if calib_points_terms:
            model.addConstr(
                gp.quicksum(calib_points_terms) <= suite['calibration_capacity_points'],
                name=f"calib_cap_{suite_id}"
            )
    
    # Constraint 4: Can only process on calibrated suites
    for (batch_id, suite_id), var in x.items():
        # x[b,s] <= required_runtime[b] * y[s]
        M = batches_data[batch_id]['required_runtime_hours']
        model.addConstr(
            var <= M * y[suite_id],
            name=f"calibration_req_{batch_id}_{suite_id}"
        )
    
    # Constraint 5: Incompatible suite pairs
    for pair in instance['incompatible_suite_pairs']:
        s1, s2 = pair[0], pair[1]
        if s1 in suites_data and s2 in suites_data:
            model.addConstr(
                y[s1] + y[s2] <= 1,
                name=f"incompatible_{s1}_{s2}"
            )
    
    return model