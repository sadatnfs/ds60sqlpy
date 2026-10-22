# The guided learning application

DS60 now has a working local coding environment in addition to its static course library. The application combines a prerequisite-aware route, the complete lesson guide, Python and PostgreSQL coding pads, saved work, progressive hints, an explicit solution reveal, and evidence notes. It runs in your browser while a local process handles storage and execution. There is no hosted application account or mandatory AI connection.

## Choose how to run it

| Route | What you install | What runs locally | Best fit |
| --- | --- | --- | --- |
| Docker Compose | Docker Engine with Compose, or Docker Desktop | Python environment, course app, and PostgreSQL | Consistent browser lab on Windows, macOS, and Linux |
| Source checkout | Supported Python and the course Core profile; PostgreSQL for SQL | The same browser app using your repository environment | Learners who want to inspect the source and use notebooks too |
| Native executable | A build for your operating system; a supported Python backend for pads; PostgreSQL for SQL | Bundled UI, catalog, lessons, and local server | A downloadable offline course with a separate native backend |
| Static library | A browser | Readable generated lessons and solutions | Reading without starting a server or running code |
| Codex MCP tutor | Codex plus the optional MCP dependency | Catalog-bound tutoring tools over stdio | Coaching with your own Codex connection |

The native executable contains its own application runtime. Its coding pads use an external Python environment so learners can install the dependencies their chosen lessons require. PostgreSQL is a separate backend. A basic pad does not replace an interactive Jupyter notebook, a database administration console, or a distributed compute service.

## Docker browser lab

