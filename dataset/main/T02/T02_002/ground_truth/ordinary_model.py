from __future__ import annotations

# BEGIN INLINE PRIVATE DEPENDENCIES (generated; no external helper files required)
import sys as _inline_sys
import types as _inline_types
import __future__ as _inline_future
from pathlib import Path as _inline_path
_inline_modules = {}

# BEGIN EMBEDDED PRIVATE MODULE: path_utils.py
_inline_module_path_utils = _inline_types.ModuleType('path_utils')
_inline_module_path_utils.__file__ = str(_inline_path(__file__).resolve().parent / 'path_utils.py')
_inline_module_path_utils.__package__ = ''
_inline_modules['path_utils'] = _inline_module_path_utils
# END EMBEDDED PRIVATE MODULE: path_utils.py

# BEGIN EMBEDDED PRIVATE MODULE: common.py
_inline_module_common = _inline_types.ModuleType('common')
_inline_module_common.__file__ = str(_inline_path(__file__).resolve().parent / 'common.py')
_inline_module_common.__package__ = ''
_inline_modules['common'] = _inline_module_common
# END EMBEDDED PRIVATE MODULE: common.py

# Execute embedded modules in dependency order.

_inline_sys.modules['path_utils'] = _inline_modules['path_utils']
exec(compile('"""Portable paths for a single benchmark item."""\n\n\nfrom pathlib import Path\n\n\ndef resolve_instance_path(filename: str = "instance.json") -> Path:\n    """Find an item instance without relying on the caller\'s current cwd."""\n    here = Path(__file__).resolve().parent\n    candidates = (\n        here / filename,\n        here.parent / "public" / filename,\n        here.parent / filename,\n        Path.cwd() / filename,\n    )\n    for candidate in candidates:\n        if candidate.is_file():\n            return candidate\n    searched = "\\n".join(str(p) for p in candidates)\n    raise FileNotFoundError(f"Could not locate {filename!r}; searched:\\n{searched}")\n', '<embedded path_utils.py>', 'exec', flags=_inline_future.annotations.compiler_flag, dont_inherit=True), _inline_modules['path_utils'].__dict__)

_inline_sys.modules['common'] = _inline_modules['common']
exec(compile('\nfrom path_utils import resolve_instance_path\n\nimport json\nfrom pathlib import Path\n\n\nROOT = Path(__file__).resolve().parent\n\n\ndef load_instance() -> dict:\n    return json.loads((resolve_instance_path()).read_text(encoding="utf-8"))\n\n\ndef configure(model) -> None:\n    model.Params.OutputFlag = 0\n    model.Params.Threads = 1\n    model.Params.Seed = 0\n    model.Params.Method = -1\n    model.Params.TimeLimit = 300\n    model.Params.MIPGap = 0\n    model.Params.FeasibilityTol = 1e-9\n    model.Params.IntFeasTol = 1e-9\n', '<embedded common.py>', 'exec', flags=_inline_future.annotations.compiler_flag, dont_inherit=True), _inline_modules['common'].__dict__)
# END INLINE PRIVATE DEPENDENCIES


import gurobipy as gp
from gurobipy import GRB

from common import configure, load_instance


def _max_units(model, data, technique):
    xs, ys, zs = [], [], []
    for i, row in enumerate(data["units"]):
        x = model.addVar(lb=0.0, name=f"x[{i}]")
        y = model.addVar(lb=0.0, name=f"y[{i}]")
        model.addConstr(row["a1"] * x + row["a2"] * y >= row["demand1"])
        model.addConstr(row["b1"] * x + row["b2"] * y >= row["demand2"])
        model.addConstr(row["r1"] * x + row["r2"] * y <= row["resource"])
        if technique:
            z = model.addVar(lb=0.0, name=f"peak[{i}]")
            model.addConstr(z >= row["time1"] * x)
            model.addConstr(z >= row["time2"] * y)
        else:
            tx = model.addVar(lb=0.0, name=f"time_x[{i}]")
            ty = model.addVar(lb=0.0, name=f"time_y[{i}]")
            z = model.addVar(lb=0.0, name=f"peak[{i}]")
            model.addConstr(tx == row["time1"] * x)
            model.addConstr(ty == row["time2"] * y)
            model.addGenConstrMax(z, [tx, ty])
        xs.append(x); ys.append(y); zs.append(z)
    model.setObjective(gp.quicksum(zs), GRB.MINIMIZE)
    return {"x": xs, "y": ys, "z": zs}


