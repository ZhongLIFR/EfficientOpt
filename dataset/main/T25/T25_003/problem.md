An archive contains a fixed collection of independent packing batches. Each batch lists the sizes of its files. Within every batch, each file must be assigned in its entirety to exactly one available disk. All disks have the same capacity, and the total size assigned to one disk may not exceed that capacity. The same number of candidate disks is available for every batch, and files from different batches cannot share a disk.

Minimize the total number of nonempty disks over all batches. Report the minimum total and a compact packing summary.

## Data schema

- `capacity`: numeric capacity of each disk.
- `candidate_disk_count`: number of candidate disks available in every batch.
- `groups`: array of batch records; each record contains `file_sizes`, an ordered array of positive integer file sizes.

The complete fixed instance is stored explicitly in `instance.json`; no numerical values are generated or sampled at runtime.
