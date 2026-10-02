import gurobipy as gp
from gurobipy import GRB


def build_model(instance):
    """T15_01 technique: full per-depot assignment model with pallet symmetry.

    Plain n x n bundle->pallet binaries per depot plus open-pallet y and the
    consecutive-usage symmetry y[d,k] >= y[d,k+1]. Objective counts open
    pallets only; mathematically the same optimum as the ordinary model.
    """
    capacity = instance["pallet_capacity"]
    depots = instance["depots"]

    model = gp.Model("t15_01_pallet_tec")

    sizes = [d["bundle_sizes"] for d in depots]
    ns = [len(s) for s in sizes]
    n_depots = len(depots)

    y = model.addVars([(d, k) for d in range(n_depots) for k in range(ns[d])], vtype=GRB.BINARY, name="y")
    x = model.addVars(
        [(d, i, k) for d in range(n_depots) for i in range(ns[d]) for k in range(ns[d])],
        vtype=GRB.BINARY,
        name="x",
    )

    model.setObjective(y.sum(), GRB.MINIMIZE)

    model.addConstrs(
        (gp.quicksum(x[d, i, k] for k in range(ns[d])) == 1 for d in range(n_depots) for i in range(ns[d])),
        name="assign",
    )

    model.addConstrs(
        (gp.quicksum(sizes[d][i] * x[d, i, k] for i in range(ns[d])) <= capacity * y[d, k]
         for d in range(n_depots) for k in range(ns[d])),
        name="cap",
    )

    model.addConstrs(
        (y[d, k] >= y[d, k + 1] for d in range(n_depots) for k in range(ns[d] - 1)),
        name="sym",
    )

    return model
