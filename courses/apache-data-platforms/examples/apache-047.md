# Managed keyed state and actual event-time timers

```bash
bash run.sh state
bash run.sh readback
```

Compare running totals, inactivity deadlines, cleared state and late output against
the complete fixture oracle. The old east deadline is replaced; a later east
activity starts fresh after the timer cleared state. Ordering across different
keys is not assumed. The same explicit timeline is used to make event-time progress
observable without claiming a wall-clock inactivity experiment.