def _balanced_units(model, data, technique):
    xs, ys, zs = [], [], []
    for i, row in enumerate(data["units"]):
        x = model.addVar(lb=row["min_x"], name=f"x[{i}]")
        y = model.addVar(lb=row["min_y"], name=f"y[{i}]")
        model.addConstr(x + y == row["total"])
        model.addConstr(x <= row["ratio"] * y)
        if technique:
            z = model.addVar(lb=0.0, name=f"completion[{i}]")
            model.addConstr(z >= row["time_x"] * x)
            model.addConstr(z >= row["time_y"] * y)
        else:
            tx = model.addVar(lb=0.0, name=f"time_x[{i}]")
            ty = model.addVar(lb=0.0, name=f"time_y[{i}]")
            z = model.addVar(lb=0.0, name=f"completion[{i}]")
            model.addConstr(tx == row["time_x"] * x)
            model.addConstr(ty == row["time_y"] * y)
            model.addGenConstrMax(z, [tx, ty])
        xs.append(x); ys.append(y); zs.append(z)
    model.setObjective(gp.quicksum(zs), GRB.MINIMIZE)
    return {"x": xs, "y": ys, "z": zs}


def _rocket(model, data, technique, peak):
    n = data["periods"]
    x = model.addVars(n + 1, lb=-GRB.INFINITY, name="position")
    v = model.addVars(n + 1, lb=-GRB.INFINITY, name="velocity")
    a = model.addVars(n, lb=-data["acceleration_bound"], ub=data["acceleration_bound"], name="acceleration")
    model.addConstr(x[0] == data["initial_position"])
    model.addConstr(v[0] == data["initial_velocity"])
    for t in range(n):
        model.addConstr(x[t + 1] == x[t] + v[t])
        model.addConstr(v[t + 1] == v[t] + a[t])
    model.addConstr(x[n] == data["final_position"])
    model.addConstr(v[n] == data["final_velocity"])
    if peak:
        z = model.addVar(lb=0.0, name="peak_thrust")
        if technique:
            for t in range(n):
                model.addConstr(z >= a[t])
                model.addConstr(z >= -a[t])
        else:
            aa = model.addVars(n, lb=0.0, name="absolute_acceleration")
            for t in range(n):
                model.addGenConstrAbs(aa[t], a[t])
            model.addGenConstrMax(z, list(aa.values()))
        model.setObjective(z, GRB.MINIMIZE)
        return {"x": x, "v": v, "a": a, "z": [z]}
    dev = model.addVars(n, lb=0.0, name="absolute_acceleration")
    if technique:
        for t in range(n):
            model.addConstr(dev[t] >= a[t])
            model.addConstr(dev[t] >= -a[t])
    else:
        for t in range(n):
            model.addGenConstrAbs(dev[t], a[t])
    model.setObjective(gp.quicksum(data["weights"][t] * dev[t] for t in range(n)), GRB.MINIMIZE)
    return {"x": x, "v": v, "a": a, "z": dev}


def _illumination(model, data, technique):
    p = model.addVars(data["num_lamps"], lb=0.0, ub=data["power_bounds"], name="power")
    peak = model.addVar(lb=0.0, name="maximum_deviation")
    if technique:
        for i, row in enumerate(data["segments"]):
            actual = gp.quicksum(c * p[j] for j, c in row["coefficients"])
            model.addConstr(peak >= actual - row["desired"])
            model.addConstr(peak >= row["desired"] - actual)
    else:
        deviations = []
        for i, row in enumerate(data["segments"]):
            residual = model.addVar(lb=-GRB.INFINITY, name=f"residual[{i}]")
            deviation = model.addVar(lb=0.0, name=f"deviation[{i}]")
            actual = gp.quicksum(c * p[j] for j, c in row["coefficients"])
            model.addConstr(residual == actual - row["desired"])
            model.addGenConstrAbs(deviation, residual)
            deviations.append(deviation)
        model.addGenConstrMax(peak, deviations)
    model.setObjective(peak, GRB.MINIMIZE)
    return {"p": p, "z": [peak]}


