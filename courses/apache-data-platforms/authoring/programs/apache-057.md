# Pinot apache-057 command notebook

Run these four actions in order from the copied Pinot project after reading its README. `prepare` records the pinned image, `start` brings up ZooKeeper, controller, broker and server, and `initialize` is the only step that loads the three order rows into a segment. The [workshop rules](../../STUDY-GUIDE.md#workshop-notebooks) explain why the pad only displays them.

```bash
bash run.sh prepare
bash run.sh start
bash run.sh initialize
bash run.sh check
```

The full source is in the copied project. Initialization is explicit. Require exact IDs and values before accepting aggregate totals.

QUALIFICATION.md records this offline segment path as accepted on Linux ARM64: rows 1, 2 and 3, east 11 and west 9, and exactly one owned offline segment. Kafka, hybrid, upsert and multistage routes have their own entries there, so a passing `check` here says nothing about them.