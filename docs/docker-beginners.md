# Start the classroom with Docker

The classroom is a local website with lessons, coding pads, results and saved
progress. Docker supplies its Linux services and language tools. You do not
need to install Python, PostgreSQL or each compiler on your computer.
Windows runs the launcher in WSL 2; macOS and Linux use Terminal.

## 1. Prepare Docker once

Follow the guide for [Windows and WSL 2](setup/windows.md),
[macOS](setup/macos.md) or [Linux](setup/linux.md). Start your engine and keep
it running while using the classroom. Docker Desktop, Docker Engine and Rancher
Desktop with the **Moby** engine can provide the required Docker interface.
A Kubernetes cluster is not required for the classroom itself.

Open a terminal and check:

```bash
docker info --format '{{.OSType}}'
docker compose version
```

The first command must print `linux`; Compose must be at least **2.28.0**.
A client version alone does not show that the engine is running. See
[troubleshooting](troubleshooting.md) if either command fails.

## 2. Get the course folder

Clone the repository if you have access, or extract its Docker Starter ZIP
into a normal local folder. If the repository is private, cloning requires
access and authentication; a source archive does not bypass that requirement.
Open the folder containing `classroom`, `compose.classroom.yaml` and `README.md`.
Use `cd` in Terminal to enter that folder. On Windows, open Ubuntu in WSL 2;
the [Windows guide](setup/windows.md) explains paths and the optional launcher.

Do not run from inside the ZIP viewer. Keep this folder for future starts.
You can move it later, but keep the same Docker engine and project name to
reach the same saved work.

## 3. Choose your first preparation

For a smaller first download and build:

```bash
./classroom --starter
```

This prepares the website, PostgreSQL and the Python Core worker. Every subject
is visible and readable. Languages requiring another worker show what to
prepare before execution. HTML/CSS and browser JavaScript/D3 previews run in
your browser. To prepare all ordinary language/framework workers:

```bash
./classroom --all
```

First builds require internet, free disk and time. The terminal shows image
layers and package installation as they happen. Keep it open until the command
finishes. If a build stops, read its first useful error, correct the cause and
repeat the command; completed build layers can be reused. Nothing is published
to Docker Hub by these commands.

An **image** is the prepared software. A **container** runs that software.
A **volume** keeps your learning work or database after a container is stopped
or replaced. The source folder and images do not contain your saved progress.

## 4. Open the browser and complete one session

The launcher checks readiness, prints the classroom address and normally opens
it. If opening the browser is unavailable, copy the printed URL into your
browser. Use `./classroom status` to recover the current address. Avoid assuming
that a previous port number is still correct.

Choose a subject from **All learning paths**, then a lesson. Read its guide,
select the learner artifact, predict what it should do, edit the pad and run
it. Wait for the saved confirmation before closing. The
[first successful session](setup/first-success.md) walks through Python and SQL.
You can switch subjects without mixing their pads, notes or histories.

For HTML/CSS or browser JavaScript/D3, enable **Live preview** when you want
updates while typing. Preview observations are not saved runs until you choose
the explicit action. See [the classroom experience](classroom-experience.md).

## 5. Stop and return without rebuilding

```bash
./classroom stop
```

Next time, start your Docker engine, return to this folder and run:

```bash
./classroom resume
```

Resume uses local images and retained containers/volumes. It never builds or
pulls images. Ordinary `./classroom` also prefers existing resources and only
prepares missing images. Your selected profiles are remembered in
`.classroom/ds60-classroom/`.

If you used a custom project name, include it each time:

```bash
./classroom resume --project my-classroom
```

A different project or engine has different volumes. An apparently empty
classroom can mean the wrong project was opened, not that the work disappeared.

## 6. Add a language or install an update

For example, prepare C++ along with the Python Core baseline:

```bash
./classroom --profile cpp20
```

An explicit profile list replaces the saved selection; repeat `--profile` for
several workers or use `--all`. Previously saved work remains in the volume even
when its worker is not running. See [runtime profiles](docker-profiles.md).

After obtaining updated source files, deliberately rebuild local images:

```bash
./classroom --local-build --rebuild
```

Resume does not silently install source updates. If you intentionally selected
published Hub images, use the separate [Hub instructions](dockerhub.md).
A source release and the image tag you run should match.

## Keep a backup

Closing the browser or stopping containers preserves work. Removing volumes,
resetting the engine or replacing your computer can remove it. Export both the
learning volume and the PostgreSQL database using the
[backup guide](docker-classroom.md#5-export-learning-work-and-the-database).
Do not use `docker compose down -v` or global volume pruning as an ordinary stop.

The [one-command reference](one-command-classroom.md) explains image modes,
ports, projects and diagnostics. The [offline guide](setup/offline.md) explains
what to prepare before disconnecting. CUDA and owned Kubernetes labs have
additional explicit requirements; they are not part of ordinary startup.
