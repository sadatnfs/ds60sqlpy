# Linux setup

The primary course experience is the unified Docker classroom. Every subject,
including Python and SQL, opens from the same `/classroom` page. You only need
a local Docker-compatible engine, Linux containers, and the documented Compose
version. The language runtimes live inside the images.


From the extracted course folder or checkout, run:

```sh
./classroom
```

The command builds locally, starts the services, checks readiness and opens the
actual browser address. Follow the [one-command walkthrough](../one-command-classroom.md)
for first-time engine installation, WSL integration, stopping, backups and
recovery. Saved work in the standard classroom uses persistent named Docker
volumes. Use `./classroom status` to rediscover its address.

## Optional native environment

The remainder of this page is for learners who also want host Python, Jupyter,
VS Code or PostgreSQL. These installations are not classroom prerequisites.
Keep a native environment's `.learning` files separate from Docker-volume state.

## 1. Install base tools

On a distribution that provides Python 3.12:

```bash
sudo apt-get update
sudo apt-get install -y git libgomp1 python3.12 python3.12-venv python3-pip
git --version
python3.12 --version
```

These package names fit Ubuntu 24.04. Check `cat /etc/os-release` first;
Debian 12 normally supplies supported Python 3.11 instead, so use `python3.11`
and its matching `python3.11-venv` package. A newer distribution's default
Python may be outside 3.11-3.12. Install a supported interpreter alongside it
with your distributor's packages or [uv's Python management](https://docs.astral.sh/uv/guides/install-python/).
Do not use `sudo pip`, `--break-system-packages`, or replace `/usr/bin/python3`.

Install [Visual Studio Code](https://code.visualstudio.com/docs/setup/linux) through the supported package for your distribution.

If your distribution does not provide Python 3.12, use a current vendor package or a Python version manager. Do not replace the distribution’s system Python.

## 2. Clone and open the repository

```bash
git clone https://github.com/sadatnfs/ds60sqlpy.git ds60sqlpy
cd ds60sqlpy
code .
test -f README.md
```

If the repository is already cloned, `cd` to the directory containing `README.md`.

## 3. Create the Python environment

```bash
bash scripts/setup.sh
.venv/bin/python --version
.venv/bin/python scripts/course.py doctor
.venv/bin/python scripts/course.py catalog
```

Activation is optional:

```bash
source .venv/bin/activate
python scripts/course.py doctor
```

In VS Code, select `.venv/bin/python` as the interpreter and notebook kernel. See [VS Code](../vscode.md).

Core setup installs notebook, data, quality, bridge, professional, and SQL
notebook tooling on every operating system. It reuses a valid `.venv` and
does not contact a database. It uses `uv.lock` when external `uv` is present,
otherwise pip installs the declarations in `pyproject.toml`. To require the
checked-in lock after installing [uv](https://docs.astral.sh/uv/getting-started/installation/):

```bash
bash scripts/setup.sh --dependency-mode locked
```

Before later specialized machine-learning, production, deep-learning,
natural-language-processing, or geospatial lessons, install the advanced
profile while connected:

```bash
bash scripts/setup.sh --advanced
```

`libgomp1` supplies the OpenMP runtime used by the LightGBM and XGBoost Linux
wheels. The advanced profile can take substantially longer and depends on
compatible platform wheels. You may defer it until the generated catalog shows
that a planned lesson needs it. Use the
[catalog-label mapping](../dependency-profiles.md): labels such as `core`,
`postgres`, and `advanced` are not literal package extras.

## 4. Set up PostgreSQL

Install PostgreSQL 16 or newer. Ubuntu 24.04 provides PostgreSQL 16 in its standard repository:

```bash
sudo apt-get install -y postgresql postgresql-contrib
psql --version
sudo systemctl enable --now postgresql
```

If the reported major version is older than 16, use the [PostgreSQL packages for your distribution](https://www.postgresql.org/download/linux/).

Debian-family installations commonly use peer authentication. Create a local PostgreSQL role matching your Linux username so normal `psql` commands work without mixing `sudo` and local authentication:

```bash
sudo -u postgres createuser --createdb "$USER"
createdb advanced_sql_training
```

If either role or database already exists, keep it and continue.

From the repository root:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
```

`00_setup.sql` drops and recreates the disposable `training` schema. Never run it against a database containing valuable data. `00_verify.sql` raises an error if expected counts, coverage, chronology, totals, or foreign keys are wrong.

Pass the same native username/socket route to doctor and guided SQL notebooks:

```bash
export DS60_DATABASE_URL=advanced_sql_training
.venv/bin/python scripts/course.py doctor
```

Expect the course database to be reachable, then launch the portal from this
same terminal. Repeat the export in a new terminal. The tools otherwise use
the configured course TCP connection. See [Local PostgreSQL](postgresql.md)
for password authentication and the separate JupySQL URL.

If `systemctl` is unavailable, use your distribution's service manager. WSL
learners should keep the repository, interpreter, VS Code remote window, and
PostgreSQL client in the same Linux environment, or follow the native Windows
guide consistently. A Windows `.venv` cannot be used as a Linux `.venv`.

### Canonical container alternative

For the full browser app, use the
[Docker beginner walkthrough](../docker-beginners.md). Its shell launcher
prepares host persistence and opens the ready browser without a native Python
environment. For a SQL-only container server or later host notebooks, use
[Local PostgreSQL](postgresql.md#route-a-the-course-container). That guide
explains seed setup, the separate host-client requirement, ports, authentication,
and shutdown that preserves data.

## 5. Start learning

For the guided dashboard, file-backed progress, and exact VS Code/Jupyter
lesson actions, start the private loopback portal and keep its terminal open:

```bash
.venv/bin/python scripts/learning_portal.py
```

The browser page clearly identifies private launcher mode. If you instead open
`START_HERE.html` directly, it is a read-only course navigator; it cannot start
local programs.

Python:

```bash
.venv/bin/python -m jupyter lab python/ds-60day/notebooks
```

SQL:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

In private launcher mode, the recommended SQL route is to open the Day 1
reader and choose **Create/open guided SQL notebook**. That creates a preserved,
ignored working copy under `.learning/sql/sql-01/` and runs the complete script
through a fixed `psql -f` path.

For `%sql` and `%%sql` in the course kernel, continue with
[PostgreSQL in Jupyter](jupyter-postgresql.md).

Use [Your first successful session](first-success.md#3-make-a-scratch-notebook-and-run-one-cell)
for the exact clicks and expected output in your first notebook.

## 6. Prepare for offline study

Run disclosed first-use downloads while connected, then follow [Offline use](offline.md). Seaborn datasets cache after first use; pretrained models require their own cache or a lesson’s offline fallback.

For common failures, see [Troubleshooting](../troubleshooting.md).
