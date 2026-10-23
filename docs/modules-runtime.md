# Optional module runtimes

The module application sends source to explicitly prepared private workers.
The original Python/SQL pads and the reading path continue to work without
these profiles. Preparing one subject does not install every framework.

## Prepare only the profiles you need

Start the ordinary Docker lab first. From the extracted complete course folder,
use the host launcher to build and start selected workers. The launcher owns
engine access; the browser and worker receive no Docker socket.

macOS or Linux:

```bash
bash scripts/module_lab.sh build --profiles python-core,cpp20
bash scripts/module_lab.sh start --profiles python-core,cpp20 --no-browser
```

Windows PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\module_lab.ps1 build -Profiles python-core,cpp20
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\module_lab.ps1 start -Profiles python-core,cpp20 -NoBrowser
```

Open `http://127.0.0.1:8765/journeys` after readiness succeeds. Use the same
profile list and project for later `status`, `start` or `stop` actions. Profile
preparation needs a connected bootstrap; practice uses the prepared local
images. Nothing uploads an image or downloads a model when you press Run.
Kubernetes uses its separate owned-cluster preparation and lease checks.

| Profile | Fixed source and operation | Prepared toolchain |
| --- | --- | --- |
| `python-core` | `main.py`, fresh Python process | Existing Core image and NumPy |
| `cpp20` | `main.cpp`, compile then execute | GCC 14.3.0 with C++20, hash-locked CMake 3.28.4 and Ninja |
| `tensorflow-cpu` | `main.py`, fresh Python process | Python 3.12, TensorFlow 2.20.0, NumPy 2.2.6 |
| `llm-torch-cpu` | `main.py`, fresh Python process | Python 3.12, PyTorch 2.9.1 CPU, NumPy 2.2.6 |
| `scala-jvm` | `Main.scala`, compile then `Main` | Spark distribution's matched Scala 2.13 compiler/library and JDK 17 |
| `spark-local-scala` | `Main.scala`, compile then local Spark submit | Spark 4.0.1, matched Scala 2.13, JDK 17, `local[2]` |
| `spark-local-python` | `main.py`, local Spark submit | Same Spark/JDK, Python 3.12, `local[2]` |

The NumPy attention foundation uses `python-core`; it does not require PyTorch.
A successful fixed compiler operation does not establish a CMake/CTest project
build. The current browser operation compiles a single source file directly.
Multi-file CMake, interactive REPL state, package resolvers, arbitrary compiler
flags, arbitrary command lines, GPU jobs, distributed Spark and external
model endpoints are outside this operation.

## What readiness and a result mean

At worker startup, a fixed bounded probe checks identity isolation and executes
an actual backend smoke: C++20 compilation and run, a Scala compilation and run,
a tiny local Spark count, or a framework tensor/array sum. That probe has a
45-second total deadline. `/health` returns its cached result and an ephemeral
`instance_id`; health polling does not repeatedly start a JVM or import a
framework. A failed probe leaves the service not ready. Preparation must inspect
that failure rather than claiming that an image definition proves readiness.

A submitted job moves through preparing, compiling when needed, running and
verifying when requested. Compilation and execution share the selected total
15, 60 or 120 second deadline. A compiler invocation also has a maximum
60-second phase deadline. Failed compilation never runs an older binary.
Cancellation kills the owned process group and, inside the dedicated worker
PID namespace, remaining processes with the fixed job UID. A job that creates
a new session does not gain an unlimited background lifetime.

Execution-only success means an actual zero exit status. It does not mark
mastery or invent checks. Registered verifiers call typed APIs against fixed
fixtures and return named boolean checks:

- `tf-gradient-v1`: three float64 gradient-step fixtures and invalid-rate cases.
- `llm-causal-attention-v1`: numeric attention values, forbidden weights,
  future-value perturbation and malformed-input cases.
- `cpp-ownership-v1`: fourteen value/ownership checks through an immutable
  compiled harness that calls the submitted functions.
- `spark-rows-v1`: paid identities, typed schema, NULL-aware golden groups,
  repartition invariance and a changed-input fixture.

A selected verifier must produce a valid bounded check report, every reported
check must pass, and the process must exit zero. Printed words such as
`success` or `checks passed` do not create verification evidence. These checks
are teaching feedback for trusted personal learner code, not a tamper-resistant
examination system. Progress and mastery still require the learner's reasoning.

## Resource and credential boundaries

`compose.modules.yaml` attaches workers only to an internal project network.
Worker port 8081 is not published. The app shares the PostgreSQL network
namespace and reaches only fixed worker service names supplied by the host
launcher. Worker credentials live in a private runtime session outside
`.learning`; portable progress backups must exclude that session.

