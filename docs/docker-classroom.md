# Docker-only classroom

> **One classroom:** the browser opens `/classroom`, where Python, PostgreSQL,
> the engineering bridge and every module/book subject share one home and
> individually themed workspaces. Choose any path and set your own pace.
> Start with `./classroom`; see the [classroom guide](classroom-experience.md) for reading, code,
> saved work and compatibility bookmarks.


The primary workflow is one command from the course folder:

```sh
./classroom
```

It resumes the same project's remembered worker selection, reuses local images,
starts existing containers and opens the browser after actual readiness checks.
Only missing images are built. A new project selects all sixteen ordinary
workers; `--starter` selects Python Core. Use `./classroom resume` for strict
no-build startup, or `./classroom --rebuild` to install source updates. The
launcher selects available loopback host ports on first startup. Windows uses the
same launcher through WSL 2. The thin Windows/Mac launchers delegate to it.
See [the beginner one-command guide](one-command-classroom.md) for engine/WSL
setup, a smaller starter, persistence, fixed ports and recovery.

The remainder of this page is the **manual Compose reference**. Direct Docker
commands remain available without the Bash wrapper. Use a local Linux-container
engine and Docker Compose 2.28.0 or newer. Its fixed default ports may differ
from the automatic host ports selected by `./classroom`; use the launcher's
printed URL or `./classroom status` for its actual address.

## 1. Check the engine and configuration

```text
docker compose version
docker info --format "{{.OSType}}"
docker compose -f compose.classroom.yaml config --quiet
```

The engine type must be `linux`; the configuration check should finish without
an error. Select your local engine rather than a remote Docker context.
An unknown `!reset` tag means Compose needs updating. A plain YAML validator
does not understand every Compose tag.

## 2. Build the starter, with visible logs

First preparation needs internet and several gigabytes of free disk. Heavy
framework and Spark images need additional space. Build one image at a time
and keep the terminal open until each command succeeds:

```text
docker compose -f compose.classroom.yaml pull postgres
docker compose -f compose.classroom.yaml --parallel 1 --progress plain build lab
docker compose -f compose.classroom.yaml --profile python-core --parallel 1 --progress plain build python-core-worker
```

Build the lab first; its Python worker reuses that base. These foreground
builds show download and package-install output; they do not publish images.
Later starts reuse the prepared local images.

### If the image registry cannot be reached

An `x509: certificate signed by unknown authority` error during image metadata
or layer download is a connection/certificate problem before the lesson code
runs. Use your organization's approved engine certificate/proxy configuration.
Keep TLS verification enabled.

