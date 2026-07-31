# Linux setup

The recommended course baseline is Python 3.12, PostgreSQL 16 or newer, and Visual Studio Code. Commands below show Debian/Ubuntu conventions; translate package-manager commands for other distributions.

Run course commands from the repository root.

## 1. Install base tools

On a distribution that provides Python 3.12:

```bash
sudo apt-get update
sudo apt-get install -y git libgomp1 python3.12 python3.12-venv python3-pip
git --version
python3.12 --version
```

Install [Visual Studio Code](https://code.visualstudio.com/docs/setup/linux) through the supported package for your distribution.

If your distribution does not provide Python 3.12, use a current vendor package or a Python version manager. Do not replace the distribution’s system Python.

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

Activation is optional:

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

### Canonical container environment

Docker-based automation uses PostgreSQL 17 and avoids host authentication differences. It requires a container runtime and a first image download. See [Validation](../validation.md).

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
