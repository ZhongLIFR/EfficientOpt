# Lexicographic route portfolio

A routing system chooses one plan per corridor with primary lateness, secondary cost, and tertiary smoothness.

Mathematical model:

Choose one option per group. Objectives are lexicographic: first minimize total primary score, then among those minimize total secondary score, then total tertiary score. The benchmark reports primary*1e6+secondary*1e3+tertiary as objective_value and the tuple in solution_summary.

Ordinary reference implementation: weighted-sum-style exhaustive combination search.

Technique implementation: lexicographic filtering by objective priority.

All coefficients and dimensions are deterministic and listed in `instance.json`.

Report the requested primary numeric result as objective_value in the final execution JSON. Put additional diagnostics such as checksums, feasibility errors, or lexicographic tuples in solution_summary.
