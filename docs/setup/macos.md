# macOS setup

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

Install:

1. [Git](https://git-scm.com/download/mac)
2. [Python 3.12](https://www.python.org/downloads/macos/) or an equivalent Homebrew installation
3. [Visual Studio Code](https://code.visualstudio.com/download)
4. PostgreSQL 16+ or Docker Desktop for the SQL track

Verify:

```bash
git --version
python3.12 --version
code --version
```

If Git requests Apple's Command Line Tools, finish that installation and
reopen Terminal. If `code` is missing, open VS Code normally and use **File →
Open Folder**; its Command Palette also offers **Shell Command: Install 'code'
command in PATH**. [Homebrew](https://brew.sh/) is a separate package manager;
install it first if you choose the `brew` commands below. Match native Apple
Silicon Python and Homebrew to an Apple Silicon Mac rather than mixing them
with an Intel/Rosetta environment.

Apple Silicon and Intel Macs are supported, but optional heavy machine-learning packages may install different platform wheels. CPU execution is the default.

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

Activation is optional. If you want an activated shell:

```bash
source .venv/bin/activate
python scripts/course.py doctor
```

In VS Code, select `.venv/bin/python` as the interpreter and notebook kernel. See [VS Code](../vscode.md).

Core setup installs notebook, data, quality, bridge, professional, and SQL
notebook tooling on every operating system. It reuses a valid `.venv` and
does not contact a database. With an existing external `uv` installation it
uses the checked-in lock; otherwise it installs the project declarations with
pip. For an explicitly locked install, use
`bash scripts/setup.sh --dependency-mode locked` after installing
[uv](https://docs.astral.sh/uv/getting-started/installation/).

Before later specialized machine-learning, production, deep-learning,
natural-language-processing, or geospatial lessons, install the advanced
profile while connected:

```bash
brew install libomp
bash scripts/setup.sh --advanced
```

The Homebrew OpenMP runtime is required by the LightGBM and XGBoost macOS
wheels. The dependency profile selects a compatible PyTorch/TorchVision pair:
the final Intel-macOS wheels on Intel Macs and a macOS 13-compatible pair on
Apple Silicon. The advanced profile can take substantially longer. You may
defer it until the generated catalog shows that a planned lesson needs it. Use
the [catalog-label mapping](../dependency-profiles.md): labels such as `core`,
`postgres`, and `advanced` are not literal package extras.

## 4. Set up PostgreSQL

### Option A: Homebrew

Install and start a supported PostgreSQL version. PostgreSQL 17 matches the canonical automation:

```bash
brew install postgresql@17
brew services start postgresql@17
export PATH="$(brew --prefix postgresql@17)/bin:$PATH"
psql --version
```

To keep that PATH setting for future Terminal sessions, add the export line to `~/.zprofile`.

Homebrew commonly creates a database role matching your macOS username rather than a `postgres` role. Use that local role:

```bash
createdb advanced_sql_training
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_setup.sql
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/00_verify.sql
```

If `createdb` says the database already exists, continue to the setup command.

`00_setup.sql` drops and recreates the disposable `training` schema. Never run it against a database that contains data you care about. `00_verify.sql` raises an error if expected counts, coverage, chronology, totals, or foreign keys are wrong.

Tell doctor and the guided SQL notebooks to use that same native local role
and socket connection, then keep this Terminal window for the portal:

```bash
export DS60_DATABASE_URL=advanced_sql_training
.venv/bin/python scripts/course.py doctor
```

Expect `Course database: advanced_sql_training is reachable`. Repeat the
export in each new Terminal session. For a password-protected native server
or the separate JupySQL lesson, use the matching connection instructions in
[Local PostgreSQL](postgresql.md).

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

For a tiny first notebook with explicit expected output, follow
[Your first successful session](first-success.md#3-make-a-scratch-notebook-and-run-one-cell).

## 6. Prepare for offline study

Run disclosed first-use downloads while connected, then follow [Offline use](offline.md). Seaborn datasets cache after first use; pretrained models require their own cache or a lesson’s offline fallback.

For common failures, see [Troubleshooting](../troubleshooting.md).
