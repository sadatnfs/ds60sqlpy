# Real restore and read-only lifecycle readback

```bash
bash run.sh check-backup
bash run.sh identity
bash run.sh stop
bash run.sh resume
bash run.sh identity
bash run.sh down
bash run.sh start
bash run.sh identity
```

`check-backup` snapshots the known source table, stages its compatible SSTable
components, imports into a distinct restore table with extended verification,
and checks every key/value. It retains a source-bound receipt and the restore
target while removing only its exact staging and snapshot. At most four restore
targets are allowed. Export receipts before explicitly destroying synthetic state.

Compare the same host UUID and retained orders at each lifecycle boundary.
Read-only identity calls do not replay writes or recreate an empty fixture.

```bash
bash run.sh destroy --confirm-owned-data-loss
```

This final command deletes only verified workshop-owned synthetic data. It is
optional cleanup after evidence export, not part of ordinary resume.
