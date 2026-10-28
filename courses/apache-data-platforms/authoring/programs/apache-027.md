# Actual scheduled TaskFlow intervals

From the repository root, copy the complete project into a fresh location:

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/airflow work/airflow
cd work/airflow
bash run.sh prepare
bash run.sh start
bash run.sh run-intervals
bash run.sh readback
```

The finite DAG is initially paused. The action unpauses only its known identifier,
waits for the two historical scheduled intervals and checks exact output/source
identities. Read `dags/classroom_workflows.py` and the project qualification ledger
for the actual TaskFlow, SQLite and scheduler boundaries.
