import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict

def build_model(instance):
    projects = instance['projects']
    agreements = instance['community_agreements']
    district_caps = instance['district_intensity_caps']
    total_cap = instance['total_intensity_cap']
    min_honoured = instance['minimum_agreements_honoured']

    model = gp.Model()

    max_intensity = {}
    public_value = {}
    district_projects = defaultdict(list)
    project_ids = []

    for p in projects:
        pid = p['id']
        project_ids.append(pid)
        max_intensity[pid] = p['maximum_intensity']
        public_value[pid] = p['public_value_per_unit']
        district_projects[p['district']].append(pid)

    x = model.addVars(project_ids, lb=0.0, ub=max_intensity, name='x')
    agreement_ids = [a['id'] for a in agreements]
    y = model.addVars(agreement_ids, vtype=GRB.BINARY, name='y')

    model.setObjective(
        gp.quicksum(public_value[pid] * x[pid] for pid in project_ids),
        GRB.MAXIMIZE
    )

    model.addConstr(
        gp.quicksum(x[pid] for pid in project_ids) <= total_cap,
        name='total_intensity'
    )

    for d, cap in district_caps.items():
        if d in district_projects:
            model.addConstr(
                gp.quicksum(x[pid] for pid in district_projects[d]) <= cap,
                name=f'district_{d}'
            )

    for a in agreements:
        aid = a['id']
        coeffs = a['disruption_coefficients']
        limit = a['disruption_limit']
        expr = gp.quicksum(coeff * x[pid] for pid, coeff in coeffs.items())
        model.addGenConstrIndicator(
            y[aid], True, expr, GRB.LESS_EQUAL, limit, name=f'agree_{aid}'
        )

    model.addConstr(
        gp.quicksum(y[aid] for aid in agreement_ids) >= min_honoured,
        name='min_honoured'
    )

    return model
