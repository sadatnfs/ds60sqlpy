# macOS setup

The recommended course baseline is Python 3.12, PostgreSQL 16 or newer, and Visual Studio Code. Commands below use a POSIX shell and run from the repository root.

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

Apple Silicon and Intel Macs are supported, but optional heavy machine-learning packages may install different platform wheels. CPU execution is the default.

## 2. Clone and open the repository

```bash
git clone <repository-url> ds60sqlpy
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

Core setup installs notebook, data, and quality tooling. Before the engineering
bridge, PostgreSQL-in-Jupyter lesson, professional modules, or later
machine-learning, production, deep-learning, natural-language-processing, or
geospatial lessons, install the advanced profile while connected:

```bash
bash scripts/setup.sh --advanced
```

The advanced profile can take substantially longer. You may defer it until the
generated catalog shows that a planned lesson needs it. Use the
[catalog-label mapping](../dependency-profiles.md): labels such as `core`,
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

### Option B: Canonical container environment

Docker-based automation uses PostgreSQL 17. It is the most consistent choice for full validation but requires Docker Desktop and a first image download. See [Validation](../validation.md).

## 5. Start learning

Python:

```bash
.venv/bin/python -m jupyter lab python/ds-60day/notebooks
```

SQL:

```bash
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
```

For `%sql` and `%%sql` in the course kernel, continue with
[PostgreSQL in Jupyter](jupyter-postgresql.md).

## 6. Prepare for offline study

Run disclosed first-use downloads while connected, then follow [Offline use](offline.md). Seaborn datasets cache after first use; pretrained models require their own cache or a lesson’s offline fallback.

For common failures, see [Troubleshooting](../troubleshooting.md).
