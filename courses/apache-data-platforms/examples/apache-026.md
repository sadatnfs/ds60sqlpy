# Fixed-host capacity comparison and bounded output

```bash
bash run.sh one-slot
bash run.sh check
bash run.sh two-slots
bash run.sh check
bash run.sh bounded-output
bash run.sh evidence
```

The container's CPU/memory allocation stays fixed. Record all timings and exact
source identity; do not interpret one tiny trial as a scaling benchmark. Source
and output bounds, process readiness and actual result checks are independent.

```bash
bash run.sh status
bash run.sh logs
bash run.sh down
```

Down retains the named data/evidence volume. Destructive deletion is a separately
confirmed action documented in the project README.
