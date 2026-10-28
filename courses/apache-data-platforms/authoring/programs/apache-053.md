# RF1 versus the actual optional RF3 outage

In the single-node copied project:

```bash
bash run.sh check
```

ONE and QUORUM both require one replica at RF1. TWO must report insufficient
replicas. For a real outage experiment, make a separate owned project copy:

```bash
cd ../..
cp -R courses/apache-data-platforms/projects/cassandra work/apache-cassandra-rf3
cd work/apache-cassandra-rf3
bash run.sh start --replicated
bash run.sh check-replication
bash run.sh replica-identity
```

The outage checker establishes RF3/ALL, stops two exact owned nodes, requires ONE
success and QUORUM unavailability, resumes those same nodes and checks quorum
readback. Three local containers share one physical failure domain. The explicit
topology needs at least 8 GiB allocated to the Docker engine.
