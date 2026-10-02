A plant chooses nonnegative fractional production levels for 30 products. `profit[j]` is the unit profit.

The plan must pass 2200 quality gates. Gate `k` provides a `nominal_load` coefficient for every product and a `kpi_matrix` whose 10 rows compute linear quality indicators from the production vector. A regulator may choose a weighting vector satisfying every row of `facet_normals * weight <= facet_rhs`. The gate is passed only when its nominal load plus the worst admissible weighted sum of its indicators is at most `gate_limit[k]`.

Maximize total profit subject to every gate holding for every admissible weighting vector. Report the maximum profit and the production levels.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `profit`: array with 30 numeric entries.
- `gate_limit`: array with 2200 numeric entries.
- `gates`: array with 2200 records. Each record contains:
  - `nominal_load`: array with 30 numeric entries;
  - `kpi_matrix`: array with 10 rows and 30 numeric entries per row;
  - `facet_normals`: array with 20 rows and 10 numeric entries per row;
  - `facet_rhs`: array with 20 numeric entries.

For every supplied gate, the facet arrays explicitly describe the box `-1 <= weight[r] <= 1`; the model must use or verify those supplied facet data rather than generate uncertainty values externally.
