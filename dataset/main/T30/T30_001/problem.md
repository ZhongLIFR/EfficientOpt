A mining operator must place 72 indivisible extraction campaigns into identical capacity containers. Every campaign must be assigned in full to exactly one container, and the combined size assigned to a container may not exceed its capacity.

Minimize the number of containers that contain at least one campaign. Report the minimum number of used containers and a compact assignment summary.

All numerical data are fixed and explicitly stored in `instance.json`; no values are generated or sampled at runtime.

## Data schema

- `capacity`: positive integer capacity of each container.
- `candidate_disk_count`: positive integer number of candidate container labels.
- `groups`: array with exactly one record.
- `groups[0].sizes`: array of exactly 72 positive integers, one size per campaign; each value is no greater than `capacity`.
