import gurobipy as gp
from gurobipy import GRB
import math


def build_model(instance):
    """T15_01 ordinary: per-depot exact bin packing, engineered reference.

    FFD greedy pallet upper bound per depot, bundles sorted descending
    (symmetry breaking), per-depot pallet variables y[p] with consecutive
    usage ordering, capacity coupling x->y, and ceil(total/capacity) lower
    bound on the pallet count.
    """
    model = gp.Model("t15_01_pallet_ord")
    capacity = instance["pallet_capacity"]
    depots = instance["depots"]
    total_y = []

    for d_idx, depot in enumerate(depots):
        sizes = depot["bundle_sizes"]
        n = len(sizes)
        if n == 0:
            continue

        # Greedy First-Fit-Decreasing upper bound on pallets for this depot
        sorted_ffd = sorted(sizes, reverse=True)
        bins = []
        for s in sorted_ffd:
            placed = False
            for i in range(len(bins)):
                if bins[i] + s <= capacity:
                    bins[i] += s
                    placed = True
                    break
            if not placed:
                bins.append(s)
        ub = len(bins)

        # Sort bundles descending by size for symmetry breaking
        indexed_sizes = sorted(enumerate(sizes), key=lambda x: x[1], reverse=True)
        sorted_sizes = [s for i, s in indexed_sizes]

        y = []
        for p in range(ub):
            y.append(model.addVar(vtype=GRB.BINARY, name=f"y_d{d_idx}_p{p}"))
        total_y.extend(y)

        cap_exprs = [gp.LinExpr() for _ in range(ub)]
        for b in range(n):
            max_p = min(b, ub - 1)
            x_vars = []
            for p in range(max_p + 1):
                x_var = model.addVar(vtype=GRB.BINARY, name=f"x_d{d_idx}_b{b}_p{p}")
                x_vars.append(x_var)
                cap_exprs[p].add(x_var, sorted_sizes[b])
            model.addConstr(gp.quicksum(x_vars) == 1, name=f"assign_d{d_idx}_b{b}")

        for p in range(ub):
            model.addConstr(cap_exprs[p] <= capacity * y[p], name=f"cap_d{d_idx}_p{p}")

        # Symmetry breaking: consecutive pallet usage
        for p in range(ub - 1):
            model.addConstr(y[p] >= y[p + 1], name=f"sym_d{d_idx}_p{p}")

        # Lower bound on number of pallets for this depot
        total_size = sum(sorted_sizes)
        min_pallets = math.ceil(total_size / capacity)
        model.addConstr(gp.quicksum(y) >= min_pallets, name=f"lb_d{d_idx}")

    if total_y:
        model.setObjective(gp.quicksum(total_y), GRB.MINIMIZE)
    else:
        model.setObjective(0, GRB.MINIMIZE)

    return model