The repository also includes an explicit, public
[build-only mirror configuration](../docker/registry-mirrors.env.txt).
It selects [Google's Docker Hub mirror](https://cloud.google.com/artifact-registry/docs/pull-cached-dockerhub-images)
for the compiler/JVM/Node/Spark bases and
[Astral's pinned Python image](https://docs.astral.sh/uv/guides/integration/docker/)
on GitHub Container Registry for the Python base. It does not contain credentials, modify the engine, or publish images.
Use the mirror configuration only when it fits your network and trust policy.
Registry availability is separate from whether a built lesson runtime works.

To build every ordinary profile with that configuration and visible logs, run
this single line from the extracted course folder on any OS:

```text
docker compose --env-file docker/registry-mirrors.env.txt --progress plain -f compose.classroom.yaml --profile "*" --parallel 1 build
```

Use this file for the **build** command only. An explicit `--env-file` replaces
Compose's automatic `.env` loading, so use the normal start command below to
retain your local port/storage settings. If you intentionally need both local
build overrides and these mirrors, put `--env-file .env` before the mirror
file, provided that `.env` exists. Shell environment values still take
precedence. A mirror may not cache every upstream image; an unavailable image
remains a build failure to resolve, not a reason to bypass certificate checks.

## 3. Start and practice

```text
docker compose -f compose.classroom.yaml --profile python-core up -d --no-build --pull never --wait lab python-core-worker
docker compose -f compose.classroom.yaml --profile "*" ps
```

Wait for readiness, then open [the unified classroom](http://127.0.0.1:8765/classroom)
yourself. Python, SQL and every subject share that entrypoint. No website
account is needed. The initializer prepares private worker
credentials and writable learner storage inside Docker volumes.

Start with a reading lesson or a `python-core` lesson such as `llm-002`.
Read the guide, predict the result, edit and save your source, then choose Run.
Save your explanation as well as your code. A successful example run does not
complete the six exercises or establish mastery. Planned lessons remain planned.

If a runtime is unavailable, prepare that profile before running its lesson:

| Profile | Service to build/start | Used for |
| --- | --- | --- |
| `python-core` | `python-core-worker` | NumPy, pandas, statistics, NLP, LLM foundations |
| `cpp20` | `cpp-worker` | C++20 compilation |
| `c17` | `c-worker` | C17 compilation and bounded execution |
| `go` | `go-worker` | Prepared standard-library compile/link/run |
| `csharp-dotnet` | `csharp-worker` | C# through the immutable offline .NET project |
| `rust-stable` | `rust-worker` | Rust 2024 edition and prepared Arrow dependency |
| `swift-linux` | `swift-worker` | Swift 6 Linux/Foundation, with Apple SDK projects separate |
| `tensorflow-cpu` | `tensorflow-worker` | Actual TensorFlow tensors and gradient updates |
| `scala-jvm` | `scala-worker` | Standalone Scala/JVM |
| `spark-local-scala` | `spark-scala-worker` | Local Spark using Scala |
| `spark-local-python` | `spark-python-worker` | Local Spark using Python |
| `llm-torch-cpu` | `llm-worker` | PyTorch and tensor-based LLM lessons |
| `java21` | `java-worker` | Java 21 compilation and the prepared H2 teaching database |
| `javascript-node` | `javascript-worker` | Node24 JavaScript ES modules |
| `typescript-node` | `typescript-worker` | Strict TypeScript5.9 compilation and Node24 execution |

For example, add C++ after the starter:

```text
docker compose -f compose.classroom.yaml --profile cpp20 --parallel 1 --progress plain build cpp-worker
docker compose -f compose.classroom.yaml --profile python-core --profile cpp20 up -d --no-build --pull never --wait lab python-core-worker cpp-worker
```

Use the matching profile and service names for another subject. Build selected
workers sequentially and start only those you need. The NumPy LLM foundations
need no pretrained model. The PyTorch route uses `llm-torch-cpu`, and its small
teaching models train locally on CPU. Optional pretrained-model experiments
have a separate explicit download and preparation guide.

To build every ordinary worker locally with visible logs, use:

```text
docker compose --progress plain -f compose.classroom.yaml --profile "*" --parallel 1 build
```

This builds all ordinary language/framework images; it does not start them or
push them to a registry. Building everything uses substantially more disk than
the starter. Select the profiles you want for `up` so unused frameworks do not
consume memory. Kubernetes cluster preparation remains a separate operation.

## 4. Pause, return, and keep your work

```text
docker compose -f compose.classroom.yaml --profile "*" stop
```

For the shared launcher, return with `./classroom` or the strict no-build
`./classroom resume`. Its `.classroom/<project>/selection.env` remembers selected
profiles and registry mode. Supply the same `--project NAME` if you used one.
Existing containers are reused. If Docker reassigns the automatic browser port
while restarting PostgreSQL, only the app is recreated from its existing image
to accept the new exact address. The database and workers retain their IDs, and
there is no image build or pull. Missing containers can also be recreated from
local images while retaining their volumes. Fixed `--port` and `--database-port`
settings give a stable address and let all existing IDs survive later unchanged
resumes; apply changed port settings deliberately with `--rebuild`.

For the manual Compose route shown above, start the same engine, open the same
course folder, and repeat your Step 3 `up` command with the same profiles.
Direct Compose does not read the launcher's saved selection or automatically
recover its port choices. Use one route consistently, or carry the exact project,
profiles and ports across deliberately. Replacing app containers preserves
the named volumes. The default project is **`ds60-classroom`**:

| Docker volume | What it keeps |
| --- | --- |
| `ds60-classroom_classroom-learning` | Pads, module drafts, notes, saved results, history, progress and caches |
| `ds60-classroom_postgres-data` | PostgreSQL tables |
| `ds60-classroom_classroom-runtime` | Private worker credential, excluded from learning exports |

This is machine-local Docker storage, usually inside the engine's Linux VM.
It is **not** the visible `.learning` folder beside your checkout. The older
host-folder launchers keep using their own storage; switching routes does not
copy or merge either learning work or databases. Keep the same Docker project
to resume the same classroom. A different project name selects different volumes.

Use `stop` for ordinary pauses. **Do not use `down -v` or remove these volumes
to troubleshoot:** that can delete saved work and database data. Engine removal
or a factory reset can also remove volumes. Export before moving machines.

## 5. Export learning work and the database

Choose unused host filenames for every backup. The date below is just an example;
change it for a new backup. Save all drafts and let active Runs finish first.
With PostgreSQL still running, create and copy its ordinary dump file:

```text
docker compose -f compose.classroom.yaml exec -T postgres pg_dump -U ds60_admin -d advanced_sql_training -Fc -f /tmp/classroom-database.dump
docker compose -f compose.classroom.yaml cp postgres:/tmp/classroom-database.dump ./classroom-database-20261022.dump
docker compose -f compose.classroom.yaml --profile "*" stop
```

Now archive only the learning volume through a temporary container. Verify the
volume name first. If it is missing, stop and check the project name rather
than creating an empty replacement. The helper name must also be unused:

```text
docker volume inspect ds60-classroom_classroom-learning --format "{{.Name}}"
docker create --name ds60-classroom-backup --network none --mount type=volume,source=ds60-classroom_classroom-learning,target=/learning,readonly --entrypoint tar postgres:17 -czf /tmp/classroom-learning.tar.gz -C /learning .
docker start -a ds60-classroom-backup
docker inspect --format "{{.State.ExitCode}}" ds60-classroom-backup
docker cp ds60-classroom-backup:/tmp/classroom-learning.tar.gz ./classroom-learning-20261022.tar.gz
```

The exit-code check must print `0` before copying. Check the copied archive
in your normal file manager or archive utility.
It should contain the saved learning files you used, including `modules/` for
module drafts. Keep both the learning archive and database dump in your backup
location. After the copy succeeds, remove **only** the temporary helper:

```text
docker rm ds60-classroom-backup
```

The source volume was read-only; private runtime credentials were not mounted
or exported. These commands avoid binary shell redirection and work without
a host Python installation. The database dump and learning archive protect
different data; neither replaces the other.

To transfer, copy both exports to the new machine and retain the originals.
An archive utility lets you inspect the exported source and notes. For a few
exercises, copy that source into a fresh workspace and Save; this does not move
its full history or database. The optional [host-folder route](docker-beginners.md#keep-the-same-learning-folder-across-a-future-checkout)
has a different storage contract. Full database/volume restoration needs a
deliberate target and ownership checks; the export commands here do not import,
merge, or overwrite another classroom.

If you chose another Compose project, substitute its actual learning-volume
name and keep that project consistent throughout. Never include the private
`classroom-runtime` volume or a Kubernetes session in a learning backup.

## Troubleshooting and optional Kubernetes

Inspect startup without deleting data:

```text
docker compose -f compose.classroom.yaml --profile "*" ps -a
docker compose -f compose.classroom.yaml logs --tail 100 lab classroom-init postgres
```

If a port is already occupied, choose unused ports for this classroom. Create
or edit the plain-text `.env` file beside `compose.classroom.yaml`, preserving
any settings already present, and add these two lines:

```dotenv
DS60_LAB_PORT=8766
DS60_POSTGRES_PORT=55433
```

Then repeat the same `up` command and open <http://127.0.0.1:8766/classroom>.
These numbers are examples; choose other unused ports if necessary. The
PostgreSQL container publishes both the database and classroom ports because
they share a network namespace. An older course database can therefore hold
port8765 even when its web app is stopped. Keeping the same Compose project
and volume names preserves this classroom's work when changing its ports.

A worker health failure needs its service log, for example
`docker compose -f compose.classroom.yaml logs --tail 100 cpp-worker`.

Kubernetes remains an extra [owned host-preparation workflow](modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab)
with an expiring scoped lease. It is not created by these commands. No engine
socket is mounted into the ordinary app or its language workers. The optional
PowerShell/Bash launchers remain available for the existing host-folder route.

Command semantics checked against Docker's official [Compose profiles](https://docs.docker.com/compose/how-tos/profiles/),
[volume storage](https://docs.docker.com/engine/storage/volumes/) and
[file-copy reference](https://docs.docker.com/reference/cli/docker/container/cp/),
plus the [Compose merge requirements](https://docs.docker.com/reference/compose-file/merge/)
on 22 October 2026. Runtime qualification is recorded in the
[implementation checkpoint](implementation/CHECKPOINT.md).


## Java, JavaScript and TypeScript workers

These profiles use the same local progress volume as the other journeys. You
need Docker with Linux containers and Compose; no host Java, Node, TypeScript
or Python installation is needed. On Windows, use your engine's WSL 2 backend.
Run these single-line commands from the repository folder in PowerShell,
Command Prompt or a macOS/Linux terminal.

Build the classroom and the three language profiles, showing every build step:

```console
docker compose --progress plain -f compose.classroom.yaml --profile java21 --profile javascript-node --profile typescript-node --parallel 1 build
```

On a fresh engine, download the database image once, then start the classroom:

```console
docker compose -f compose.classroom.yaml pull postgres
docker compose -f compose.classroom.yaml --profile java21 --profile javascript-node --profile typescript-node up -d --no-build --pull never --wait
```

Open <http://localhost:8765/classroom>. Compose itself cannot open a host browser;
the shared and double-click launchers open it for the project's saved selection.
You can add the `--profile python-core` flag to both commands above to run
statistics and LLM examples alongside the language tracks. The `--wait` flag
checks actual worker startup probes. Read the last error if a service fails to
become healthy; do not repeatedly delete volumes to diagnose a build.

Java uses a prepared Java 21 compiler, saves the pad as `Main.java`, compiles to
`classes/`, and runs `Main` with assertions enabled. Keep `public class Main`
and omit a package declaration in this single-file pad. JavaScript uses Node24
ES modules saved as `main.mjs`. TypeScript uses `main.mts`, strict TypeScript5.9
checking and NodeNext module rules, then runs the emitted `compiled/main.mjs`.
Compilation errors prevent execution. The pad's **How this code runs** panel
explains the filename and lets you download the current source.

Node is a JavaScript host with filesystem and server APIs. Browser `document`
and `window` are different APIs. Browser DOM chapters disclose their separate
browser workflow and are not executed as if those APIs existed in Node.
External Java libraries and npm packages are not implicitly installed by a pad.
Runtime files are temporary; the saved source, notes and job receipts persist.

View running logs or stop the classroom while retaining progress:

```console
docker compose -f compose.classroom.yaml logs --follow lab java-worker javascript-worker typescript-worker
docker compose -f compose.classroom.yaml --profile java21 --profile javascript-node --profile typescript-node stop
```

Press Ctrl+C to leave the log view. Stopping containers retains local named
volumes. Do not use `down -v` unless you deliberately intend to erase their data.

### Reproducible language toolchain inputs

The Node and Java image recipes pin multi-architecture upstream manifest
digests. The TypeScript toolchain uses a checked-in npm lock with integrity
hashes for TypeScript5.9.3, Node24 types and their undici-types dependency.
The lock uses the TLS-verified Yarn registry mirror for the same upstream
package bytes. npm lifecycle scripts are disabled during installation. Network
access is needed while building; examples run offline after those images exist.
Java and Node run in separate private workers with the same bounded output,
scratch, deadline and cancellation rules as the other language profiles.


## NLP, fine-tuning and RAG classroom

Most NLP, retrieval, evaluation and statistics examples use `python-core`.
The small neural training, LoRA, preference and embedding-adaptation examples
use the CPU `llm-torch-cpu` profile. Build them with visible logs:

```console
docker compose --progress plain -f compose.classroom.yaml --profile python-core --profile llm-torch-cpu --parallel 1 build
```

After the initial database-image preparation above, start both profiles:

```console
docker compose -f compose.classroom.yaml --profile python-core --profile llm-torch-cpu up -d --no-build --pull never --wait
```

These default examples use small authored data, no paid API and no model-weight
download. They expose mechanisms on CPU, with explicit limits on what tiny
models demonstrate. The applied course's optional pretrained-model chapter
has a separate download, artifact verification and offline training workflow.
Its model assets and training outputs need the documented user-mounted folder;
temporary classroom job files are discarded after each run. Source drafts,
notes, read markers and job receipts persist in the learning volume.

To build every ordinary profile locally, including Java, Node, TensorFlow and
Spark, use this single-line command in any supported shell:

```console
docker compose --progress plain -f compose.classroom.yaml --profile "*" --parallel 1 build
```

This can download several gigabytes on a fresh engine. It builds local images
and does not push to a registry. Kubernetes retains its separate explicit owned
cluster preparation. You can keep the initial classroom small and add profiles
when a lesson needs them. The optional Makefile accepts, for example,
`make classroom-build CLASSROOM_PROFILES="python-core llm-torch-cpu"`.


## Optional Kubernetes inside the same classroom

Kubernetes uses a separately prepared, owned disposable kind cluster. It does
not attach to an existing personal or company cluster. Follow
[the Kubernetes runtime preparation guide](modules-runtime.md) for the pinned
host tools, local fixture image and owned-session workflow. That explicit host
preparation is separate from the Docker-only ordinary classroom and may need
host Python, kind and kubectl. Windows users run this companion inside WSL 2
with Linux paths and a Unix-socket Docker endpoint. Native Windows credential
preparation and named-pipe endpoints are unsupported.
The browser and worker never receive the Docker engine socket.

Finish tool preparation and all image builds before creating the fresh session.
Build the private broker directly from the repository root, so this build does
not require an existing lease path for Compose interpolation:

```console
docker build --progress=plain -f docker/kubernetes/Dockerfile.worker -t ds60sqlpy-worker-k8s-kind:0.4.0 .
```

The preparation guide also gives the fixture-image build and any explicitly
selected base-image override. Once these builds have succeeded, create the new
owned session immediately before starting the broker. Its scoped credential
lasts about 15 minutes; downloading or compiling after preparation can consume
that lease before the first lesson. If it expires, release that exact session
and prepare a new one. Do not edit its timestamps or reuse released credentials.

After preparation, set `DS60_K8S_SESSION_DIR` to the exact private session path
printed by the helper. In the same Linux, WSL 2 or macOS Bash terminal, use
`export DS60_K8S_SESSION_DIR="printed-path"`.
Never copy credential contents into the learning folder or a message.

Start the already built private broker in the same classroom and progress volume:

```console
docker compose -f compose.classroom.yaml -f compose.classroom.kubernetes.yaml --profile k8s-kind up -d --no-build --pull never --wait lab kubernetes-worker
```

This overlay preserves the ordinary worker endpoints and adds only the scoped
Kubernetes endpoint. It reuses the private classroom credential volume and
mounts the prepared lease/config read-only. It does not provision a cluster,
use an ambient kubeconfig, publish the worker port or install tools in the browser.
The current fixture0.2 operations support the curated hello Deployment/Service,
fixed ConfigMap inputs, finite task Job and fixed probe paths. Other Kubernetes
lessons explicitly identify their separate reading or owned host-lab workflow.

When finished, stop the broker and then release the exact owned session using
the preparation guide. Keep the private session path until release succeeds;
that receipt is how cleanup identifies the resources it owns.

```console
docker compose -f compose.classroom.yaml -f compose.classroom.kubernetes.yaml --profile k8s-kind stop kubernetes-worker
python scripts/prepare_kubernetes.py release --session "printed-path" --confirm-release
```

A normal classroom start without the overlay leaves Kubernetes unprepared.
Existing source drafts and receipts remain available for reading. Never use
`down -v` as a cluster cleanup shortcut; classroom volumes contain learning work.
