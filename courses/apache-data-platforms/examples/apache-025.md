# Explicit owned fault experiments

Run only in the copied workshop with its canonical fixture and known ownership.

```bash
bash run.sh check
bash run.sh failure-check
bash run.sh evidence
```

The report distinguishes one-slot fresh-query behavior, scheduler restart,
retained source/receipts and a separately identified new request. It does not
silently rerun an old receipt or claim recovery of an unidentified in-flight task.

For whole-container lifecycle:

```bash
bash run.sh stop
bash run.sh resume
bash run.sh check
```

Consult QUALIFICATION for the exact observed failure result on the native platform.