def _regression(model, data, technique, quadratic, linf):
    a = model.addVar(lb=-GRB.INFINITY, name="intercept")
    b = model.addVar(lb=-GRB.INFINITY, name="linear_coefficient")
    c = model.addVar(lb=-GRB.INFINITY, name="quadratic_coefficient") if quadratic else None
    if linf:
        peak = model.addVar(lb=0.0, name="maximum_deviation")
        deviations = []
    else:
        dev = model.addVars(len(data["observations"]), lb=0.0, name="absolute_deviation")
    for i, row in enumerate(data["observations"]):
        pred = a + b * row["x"] + (c * row["x"] * row["x"] if quadratic else 0.0)
        residual_expr = pred - row["y"]
        if technique:
            target = peak if linf else dev[i]
            model.addConstr(target >= residual_expr)
            model.addConstr(target >= -residual_expr)
        else:
            residual = model.addVar(lb=-GRB.INFINITY, name=f"residual[{i}]")
            deviation = model.addVar(lb=0.0, name=f"deviation[{i}]")
            model.addConstr(residual == residual_expr)
            model.addGenConstrAbs(deviation, residual)
            if linf:
                deviations.append(deviation)
            else:
                model.addConstr(dev[i] == deviation)
    if linf:
        if not technique:
            model.addGenConstrMax(peak, deviations)
        model.setObjective(peak, GRB.MINIMIZE)
        z = [peak]
    else:
        model.setObjective(gp.quicksum(row["weight"] * dev[i] for i, row in enumerate(data["observations"])), GRB.MINIMIZE)
        z = dev
    return {"a": [a], "b": [b], "c": [c] if c is not None else [], "z": z}


def _patient_min(model, data, technique):
    temperatures, bloods, patients = [], [], []
    for i, row in enumerate(data["stations"]):
        temperature = model.addVar(lb=0.0, name=f"temperature_checks[{i}]")
        blood = model.addVar(lb=row["minimum_blood"], name=f"blood_tests[{i}]")
        patient = model.addVar(lb=0.0, name=f"fully_screened_patients[{i}]")
        model.addConstr(row["temperature_minutes"] * temperature + row["blood_minutes"] * blood <= row["staff_minutes"])
        model.addConstr(temperature >= row["temperature_ratio"] * blood)
        if technique:
            model.addConstr(patient <= temperature)
            model.addConstr(patient <= blood)
        else:
            model.addGenConstrMin(patient, [temperature, blood])
        temperatures.append(temperature); bloods.append(blood); patients.append(patient)
    model.setObjective(gp.quicksum(patients), GRB.MAXIMIZE)
    return {"temperature": temperatures, "blood": bloods, "z": patients}


def _production_tv(model, data, technique):
    n = len(data["demand"])
    production = model.addVars(n, lb=0.0, ub=data["production_capacity"], name="production")
    inventory = model.addVars(n + 1, lb=0.0, name="inventory")
    switch = model.addVars(n - 1, lb=0.0, name="absolute_switch")
    model.addConstr(inventory[0] == data["initial_inventory"])
    for t in range(n):
        model.addConstr(inventory[t + 1] == inventory[t] + production[t] - data["demand"][t])
    model.addConstr(inventory[n] == data["final_inventory"])
    for t in range(n - 1):
        if technique:
            model.addConstr(switch[t] >= production[t + 1] - production[t])
            model.addConstr(switch[t] >= production[t] - production[t + 1])
        else:
            difference = model.addVar(lb=-GRB.INFINITY, name=f"production_difference[{t}]")
            model.addConstr(difference == production[t + 1] - production[t])
            model.addGenConstrAbs(switch[t], difference)
    model.setObjective(
        data["production_cost"] * gp.quicksum(production.values())
        + data["storage_cost"] * gp.quicksum(inventory[t + 1] for t in range(n))
        + data["switch_cost"] * gp.quicksum(switch.values()), GRB.MINIMIZE)
    return {"production": production, "inventory": inventory, "z": switch}


def _overtime_positive_part(model, data, technique):
    productions, overtimes = [], []
    objective = gp.LinExpr()
    for d, row in enumerate(data["divisions"]):
        x = model.addVars(len(row["profits"]), lb=0.0, name=f"batches[{d}]")
        for m, capacity in enumerate(row["machine_capacity"]):
            hours = gp.quicksum(row["time_required"][m][p] * x[p] for p in range(len(row["profits"])))
            if m == 0:
                overtime = model.addVar(lb=0.0, ub=row["overtime_limit"], name=f"overtime[{d}]")
                if technique:
                    model.addConstr(overtime >= hours - capacity)
                else:
                    excess = model.addVar(lb=-GRB.INFINITY, name=f"excess_hours[{d}]")
                    zero = model.addVar(lb=0.0, ub=0.0, name=f"zero[{d}]")
                    model.addConstr(excess == hours - capacity)
                    model.addGenConstrMax(overtime, [excess, zero])
                overtimes.append(overtime)
                model.addConstr(hours <= capacity + row["overtime_limit"])
            else:
                model.addConstr(hours <= capacity)
        objective += gp.quicksum(row["profits"][p] * x[p] for p in range(len(row["profits"]))) - row["overtime_cost"] * overtimes[-1]
        productions.extend(x.values())
    model.setObjective(objective, GRB.MAXIMIZE)
    return {"production": productions, "z": overtimes}


