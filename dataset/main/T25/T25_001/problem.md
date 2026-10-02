An archive contains a fixed list of files. Every file must be assigned in its entirety to exactly one available disk. All available disks have the same capacity, and the total size assigned to any one disk may not exceed that capacity. At most the stated number of candidate disks is available.

Minimize the number of disks that contain at least one file. Report the minimum number of used disks and a compact assignment summary.

## Data schema

- `capacity`: numeric capacity of each disk.
- `candidate_disk_count`: number of available candidate disks.
- `file_sizes`: ordered array of 60 positive integer file sizes.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
