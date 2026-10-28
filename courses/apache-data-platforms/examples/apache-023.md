# Actual distributed plans with independent result checks

```bash
bash run.sh plans
bash run.sh evidence
```

Compare balanced and hot-key fixture distributions, returned results and recorded
plan text. Operator spelling can change with the selected release; exact result
checks remain mandatory. A requested partition count is not proof that all
executors were busy, and a local frequency report is not task timing telemetry.

The complete implementation is `client.py`. It uses real Ballista execution and
separate fixture-derived expected values rather than a Python scheduler model.
