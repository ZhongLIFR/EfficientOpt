def build_model(instance):
    import gurobipy as gp
    from gurobipy import GRB
    from collections import defaultdict

    def val(rec, key, idx):
        if isinstance(rec, dict):
            return rec[key]
        return rec[idx]

    # -------------------------
    # Parse data robustly
    # -------------------------
    arms_raw = instance['arms']
    parts_raw = instance['parts']
    slots_raw = instance['processing_slots']
    arcs_raw = instance['allowed_route_arcs']
    mutex_raw = instance.get('mutex', [])

    arm_ids = []
    proc = {}
    for r in arms_raw:
        a = int(val(r, 'arm_id', 0))
        arm_ids.append(a)
        proc[a] = int(val(r, 'processing_time', 1))

    part_ids = []
    demand = {}
    recovery = {}
    p_start = {}
    p_end = {}
    for r in parts_raw:
        p = int(val(r, 'id', 0))
        part_ids.append(p)
        demand[p] = int(val(r, 'demand', 1))
        recovery[p] = int(val(r, 'recovery_time', 2))
        p_start[p] = int(val(r, 'start_time', 3))
        p_end[p] = int(val(r, 'end_time', 4))

    slot_ids = []
    slot_part = {}
    slot_pass = {}
    part_slots = defaultdict(list)
    for r in slots_raw:
        s = str(val(r, 'slot_id', 0))
        p = int(val(r, 'part_id', 1))
        k = int(val(r, 'pass_index', 2))
        slot_ids.append(s)
        slot_part[s] = p
        slot_pass[s] = k
        part_slots[p].append(s)

    slot_set = set(slot_ids)
    source = 'SOURCE'
    sink = 'SINK'

    arc_ids = []
    arc_from = {}
    arc_to = {}
    setup = {}
    out_arcs = defaultdict(list)
    in_arcs = defaultdict(list)
    max_setup = 0
    for r in arcs_raw:
        e = str(val(r, 'arc_id', 0))
        u = str(val(r, 'from_slot', 1))
        v = str(val(r, 'to_slot', 2))
        st = int(val(r, 'setup_time', 3))
        arc_ids.append(e)
        arc_from[e] = u
        arc_to[e] = v
        setup[e] = st
        out_arcs[u].append(e)
        in_arcs[v].append(e)
        if st > max_setup:
            max_setup = st

    max_proc = max(proc.values()) if proc else 0
    max_end = max(p_end.values()) if p_end else 512
    # A safe finite bound. Visited slots are further bounded by end/recovery constraints.
    H = max(512, max_end) + max_setup + max_proc
    M_arc = H + max_setup + max_proc
    M_gap = H + max_proc + 5

    # Sort part slots by pass index once.
    for p in part_slots:
        part_slots[p].sort(key=lambda s: slot_pass[s])

    # -------------------------
    # Model and variables
    # -------------------------
    m = gp.Model('dual_arm_precision_processing_schedule')

    x = m.addVars(arm_ids, arc_ids, vtype=GRB.BINARY, name='x')
    y = m.addVars(arm_ids, slot_ids, vtype=GRB.BINARY, name='y')
    z = m.addVars(part_ids, vtype=GRB.BINARY, name='z')
    C = m.addVars(slot_ids, lb=0.0, ub=H, vtype=GRB.CONTINUOUS, name='C')

    # Small reusable expressions for slot visit count and slot processing duration.
    V = {}
    Pdur = {}
    for s in slot_ids:
        V[s] = gp.quicksum(y[a, s] for a in arm_ids)
        Pdur[s] = gp.quicksum(proc[a] * y[a, s] for a in arm_ids)

    # -------------------------
    # Objective
    # -------------------------
    m.setObjective(gp.quicksum(demand[p] * z[p] for p in part_ids), GRB.MAXIMIZE)

    # -------------------------
    # Route flow constraints
    # -------------------------
    for a in arm_ids:
        m.addConstr(gp.quicksum(x[a, e] for e in out_arcs.get(source, [])) == 1, name=f'source_out[{a}]')
        m.addConstr(gp.quicksum(x[a, e] for e in in_arcs.get(sink, [])) == 1, name=f'sink_in[{a}]')

        for s in slot_ids:
            m.addConstr(gp.quicksum(x[a, e] for e in in_arcs.get(s, [])) == y[a, s], name=f'flow_in[{a},{s}]')
            m.addConstr(gp.quicksum(x[a, e] for e in out_arcs.get(s, [])) == y[a, s], name=f'flow_out[{a},{s}]')

    # Each slot at most one arm.
    for s in slot_ids:
        m.addConstr(V[s] <= 1, name=f'slot_capacity[{s}]')

    # -------------------------
    # Part acceptance and demand
    # -------------------------
    for p in part_ids:
        slots_p = part_slots.get(p, [])
        if slots_p:
            m.addConstr(
                gp.quicksum(proc[a] * y[a, s] for s in slots_p for a in arm_ids) >= demand[p] * z[p],
                name=f'demand[{p}]'
            )
            for s in slots_p:
                m.addConstr(V[s] <= z[p], name=f'visit_only_if_accepted[{s}]')
        else:
            m.addConstr(z[p] == 0, name=f'no_slots_no_accept[{p}]')

    # Mutex part pairs.
    for i, r in enumerate(mutex_raw):
        p1 = int(val(r, 'id1', 0))
        p2 = int(val(r, 'id2', 1))
        if p1 in demand and p2 in demand:
            m.addConstr(z[p1] + z[p2] <= 1, name=f'mutex[{i}]')

    # -------------------------
    # Time windows, recovery, and inactive completion fixing
    # -------------------------
    for s in slot_ids:
        p = slot_part[s]
        # If unvisited, C[s] is forced to 0. If visited, completion is bounded by
        # availability end and by recovery completion no later than 512.
        latest = min(p_end[p], 512 - recovery[p])
        m.addConstr(C[s] <= latest * V[s], name=f'latest_completion[{s}]')
        # Start of processing must be no earlier than part start_time:
        # C[s] - processing_duration[s] >= start[p] when visited, and 0 >= 0 when not.
        m.addConstr(C[s] >= p_start[p] * V[s] + Pdur[s], name=f'earliest_start[{s}]')

    # -------------------------
    # Arc timing constraints
    # -------------------------
    for a in arm_ids:
        pa = proc[a]
        for e in arc_ids:
            u = arc_from[e]
            v = arc_to[e]
            if v not in slot_set:
                continue
            st = setup[e]
            if u == source:
                m.addConstr(C[v] >= st + pa - M_arc * (1 - x[a, e]), name=f'time_src[{a},{e}]')
            elif u in slot_set:
                m.addConstr(C[v] >= C[u] + st + pa - M_arc * (1 - x[a, e]), name=f'time_arc[{a},{e}]')
            else:
                # Unusual non-slot, non-source predecessor: treat its time origin as 0.
                m.addConstr(C[v] >= st + pa - M_arc * (1 - x[a, e]), name=f'time_other[{a},{e}]')

    # -------------------------
    # Pass-order and inter-pass timing constraints
    # -------------------------
    for p in part_ids:
        slots_p = part_slots.get(p, [])
        if len(slots_p) <= 1:
            continue
        for idx in range(1, len(slots_p)):
            prev_s = slots_p[idx - 1]
            cur_s = slots_p[idx]
            # Later pass may be visited only if the immediately previous pass is visited.
            m.addConstr(V[cur_s] <= V[prev_s], name=f'pass_prefix[{p},{cur_s}]')

            start_cur = C[cur_s] - Pdur[cur_s]
            # If current pass is visited, its start is in [completion(prev), completion(prev)+5].
            m.addConstr(start_cur >= C[prev_s] - M_gap * (1 - V[cur_s]), name=f'pass_min_gap[{p},{cur_s}]')
            m.addConstr(start_cur <= C[prev_s] + 5 + M_gap * (1 - V[cur_s]), name=f'pass_max_gap[{p},{cur_s}]')

    m.update()
    return m
