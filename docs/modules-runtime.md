# Classroom runtime contracts

Use `./classroom` for the supported Linux-container classroom on Linux, macOS
or Windows through WSL 2. Every subject uses the same `/classroom` interface.
The [startup guide](one-command-classroom.md) owns installation, image selection,
resume and rebuild instructions; [profile selection](docker-profiles.md) explains
how to prepare a smaller set. This reference describes what each execution
surface actually accepts and how the optional owned Kubernetes session works.

A new project prepares sixteen ordinary worker profiles. `--starter` prepares
only the app, PostgreSQL and Python Core. Explicit `--profile` selections include
Core and replace the remembered selection; they do not stop unselected workers
already running. Repeat a custom `--project NAME` on later commands. `resume`
never builds or pulls, and `--rebuild` deliberately applies changed source or
configuration. GPU and owned-cluster preparation remain separate opt-ins.

## Ordinary source contracts

The app sends submitted source to a fixed private operation. It does not send
an arbitrary shell command, compiler flags, package manifest or host path.
The worker stages that source under the filename below. Source may create
bounded temporary files during execution, but those files are not a project
upload channel or durable storage.

| Profile | Staged source | Actual operation |
| --- | --- | --- |
| `python-core` | `main.py` | Fresh Python process with the prepared Core dependencies |
| `cpp20` | `main.cpp` | C++20 compile and link, then execute; pthread support and compiler warnings enabled |
| `c17` | `main.c` | C17 compile and link, then execute; pthread and math libraries available |
| `go` | `main.go` | Fixed `go tool compile` and link using the image's prepared standard-library import configuration |
| `csharp-dotnet` | `Program.cs` | Compile inside an immutable trusted .NET project with offline package sources, then run its DLL |
| `rust-stable` | `main.rs` | Rust 2024 compilation with the prepared Arrow library, then execute |
| `swift-linux` | `main.swift` | Swift 6 Linux compilation with `-parse-as-library`; use the guide's explicit entry point |
| `java21` | `Main.java` | `javac --release 21`, public `Main`, then `java -ea`; prepared H2 JDBC library available |
| `javascript-node` | `main.mjs` | Node ES module with strict unhandled-rejection behavior |
| `typescript-node` | `main.mts` | Strict NodeNext type checking and compilation, then execute emitted `compiled/main.mjs` |
| `tensorflow-cpu` | `main.py` | Fresh Python process with its separately locked TensorFlow dependencies and GPU visibility disabled |
| `llm-torch-cpu` | `main.py` | Fresh Python process with its separately locked PyTorch CPU dependencies |
| `scala-jvm` | `Main.scala` | Compile with the prepared Scala toolchain, then run `Main` |
| `spark-local-scala` | `Main.scala` | Compile and submit to bounded local Spark with `local[2]` |
| `spark-local-python` | `main.py` | Submit to the prepared local PySpark environment with `local[2]` |
| `php-cli` | `main.php` | PHP syntax check followed by CLI execution, with assertions and PDO SQLite enabled |

The authoritative commands are in
[`worker_operations.py`](../src/ds60sqlpy/worker_operations.py); image inputs and
locks are under `docker/workers/` and
[`compose.modules.yaml`](../compose.modules.yaml). Read the lesson's capability
notice before assuming an additional library exists. A prepared compiler does
not imply Maven, Cargo, Composer, CMake, a browser DOM, interactive stdin or an
arbitrary multi-file build. Larger project fixtures have their own documented
preparation and cleanup. SwiftUI and Apple SDKs need the separate Xcode route.

The original Python and SQL classroom pads use their own bounded adapters.
Notebook-style Python cells can share variables within one Run; a later Run
starts a fresh process. PostgreSQL is a classroom service, not a worker profile.
SQL snippets and **Whole SQL lesson (psql)** have different transaction and
include-file behavior. Whole lessons use guarded cataloged source and fixed
includes. Preparing the `training` schema is a deliberate reset of disposable
course tables. See [PostgreSQL setup](setup/postgresql.md) and
[classroom controls](classroom-experience.md).

## Browser and optional GPU surfaces

`html-browser` and `javascript-browser` are browser capabilities, not launcher
`--profile` names. They need no additional compiler worker. HTML/CSS accepts one
complete document with embedded styles and bounded inline JavaScript. D3 uses
the bundled library, `#chart` and `#output`, with inline offline data. Node source
has no browser DOM. External imports, fetches and navigation are not part of the
opaque preview contract.

