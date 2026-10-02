For each portfolio, allocate exactly `total` whole units among nonnegative integer quantities `x`, `y`, and `z`. Respect the portfolio-specific lower bound for each quantity and minimize the stated basis-point-weighted total. Report the minimum total objective value.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `portfolios`: array of independent records. Each record contains a string `portfolio`; integer `total`; nonnegative integer lower bounds `min_x`, `min_y`, and `min_z`; and numeric weights `return_x_bps`, `return_y_bps`, and `return_z_bps`.
