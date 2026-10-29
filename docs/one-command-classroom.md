# One command from source to a ready classroom

> **Classroom entrypoint:** the browser opens `/classroom`, where Python, PostgreSQL,
> the engineering bridge and every module/book subject share one home and
> individually themed workspaces with saved code and notes.
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
verifies the web page and opens its actual local address. Local-build mode
builds only missing images; saved Hub mode pulls missing selected images.
Ordinary startup uploads nothing. A new project selects the classroom and all ordinary workers
unless you choose `--starter` or specific profiles.

Repeat the same command to **resume your existing installation**. Updating the
source folder does not automatically rebuild installed images. Use
`./classroom --local-build --rebuild` when you deliberately want to install
updated local source. Published Hub images have their own update mode below.

The command uses Bash, already available on macOS and in Ubuntu/WSL. Confirm
that `docker info` succeeds as your normal user before starting; engine access
permissions and WSL integration belong to the engine installation. The course
runtimes run inside Docker: you do not install Python, PostgreSQL, GCC, Go,
.NET, Rust, Swift, Java, Node, PHP, R, Julia, Stan, TensorFlow, PyTorch or Spark
on the host. Polars, dbt and ML engineering dependencies are also prepared in
their dedicated images.
First preparation needs internet and downloads several large SDK and framework
images. For the full runtime set, budget about **80 GB of free disk**
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
observed. The product runs in Linux containers. Windows uses the same Bash launcher
inside its prepared WSL 2 distribution.

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
| Continue studying | `./classroom` | Resume the saved selection; prepare only missing images using the saved local/Hub mode |
| Continue without any downloads or builds | `./classroom resume` | Use existing containers/images or report missing preparation |
| Pause until later | `./classroom stop` | Stop project containers; retain all volumes and settings |
| Install changed local source files | `./classroom --local-build --rebuild` | Build selected local images and update containers while retaining volumes |
| Prepare local images for later | `./classroom build --local-build` | Build selected images without starting services |
| Download a configured Hub release for later | `./classroom pull` | Pull selected Hub images without starting services; requires saved Hub configuration |
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

The app serves the complete library, PostgreSQL stores the disposable course
database, and the ordinary workers provide the language/framework
runtimes. [Runtime profiles](docker-profiles.md) lists their exact names,
filenames and boundaries. HTML/CSS and browser JavaScript/D3 need only the app's
bundled preview. PHP uses its own CLI worker. Julia, native Stan, Polars and
real dbt have their declared ordinary profiles. A separate ML service or full
dbt/Stan project starts only through its documented project instructions.
See [the scientist roadmap](scientist-roadmap.md) for the learning routes.

Kubernetes cluster preparation, pretrained-model downloads and optional
NVIDIA GPU workers remain explicit workflows. GPU profiles are excluded from
`--all`; a CPU-only machine can still read the CUDA subject and run its CPU
models. Opening the classroom does not create a cluster, download model
weights or call a paid API.

A new project uses the repository's pinned/public registry alternatives by
default, with TLS verification enabled. The chosen registry mode is remembered
per project; it matters when an image needs preparation. Use it when the selected public base registry is the appropriate route for your network. Existing `.env` and shell overrides remain
in effect. To use ordinary upstream image defaults instead, run:

```sh
./classroom --registry upstream
```

A build log line marked `CACHED` means Docker reused an unchanged step. `RUN`
steps install the image's dependencies; `COPY` steps place the course sources
inside it. The image is saved to your local engine. No command pushes an image,
prunes caches or deletes a learning volume.

## Local builds and published Hub images

Local builds are the default. To install the current local source with visible
build logs, use:

```sh
./classroom --all --local-build --tag 1.0.1 --rebuild
```

### Install a combined CI release

Use a checkout or starter ZIP matching the published version. The default Hub
layout is the combined Linux AMD64/ARM64 release produced by the full
`[publish-docker]` GitHub workflow for marked pushes to main. After that full
1.0.1 workflow completes successfully, start it with:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.1
```

For a new Hub selection, you may omit `--tag`. The launcher resolves the
app's `latest` alias once, uses that concrete version for workers and saves
it. The accepted partial 1.0.0 App/Core plus JavaScript and TypeScript release
needs only its published profiles. Pin 1.0.0 explicitly after full latest moves:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

Python Core is included automatically. `--all` requires every ordinary
worker at the selected app version and fails if a partial release omitted
one. A missing worker never causes a local fallback build.

A completed full release uses `USER/ds60sqlpy:1.0.1` for the App and
workers use tags such as
`USER/ds60sqlpy:1.0.1-worker-python-core`. Docker selects the native architecture
from each index. Startup validates the resolved Linux platform and does not
fall back to local builds. Use `--starter` instead of `--all` for a smaller
installation. Private Hub repositories require Docker authentication.

For a new project using a completed full release, separate downloading from startup:

```sh
./classroom pull --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.1
./classroom resume
```

The project remembers profiles, namespace, layout and version. `resume` and
`--no-build` never pull, build or resolve latest. A later bare `./classroom` prepares only missing
images from the saved source. Pull-only preparation does not replace existing
containers.

### Pin latest to a concrete release

To select the current completed full CI release for a new Hub project:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER
```

When `latest` points to a partial release, use the selected-profile command
above instead of `--all`. The launcher resolves the app version and requires
a matching source checkout.
It then uses the corresponding immutable worker version tags and saves that
concrete release. A mismatch asks you to update the checkout or ZIP. Later
resume keeps that resolved version; it does not advance automatically.
`latest` is available only for the combined Hub layout.
Repeating `--from-hub` for the same saved namespace also keeps its pin. To
choose a newer completed release, use `--tag latest --rebuild` with the same
project and a matching checkout or ZIP.