Live preview is an explicit page-session opt-in. Editing can refresh that
preview, but it does not automatically save result receipts. Manual Run and
**Save observation** are separate actions. Switching lessons, viewing history,
Stop and reload must not silently rerun source. Browser observations retain the
submitted source identity and `verified: false`; they are not server-side tests.
The initial preview has a 120-second UI wait budget, not an operating-system CPU
quota or a promise to interrupt arbitrary synchronous browser code. See the
[preview studio guide](classroom-experience.md#explore-in-the-preview-studio).

PHP CLI prints program output and supports prepared SQLite examples. It does
not serve HTTP or implement real browser cookies or sessions. Those topics use
[the separately prepared web project](../courses/web-development/fixtures/php-http-lab/README.md).
A request simulation must not be described as an actual browser exchange.

The optional `cuda-cpp`, `cuda-python`, `pytorch-cuda` and `tensorflow-cuda`
profiles require an explicitly selected compatible NVIDIA device. The first
stages `main.cu`; the others stage `main.py`. Current workers target Linux amd64
and remain outside default startup and `--all`. They perform real allocation,
kernel/tensor computation, synchronization and readback before becoming ready.
CPU models and compiler-only checks remain useful, separate evidence. Ordinary
CPU profiles stay CPU profiles on an NVIDIA host. Follow
[CUDA setup and recovery](cuda-classroom.md) for platform support, pinned
compiler/runtime differences, device selection and actual qualification limits.

## Readiness, execution, verification and recovery

These observations answer different questions:

| Observation | What it establishes |
| --- | --- |
| An image exists | Build inputs were assembled; a runtime might still fail to start |
| A worker is ready | Its fixed startup probe passed for this worker instance |
| A submitted program exits zero | That submitted source completed under the selected runtime and limits |
| Registered checks pass | A named verifier observed its stated fixture invariants |
| A saved result is readable | The earlier receipt survived; the current source has not been rerun |

Ordinary startup probes have a 45-second total deadline and compile or execute
small real examples. Health returns the cached result and instance identity;
polling does not repeatedly import a framework or start a JVM. Identity and
credential-isolation checks must also pass. Failure leaves the service
unavailable. Read its diagnostic instead of inferring readiness from its name.

Jobs progress through preparation, compilation when applicable, execution and
optional verification. Compilation and execution share the selected total
15, 60 or 120 second budget; a compile phase also has a 60-second ceiling.
Failed compilation does not run an old executable. Cancellation and shutdown
reap owned process groups and isolated learner descendants. A normal syntax
error can be repaired and resubmitted. Infrastructure failures that leave
cleanup uncertain disable readiness and require inspection.

Registered verifier IDs include `tf-gradient-v1`, `llm-causal-attention-v1`,
`cpp-ownership-v1`, `spark-rows-v1` and the dedicated `k8s-readiness-v1`.
Their reviewed fixtures test specific numerical, ownership, row/schema or
cluster properties. A registered verifier must produce a bounded structured
report with passing checks and a successful exit. Printed success markers do
not create typed checks, and passing a fixture does not establish mastery.

The app saves module source, notes and source-bound receipts in the learning
volume. Recovery polls an existing worker job; it never resubmits learner source
automatically. A replaced worker may no longer know an earlier in-flight job.
Preserve that interrupted receipt and inspect its outcome before deciding to
run again. [Saved work and history](classroom-experience.md#save-work-and-understand-history)
explains the learner controls.

GPU timeout, cancellation, resource interruption, signal exit or a recognized
serious device fault additionally requires owner review. Child-process cleanup
does not prove device recovery. The worker keeps the receipt, rejects another
job and never resets a GPU automatically. Ordinary compiler errors remain
repairable. Restart an affected worker only after appropriate device inspection,
so its real startup probe runs again.

## Resource and credential boundaries

Workers join the internal module network and do not publish their control
port. `compose.classroom.yaml` mounts the private `classroom-runtime` volume
read-only in workers. Shared service definitions supply the toolchains and
resource limits; classroom composition owns the credential storage. That volume
is separate from learner exports. The root-private `/run/ds60` directory and
child-read probe protect worker credentials; learner processes use UID/GID
65534 with supplementary groups cleared. The supervisor owns only the
capabilities needed for identity changes and cleanup. No engine socket,
learner-home mount or ambient cloud credentials enter an ordinary worker.

The classroom is for trusted personal learner code. These controls do not make
it a hostile multi-user service. Host, origin and session-token checks protect
the local app; private worker requests use a separate token. Keep tokens and
Kubernetes credentials out of screenshots, notes, source and portable backups.

Current ordinary module limits are:

- The browser/module editor accepts at most 48,000 UTF-8 source bytes. The worker
  protocol independently caps source at 256 KiB; this does not enlarge the editor.
- Worker output retains a bounded 128,000-byte head/tail transcript. Browser
  observation output has its own 32,000-byte validation bound.
- A worker accepts one active job and retains at most 32 terminal control
  snapshots. Durable learner receipts live in the app's state, not that cache.
- A job's scratch tree allows 32 MiB and 1,024 files. Per-file limits are normally
  32 MiB; the trusted .NET compile phase permits 64 MiB per file while retaining
  the 32 MiB monitored workspace allowance.
- Ordinary workers have a private 128 MiB executable tmpfs, two CPUs, 2 GiB RAM
  and a 128-process limit. TensorFlow, PyTorch and Spark use 3 GiB; Spark allows
  384 tasks. Optional GPU workers use 4 GiB and a 256 MiB tmpfs. Kubernetes has
  its separate smaller supervisor and cluster budgets.

These are small-lab limits, not a promise to train a large model or run a
production cluster. Models, Spark outputs and arbitrary worker-created files
are not exported through the single-source protocol. Keep durable work in the
classroom's supported source, notes, history and result channels.

## Prepare and run the owned Kubernetes lab

Kubernetes is an explicit host-assisted extension. `./classroom --profile
k8s-kind` and `--k8s-session` are not supported launcher options. The ordinary
classroom never creates a cluster. This workflow uses the self-contained
`compose.classroom.kubernetes.yaml` overlay and one newly owned disposable kind
node, with no ambient kubeconfig or existing cluster selection.

Use a POSIX shell and a prepared Python 3.11 or 3.12 interpreter on Linux, WSL 2
or macOS. The examples call it `python3`. Windows needs Linux paths and the
WSL engine's local Unix socket; native Windows credentials and named pipes are
unsupported. Ordinary classroom learning still needs no host Python. Review
engine disk/RAM availability before preparing another node.

1. Choose a dedicated project and unused fixed ports. This example deliberately
   uses `ds60-k8s-study`, browser port 8787 and database port 55433. If a port is
   occupied, choose another and change both the exported value and launcher
   argument. Pin the selected local engine for every command in this shell:

   ```sh
   if [ -n "${DOCKER_HOST:-}" ]; then
     CLASSROOM_ENGINE="$DOCKER_HOST"
   else
     CLASSROOM_ENGINE="$(docker context inspect --format '{{.Endpoints.docker.Host}}')"
   fi
   export DOCKER_HOST="$CLASSROOM_ENGINE"
   unset DOCKER_CONTEXT
   export COMPOSE_PROJECT_NAME=ds60-k8s-study
   export DS60_CLASSROOM_PORT=8787 DS60_POSTGRES_PORT=55433 DS60_PUBLIC_PORT=8787
   ./classroom --local-build --registry upstream --starter --project ds60-k8s-study \
     --port 8787 --database-port 55433 --no-browser
   ```

   The preparation helper below accepts only a local `unix:///...` endpoint.
   Do not substitute a remote context or another engine after the classroom starts.
   This recipe uses locally built release images and the upstream registry
   selection consistently. Hub mode and an unrelated learner project are not
   part of this optional preparation example.

2. Finish image and tool preparation before starting the short lease. The
   fixture tag is its own protocol version; the worker tag follows the checkout's
   package version. These builds do not create a cluster or publish images:

   ```sh
   CLASSROOM_VERSION="$(python3 -c 'import pathlib,tomllib; print(tomllib.loads(pathlib.Path("pyproject.toml").read_text())["project"]["version"])')"
   docker build --progress=plain -f docker/kubernetes/Dockerfile.fixture \
     -t ds60sqlpy-k8s-fixture:0.2.0 .
   docker build --progress=plain -f docker/kubernetes/Dockerfile.worker \
     -t "ds60sqlpy-worker-k8s-kind:$CLASSROOM_VERSION" .
   python3 scripts/prepare_kubernetes.py tools --allow-download
   python3 scripts/prepare_kubernetes.py doctor
   ```

   Tools are pinned and checked against official SHA256 metadata. The helper's
   default tool cache is `work/kubernetes-tools`; it does not install globally.
   Both Dockerfiles accept a deliberately selected `DS60_PYTHON_IMAGE` build
   argument when a reviewed TLS-preserving base mirror is required. See
   [image and fixture details](../docker/kubernetes/README.md).

3. Prepare immediately before practice. This command creates a new owned node
   and namespace, loads the existing fixture image and requests a short-lived
   scoped credential. `--allow-node-download` explicitly permits fetching the
   pinned node image when absent; omit it for an already cached run:

   ```sh
   python3 scripts/prepare_kubernetes.py prepare --confirm-create \
     --docker-host "$DOCKER_HOST" --allow-node-download
   ```

   Copy the returned `session_dir` path, not credential contents. Replace the
   following placeholder with that exact absolute private path:

   ```sh
   export DS60_K8S_SESSION_DIR="/absolute/private/path/from/session_dir"
   python3 scripts/prepare_kubernetes.py inspect \
     --session "$DS60_K8S_SESSION_DIR" --docker-host "$DOCKER_HOST"
   ```

   Inspection checks the lease, matching private host receipt, chosen endpoint
   and remaining lifetime without changing the cluster. The token is requested
   for 15 minutes; its returned expiry governs validity. A fresh session needs
   enough time for the longest job and cleanup reserve. Do not edit timestamps,
   move credentials into `.learning`, or treat a paused browser as a lease renewal.

4. Start only the already prepared app overlay and Kubernetes worker. Existing
   PostgreSQL, Core worker and private runtime volume remain in place:

   ```sh
   docker compose -p "$COMPOSE_PROJECT_NAME" \
     -f compose.classroom.yaml -f compose.classroom.kubernetes.yaml \
     --profile k8s-kind up -d --no-deps --no-build --pull never \
     --wait --wait-timeout 120 lab kubernetes-worker
   ```

   `DS60_PUBLIC_PORT` must match the actual published browser port so exact
   Host/Origin authentication continues to work. This overlay retains every
   ordinary and optional GPU endpoint and adds only Kubernetes. It mounts the
   scoped lease/config read-only, joins the owned kind network and publishes no
   worker port. Open `http://127.0.0.1:8787/classroom` for the example ports.
   Read the capability notice before choosing an executable Kubernetes variant.

5. Inspect or stop using the same project, overlay and session variable. Status
   and stop do not renew a lease or create a cluster and remain usable after
   expiry:

   ```sh
   docker compose -p "$COMPOSE_PROJECT_NAME" \
     -f compose.classroom.yaml -f compose.classroom.kubernetes.yaml \
     --profile k8s-kind ps --all lab kubernetes-worker
   docker compose -p "$COMPOSE_PROJECT_NAME" \
     -f compose.classroom.yaml -f compose.classroom.kubernetes.yaml \
     --profile k8s-kind stop lab kubernetes-worker
   python3 scripts/prepare_kubernetes.py release \
     --session "$DS60_K8S_SESSION_DIR" --confirm-release
   ```

   Release checks the recorded full container ID, ownership and namespace UID.
   It preserves same-name replacements and ambiguous resources, then proves
   node absence before removing credentials. Keep the private receipt until
   release succeeds. Learner volumes, unrelated containers and shared networks
   remain intact; `down -v` is not a cluster-release shortcut.

6. Restore the ordinary app configuration from its existing image, with no
   build or pull, before using normal classroom resume again:

   ```sh
   docker compose -p "$COMPOSE_PROJECT_NAME" -f compose.classroom.yaml \
     --profile python-core up -d --no-deps --no-build --pull never --wait lab
   ./classroom stop --project ds60-k8s-study
   ./classroom resume --project ds60-k8s-study
   ```

   The overlay is an explicit session configuration, not a saved launcher
   profile. An expired or released Kubernetes session requires a new preparation
   and inspection followed by the overlay start. Normal `./classroom resume`
   does not recreate its cluster or credentials.

The Kubernetes adapter admits reviewed Deployment/Service/ConfigMap or finite
Job shapes, not arbitrary Kubernetes administration. It verifies owner and
resource identities, bounded readiness, fixed in-cluster HTTP observations or
finite-task output, then cleans only resources bound to that Run's nonce and
UIDs. Work gets its selected deadline plus an independent 15-second cleanup
reserve. Unproved cleanup is a failure, not a clean cancellation. The detailed
[fixture contract](../docker/kubernetes/README.md#fixture-contract-2-and-bounded-ordinary-labs)
defines what is and is not executed; other networking and operations chapters
remain reading or separately prepared host labs.

## Qualification evidence

Use [validation](validation.md) and the current
[implementation checkpoint](implementation/CHECKPOINT.md) for revision-specific
acceptance. Keep source tests, image builds, startup probes, actual lesson runs,
browser observations, hardware tests and hosted CI as separate records. A Linux
arm64 success does not establish Linux amd64, WSL host integration, emulation or
NVIDIA execution. A saved historical receipt does not qualify changed source.
