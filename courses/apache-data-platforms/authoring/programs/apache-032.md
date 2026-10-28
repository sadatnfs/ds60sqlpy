# Health, saved history and exact resume

```bash
bash run.sh health
bash run.sh readback
bash run.sh stop
bash run.sh resume
bash run.sh health
bash run.sh readback
```

Readback is inspection only. For retained-volume replacement:

```bash
bash run.sh down
bash run.sh start
bash run.sh readback
```

Inspect bounded logs before changing state:

```bash
bash run.sh logs
```

The README documents the separate `destroy --confirm-owned-data-loss` action.
It is never implied by stop, resume, down or a health failure.
