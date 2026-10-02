A production planner manages `blocks` independent production blocks over `periods` periods. Each block has `modes` operating modes. For block `b`, mode `m`, and period `t`, `value`, `resource`, `minrun`, `maxout`, and `fixed` describe the value, resource use, minimum and maximum intensity when used, and activation cost. `demand` is the required output and `capacity` is the resource limit.

Choose a nonnegative intensity for every mode and period, together with use and activation decisions. Each block must meet its demand and resource limit in every period, use is bounded by the mode's minimum and maximum intensity, at most `max_active_per_period` modes may be used in a period, and a used mode must be activated. If a mode is used in period `t`, it must be activated in period `t` and every earlier period.

Maximize total production value minus activation costs. Report the objective and the production, use, and activation decisions.

All numerical data are fixed and provided in the instance file.

## Data schema

- `blocks`: integer scalar.
- `modes`: integer scalar.
- `periods`: integer scalar.
- `max_active_per_period`: integer scalar.
- `value`: array with 1000 rows; each row is an array with 8 rows; each row is an array with 12 values.
- `resource`: array with 1000 rows; each row is an array with 8 rows; each row is an array with 12 values.
- `fixed`: array with 1000 rows; each row is an array with 8 rows; each row is an array with 12 values.
- `minrun`: array with 1000 rows; each row is an array with 8 values.
- `maxout`: array with 1000 rows; each row is an array with 8 values.
- `capacity`: array with 1000 rows; each row is an array with 12 values.
- `demand`: array with 1000 rows; each row is an array with 12 values.

The instance may contain auxiliary identifier or provenance fields; these are not decision data.
