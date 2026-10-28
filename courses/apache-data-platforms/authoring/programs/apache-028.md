# Retry state and idempotent outputs

```bash
bash run.sh run-intervals
bash run.sh retry-check
bash run.sh readback
bash run.sh logs
```

The first intentional failure belongs to the owned `fail_once` task. Its successful
retry must be visible in actual task metadata, and each day still has exactly one
current output partition with the expected source-bound values. Logs and output
readback establish different claims.

Inspect the atomic writer in `project_data.py` before adapting it to another sink.
It is a local-file commit, not a transaction across unrelated services.
