# Asset scheduling and bounded mapping

```bash
bash run.sh asset-check
bash run.sh readback
```

The checker unpauses the known consumer before requesting producer work, waits for
actual scheduler-created consumer runs, checks two map indexes and verifies the
one-slot pool. Saved summaries identify which source partitions each run observed.

Inspect the `Asset`, `outlets`, `schedule`, `expand` and `pool` declarations in
`dags/classroom_workflows.py`. The URI is a scheduling identity, not a data transfer.