def _farm_extra_capacity(model, data, technique):
    cows, crops, extras = [], [], []
    objective = gp.LinExpr()
    for i, row in enumerate(data["farms"]):
        cow = model.addVar(lb=0.0, name=f"dairy_cows[{i}]")
        crop = model.addVar(lb=0.0, name=f"feed_crop[{i}]")
        extra = model.addVar(lb=0.0, name=f"extra_housing[{i}]")
        model.addConstr(row["cow_land"] * cow + crop <= row["land"])
        model.addConstr(row["feed_per_cow"] * cow <= row["feed_yield"] * crop + row["purchased_feed"])
        if technique:
            model.addConstr(extra >= cow - row["base_housing"])
        else:
            excess = model.addVar(lb=-GRB.INFINITY, name=f"housing_excess[{i}]")
            zero = model.addVar(lb=0.0, ub=0.0, name=f"zero[{i}]")
            model.addConstr(excess == cow - row["base_housing"])
            model.addGenConstrMax(extra, [excess, zero])
        objective += row["cow_profit"] * cow + row["crop_profit"] * crop - row["extra_housing_cost"] * extra
        cows.append(cow); crops.append(crop); extras.append(extra)
    model.setObjective(objective, GRB.MAXIMIZE)
    return {"cows": cows, "crops": crops, "z": extras}


def _hybrid_grouping(model, data, technique):
    n, g = data["num_students"], data["num_groups"]
    assign = model.addVars(n, g, vtype=GRB.BINARY, name="assignment")
    for s in range(n):
        model.addConstr(gp.quicksum(assign[s, j] for j in range(g)) == 1)
    loads = []
    for j in range(g):
        load = model.addVar(lb=0.0, name=f"group_load[{j}]")
        model.addConstr(load == gp.quicksum(data["student_loads"][s] * assign[s, j] for s in range(n)))
        loads.append(load)
    peak = model.addVar(lb=0.0, name="peak_group_load")
    if technique:
        for load in loads:
            model.addConstr(peak >= load)
    else:
        model.addGenConstrMax(peak, loads)
    preference_penalty = gp.quicksum(
        data["preference_penalty"][s][j] * assign[s, j] for s in range(n) for j in range(g)
    )
    model.setObjective(data["peak_weight"] * peak + preference_penalty, GRB.MINIMIZE)
    return {"assignment": assign, "loads": loads, "z": [peak]}


def _hybrid_capacity_excess(model, data, technique):
    n, g, c = data["num_students"], data["num_groups"], data["num_classes"]
    assign = model.addVars(n, g, vtype=GRB.BINARY, name="assignment")
    for s in range(n):
        model.addConstr(gp.quicksum(assign[s, j] for j in range(g)) == 1)
    enrolled_by_class = [[] for _ in range(c)]
    for s, classes in enumerate(data["enrollments"]):
        for course in classes:
            enrolled_by_class[course].append(s)
    excesses = []
    for course in range(c):
        for j in range(g):
            load = gp.quicksum(assign[s, j] for s in enrolled_by_class[course])
            excess = model.addVar(lb=0.0, name=f"capacity_excess[{course},{j}]")
            if technique:
                model.addConstr(excess >= load - data["class_capacity"][course][j])
            else:
                difference = model.addVar(lb=-GRB.INFINITY, name=f"load_minus_capacity[{course},{j}]")
                zero = model.addVar(lb=0.0, ub=0.0, name=f"zero[{course},{j}]")
                model.addConstr(difference == load - data["class_capacity"][course][j])
                model.addGenConstrMax(excess, [difference, zero])
            excesses.append(excess)
    preference = gp.quicksum(data["preference_penalty"][s][j] * assign[s, j] for s in range(n) for j in range(g))
    model.setObjective(data["excess_weight"] * gp.quicksum(excesses) + preference, GRB.MINIMIZE)
    return {"assignment": assign, "z": excesses}


