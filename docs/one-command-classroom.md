# One command from source to a ready classroom

> **One classroom:** the browser opens `/classroom`, where Python, PostgreSQL,
> the engineering bridge and every module/book subject share one home and
> individually themed workspaces. Choose any path and set your own pace.
> Start with `./classroom`; see the [classroom guide](classroom-experience.md) for reading, code,
> saved work and compatibility bookmarks.


After Docker is installed and running, open a terminal in the extracted course
folder or repository and run:

```sh
./classroom
```

That is the complete ordinary startup command on **macOS, Linux and Windows
through WSL 2**. It checks the engine and Compose version, reuses the current
project's saved selection, starts existing containers, waits for health checks,
verifies the web page and opens its actual local address. It builds only missing
images. A new project selects the classroom and all fifteen ordinary workers
unless you choose `--starter` or specific profiles.

Repeat the same command to **resume your existing installation**. Updating the
source folder does not automatically rebuild installed images. Use
`./classroom --rebuild` when you deliberately want to install those updates.

The command uses Bash, already available on macOS and in Ubuntu/WSL. Confirm
that `docker info` succeeds as your normal user before starting; engine access
permissions and WSL integration belong to the engine installation. The course
runtimes run inside Docker: you do not install Python, PostgreSQL, GCC, Go,
.NET, Rust, Swift, Java, Node, TensorFlow, PyTorch or Spark on the host.
First preparation needs internet and downloads several large SDK and framework
images. For the full fifteen-worker set, budget about **60 GB of free disk**
for images, dependencies and build cache, and start with **8 GB of engine
memory**. This is planning guidance, not a measured minimum or a guarantee:
architecture, selected profiles and retained builds change storage use.
Check both your host's free space and the engine VM's available disk before a
full build. If space is limited, use `./classroom --starter`, then add only the
profiles you need. Never remove learning volumes to recover build-cache space.

## Windows: the same command in WSL 2

1. Install WSL 2 with a normal Linux distribution such as Ubuntu. Microsoft's
   [WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install)
   covers the one-time administrator/reboot steps. Complete Ubuntu's first-run
   username setup. The course launcher does not install or reset distributions.
