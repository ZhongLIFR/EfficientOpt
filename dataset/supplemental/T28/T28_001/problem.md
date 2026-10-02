# Hospital coverage feasibility repair

A hospital system checks a fixed nurse-hour plan for 120 wards over 24 shifts. Ward `w` in shift `h` requires `required[w,h]` nurse-hours, but the current roster can provide only `available[w,h]` nurse-hours. The original hard model would impose `available[w,h] >= required[w,h]` for every ward and shift, which is infeasible for this fixed instance.

The hospital permits controlled understaffing, but every shortage must be explicitly reported and penalized at 95 cost units per nurse-hour. Introduce a nonnegative shortage variable `s[w,h]` only where needed, enforce `available[w,h] + s[w,h] >= required[w,h]`, and minimize the total shortage penalty.

The fixed instance is deterministic: `required[w,h] = 800 + ((37*w + 19*h) mod 420)` and `available[w,h] = max(0, required[w,h] - 4 * (80 + ((23*w + 11*h) mod 220)))`.

Return the minimum total penalty and a summary of the total shortage.

This benchmark is designed to test whether the modeler recognizes that the coverage rows are soft repair constraints. A weak formulation may repeatedly test hard infeasible rows or search over shortage budgets, while the technique formulation should add interpretable slack variables directly.
