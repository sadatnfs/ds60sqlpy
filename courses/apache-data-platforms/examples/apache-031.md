# Real runtime connection resolution

```bash
bash run.sh connection-check
bash run.sh readback
```

The task resolves the known local reference, rejects an intentionally missing
identifier and stores only a redacted observation. No external database or cloud
credential is contacted. Inspect the container's declared connection schema and
the task's SDK calls, without printing full connection objects or secret values.

Provider installation is an image-preparation operation, never an automatic task
recovery step after an import error.
