# Pinot apache-060 command notebook

These two files come from the copied Pinot project. `realtime-table.json` defines the stream table `ds60_orders_stream` with time column `event_ts`, and `schema.json` holds the field types; neither file declares primary key columns or an upsert mode.

```bash
cat realtime-table.json
cat schema.json
```

This displays a prepared real-time table, not a hybrid/upsert acceptance test. Create separately named hybrid and upsert experiments with explicit time boundaries, primary keys, comparison columns and source identities as described in the guide.

Hybrid tables and upsert behavior appear in QUALIFICATION.md only as prepared extensions. A receipt for either needs the time boundary, the primary key and the comparison column that decided each duplicate.