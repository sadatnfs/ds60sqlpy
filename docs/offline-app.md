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

From the repository root, while connected for the build:

```text
docker compose --profile lab up --build
```

Wait for PostgreSQL to be healthy and the application startup message. Open [the local coding lab](http://127.0.0.1:8765/learn) using that exact address. The application validates its Host header. `localhost` is a different host label and is deliberately not an alias for this session.

The database and app share a container network namespace. The application reaches PostgreSQL through loopback rather than weakening the course database's local-target validation. Host ports are published only on `127.0.0.1`. The app runs as the unprivileged `learner` operating-system user, with dropped capabilities, a process limit, and a memory limit. This is a personal trusted-code environment, not a service for untrusted users or arbitrary submissions from the Internet.

The `postgres-data` named volume holds database data. The `learner-work` volume holds a persistent copy of the course and `.learning/` pads, progress, and evidence. Stop with Ctrl+C; start again with the same command or `docker compose --profile lab up`. Stop detached services with:

```text
docker compose --profile lab stop
```

Do not remove volumes to troubleshoot a lesson. Volume removal deletes saved work or database state. To back up work, copy `/workspace/.learning/` out of the app container before moving to another computer. Docker's [volume documentation](https://docs.docker.com/engine/storage/volumes/) explains persistence and backup.

The image uses the checked-in `uv.lock` and installs the Core profile. Building requires package/image downloads. Once both images and volumes are present, start the lab without downloading again. Heavy optional deep-learning, NLP, and geospatial dependencies are not included in the default image. A lesson's dependency label still applies. For a deliberately offline classroom, rehearse every selected lesson before disconnecting, following [offline preparation](setup/offline.md).

The app image does not automatically seed or reset SQL data. Start with `SELECT 1 AS first_result;`, then follow [PostgreSQL setup](setup/postgresql.md) to prepare the disposable training schema. The standalone beginner SQL lessons also include their own small temporary fixtures. Historical complete `.sql` scripts containing `psql` backslash commands run through the guided SQL notebook or terminal route; the SQL pad accepts SQL statements.

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
3. Write a prediction before running code. The pad uses a fresh process or connection for each submission. Python names do not persist between runs; saved code does.
4. Use `print()` and assertions to inspect Python results. Ordinary Matplotlib figures are captured as PNG images after execution. SQL result sets show a bounded table and a transcript; `NULL` is displayed explicitly.
5. Save your attempt and actual evidence. Hints come from the checked-in guide when available; the fallback asks you to inspect an input, result, or boundary. This offline guidance does not generate a personalized AI answer.
6. Reveal the worked solution only when you choose to compare. Record what changed in your understanding.
7. Explain the main idea without copying. After recording prediction, attempt, and explanation and confirming the check, record the lesson as demonstrated. Completion is self-reported evidence, not automatic grading.

Both pads save under `.learning/pads/<lesson-id>/`; coaching notes live in `.learning/coaching.json`. Progress uses `.learning/progress.json`, shared with the portal, CLI, and optional MCP server. Existing files are preserved. Switching lessons saves the current pad and evidence. Closing a tab with unsaved edits prompts you to save first.

The default Python run limit is 15 seconds, with bounded printed output. Long model training, interactive input, interactive plots, notebook magics, and advanced server exercises use the notebook/editor workflow described in their lesson. SQL has statement/lock timeouts and displays at most 100 rows per result set. Submissions use the database transaction by default; explicit transaction statements in your SQL change that boundary. Errors show the real exit status or SQLSTATE rather than silently counting as success.

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
| Python variables disappear | Each Run is a fresh process | Keep the complete small example in the pad or use the lesson notebook |
| SQL syntax error at `\` | Complete script contains `psql` commands | Run the complete script through its guided notebook, or copy one pure SQL query |
| `UndefinedTable` | SQLSTATE `42P01` and target database | Complete seed setup, or run the lesson's temporary fixture in the same submission |
| SQL backend unavailable | Interpreter's Psycopg import and local database | Follow the native or container authentication route; do not paste credentials into notes |
| Pad reaches the time limit | Workload and printed stop reason | Reduce the example; use the documented notebook workflow for long jobs |
| Route says a prerequisite is missing | Saved evidence for that stable ID | Demonstrate or review the prerequisite before recording completion |
| Old workspace lacks a new lesson | Workspace/catalog release | Start the new release in a new workspace and preserve old work |

See [MCP tutoring](mcp-tutor.md) for the optional Codex experience and [validation](validation.md) for the exact tested surfaces and remaining evidence boundaries.

## Limited database logins and existing Docker volumes

New Docker volumes initialize two separate roles. `ds60_admin` is the
bootstrap administrator; the application and SQL runner continue to use
`ds60`, a login with `NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION
NOBYPASSRLS`, no elevated predefined-role memberships, and ownership of only
the disposable `advanced_sql_training` database. The public local-course
passwords are `ds60_admin` and `ds60` respectively. Keep these development
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
its writers and back up any course state you want to keep. First inspect the
old login without changing it:

```text
docker compose exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -c "SELECT oid, rolsuper FROM pg_roles WHERE rolname='ds60';"
```

If its OID is **10**, this is PostgreSQL's bootstrap superuser. PostgreSQL does
not permit removing its `SUPERUSER` attribute, even from another administrator.
Use the [side-by-side migration](#bootstrap-role-volumes-side-by-side-migration)
below. Both administration scripts explicitly reject that case before changing
roles, ownership, passwords, or rows. Creating another administrator cannot
remove this PostgreSQL restriction.

For a non-bootstrap `ds60` role, read
`docker/admin/create-bootstrap-admin.sql` and
`docker/admin/upgrade-course-role.sql`. When ready, run these two explicit
commands from the repository root in PowerShell, macOS, or Linux:

```text
docker compose exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -f /opt/course-admin/create-bootstrap-admin.sql
docker compose exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60_admin -d advanced_sql_training -f /opt/course-admin/upgrade-course-role.sql
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
docker compose exec postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -f /opt/course-admin/verify-course-role.sql
```

Expect `ds60` and `advanced_sql_training` with no exception. Then restart the
app service if needed. Do not delete either named volume to perform this
upgrade. A failure about inherited memberships requires inspecting that
volume's role configuration, not bypassing the SQL pad's role guard.

### Bootstrap role volumes: side-by-side migration

Keep the original database volume. A new cluster with the corrected bootstrap
role lets restored course objects belong to the limited `ds60` login without
renaming the old bootstrap role or reassigning system catalogs. This is an
explicit migration you choose to perform, not something app startup executes.
The recipe below assumes the original default Compose project; add your original
`--project-name` to source commands if you used a different project name.

Freeze all writers first. Stop the old lab while retaining its database:

```text
docker compose stop lab
```

Choose unused archive directory names. The example date is only a label;
substitute a fresh name rather than reusing an existing backup directory.
Create an empty host directory. These commands intentionally fail if the final
directory already exists.

```powershell
# Windows PowerShell, repository root
if (-not (Test-Path work)) { New-Item -ItemType Directory -Path work | Out-Null }
New-Item -ItemType Directory -Path work\course-migration-20261022
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
docker compose exec -T postgres mkdir /tmp/ds60-course-migration-20261022
docker compose exec -T postgres pg_dump --username ds60 --dbname advanced_sql_training --format custom --file /tmp/ds60-course-migration-20261022/course.dump
docker compose cp postgres:/tmp/ds60-course-migration-20261022/course.dump work/course-migration-20261022/course.dump
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
project creates its own database and learner-work volumes:

```text
docker compose stop postgres
docker compose --project-name ds60-limited up -d postgres
```

Wait for the new database to become healthy, then copy the archive into the new
container and restore as the limited course owner:

```text
docker compose --project-name ds60-limited cp work/course-migration-20261022/course.dump postgres:/tmp/course.dump
docker compose --project-name ds60-limited exec -T postgres pg_restore --exit-on-error --single-transaction --no-owner --no-acl --username ds60 --dbname advanced_sql_training /tmp/course.dump
docker compose --project-name ds60-limited exec -T postgres psql -X -v ON_ERROR_STOP=1 -U ds60 -d advanced_sql_training -f /opt/course-admin/verify-course-role.sql
```

`--no-owner --no-acl` restores objects under the new limited owner rather than
copying the bootstrap owner's identity and grants. `--single-transaction`
makes a restore error roll back that restore. If custom extensions or other
administrator-only objects prevent a limited restore, stop and review those
objects; do not grant the new pad login global privileges. The old volume and
archive remain available. PostgreSQL documents these restore options in its
[pg_restore reference](https://www.postgresql.org/docs/17/app-pgrestore.html).

Compare your own table counts, selected identities, constraints, and business
control totals between the archive's source and the restored database before
calling the migration accepted. The repository's real PostgreSQL 17 rehearsal
restored an independent sentinel row with value 7, proved that its new table
owner is `ds60`, denied server-file access to that role, and verified unchanged
source role flags, database ownership, and sentinel contents. That rehearsal
is evidence for the supplied fixture, not acceptance of arbitrary learner data.

Only after verification, start the new project's lab:

```text
docker compose --project-name ds60-limited --profile lab up -d lab
```

The new project's learner workspace starts empty of personal progress. Keep the
old learner-work volume intact; copy evidence deliberately into unused target
paths or continue using a separately preserved workspace. Do not overwrite an
existing `.learning/` tree. If you need to return to the original database,
stop the new project with `docker compose --project-name ds60-limited stop`
and restart the original project's `postgres` service. Its original bootstrap
login remains administrative, so its SQL pad will still reject that login.
Do not remove either project's volumes until you have independently accepted
and backed up the new state.

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
tagging that image does not publish it. Once it is built and the public
PostgreSQL base is cached, start it without rebuilding or pulling:

```text
docker compose --profile lab up --detach --no-build --pull never
```

If another local PostgreSQL server already uses port 5432, select a different
host database port before starting the course stack:

```powershell
# Windows PowerShell
$env:DS60_POSTGRES_PORT = "58435"
docker compose --profile lab up --detach --no-build --pull never
```

```bash
# macOS/Linux
export DS60_POSTGRES_PORT=58435
docker compose --profile lab up --detach --no-build --pull never
```

The app still connects over the private shared namespace to port 5432; this
setting changes only the host's published database port. The browser address
remains `http://127.0.0.1:8765/learn`. Use a Docker-compatible local engine with
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