The worker token is mounted inside the image-owned `/run/ds60` directory,
which is root-owned mode 0700. This also protects token files when Windows
file sharing expands their POSIX mode bits; it is not a general permission
exception for arbitrary paths. The mandatory child-read probe still applies.
The HTTP supervisor reads its private token, then each learner process runs as
UID/GID 65534 with supplementary groups cleared. Readiness proves that this
identity cannot open the credential and that the supervisor can terminate a
process with that identity. Images require a private container PID namespace
and the narrow CHOWN, SETUID, SETGID, DAC_OVERRIDE and KILL capabilities for
this supervisor. Learner processes do not retain those capabilities. There is
no engine socket, repository mount, learner home mount or cloud credential.
The ordinary personal app remains a trusted-code environment, not a hostile
multi-user sandbox.

Requests require `X-DS60-Worker-Token`, including health. Cross-origin browser
requests are refused. A worker accepts one active job, retains at most 32
terminal snapshots, rejects bodies above a fixed bound and source above
256 KiB, and keeps at most 128000 bytes of output with a head/tail truncation
notice. Output draining preserves final errors and exit status. The browser
may impose a smaller source limit.

Each job has a disposable scratch directory, a 32 MiB total file allowance,
a 1024-file allowance and a per-file 32 MiB limit. Container tmpfs is 128 MiB and explicitly permits execution of compiled job
files; it is private disposable memory, not a host filesystem mount.
ordinary workers have a 2 GiB memory cap and heavy framework/Spark profiles
have 3 GiB. Two CPUs and 128 processes are the ordinary worker ceilings; Spark services
allow 384 tasks because JVM and Python worker threads count toward that limit.
JVMs receive ActiveProcessorCount=2 and fixed small GC thread budgets.
Health, polling and cancellation use an existing HTTP control thread so child
PID pressure cannot prevent creation of a request-control thread. These are
initial small-lab budgets, not guarantees for long training or large data.
Enable a small number of workers within the engine's available memory.
No model, generated dataset or Spark output is exported by this initial
worker protocol. Source, notes and bounded results are saved through the app's
existing host-mounted learning workspace; disposable worker files are removed.

## Reproducibility and qualification

TensorFlow and CPU PyTorch use separate Linux amd64 and arm64 requirements
locks in `docker/workers/`, with exact transitive versions and wheel hashes.
Builds use `--require-hashes --only-binary=:all:`. Re-resolve these locks
intentionally, then repeat import, numeric verifier and process-cleanup proofs.
Do not install the isolated TensorFlow tuple into the base course environment.
Base-image version tags select the reviewed toolchain family; capture actual
image IDs/digests and architecture from a successful build when qualifying it.
A tag or a resolved dependency graph alone is not a runtime proof.

As of 22 October 2026, the upstream TensorFlow 2.20.0 release has CPython 3.12
Linux x86_64 and ARM64 wheels. The `tensorflow_cpu` package has no corresponding
ARM64 wheel in that release, so the common profile uses `tensorflow` without a
CUDA extra and disables GPU visibility. Official CPU PyTorch 2.9.1+cpu wheels
exist for both Linux architectures. These metadata checks establish an
available build input, not a successful import on either architecture.
[TensorFlow installation](https://www.tensorflow.org/install/pip),
[TensorFlow 2.20.0 release metadata](https://pypi.org/project/tensorflow/2.20.0/),
[official PyTorch CPU wheels](https://download.pytorch.org/whl/cpu/torch/).

Spark 4.0.1 requires Java 17/21 and Scala 2.13 with the same Scala version used by
the distribution. The worker copies the official Spark distribution into its
own Python 3.12/JDK 17 image and compiles against that distribution's jars.
No Maven, Scala CLI or pip resolver runs during a learner job.
[Spark 4.0.1 prerequisites](https://spark.apache.org/docs/4.0.1/),
[Apache Spark image source](https://github.com/apache/spark-docker),
[official GCC image architectures](https://hub.docker.com/_/gcc).

Windows uses a Linux-container engine; macOS uses its engine's Linux VM.
Native amd64 and native arm64 are separate qualification rows. A successful
arm64 run does not prove Windows host mount behavior, amd64 execution or an
emulated platform. Record exact runtime evidence in the implementation
checkpoint rather than filling an untested row with a checkmark.

For an explicitly trusted registry mirror, build arguments `DS60_CPP_IMAGE`,
`DS60_PYTHON_IMAGE`, `DS60_SPARK_IMAGE` and `DS60_CORE_IMAGE` can override the
corresponding reviewed base. Keep the same toolchain family and record the
resolved digest and platform. Never disable TLS to repair registry access.
An override is a new image input and needs the same runtime qualification.