Begin with the [Docker beginner walkthrough](docker-beginners.md) if installing
an engine, WSL 2, terminals, or container persistence is new. It covers Windows,
macOS, Linux, and a Docker-compatible local Rancher Desktop Moby engine.
The browser route requires no host Python, native PostgreSQL, or course package
installation. With the engine running, Windows users can double-click
`START_DOCKER_LAB.cmd`; Mac users can double-click
`START_DOCKER_LAB.command`. Terminal alternatives from the repository root are:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start
```

```bash
# macOS/Linux/WSL
bash scripts/docker_lab.sh start
```

The launcher builds when needed, starts the containers, waits for HTTP
readiness, and opens the host browser. Use the printed exact URL, normally
[the local coding lab](http://127.0.0.1:8765/learn). The app validates its Host
header. `localhost` is a different host label. For ports, a custom learning
folder, no-browser mode, or a deliberate rebuild, see the
[launcher examples](docker-beginners.md#7-stop-resume-and-rebuild-without-losing-progress).

Course files are copied from the current image into the replaceable container
workspace. Only the host learning folder is mounted at
`/workspace/.learning`. Its default is `.learning` inside the repository;
`--data-dir` on Bash/Python or `-DataDir` on PowerShell selects another absolute
host folder. Saved pads, history, evidence, and progress therefore survive
container replacement and can be reused by a future course image. The user
home for container settings/caches also lives under `.learning/home`.
Matplotlib uses reusable platform-specific font metadata under
`.learning/cache/matplotlib/`, so cache preparation can be reused across lessons
and future containers. Rendered plot images remain run output; save the code
and evidence needed to reproduce them.
[Backup and restore instructions](docker-beginners.md#8-back-up-and-restore-the-learning-folder)
cover copying that host folder while the app is stopped. Existing host data is
preserved. Older `learner-work` volumes require an explicit export into an
unused host folder; startup does not merge or overwrite learner evidence.

PostgreSQL stores tables separately in the project's `postgres-data` named
volume. The default project is `ds60-learning`, browser port 8765, and host
database port 55432. Inside the shared container network namespace the app uses
loopback port 5432, preserving the course database's exact local-target rule.
The fresh course login is `admin` / `admin`, with limited database privileges;
a separate bootstrap login owns cluster administration. The browser supplies
the course connection internally and needs no website account.

Use the same launcher with `stop` to pause services while preserving both
stores. Rebuild deliberately with `start --build` on Bash or `start -Build` in
PowerShell when updating the image. An image build does not replace the host
learning folder or publish an image. Container removal alone also preserves
the host folder; database volume deletion is a separate destructive operation.

The image uses `uv.lock` and includes Core dependencies plus PostgreSQL 17
client tools. Building needs downloads. Later starts reuse local images;
heavy deep-learning, NLP, and geospatial dependencies and first-use lesson
assets remain optional. Build the [optional Docker package profiles](docker-profiles.md)
you need explicitly; pressing Run does not install packages. Rehearse planned lessons while connected using
[offline preparation](setup/offline.md). For direct Compose without the
launcher, explicitly create the bind directory and pass the correct host UID
and GID as shown in the [manual route](docker-beginners.md#direct-compose-alternative-without-host-python).

The app does not seed or reset SQL automatically. Start with
`SELECT 1 AS first_result;`, then use the beginner lesson's temporary fixture
or explicitly prepare the course schema through the UI. Read the `RESET
TRAINING` acknowledgement before replacing seeded data. Use **Whole SQL lesson
(psql)** mode for a cataloged SQL file with its reviewed backslash directives
and relative includes. Keep those fixed directives intact. **SQL snippet** mode
accepts ordinary SQL statements through Psycopg. The guided SQL notebook and
terminal remain alternatives. The app runs trusted local learner
code, under the configured mapped user, and exposes no public classroom or
hosted submission service.

## Source application

Finish [the first-success setup](setup/first-success.md). On Windows, double-click `START_LEARNING_LAB.cmd`; it reuses the existing Windows discovery/bootstrap workflow and opens the coding application.

You can launch directly with the repository interpreter too.

```powershell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\learning_lab.py
```

```bash
.venv/bin/python scripts/learning_lab.py
```

A free loopback port is chosen. Keep the terminal open; Ctrl+C stops the server. Use `--no-browser` to print the URL without opening it. Use `--python` with an absolute executable path to choose a different supported backend. Never point the SQL backend at a shared or valuable database. `DS60_DATABASE_URL` uses the same exact local `advanced_sql_training` contract as the rest of the course.

`START_DS60.cmd` and `scripts/learning_portal.py` remain the reading/navigation and allowlisted editor-launch workflow. That portal does not acquire arbitrary execution endpoints. The coding lab is a separate, explicit entry point.

## Learn inside the application

1. Choose a goal and a realistic weekly time budget. **Build my route** expands actual catalog prerequisites and excludes saved completions. Time estimates exclude repeated attempts and review.
2. Read the guide beside the pad. Follow its prerequisites and the small worked examples. The full reader opens in another tab if you want the learner artifact and separate solutions together.
3. Write a prediction before running code. Each Run starts a fresh process or connection. Python cells within that one Run share names; names do not carry into the next Run. Saved code does.
4. Use `print()` and assertions to inspect Python results. Ordinary Matplotlib figures are captured as PNG images after execution. SQL result sets show a bounded table and a transcript; `NULL` is displayed explicitly.
5. Save your attempt and actual evidence. Hints come from the checked-in guide when available; the fallback asks you to inspect an input, result, or boundary. This offline guidance does not generate a personalized AI answer.
6. Reveal the worked solution only when you choose to compare. Record what changed in your understanding.
7. Explain the main idea without copying. After recording prediction, attempt, and explanation and confirming the check, record the lesson as demonstrated. Completion is self-reported evidence, not automatic grading.

Both pads save under `.learning/pads/<lesson-id>/`; coaching notes live in `.learning/coaching.json`. Progress uses `.learning/progress.json`, shared with the portal, CLI, and optional MCP server. Existing files are preserved. Switching lessons saves the current pad and evidence. Closing a tab with unsaved edits prompts you to save first.

### Python notebook cells and magics

**Run code** executes the current pad from the beginning. Loaded notebook
starters keep top-level `# %%` boundaries between their code cells. Within a
single Run, those cells execute in order in one fresh IPython namespace, so an
import or variable from an earlier cell is available to later cells. A new Run
starts over; it does not resume a persistent Jupyter kernel. Keep the dependency
chain you need in the pad. Ordinary Python scripts without cell markers or
IPython syntax keep normal script execution.

