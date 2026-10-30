# Isolated Spark Compose qualification

This harness exercises this standalone package with a Spark master, two worker
containers and a separate client-mode driver container on one native Linux
engine. Copy the entire package folder into a fresh directory first if testing
independence. The folder can be renamed. The harness never imports another
classroom checkout and compares the supplied wheel's Python source with the
copied package before running it.

The source defines an acceptance procedure. A checked-in Compose file or passing
validator tests do not establish distributed runtime acceptance. Only a completed
`RESULT.json` with `accepted: true`, exact source/image/artifact identities and
retained driver evidence qualifies the observed environment. ARM64 and AMD64,
multi-container and multi-machine, CPU and GPU are separate claims.

## Prepare explicit inputs

Prepare the package wheel and a compatible local image through the package's
installation/build instructions. The image must already contain Python3.11 or
3.12, pip, JDK17 or21, Spark4.0.1 with Scala2.13 at `/opt/spark`, and the numerical
libraries required by this package. The integration harness does not prepare
missing dependencies. The Torch package needs its declared Torch/NumPy/SciPy
extras available in the image; the native package needs compatible native
system libraries and its separately assembled installation.

All services install exactly the supplied wheel into their own temporary
`/work/python` directory, with `--no-index --no-deps`. The driver's installed
source must match the supplied wheel and the copied package. No editable install
or classroom Python path is used. The native package's prepared installation is
mounted read-only on the driver only; its normal SparkFiles path distributes
bound native artifacts to workers. Workers do not receive that shared mount.

The image must match the engine's native architecture. Missing images, wrong
architecture, image `VOLUME` declarations, mismatched wheels, stale dependencies
and absent preparation fail before or during explicit qualification. The runner
uses `--pull never` and never contacts a registry. A previously prepared classroom
image can be supplied explicitly for a compatibility check, but that does not
qualify a neutral standalone Docker build. Record that distinct build separately.

With the current package as the working directory and already prepared inputs:

```sh
python3 integration/run.py --image YOUR_PREPARED_LOCAL_IMAGE \
  --wheel /absolute/path/to/current-package.whl \
  --output /absolute/path/to/fresh-integration-evidence
```

Use the actual wheel filename emitted by the package build. It must retain its
valid wheel filename. Choose a fresh evidence directory outside the package.
Never reuse a failed result directory or replace old receipts. The runner needs
Docker Compose v2 and a running Linux-container engine; use your explicitly
chosen Docker context when several engines are available.

## What the test actually proves

The runner compiles a small original Scala probe offline against the selected
image's installed Spark jars. The compiler receipt records all toolchain JAR
hashes and probe source/JAR hashes. No Maven or dependency download occurs.
The four services share an internal-only Compose network. No ports are published
on the host, no service has an engine socket and no named data volume is created.
Their root filesystems are read-only; temporary state is kept in bounded tmpfs.
The host orchestrator controls only its unique owned project's containers.

The test then:

1. Confirms two simultaneous Spark executor tasks run on distinct `worker1` and
   `worker2` container hosts, with executor IDs and JVM process IDs. Equal PID
   numbers across namespaces are valid; host/container identity is also required.
2. Sets driver `maxResultSize` to128KiB and verifies that an intentionally
   oversized raw-data collection fails for that specific limit. Normal modeling
   actions return bounded summaries and only a few predictions.
3. Fits the package's actual numerical model to32,768 deterministic observations
   across eight partitions. Independent analytic parameter/prediction formulas
   must agree, the fit must converge, and the accepted row count must match.
4. Records complete partition identities, row counts, sums and SHA256 digests of
   ordered row IDs. Every expected range partition must appear exactly once in
   at least one complete materialization stage. Partial or duplicate partition
   results cannot satisfy this evidence check.
5. Starts a fresh fit whose JVM input partitions wait at a bounded test gate.
   Once both worker hosts have active tasks, the host stops only `worker2` and
   releases the surviving and retried tasks. The fit must finish using the
   surviving worker. This is a controlled input-partition interruption, not a
   fault injected inside a native numerical kernel.
6. Requires a Spark task-end failure for the exact interrupted task ID and a
   successful retry for the same stage/partition on a different executor, with
   an increased task or stage attempt. A restart or successful unrelated job
   alone does not prove recovery.
7. Restarts the same stopped worker container, observes a replacement executor,
   repeats package forecasts/predictions and compares baseline and recovered fits.

The native workload fits a normal model and a real AR1 model, then verifies
three conditional-history forecasts against finite innovation-moment formulas.
The Torch workload fits a Gaussian regression using distributed additive Torch
likelihood evaluation and tests response-free point predictions at future
covariates. Those are explicitly labeled future-covariate predictions, not an
AR/history forecast API, DDP/FSDP training or automatic distribution of arbitrary
Torch programs.

## Resources, failure and evidence

The default environment caps master memory at384MiB, each worker at1536MiB,
and the driver at2048MiB. Executors each have one core and512MiB heap. Services
have PID limits and CPU limits; combined configured CPU capacity is3.5 cores
and memory capacity is5504MiB, plus bounded compilation before cluster startup.
The host records cgroup memory/PID events and refuses OOM or PID-limit failures.
CPU/memory limits, actual peak usage and scientific correctness are distinct.

The default workload deadline is20minutes. The runner also bounds individual
Docker calls, compiler execution, fault gates and cleanup. A timeout is a failed
run, with diagnostics retained where collection remains possible. The driver
stays alive briefly after the test so tmpfs evidence can be copied before owned
cleanup. It does not schedule background work or leave an unbounded server.

`RESULT.json` binds the observed engine platform, image ID, wheel and integration
source hashes, four container identities, internal network, fault action,
resource samples, task retry proof and volume inventories. `driver/driver.json`
contains numerical results, complete partition evidence, installed package
hashes and bounded Spark listener events. Service logs and the compiler receipt
are retained separately. Failed receipts remain failed and must be preserved.

Cleanup uses only the unique project created by this invocation. It does not
remove volumes, images, base images, another Compose project or learner state.
The before/after volume check requires every preexisting volume to survive.
If the host is interrupted before cleanup, inspect `RESULT.json` and the unique
`ds60-it-*` project identity before removing only that project's containers and
network. Never use a broad prune.

Lightweight validator tests run without Spark or Docker:

```sh
python3 -m unittest discover -s integration -p 'test_*.py' -v
```

These tests reject malformed wheels, stale source/artifact identities, wrong
platforms, cross-project ownership, incomplete/duplicated coverage, altered row identities,
missing failed attempts, same-executor pseudo-recovery and driver/same-host
identity substitutions. They do not replace actual Compose execution.

The integration instrumentation is original source under this package's license.
It does not change the licensing of Spark, Torch or native dependencies.
