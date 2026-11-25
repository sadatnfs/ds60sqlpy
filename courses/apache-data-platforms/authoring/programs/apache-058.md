# Pinot apache-058 command notebook

Both `cat` commands only print files from the copied Pinot project; nothing connects to Kafka. In `realtime-table.json` find the topic `ds60-orders`, the broker list `kafka:9092` and the offset reset `smallest`, then match each decoded field against `schema.json`.

```bash
cat realtime-table.json
cat schema.json
```

This displays the released connector configuration only. Prepare a separately owned Kafka route, reconcile partition positions and exact decoded IDs, and record malformed-event handling before calling the streaming route qualified.

QUALIFICATION.md lists Kafka ingestion as a prepared extension with no actual gate yet. Until a stream run records consumed offsets beside the decoded IDs, this lesson's evidence is a reviewed configuration, not an ingested table.