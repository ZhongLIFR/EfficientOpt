import gurobipy as gp
from gurobipy import GRB, quicksum

def build_model(instance):
    model = gp.Model()
    
    nodes = [n['node_id'] for n in instance['network_nodes']]
    arcs = instance['network_arcs']
    commodities = instance['commodities']
    
    arc_ids = [a['id'] for a in arcs]
    comm_ids = [c['commodity_id'] for c in commodities]
    
    fixed_costs = {a['id']: a['fixed_cost'] for a in arcs}
    var_costs = {a['id']: a['var_cost'] for a in arcs}
    comm_data = {c['commodity_id']: c for c in commodities}
    
    out_arcs = {n: [] for n in nodes}
    in_arcs = {n: [] for n in nodes}
    for a in arcs:
        out_arcs[a['source']].append(a['id'])
        in_arcs[a['target']].append(a['id'])
        
    y = model.addVars(arc_ids, vtype=GRB.BINARY, name='y')
    x = model.addVars(arc_ids, comm_ids, vtype=GRB.CONTINUOUS, lb=0, name='x')
    
    obj_fixed = quicksum(fixed_costs[a] * y[a] for a in arc_ids)
    obj_var = quicksum(var_costs[a] * x[a, c] for a in arc_ids for c in comm_ids)
    model.setObjective(obj_fixed + obj_var, GRB.MINIMIZE)
    
    for c in comm_ids:
        c_info = comm_data[c]
        orig = c_info['origin']
        dest = c_info['destination']
        dem = c_info['demand']
        for v in nodes:
            if v == orig:
                rhs = dem
            elif v == dest:
                rhs = -dem
            else:
                rhs = 0
            
            if not out_arcs[v] and not in_arcs[v] and rhs == 0:
                continue
                
            lhs = quicksum(x[a, c] for a in out_arcs[v]) - quicksum(x[a, c] for a in in_arcs[v])
            model.addConstr(lhs == rhs, name=f'flow_{c}_{v}')
            
    model.addConstrs((quicksum(x[a, c] for c in comm_ids) <= 1500 * y[a] for a in arc_ids), name='capacity')
    
    return model