2. Start your Docker-compatible engine in Linux-container mode. For Docker
   Desktop, enable its WSL 2 backend and integration for **your Ubuntu
   distribution**, following [Docker's WSL guide](https://docs.docker.com/desktop/features/wsl/).
   For Rancher Desktop, use its Moby engine and enable the distribution's
   [WSL integration](https://docs.rancherdesktop.io/ui/preferences/wsl/integrations/). Do not install a competing daemon inside Ubuntu merely because
   the engine integration is disabled.
3. In the Ubuntu terminal, `docker info` and `docker compose version` should
   succeed. Open the extracted repository directory, then run `./classroom`.
   A Windows path such as `C:\Users\Ada\Downloads\DS60LearningLab` is usually
   `/mnt/c/Users/Ada/Downloads/DS60LearningLab` inside Ubuntu. Quote paths with
   spaces. A checkout in Ubuntu's Linux filesystem is also supported.

From Windows Explorer you may instead double-click
**START_DOCKER_CLASSROOM.cmd**, or run `classroom.cmd` in Command Prompt. This
thin wrapper invokes the same Bash entrypoint through the default WSL
distribution. Set Ubuntu as your default distribution when necessary, using
Microsoft's [WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands).
The wrapper preserves the selected course directory; it does not maintain a
second Windows implementation of the build workflow. On Mac, double-click
**START_DOCKER_CLASSROOM.command** if you prefer a launcher to a terminal.

A Docker Desktop WSL backend alone does not imply that a user Ubuntu shell and
its Docker integration are ready. The distinction matters for the Windows
wrapper. If Windows execution is blocked by installation policy, follow your
organization's approved setup route. WSL installation and engine integration
cannot be established by a macOS run; the release report states what was
observed. The product runs in Linux containers. Native Windows Python backends
and executable bundles are outside the supported route and release gates.

## Resume, recover or update

Start the same Docker engine, open the same source folder and run:

```sh
./classroom
```

For a project whose required containers already exist with the same settings,
the launcher reuses them without building or pulling images. Already running
containers stay running. Docker can assign new automatic host ports when a
stopped database container starts, even though that container keeps its ID. If
the browser port changes, the launcher recreates only the app from its existing
image so its exact allowed browser address remains correct. Database and worker
containers retain their IDs; named volumes retain all saved work.

If a container is missing but its image exists, the launcher recreates it using
the same project volumes. If an image is missing, ordinary startup prepares only
the missing image and its required build dependencies.

For a strict return to prepared local images, use:

```sh
./classroom resume
```

This is equivalent to `./classroom --no-build`: it never builds or pulls. It can
recreate a missing container from its existing image. If preparation is
incomplete, it reports what is missing and stops. To finish an interrupted first
build instead, use ordinary `./classroom`. The selected profiles, registry mode
and requested ports are saved before preparation starts, and completed images
are reused.

| Your intention | Command | Effect |
| --- | --- | --- |
| Continue studying | `./classroom` | Resume the saved selection; build only missing images |
| Continue without any downloads or builds | `./classroom resume` | Use existing containers/images or report missing preparation |
| Pause until later | `./classroom stop` | Stop project containers; retain all volumes and settings |
| Install changed source files | `./classroom --rebuild` | Rebuild the selected images and update containers as needed |
| Prepare updated images for later | `./classroom build` | Build selected images without starting services |
| Prepare every ordinary runtime | `./classroom --all` | Save the full selection and prepare its missing images |

A source, container configuration or deliberate port-setting change uses the
explicit `--rebuild` update path. Named volumes retain your work through that
update. An automatically reassigned browser port is different: the launcher
repairs only the app from its prepared image without a build or pull, including
in strict `resume` mode. If the database container itself was removed, the app's
shared network connection also needs this targeted repair. Use the newly printed
URL after an automatic port changes.

The default project is `ds60-classroom`. If you originally used a custom name,
repeat that name on every command:

```sh
./classroom resume --project my-study
./classroom status --project my-study
./classroom stop --project my-study
```

The launcher does not guess among unrelated projects. A different project name
selects different volumes, even when its images are the same.

## What a new default project prepares

| Runtime | Service |
| --- | --- |
| Python, NumPy, pandas, statistics and NLP | `python-core-worker` |
| C++20 compiler | `cpp-worker` |
| C17 compiler | `c-worker` |
| Go compiler and prepared standard library | `go-worker` |
| C# and .NET compiler/runtime | `csharp-worker` |
| Rust compiler and prepared Arrow dependency | `rust-worker` |
| Swift 6 Linux/Foundation compiler | `swift-worker` |
| Java compiler and JVM | `java-worker` |
| JavaScript with Node | `javascript-worker` |
| Strict TypeScript compilation | `typescript-worker` |
| TensorFlow on CPU | `tensorflow-worker` |
| PyTorch and tensor-based LLM lessons | `llm-worker` |
| Scala/JVM | `scala-worker` |
| Spark with Scala | `spark-scala-worker` |
| PySpark | `spark-python-worker` |

Kubernetes cluster preparation and optional pretrained-model downloads remain
explicit lesson workflows. Opening the classroom does not create a cluster,
download model weights or call a paid API. The ordinary lessons are usable
offline after their images and local fixtures are prepared.

A new project uses the repository's pinned/public registry alternatives by
default, with TLS verification enabled. The chosen registry mode is remembered
per project; it matters when an image needs preparation. This handles the
Docker Hub CDN issue observed during local validation. Existing `.env` and shell overrides remain
in effect. To use ordinary upstream image defaults instead, run:

```sh
./classroom --registry upstream
```

A build log line marked `CACHED` means Docker reused an unchanged step. `RUN`
steps install the image's dependencies; `COPY` steps place the course sources
inside it. The image is saved to your local engine. No command pushes an image,
prunes caches or deletes a learning volume.

## Ports and saved work

For a new project without explicit port settings, Docker selects available
**loopback-only** host ports. The application keeps its fixed internal port;
the launcher reads the actual published address after startup. It prints the
URL even if browser opening is unavailable, and saves it in
`.classroom/<project>/classroom.url`. You do not need to guess port 8765 or stop
another application that already uses it.

A repeat start keeps the same project and its Docker volumes. Saved pads,
notes, progress and job history live in the learning volume, while PostgreSQL
uses its own volume. Port selection does not identify your progress. Docker can
assign new automatic host ports when a stopped database container restarts,
without replacing that container. The launcher opens the new address and, when
the browser port changes, recreates only the app from the same existing image.
This repair does not rebuild images or touch learning volumes. Replacing a
missing database container can also change its automatic ports.

The launcher supplies the mapped browser port to the container while retaining
one exact allowed Host and Origin. Do not configure arbitrary public hosts or
relax that check to fix a port error. Direct manual Compose operation should
use fixed ports; use `./classroom` for automatic port discovery.

The ignored `.classroom/<project>/` directory contains `selection.env` for the
selected runtime profiles and registry mode, `ports.env` for host-port choices,
`classroom.url` for the last ready address, and a transient launch lock. The
profile/registry selection and requested ports are saved before image
preparation; the ready URL is written only after the browser endpoint responds.
Existing projects without `selection.env` infer known profiles from their own worker containers;
if neither saved selection nor recognizable workers exists, the new-project
default applies. Explicit profile flags override the remembered selection.

These files are not the learning database or a backup. Keep this directory for
convenient restarts; deleting it does not delete Docker volumes, but can lose
profile or port preferences. It is excluded from images and archives. The older
host-folder `.learning` workflow remains a separate storage route; follow the backup/transfer guidance before moving between them.

To request fixed host ports explicitly:

```sh
./classroom --port 8766 --database-port 55433
```

For an existing project, changing its ports needs the explicit update path:

```sh
./classroom --rebuild --port 8766 --database-port 55433
```

Those choices are remembered. Later `./classroom` or `./classroom resume` starts
keep the stable browser address and reuse all existing container IDs when the
configuration is unchanged. This avoids the app-only repair needed if an
automatically assigned browser port changes. The chosen fixed ports must remain
available; the launcher does not stop another application to claim them.

Command-line options take precedence for that run. Explicit shell/`.env` port
settings take precedence over saved launcher settings on later runs. The
launcher never rewrites `.env`. `DS60_CLASSROOM_PORT` controls the browser's
host port; `DS60_LAB_PORT` remains the app's internal port. Existing
`DS60_LAB_PORT` settings also remain a supported fixed-host-port fallback.
Use `--port 0 --database-port 0` for automatic selection when an explicit port
is busy. The launcher reports a failure and retains volumes instead of stopping
an unrelated service to obtain that port.

## Useful variations

```sh
# A lightweight first study session.
./classroom --starter

# Select Core plus C++ and Java; remember that selection for later starts.
./classroom --profile cpp20 --profile java21

# Select every ordinary runtime, including ones not prepared earlier.
./classroom --all

# Resume the saved selection without pulling or rebuilding.
./classroom resume

# Install source updates, retaining learning and database volumes.
./classroom --rebuild

# Build updated selected images without starting services.
./classroom build

# Check prerequisites without creating state or starting services.
./classroom doctor

# Inspect status or the recent app/database logs.
./classroom status
./classroom logs

# Stop this classroom while retaining every named volume.
./classroom stop
```

`--starter` replaces the remembered selection with Python Core. Explicit
`--profile` flags replace it with Core plus exactly the listed profiles; include
every optional profile you want in that selection. `--all` selects all fifteen.
A later bare `./classroom` reuses your last selection.

Starting a subset does not stop other workers that are already running. To
switch to a smaller running set, stop the classroom first and then start with
`--starter` or explicit `--profile` options. `--project NAME` intentionally
selects a separate project and learning volumes; use the same name on later
commands to resume that project.

## When something fails

Read the first failed step. An unavailable engine calls for starting the engine;
a missing Docker command inside WSL calls for enabling distribution integration;
an old Compose version calls for updating Compose. The shared launcher requires **Compose 2.28.0 or newer**, including its
resolved-environment query. Manual Compose files alone require 2.24.4 for
reset/override tags.

Build and startup failures stop the workflow before it opens a browser. No
failed command silently deletes data. Fix the indicated problem and rerun the
same command. Ctrl+C cancels the launcher and releases its own lock. A second
launcher for the same project refuses a concurrent start; rerun it after the
first finishes. It does not race two database initializers. A stale lock from
a terminated process is reclaimed only when its recorded process is absent and
its lock directory contains no unexpected files. Recovery has its own atomic
lock, so two simultaneous restarts cannot remove each other's ownership. If a
process is terminated during recovery and leaves a recovery lock, inspect it
before retrying; the launcher preserves ambiguous state.

A full backup of the learning volume preserves saved code, notes, progress,
source versions and recorded run output. Python and SQL receipts live under
`classroom-runs` in that volume and appear in the shared **Saved runs** view.
Opening a prior receipt displays its recorded source and output without
re-executing it or replacing your pad. Source version history remains separate
from execution history. The older completion-JSON export contains completion
markers only; use the complete learning-volume backup when transferring your
whole workspace, and back up PostgreSQL separately when you need its state.

For backup, manual Compose operation and optional host labs, continue to the
[full classroom reference](docker-classroom.md). Direct Compose remains an
advanced alternative; use the single entrypoint when you want it to handle the
image, readiness and URL steps together.
