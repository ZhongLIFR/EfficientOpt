
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
exec(compile('\nfrom path_utils import resolve_instance_path\nimport json\nfrom pathlib import Path\n\nimport gurobipy as gp\n\n\nHERE = Path(__file__).resolve().parent\n\n\ndef load_data():\n    return json.loads((resolve_instance_path()).read_text(encoding="utf-8"))\n\n\ndef configured(name):\n    model = gp.Model(name)\n    model.Params.OutputFlag = 0\n    model.Params.Threads = 1\n    model.Params.Seed = 0\n    model.Params.TimeLimit = 300\n    model.Params.MIPGap = 0\n    return model\n\n\ndef audit_trajectories(data, accelerations, positions, velocities):\n    n = data["time_steps"]\n    dt = data["step_duration_seconds"]\n    tolerance = 1e-5\n    dynamics_violation = 0.0\n    boundary_violation = 0.0\n    acceleration_violation = 0.0\n    recomputed_objective = 0.0\n    mission_rows = []\n    for mission, acceleration, position, velocity in zip(\n        data["missions"], accelerations, positions, velocities\n    ):\n        mission_dynamics = 0.0\n        for t in range(n):\n            mission_dynamics = max(\n                mission_dynamics,\n                abs(velocity[t + 1] - velocity[t] - dt * acceleration[t]),\n                abs(position[t + 1] - position[t] - dt * velocity[t]),\n            )\n        mission_boundary = max(\n            abs(position[0] - mission["initial_position"]),\n            abs(velocity[0] - mission["initial_velocity"]),\n            abs(position[n] - mission["final_position"]),\n            abs(velocity[n] - mission["final_velocity"]),\n        )\n        mission_acceleration = max(\n            max(abs(value) - mission["acceleration_bound"] for value in acceleration),\n            0.0,\n        )\n        mission_fuel = mission["fuel_weight"] * sum(abs(value) for value in acceleration)\n        recomputed_objective += mission_fuel\n        dynamics_violation = max(dynamics_violation, mission_dynamics)\n        boundary_violation = max(boundary_violation, mission_boundary)\n        acceleration_violation = max(acceleration_violation, mission_acceleration)\n        mission_rows.append({\n            "name": mission["name"],\n            "dynamics_violation": mission_dynamics,\n            "boundary_violation": mission_boundary,\n            "acceleration_violation": mission_acceleration,\n            "weighted_fuel": mission_fuel,\n        })\n    shared_power_violation = max(\n        max(\n            sum(abs(accelerations[r][t]) for r in range(len(data["missions"])))\n            - data["shared_absolute_acceleration_limit"]\n            for t in range(n)\n        ),\n        0.0,\n    )\n    return {\n        "feasible": max(\n            dynamics_violation,\n            boundary_violation,\n            acceleration_violation,\n            shared_power_violation,\n        ) <= tolerance,\n        "dynamics_violation": dynamics_violation,\n        "boundary_violation": boundary_violation,\n        "acceleration_violation": acceleration_violation,\n        "shared_power_violation": shared_power_violation,\n        "recomputed_objective": recomputed_objective,\n        "missions": mission_rows,\n    }\n', '<embedded common.py>', 'exec', flags=_inline_future.annotations.compiler_flag, dont_inherit=True), _inline_modules['common'].__dict__)
# END INLINE PRIVATE DEPENDENCIES

import json

import gurobipy as gp
from gurobipy import GRB

from common import audit_trajectories, configured, load_data




TECHNIQUE = False
MODEL_NAME = 'ordinary_dense_constellation_dynamics'

def build_model(instance):
    data = instance
    missions = data["missions"]
    r_count = len(missions)
    n = data["time_steps"]
    dt = data["step_duration_seconds"]
    model = configured(MODEL_NAME)
    acceleration = model.addVars(r_count, n, lb=-GRB.INFINITY, name="acceleration")
    absolute = model.addVars(r_count, n, lb=0.0, name="absolute_acceleration")
    position = model.addVars(r_count, n + 1, lb=-GRB.INFINITY, name="position")
    velocity = model.addVars(r_count, n + 1, lb=-GRB.INFINITY, name="velocity")
    for r, mission in enumerate(missions):
        for t in range(n):
            acceleration[r, t].LB = -mission["acceleration_bound"]
            acceleration[r, t].UB = mission["acceleration_bound"]
            model.addConstr(absolute[r, t] >= acceleration[r, t])
            model.addConstr(absolute[r, t] >= -acceleration[r, t])
            if TECHNIQUE:
                model.addConstr(velocity[r, t + 1] == velocity[r, t] + dt * acceleration[r, t])
                model.addConstr(position[r, t + 1] == position[r, t] + dt * velocity[r, t])
        model.addConstr(position[r, 0] == mission["initial_position"])
        model.addConstr(velocity[r, 0] == mission["initial_velocity"])
        if not TECHNIQUE:
            for t in range(1, n + 1):
                model.addConstr(
                    velocity[r, t]
                    == mission["initial_velocity"]
                    + gp.quicksum(dt * acceleration[r, k] for k in range(t))
                )
                model.addConstr(
                    position[r, t]
                    == mission["initial_position"]
                    + t * dt * mission["initial_velocity"]
                    + gp.quicksum(
                        (t - 1 - k) * dt * dt * acceleration[r, k]
                        for k in range(t - 1)
                    )
                )
        model.addConstr(position[r, n] == mission["final_position"])
        model.addConstr(velocity[r, n] == mission["final_velocity"])
    model.addConstrs(
        gp.quicksum(absolute[r, t] for r in range(r_count))
        <= data["shared_absolute_acceleration_limit"]
        for t in range(n)
    )
    model.setObjective(
        gp.quicksum(
            missions[r]["fuel_weight"] * absolute[r, t]
            for r in range(r_count)
            for t in range(n)
        ),
        GRB.MINIMIZE,
    )
    return model
