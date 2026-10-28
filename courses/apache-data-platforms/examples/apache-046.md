# Actual controlled event-time windows

```bash
bash run.sh event-time
bash run.sh readback
```

Read the fixed timeline: three events before watermark2000, one older event after
it, then a second-window event before watermark4000. The checker reconciles exact
key/window/count/amount tuples and the separate late-record identity. No wall-clock
sleep is used as evidence that a particular event became late.

The source timestamp and watermark code is in the maintained Java project. These
commands run in the copied owned Docker workshop, not in a classroom pad.