Line magics such as `%timeit` and cell magics such as `%%sql` are preserved.
Keep each cell-magic header and its body in the same marked cell. A syntax or
execution error stops subsequent cells and reports a submitted-source line when
available. IPython needs the selected backend's `notebooks` profile; Docker
Core includes it. Missing lesson packages still need their declared profile
and any explicit first-download preparation. See
[dependency profiles](dependency-profiles.md) and
[optional Docker profiles](docker-profiles.md). No package is installed by Run.

Static Matplotlib plots, including inline notebook figures, appear in the
output. Desktop GUI event loops, interactive `input()`, long-running services,
and jobs beyond the available budget use the notebook/editor workflow in their
lesson. These controls do not create a persistent kernel or an unbounded run.

### Run limits and SQL modes

Python and SQL snippets default to a 15-second run budget; whole SQL lessons
default to 60 seconds. **Run limit** offers 15, 60, or 120 seconds. Source and
printed output remain bounded at 60,000 and 128,000 UTF-8 bytes respectively;
stopping at a limit is reported as a stop, not successful completion.

SQL snippets use a fresh database connection, show at most 100 rows per result
set, and commit their current transaction on success. An error rolls back the
current transaction; explicit `COMMIT` or `ROLLBACK` statements establish their
own boundaries. Whole SQL mode uses guarded `psql` execution and console tables;
the script controls transaction boundaries, so earlier committed statements
can remain after a later failure. Both modes retain the disposable database
boundary and statement/lock limits. Use `BEGIN` and `ROLLBACK` for a temporary
fixture. Errors preserve the real exit status, traceback, or SQLSTATE.

## Build a native executable

