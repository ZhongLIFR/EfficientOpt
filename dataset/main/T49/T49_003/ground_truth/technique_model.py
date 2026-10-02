import gurobipy as gp
from gurobipy import GRB

def build_model(instance):
    model = gp.Model("RegionalSpecialtyClinicPlan")
    
    clinics = instance['clinics']
    patients = instance['patients']
    assignment_costs = instance['assignment_costs']
    
    # Precompute lookups for fast access
    clinic_cap = {c['id']: c['capacity_minutes'] for c in clinics}
    clinic_open_cost = {c['id']: c['opening_cost'] for c in clinics}
    patient_treat_min = {p['id']: p['treatment_minutes'] for p in patients}
    
    # Decision variables for opening clinics
    y = {}
    for c in clinics:
        c_id = c['id']
        y[c_id] = model.addVar(vtype=GRB.BINARY, obj=clinic_open_cost[c_id], name=f"open_{c_id}")
        
    # Decision variables for assignments
    x = {}
    clinics_for_patient = {p['id']: [] for p in patients}
    patients_for_clinic = {c['id']: [] for c in clinics}
    
    for ac in assignment_costs:
        p = ac['patient']
        c = ac['clinic']
        x[p, c] = model.addVar(vtype=GRB.BINARY, obj=ac['cost'], name=f"assign_{p}_{c}")
        clinics_for_patient[p].append(c)
        patients_for_clinic[c].append(p)
        
    # Constraints
    
    # 1. Each patient must be assigned to exactly one eligible clinic
    for p in patients:
        p_id = p['id']
        model.addConstr(
            gp.quicksum(x[p_id, c] for c in clinics_for_patient[p_id]) == 1,
            name=f"assign_one_{p_id}"
        )
        
    # 2. Capacity constraints and strong formulation
    for c in clinics:
        c_id = c['id']
        p_list = patients_for_clinic[c_id]
        if p_list:
            # Capacity constraint: total treatment minutes cannot exceed clinic capacity
            model.addConstr(
                gp.quicksum(patient_treat_min[p] * x[p, c_id] for p in p_list) <= clinic_cap[c_id] * y[c_id],
                name=f"capacity_{c_id}"
            )
            # Strong formulation: patient can only be assigned if clinic is open
            for p in p_list:
                model.addConstr(x[p, c_id] <= y[c_id], name=f"open_to_serve_{p}_{c_id}")
                
    return model
