# Historical coverage and one-day correction

```bash
bash run.sh run-intervals
bash run.sh readback
bash run.sh backfill-check
bash run.sh readback
```

The correction uses a fixed allowed day and a new fixture revision. Its result
must show one changed partition and the other partition's unchanged bytes. The
command inspects existing successful correction state before deciding whether a
new trigger is required, so reviewing the example does not silently replay work.

Read the project ledger for the actual scheduled interval and manual-trigger
behavior verified on Airflow 3.3.2.
