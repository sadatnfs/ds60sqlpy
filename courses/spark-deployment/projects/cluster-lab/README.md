# Owned Spark deployment workshop

This project teaches a real separate-driver Standalone topology and provides
portable Kubernetes instructions. It is independent of classroom imports and
can be copied as a directory. Its source is not a runtime acceptance receipt;
see [qualification](QUALIFICATION.md).

## Prepare explicitly

Use Python 3.11 or newer on the host, Docker with Compose 2.28 or newer, and a
locally prepared native Linux Spark 4.0.1 image. The runtime image must have
Python, `/opt/spark/bin/spark-submit`, `/opt/spark/bin/spark-class`, a compatible
Java runtime and a working nonroot UID 65534. Check sufficient whole-engine
memory, CPU, disk and PID capacity before starting. Run one heavy local lab at
a time. No command below pulls, logs into a registry or emulates another CPU.

```sh
python3 lab.py init --image YOUR_PREPARED_LOCAL_SPARK_IMAGE
python3 lab.py up
python3 lab.py status
python3 lab.py submit --hold-seconds 60
```

The image placeholder names an actual existing local image. Initialization
checks its native architecture and saves its immutable engine ID. `up` starts
master, worker-a, worker-b, a separate driver and History Server on an internal
network. A bounded UI relay joins that network and a separate ingress network,
publishing only fixed UI destinations on host loopback. Compute services have
no external network. The program collects eight small partition summaries from 100000 rows,
checks exact moment/coverage oracles, fits intercept 3 and slope 2 and produces
two future-covariate predictions. This is a closed-form linear fixture, not a
general conditional-history forecaster or either independent modeling package.

`python3 lab.py urls` prints dynamic loopback UI endpoints. Open the driver UI
while the bounded hold is active; after application exit use History Server.
Reports and event logs remain under `.workshop`. The state parent is private,
while individual mounted data directories permit writes by the container UID.
Do not share that state directory or its notebook token. Source mounts are
explicit files/directories and exclude the private state tree.

## Lifecycle and an owned failure experiment

```sh
python3 lab.py stop
python3 lab.py resume
python3 lab.py down
python3 lab.py up
```

Resume starts existing containers without build/pull. Down removes only this
project's containers/network and leaves state intact. No command deletes files,
volumes or images. To preserve a different experiment, use a new `--state PATH`
and repeat that same path on every operation. Moving source/state invalidates the
binding deliberately; create a new owned lab rather than editing owner.json.

For controlled loss, run `submit --partition-seconds 15 --allow-one-worker`,
observe an active worker-a task in the live UI, then run `worker-stop worker-a`
from another terminal. Retain host stop identity/timestamp and application
task/attempt evidence. The numerical receipt alone does not prove that loss
interrupted useful work. Restore with `worker-start worker-a`, then rerun the
ordinary two-worker baseline. Retain both receipts and failure logs.

## Optional notebook

Supply a compatible already prepared image with JupyterLab and PySpark installed:

```sh
python3 lab.py --state .notebook-lab init \
  --image YOUR_PREPARED_LOCAL_SPARK_IMAGE \
  --notebook-image YOUR_PREPARED_LOCAL_NOTEBOOK_IMAGE
python3 lab.py --state .notebook-lab up
python3 lab.py --state .notebook-lab notebook
python3 lab.py --state .notebook-lab urls
```

Use the login form with the token in the private state file; do not paste it
into shared logs or notebooks. The source recipe `Dockerfile.notebook` requires
an explicitly prepared complete hash-checked wheel lock and wheelhouse. They are
not supplied or claimed qualified. Run `app/notebook_session.py` in the kernel
to test driver callbacks and a bounded aggregate. A notebook-only import does
not qualify executor dependencies. Stop the session and owned kernel afterward.

## Kubernetes route

`Dockerfile.cluster` preserves a reviewed Spark base's Kubernetes entrypoint and
adds the bounded application. `kubernetes/access.yaml`, `resources.yaml`,
`notebook-service.yaml`, `executor-template.yaml` and `network-policy.yaml` are
reviewable templates. Replace namespace/session placeholders in owned copies.
Match the actual image UID; the executor template's UID 185 is an explicit
example, not a discovered property. The network template needs actual API/storage
egress rules and CNI enforcement qualification before use.

`kubernetes/submit.py` requires namespace, context, kubeconfig, API URL and image
digest and prints a plan by default. `--execute` deliberately submits to that
target with a ten-minute command bound after comparing its API URL to the selected
kubeconfig context. It never provisions a cluster. Do not
use an ambient kubeconfig or claim cloud qualification from local tests. Preserve
observed Pod UIDs and storage before any scoped cleanup.

The [tutorial route](../../README.md) explains every command's network, identity,
storage and evidence contract, including secure UI access and troubleshooting.
