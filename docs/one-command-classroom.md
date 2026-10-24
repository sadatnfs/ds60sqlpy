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
through WSL 2**. It checks the engine and Compose version, prepares the database
image, builds the classroom and all ten ordinary workers with visible logs,
starts them in a controlled order, waits for health checks, verifies the web
page, and opens its actual local address. Repeat the same command to rebuild
changed sources and resume your saved work.

The command uses Bash, already available on macOS and in Ubuntu/WSL. Confirm
that `docker info` succeeds as your normal user before starting; engine access
permissions and WSL integration belong to the engine installation. The course
runtimes run inside Docker: you do not install Python, PostgreSQL, GCC, Java,
Node, TensorFlow, PyTorch or Spark on the host. First preparation needs internet
and several gigabytes of downloads. Allow room for images and build cache;
roughly 20 GB of free storage and 8 GB of engine memory is a practical starting
point for the full set. Actual requirements depend on the selected lessons.
For a smaller start, use `./classroom --starter`.

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

## What the default command prepares

| Runtime | Service |
| --- | --- |
| Python, NumPy, pandas, statistics and NLP | `python-core-worker` |
| C++20 compiler | `cpp-worker` |
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

The launcher uses the repository's pinned/public registry alternatives by
default, with TLS verification enabled. This handles the Docker Hub CDN issue
observed during local validation. Existing `.env` and shell overrides remain
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
uses its own volume. Port selection does not identify your progress. A database
container replacement can receive a new automatically assigned port; the
launcher opens the new address while the named volumes preserve your work.

The launcher supplies the mapped browser port to the container while retaining
one exact allowed Host and Origin. Do not configure arbitrary public hosts or
relax that check to fix a port error. Direct manual Compose operation should
use fixed ports; use `./classroom` for automatic port discovery.

The ignored `.classroom/` directory contains only launcher settings and a
transient lock. It is not the learning database and is excluded from images
and archives. The older host-folder `.learning` workflow remains a separate
storage route; follow the backup/transfer guidance before moving between them.

To request fixed host ports explicitly:

```sh
./classroom --port 8766 --database-port 55433
```

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

# Prepare Core plus selected language workers in one command.
./classroom --profile cpp20 --profile java21

# Resume prepared images without pulling or rebuilding.
./classroom --no-build

# Build without starting services.
./classroom build

# Check prerequisites without creating state or starting services.
./classroom doctor

# Inspect status or the recent app/database logs.
./classroom status
./classroom logs

# Stop this classroom while retaining every named volume.
./classroom stop
```

Starting a subset does not stop other workers that are already running. To
switch to a smaller running set, stop the classroom first and then start with
`--starter` or explicit `--profile` options. `--project NAME` intentionally
creates a separate project and learning volumes; use the same name on later
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