Build on the operating system and CPU architecture you intend to distribute to. PyInstaller bundles are [specific to the build platform](https://pyinstaller.org/en/stable/operating-mode.html). Building a macOS executable does not produce a Windows executable or validate Windows behavior.

Install only the optional builder in a separate environment if you want a small application bundle:

```powershell
py -3.12 -m venv .app-build
& .\.app-build\Scripts\python.exe -m pip install ".[desktop-build]"
& .\.app-build\Scripts\python.exe scripts\build_app.py
& .\dist\DS60LearningLab.exe --self-check
```

```bash
python3.12 -m venv .app-build
.app-build/bin/python -m pip install '.[desktop-build]'
.app-build/bin/python scripts/build_app.py
./dist/DS60LearningLab --self-check
```

The equivalent Make target is `make app PYTHON=.app-build/bin/python`. Windows users do not need Make. Build output is ignored under `dist/`; intermediary payloads live under `build/`. The payload allowlist excludes Git history, credentials, package caches, notebooks' saved outputs, and learner state. Notebook source and separate solutions are included as course content.

Run the executable. Its first launch copies the bundled course into `~/DS60 Learning Lab/0.3/`, then opens the browser lab. A valid existing workspace is reused without overwriting learner edits. A nonempty unrelated directory is rejected. Use `--workspace` to select an empty directory or an existing DS60 course, or `--repo` to use a checkout. For a new course release, use a new workspace and copy evidence deliberately instead of silently replacing edited artifacts.

Point `--python` or `DS60_PYTHON` at the backend environment's Python, then install required lesson extras there. The build itself does not install PostgreSQL or mutate Codex settings. Native signing/notarization and public distribution remain release work; the development executable is unsigned.

The manual **Application builds** GitHub Actions workflow defines Windows, macOS, and Linux builds, bundle self-checks, and uploaded artifacts. A configured workflow is not a completed platform test; consult its actual run before distributing that platform's executable.

## Troubleshooting

| Symptom | Inspect | Repair |
| --- | --- | --- |
| No browser opens | Terminal URL and server process | Copy the printed exact loopback URL; keep the process open |
| `ModuleNotFoundError` in a pad | Backend path and selected lesson profile | Install the profile in that backend, not another Python environment |
| Python variables disappear | Each Run is a fresh process | Keep dependent cells together with their `# %%` boundaries; rerun the complete chain |
| A magic reports missing IPython | Selected backend's notebook packages | Install the `notebooks` profile in that backend; Docker Core already includes it |
| SQL syntax error at `\` | Mode and fixed script directives | Use whole SQL lesson mode for its cataloged script, or SQL snippet mode for ordinary SQL only |
| `UndefinedTable` | SQLSTATE `42P01` and target database | Complete seed setup, or run the lesson's temporary fixture in the same submission |
| SQL backend unavailable | Interpreter's Psycopg import and local database | Follow the native or container authentication route; do not paste credentials into notes |
| Pad reaches the time limit | Workload and printed stop reason | Reduce the example; use the documented notebook workflow for long jobs |
| Route says a prerequisite is missing | Saved evidence for that stable ID | Demonstrate or review the prerequisite before recording completion |
| Old workspace lacks a new lesson | Workspace/catalog release | Start the new release in a new workspace and preserve old work |

See [MCP tutoring](mcp-tutor.md) for the optional Codex experience and [validation](validation.md) for the exact tested surfaces and remaining evidence boundaries.

## Limited database logins and existing Docker volumes

New Docker volumes initialize two separate roles. `ds60_admin` is the
bootstrap administrator; the application and SQL runner use `admin`, a login
with `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS`, no elevated
predefined-role memberships, and ownership of only the disposable
`advanced_sql_training` database. Its course password is `admin`; the separate
bootstrap password is `ds60_admin`. The course role's name does not grant it
cluster-administrator capabilities. Keep these development
services bound to loopback. The app never uses the bootstrap administrator.
A limited database owner can create ordinary course objects and reset its own
course schema, but cannot run server-side programs or read server files using
administrative PostgreSQL capabilities. Optional role-administration lessons
retain their documented capability-check fallback.

The SQL pad rejects an administrative backend login even on a local database.
This check is separate from validating the database's name and host. Native
installations whose default PostgreSQL login is a superuser need a separate
limited pad login, described below. The course's explicit terminal or guided
administration lessons keep their existing capability rules.

PostgreSQL initialization scripts run only on an empty volume. Rebuilding the
app image does **not** demote a legacy `ds60` superuser, change a saved password,
or erase database data. For an existing disposable course volume, first stop
its writers and back up any course state you want to keep. The legacy source
examples explicitly use its former default project name, `ds60sqlpy`. Inspect
`docker compose ls` and substitute your real old project name if it differs.
First inspect the old login without changing it:

```text
docker compose --project-name ds60sqlpy exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -c "SELECT oid, rolsuper FROM pg_roles WHERE rolname='ds60';"
```

If its OID is **10**, this is PostgreSQL's bootstrap superuser. PostgreSQL does
not permit removing its `SUPERUSER` attribute, even from another administrator.
Use the [side-by-side migration](#bootstrap-role-volumes-side-by-side-migration)
below. Both administration scripts explicitly reject that case before changing
roles, ownership, passwords, or rows. Creating another administrator cannot
remove this PostgreSQL restriction.

The following legacy commands apply to old volumes whose course role was
named `ds60`, not a newly initialized `admin` volume. For a non-bootstrap
legacy `ds60` role, read
`docker/admin/create-bootstrap-admin.sql` and
`docker/admin/upgrade-course-role.sql`. When ready, run these two explicit
commands from the repository root in PowerShell, macOS, or Linux:

```text
docker compose --project-name ds60sqlpy exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -f /opt/course-admin/create-bootstrap-admin.sql
docker compose --project-name ds60sqlpy exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60_admin -d advanced_sql_training -f /opt/course-admin/upgrade-course-role.sql
```

The first command uses the old course administrator to create a separate
administrator if absent. An existing `ds60_admin` is preserved unchanged.
The second command must connect as that separate administrator; it refuses
self-demotion through `ds60`. It removes direct elevated memberships, rejects
unresolved inherited elevated memberships, and changes privileges and database
ownership in one transaction. It preserves the `ds60` password, application
pads, progress, and table rows. If your volume uses another administrator,
substitute that existing administrative login in the second command. If local
authentication has been customized, use your established password mechanism;
do not paste a password into a SQL file or commit it to the repository.

Verify through the limited course login:

```text
docker compose --project-name ds60sqlpy exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -f /opt/course-admin/verify-course-role.sql
```

Expect `ds60` and `advanced_sql_training` with no exception for that legacy
path. To keep using this explicitly selected legacy login with the new image,
set `DS60_COURSE_USER=ds60` and `DS60_COURSE_PASSWORD` to its existing local
password in your private Compose configuration. Fresh defaults are
`admin` / `admin`; changing defaults does not change stored passwords. Then
restart the app service if needed. Do not delete either named volume to perform this
upgrade. A failure about inherited memberships requires inspecting that
volume's role configuration, not bypassing the SQL pad's role guard.

### Bootstrap role volumes: side-by-side migration

Keep the original database volume. A new cluster with the corrected bootstrap
role lets restored course objects belong to the limited `admin` login without
renaming the old bootstrap role or reassigning system catalogs. This is an
explicit migration you choose to perform, not something app startup executes.
The source commands below explicitly name the old default project
`ds60sqlpy`. Confirm your original project with `docker compose ls`, and
substitute its actual name if different. The new launcher defaults to
`ds60-learning`, so a bare command could otherwise select a different project.

Freeze all writers first. Stop the old lab while retaining its database:

```text
docker compose --project-name ds60sqlpy stop lab
```

Choose unused archive directory names. The example date is only a label;
substitute a fresh name rather than reusing an existing backup directory.
Create an empty host directory. These commands intentionally fail if the final
directory already exists.

```powershell
# Windows PowerShell, repository root
if (-not (Test-Path work)) { New-Item -ItemType Directory -Path work | Out-Null }
New-Item -ItemType Directory -Path work\course-migration-20261022 -ErrorAction Stop
```

```bash
# macOS/Linux, repository root
mkdir -p work
mkdir work/course-migration-20261022
```

Write a single-database custom archive inside the old container, then copy it
as a binary file. No shell redirection or text pipe touches the archive, which
keeps this procedure usable in Windows PowerShell as well as POSIX terminals.
The container-side `mkdir` also refuses an existing destination:

```text
docker compose --project-name ds60sqlpy exec -T postgres mkdir /tmp/ds60-course-migration-20261022
docker compose --project-name ds60sqlpy exec -T postgres pg_dump --username ds60 --dbname advanced_sql_training --format custom --file /tmp/ds60-course-migration-20261022/course.dump
docker compose --project-name ds60sqlpy cp postgres:/tmp/ds60-course-migration-20261022/course.dump work/course-migration-20261022/course.dump
```

The archive contains course data and may contain any personal data you added.
Keep it private under ignored `work/`. Do not commit it or import cluster roles.
The original database's passwords, objects, and rows remain unchanged. Preserve
your existing `learner-work` volume and its `.learning/` directory separately;
a database dump does not contain saved pads, evidence, or progress.

For the cutover, stop the old database container to free its published ports,
without deleting containers' volumes. Choose a **new, unused** target Compose
project name; `ds60-limited` below is an example. If containers or volumes
already exist for that name, choose another name before continuing. The new
project creates its own database volume. Keep its learning-folder choice
explicit; do not overwrite or merge an existing host `.learning` tree:

```text
docker compose --project-name ds60sqlpy stop postgres
docker compose --project-name ds60-limited up -d postgres
```

Wait for the new database to become healthy, then copy the archive into the new
container and restore as the limited course owner:

```text
docker compose --project-name ds60-limited cp work/course-migration-20261022/course.dump postgres:/tmp/course.dump
docker compose --project-name ds60-limited exec -T postgres pg_restore --exit-on-error --single-transaction --no-owner --no-acl --username admin --dbname advanced_sql_training /tmp/course.dump
docker compose --project-name ds60-limited exec -T postgres psql -X -v ON_ERROR_STOP=1 -U admin -d advanced_sql_training -f /opt/course-admin/verify-course-role.sql
```

`--no-owner --no-acl` restores objects under the new limited owner rather than
copying the bootstrap owner's identity and grants. `--single-transaction`
makes a restore error roll back that restore. If custom extensions or other
administrator-only objects prevent a limited restore, stop and review those
objects; do not grant the new pad login global privileges. The old volume and
archive remain available. PostgreSQL documents these restore options in its
[pg_restore reference](https://www.postgresql.org/docs/17/app-pgrestore.html).

Compare your own table counts, selected identities, constraints, and business
control totals between the source and restored database before accepting the
migration. The source volume stays intact, and restoration must pass through
the limited course owner without global privilege grants. PostgreSQL dump
files do not contain learner pads, progress, or private evidence notes.

Only after verification, start the new project's lab using its new or
explicitly selected host learning folder. The shell launchers prepare that
bind mount and your user identity:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\docker_lab.ps1 start -Project ds60-limited -DataDir "C:\Users\Ada\Documents\DS60 migrated learning"
```

```bash
# macOS/Linux/WSL
bash scripts/docker_lab.sh start --project ds60-limited --data-dir "$HOME/DS60 migrated learning"
```

Replace the example path with your actual user-owned target folder. Export
old `/workspace/.learning` into a separate unused host folder before retiring
its old container; retain the original `learner-work` volume until the exported
files are verified. Reuse a preserved working copy through `--data-dir` or
`-DataDir` rather than overwriting another active learning folder. For details,
see [backing up learning work](docker-beginners.md#8-back-up-and-restore-the-learning-folder).

To return to the original database, stop the new project with
`docker compose --project-name ds60-limited stop` and restart the original
project's `postgres` service. Its original bootstrap login remains
administrative, so the SQL pad still rejects it. Do not remove either project's
volumes until you have independently accepted and backed up the new state.

For a native installation, connect once through your local administrator and
create a separate login using an interactive `psql` session:

```sql
CREATE ROLE ds60_pad LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
  NOREPLICATION NOBYPASSRLS;
\password ds60_pad
GRANT CONNECT, CREATE, TEMPORARY ON DATABASE advanced_sql_training TO ds60_pad;
```

The `\password` command prompts interactively; credentials stay out of SQL
source. Configure the backend's normal local authentication as documented in
[PostgreSQL setup](setup/postgresql.md), and set `DS60_DATABASE_URL` to the local
course target using the `ds60_pad` login. For example, the target without an
embedded password is
`postgresql://ds60_pad@127.0.0.1:5432/advanced_sql_training`; use your normal
private PostgreSQL password file or existing local authentication policy.
The standalone beginner fixtures work with temporary tables under this role.
To query an already seeded `training` schema owned by another local role, its
owner can explicitly grant read access:

```sql
GRANT USAGE ON SCHEMA training TO ds60_pad;
GRANT SELECT ON ALL TABLES IN SCHEMA training TO ds60_pad;
```

Those read grants do not transfer schema ownership or authorize resetting
another role's objects. Keep schema preparation under the course schema owner,
or deliberately create a separate disposable course installation owned by the
limited role. The app reports an ownership failure instead of escalating the
pad login automatically.

## Concurrent progress and evidence storage

The app, portal, CLI, and optional MCP service may open the same workspace.
Progress and coaching mutations hold a shared operating-system file lock for
the entire read, change, and atomic-replace operation. Each write uses a unique
temporary file, so one service cannot replace another service's scratch file.
Reads create neither `.learning/` nor a lock file. Explicit mutations may leave
small `progress.json.lock` and `coaching.json.lock` anchors, including after a
progress reset. Keep these files in place while services can access the
workspace; deleting a lock anchor can break coordination between processes.
They contain no learner notes. These advisory locks are intended for local
course workspaces; synchronize or back up a closed workspace when moving it
between computers instead of concurrently editing a network-mounted copy.

## Local image names, ports, and Rancher Desktop

Compose builds the application as the local image `ds60sqlpy-lab:0.3.0`. Its
`pull_policy: never` prevents an application-image registry pull. Building or
tagging that image does not publish it. Once it is built and the public PostgreSQL base is cached, use the shell
launcher for an ordinary start. A manual Compose start additionally needs the
[bind-directory and user-identity setup](docker-beginners.md#direct-compose-alternative-without-host-python)
in the current terminal. With that setup in place, start without rebuilding
or pulling:

```text
docker compose --profile lab up --detach --no-build --pull never
```

The course defaults to host database port 55432. If that port is occupied,
select a different host database port before starting the course stack:

```powershell
# Windows PowerShell
$env:DS60_POSTGRES_PORT = "55433"
docker compose --profile lab up --detach --no-build --pull never
```

```bash
# macOS/Linux
export DS60_POSTGRES_PORT=55433
docker compose --profile lab up --detach --no-build --pull never
```

The app still connects over the private shared namespace to port 5432; this
setting changes only the host's published database port. The browser address
remains `http://127.0.0.1:8765/learn` unless you change `DS60_LAB_PORT`. Use a Docker-compatible local engine with
Compose. For Rancher Desktop, verify that its local Moby engine is running
with `docker info` and `docker compose version`. Inspect the selected context
and endpoint before using a machine that also has remote Docker contexts.

### A TLS-verified fallback for a blocked Docker Hub CDN

Some networks can verify GitHub's registry and Google's public mirror while
rejecting Docker Hub's CDN certificate chain. Keep TLS verification enabled.
When those alternative endpoints are trusted and available, the Dockerfile's
`DS60_BASE_IMAGE` argument permits this explicit local build:

```text
docker pull ghcr.io/astral-sh/uv:python3.12-bookworm-slim
docker pull mirror.gcr.io/library/postgres:17
docker image tag mirror.gcr.io/library/postgres:17 postgres:17
docker compose --profile lab build --build-arg DS60_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim lab
docker compose --profile lab up --detach --no-build --pull never
```

The Python base is published by the [official uv project](https://docs.astral.sh/uv/guides/integration/docker/).
Google documents `mirror.gcr.io` as a [managed cache of public Docker Hub images](https://docs.cloud.google.com/artifact-registry/docs/pull-cached-dockerhub-images).
The tag operation above changes a local name; it does not upload an image.
No daemon restart, global registry mirror setting, or insecure registry is
required for this route. A cache may not contain every public image. If an
endpoint still fails certificate verification, resolve that endpoint's trust
with your network administrator rather than disabling verification.

The default Dockerfile base remains `python:3.12-slim-bookworm`. Dependency
installation is cached separately from the course files, and the final source
installation runs offline against the already installed build tooling. A
curriculum or guide edit therefore does not require downloading all Core
packages again.

The image installs `postgresql-client-17` from the PostgreSQL project's
[signed Debian package repository](https://www.postgresql.org/download/linux/debian/),
matching the PostgreSQL 17 course server. This repository/key setup exists
inside the image; it does not change the host's package sources or trust store.

## Package the Windows starter

The Windows starter is a complete source ZIP with `START_DOCKER_LAB.cmd` at
its entry point. A learner extracts it and double-clicks that file; Git and
host Python are not required. The first-run Windows wizard checks the engine
and prerequisites before handing over to the normal Docker launcher. Windows
installation consent, UAC, or a required restart remain visible steps. See the
[beginner Windows walkthrough](docker-beginners.md#windows-start-with-the-first-run-wizard).

Maintainers can build the ZIP on any supported development OS:

```bash
python scripts/build_windows_starter.py
```

Or use `make windows-starter` on macOS/Linux. The archive is written to
`dist/DS60LearningLab-0.3.0-Windows-Starter.zip`. Packaging checks the generated
readers, includes the authored course and Docker build files, and excludes
local progress, environments, authentication files, and symlinks. The
application-build workflow also produces this starter as a downloadable CI
artifact. It does not publish a release or push an image.

## Watch a local image build

Run a build in the foreground with plain progress output:

```bash
BUILDKIT_PROGRESS=plain bash scripts/docker_lab.sh build
```

The terminal shows the Dockerfile steps, package installation, and cache hits.
The command builds the local image and does not start services or push it.
Cached steps report `CACHED`; this is expected after a successful build. To
inspect a completely fresh dependency installation, use the direct Compose
command `docker compose --progress plain --profile lab build --no-cache lab`.
This reruns dependency installation, so it takes longer. BuildKit's separate
package-download caches can still avoid downloading every package again.

On a network that requires the verified alternate base above:

```bash
DS60_BASE_IMAGE=ghcr.io/astral-sh/uv:python3.12-bookworm-slim BUILDKIT_PROGRESS=plain bash scripts/docker_lab.sh build
```

Windows PowerShell uses the same plain-output environment setting:

```powershell
$env:BUILDKIT_PROGRESS = 'plain'
.\scripts\docker_lab.ps1 build
```
