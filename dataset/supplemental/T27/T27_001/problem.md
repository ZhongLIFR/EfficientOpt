# Lexicographic schedule design

A scheduling model ranks feasible slot choices by violations first, then labor cost, then preference score.

Mathematical model:

Choose one option per group. Objectives are lexicographic: first minimize total primary score, then among those minimize total secondary score, then total tertiary score. The benchmark reports primary*1e6+secondary*1e3+tertiary as objective_value and the tuple in solution_summary.

Ordinary reference implementation: full multiobjective combination enumeration.

Technique implementation: sequentially solve primary, secondary, and tertiary priorities.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