def _medication_peak(model, data, technique):
    calciums, vitamins, completions = [], [], []
    for i, row in enumerate(data["patients"]):
        calcium = model.addVar(lb=0.0, vtype=GRB.INTEGER, name=f"calcium_pills[{i}]")
        vitamin = model.addVar(lb=row["minimum_vitamin"], vtype=GRB.INTEGER, name=f"vitamin_d_pills[{i}]")
        model.addConstr(calcium + vitamin >= row["minimum_total"])
        model.addConstr(calcium >= row["calcium_ratio"] * vitamin)
        completion = model.addVar(lb=0.0, name=f"completion_time[{i}]")
        if technique:
            model.addConstr(completion >= row["calcium_minutes"] * calcium)
            model.addConstr(completion >= row["vitamin_minutes"] * vitamin)
        else:
            calcium_time = model.addVar(lb=0.0, name=f"calcium_time[{i}]")
            vitamin_time = model.addVar(lb=0.0, name=f"vitamin_time[{i}]")
            model.addConstr(calcium_time == row["calcium_minutes"] * calcium)
            model.addConstr(vitamin_time == row["vitamin_minutes"] * vitamin)
            model.addGenConstrMax(completion, [calcium_time, vitamin_time])
        calciums.append(calcium); vitamins.append(vitamin); completions.append(completion)
    model.setObjective(gp.quicksum(completions), GRB.MINIMIZE)
    return {"calcium": calciums, "vitamin": vitamins, "z": completions}


def _build_model_baseline(technique: bool):
    data = load_instance()
    model = gp.Model(data["problem_id"] + ("_technique" if technique else "_ordinary"))
    configure(model)
    kind = data["kind"]
    if kind == "factory_peak":
        variables = _max_units(model, data, technique)
    elif kind == "balanced_peak":
        variables = _balanced_units(model, data, technique)
    elif kind == "rocket_l1":
        variables = _rocket(model, data, technique, False)
    elif kind == "rocket_linf":
        variables = _rocket(model, data, technique, True)
    elif kind == "illumination_linf":
        variables = _illumination(model, data, technique)
    elif kind == "linear_linf":
        variables = _regression(model, data, technique, False, True)
    elif kind == "quadratic_l1":
        variables = _regression(model, data, technique, True, False)
    elif kind == "patient_min":
        variables = _patient_min(model, data, technique)
    elif kind == "production_tv":
        variables = _production_tv(model, data, technique)
    elif kind == "overtime_positive_part":
        variables = _overtime_positive_part(model, data, technique)
    elif kind == "farm_extra_capacity":
        variables = _farm_extra_capacity(model, data, technique)
    elif kind == "hybrid_grouping":
        variables = _hybrid_grouping(model, data, technique)
    elif kind == "hybrid_capacity_excess":
        variables = _hybrid_capacity_excess(model, data, technique)
    elif kind == "medication_peak":
        variables = _medication_peak(model, data, technique)
    else:
        raise ValueError(kind)
    model.update()
    return model, variables


def solve(technique: bool) -> dict:
    model, variables = build_model(technique)
    model.optimize()
    if model.Status != GRB.OPTIMAL:
        raise RuntimeError(f"status={model.Status}")
    checksum = 0.0
    for group in variables.values():
        vals = group.values() if hasattr(group, "values") else group
        checksum += sum((i + 1) * var.X for i, var in enumerate(vals) if var is not None)
    try:
        integrality_violation = model.IntVio
    except AttributeError:
        integrality_violation = 0.0
    result = {
        "objective": model.ObjVal,
        "runtime": model.Runtime,
        "work": model.Work,
        "variables": model.NumVars,
        "constraints": model.NumConstrs,
        "general_constraints": model.NumGenConstrs,
        "nonzeros": model.NumNZs,
        "constraint_violation": model.ConstrVio,
        "bound_violation": model.BoundVio,
        "integrality_violation": integrality_violation,
        "checksum": checksum,
    }
    data = load_instance()
    if data["kind"] == "rocket_linf":
        n = data["periods"]
        result["decision_data"] = {
            "position": [variables["x"][t].X for t in range(n + 1)],
            "velocity": [variables["v"][t].X for t in range(n + 1)],
            "acceleration": [variables["a"][t].X for t in range(n)],
            "peak_thrust": variables["z"][0].X,
        }
    return result

# Standalone branch: model_core.py was inlined here.

if __name__ == "__main__":
    import json
    print(json.dumps(solve(False)))


# Fixed-runner adapter: expose the complete ordinary model.
def build_model(instance):
    model, _ = _build_model_baseline(False)
    return model
