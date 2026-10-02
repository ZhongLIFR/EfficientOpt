import gurobipy as gp
from gurobipy import GRB, quicksum

def build_model(instance):
    model = gp.Model()

    slots = instance['slots']
    segments = instance['segments']
    actions = instance['actions']
    action_contribs = instance['action_contributions']
    fallbacks = instance['fallback']
    fallback_bounds = instance['fallback_bounds']
    nodes = instance['nodes']
    equations = instance['equations']
    eq_terms = instance['equation_terms']

    # Requirement lookup
    req_map = {s['slot_id']: s['requirement'] for s in slots}

    # Binary node variables
    node_ids = [n['node_id'] for n in nodes]
    z = model.addVars(node_ids, vtype=GRB.BINARY, name="z")

    # Continuous segment coverage variables.  The physical upper bound remains
    # on the variable itself so that the integer feasible set is exact.
    seg_ids = [s['segment_id'] for s in segments]
    seg_ub = {s['segment_id']: s['threshold_high'] for s in segments}
    x = model.addVars(seg_ids, vtype=GRB.CONTINUOUS, lb=0.0, ub=seg_ub, name="x")

    # Continuous fallback purchase variables
    fb_ids = [f['fallback_id'] for f in fallbacks]
    y = model.addVars(fb_ids, vtype=GRB.CONTINUOUS, lb=0.0, name="y")

    # Apply fallback bounds
    fb_bounds_map = {fb['fallback_id']: (fb['min_amount'], fb['max_amount']) for fb in fallback_bounds}
    for fb_id, (lb, ub) in fb_bounds_map.items():
        y[fb_id].lb = lb
        y[fb_id].ub = ub

    # Map ref_id to node_id for switches
    seg_node_map = {n['ref_id']: n['node_id'] for n in nodes if n['node_kind'] == 'segment_switch'}
    action_node_map = {n['ref_id']: n['node_id'] for n in nodes if n['node_kind'] == 'action_switch'}

    # Baseline activation constraints: use a valid but deliberately loose
    # linking coefficient.  Because x has the physical upper bound `high`,
    # this is exactly equivalent for binary z; its LP relaxation is weaker
    # than the technique formulation x <= high * z.
    for s in segments:
        sid = s['segment_id']
        nid = seg_node_map[sid]
        low = s['threshold_low']
        high = s['threshold_high']
        link_m = max(high, req_map[s['slot_id']])
        if low > 0:
            model.addConstr(x[sid] >= low * z[nid], name=f"seg_low_{sid}")
        model.addConstr(x[sid] <= link_m * z[nid], name=f"seg_high_{sid}")

    # Group data by slot for efficient coverage constraint construction
    segs_by_slot = {}
    for s in segments:
        segs_by_slot.setdefault(s['slot_id'], []).append(s['segment_id'])

    contrib_by_slot = {}
    for ac in action_contribs:
        contrib_by_slot.setdefault(ac['slot_id'], []).append((ac['action_id'], ac['contribution']))

    fbs_by_slot = {}
    for f in fallbacks:
        fbs_by_slot.setdefault(f['slot_id'], []).append(f['fallback_id'])

    # Slot coverage equality constraints
    for slot_id, req in req_map.items():
        terms = []
        for sid in segs_by_slot.get(slot_id, []):
            terms.append(x[sid])
        for aid, contrib in contrib_by_slot.get(slot_id, []):
            nid = action_node_map[aid]
            terms.append(contrib * z[nid])
        for fid in fbs_by_slot.get(slot_id, []):
            terms.append(y[fid])
        model.addConstr(quicksum(terms) == req, name=f"cov_{slot_id}")

    # Group equation terms by equation ID
    eq_terms_by_id = {}
    for et in eq_terms:
        eq_terms_by_id.setdefault(et['eq_id'], []).append((et['node_id'], et['sign']))

    # Policy equation constraints
    for eq in equations:
        eid = eq['eq_id']
        rhs = eq['rhs']
        terms = [sign * z[nid] for nid, sign in eq_terms_by_id.get(eid, [])]
        model.addConstr(quicksum(terms) == rhs, name=f"eq_{eid}")

    # Objective function
    obj_terms = []
    for s in segments:
        obj_terms.append(s['unit_price'] * x[s['segment_id']])
    for a in actions:
        nid = action_node_map[a['action_id']]
        obj_terms.append(a['fixed_price'] * z[nid])
    for n in nodes:
        obj_terms.append(n['price'] * z[n['node_id']])
    for f in fallbacks:
        obj_terms.append(f['unit_price'] * y[f['fallback_id']])

    model.setObjective(quicksum(obj_terms), GRB.MINIMIZE)

    return model