### Choose a version for each image

`--tag VERSION` chooses the default app and worker release. Add repeatable
`--image-tag PROFILE=VERSION` options to select individual images, including
`app`. For example:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0 \
  --image-tag app=1.0.0 \
  --image-tag javascript-node=1.0.0 \
  --image-tag typescript-node=1.0.0
```

You may use `latest` for one image, such as
`--image-tag javascript-node=latest`. The launcher checks the worker's
published index metadata with Docker Buildx, then saves its concrete version.
Any different worker patch version must stay in the app's major.minor line
and share its qualified source revision. Current CI binds one checked-in
version to each revision, so its releases do not qualify mixing workers from
different versions. Missing or incompatible workers stop startup with saved
volumes intact. Strict resume uses saved versions without querying the registry.
To clear a saved worker pin, run
`./classroom --image-tag javascript-node=default --rebuild` with your
selected project. That worker
then inherits the app's version. Supplying a new `--tag VERSION` also resets
previous worker pins unless you repeat them.

### Publish through GitHub or from a local machine

Full GitHub publication runs only on a push to `main` with `[publish-docker]`
in the HEAD commit message. The targeted workflow accepts
`[build-test-ALIAS]` on a branch without uploading and
`[publish-ALIAS]` on `main` for a partial versioned release. Use exactly
one Docker marker. Publication uses repository secrets `DOCKERHUB_USERNAME`
and `DOCKERHUB_TOKEN`, with no extra enable variable or protected environment.
Native AMD64/ARM64 jobs stage and qualify the selected image set before
promoting completed version tags and then latest. The checked-in source
version controls the release; conflicting existing versions are not
overwritten. See
[the publication guide](dockerhub.md#5-github-actions-publication) before
creating a marked release commit.

The independent local publisher previews existing images:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.0.1
```

After local testing and preview review, add `--push` to upload that selection.
The operator handles `docker login` if needed. Missing selected images stop
preflight; the publisher does not build or authenticate. Its default is the
app plus all ordinary workers, with exact partial selection described in
[Docker Hub distribution](dockerhub.md).

Local publication provides one actual architecture and does not create
combined manifests. Consume its architecture tags explicitly:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.1 --architecture-tags
```

Publishing only ARM64 does not provide AMD64 images. Existing saved Hub
settings from older launcher versions retain their architecture-tag layout.
New explicit Hub selections default to combined tags unless
`--architecture-tags` is supplied.

### Apply an image update while retaining progress

Keep the same project and matching checkout when switching from local images,
changing tag layout, or applying a published release:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.0.1 --rebuild
```

Use the intended source release/version. For an intentional latest update,
obtain the matching checkout/ZIP and use `--tag latest --rebuild`.
In Hub mode, `--rebuild` pulls and applies images without compiling locally.
Strict resume cannot apply a changed source/version configuration.

Keep the same custom `--project NAME` on every command. A new project name
selects different volumes rather than moving progress. Return to local
development deliberately with `./classroom --local-build --tag 1.0.1 --rebuild`.
`--registry` controls public base-image sources for local preparation;
`--from-hub` selects published classroom images.

Images contain course/runtime files, not drafts, notes, receipts or database
state. Follow [backup and transfer](#backup-and-transfer) when moving machines
or upgrading. Neither local tests nor a configured workflow establish that
registry publication has completed; check the actual release tags and results.

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
`images.env` for local/Hub image selection and release, `classroom.url` for
the last ready address, and a transient launch lock. The
profile/registry selection, image-source settings and requested ports are saved before image
preparation; the ready URL is written only after the browser endpoint responds.
Existing projects without `selection.env` infer known profiles from their own worker containers;
if neither saved selection nor recognizable workers exists, the new-project
default applies. Explicit profile flags override the remembered selection.

These files are not the learning database or a backup. Keep this directory for
convenient restarts; deleting it does not delete Docker volumes, but can lose
profile or port preferences. It is excluded from images and archives. If you have an older host-folder `.learning` backup, keep it intact and
separate until a deliberate transfer has been verified. Startup does not
automatically merge it into a Docker volume.

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

# Install local source updates, retaining learning and database volumes.
./classroom --local-build --rebuild

# Build updated selected local images without starting services.
./classroom build --local-build

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
every optional profile you want in that selection. `--all` selects the full ordinary set.
A later bare `./classroom` reuses your last selection.

Starting a subset does not stop other workers that are already running. To
switch to a smaller running set, stop the classroom first and then start with
`--starter` or explicit `--profile` options. `--project NAME` intentionally
selects a separate project and learning volumes; use the same name on later
commands to resume that project.

## Backup and transfer

There are three separate things to retain:

| Item | What it preserves |
| --- | --- |
| Source folder or release ZIP | Lesson content, launch scripts and build instructions |
| Project learning-volume backup | Saved drafts, notes, source versions and run observations/receipts |
| PostgreSQL database dump | SQL tables and other database state |

The `.classroom/<project>/` folder stores selection and port preferences. It
helps you resume, but it is not a backup of learning data. A Docker image or Hub
pull also does not contain your saved progress.

Save your drafts, let active Runs finish, and follow the
[learning and database export procedure](docker-classroom.md#5-export-learning-work-and-the-database).
Use a new restore project to test recovery before replacing any existing
workspace. Exclude the private `classroom-runtime` credential volume from
learning exports. Keep original backups until the restored drafts, notes,
results and SQL data have been checked.

## When something fails

Read the first failed step. An unavailable engine calls for starting the engine;
a missing Docker command inside WSL calls for enabling distribution integration;
an old Compose version calls for updating Compose. The shared launcher requires **Compose 2.28.0 or newer**, including its
resolved-environment query. Use that same supported baseline for this course
even if an older Compose understands some individual configuration features.

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
