# Source, saved work and caches

The repository and starter ZIP contain course source. Your Docker engine stores
classroom work separately. A Git push or source download does not back up notes,
code, results or the database.

## Know which storage you are using

| Location | Purpose | What to retain |
| --- | --- | --- |
| `<project>_classroom-learning` Docker volume | Drafts, notes, progress, source history and saved results | Back up the complete learning volume |
| `<project>_postgres-data` Docker volume | PostgreSQL database files | Preserve; use the documented database backup procedure |
| `<project>_classroom-runtime` Docker volume | Private worker authentication and coordination | Let the classroom manage it; do not distribute runtime credentials |
| `.classroom/<project>/` | Selected profiles, image source/tag, GPU choice, ports and last URL | Preserve preferences when updating; this is not a learner-data backup |
| `.learning/` beside a contributor checkout | Local contributor-tool state and generated SQL notebooks | Preserve if used; it does not automatically sync with Docker |
| Browser storage for `START_HERE.html` | Static-reader markers and preferences | Separate from server-backed classroom state |
| `.venv/` | Optional contributor interpreter and packages | Recreate from the lock on each machine |
| `artifacts/`, `mlruns/`, model/data caches | Experiments and prepared offline assets | Inspect and preserve anything you need |
| Python bytecode and test/lint caches | Regenerable tool state | Recreate when needed |
| `START_HERE.html`, `lesson-pages/`, `reference-pages/` | Maintained offline readers | Keep in distributions; regenerate through their tools |
| `uv.lock`, worker locks and course fixtures | Reproducible environment and lesson inputs | Keep in source control |

The default project is `ds60-classroom`. A custom project, another Docker context
or another engine selects different storage. An empty classroom can mean you
opened a different workspace. Inspect `./classroom status --project NAME` first.

## Resume, update and back up

```sh
./classroom stop
./classroom resume
```

These commands retain data. Strict resume does not build or pull. Use
`./classroom --rebuild` to install changed source, retaining the same project name.
Docker may assign another browser port; use the newly printed address.

Do not delete volumes or reset an engine as a normal restart procedure. An ignored
file can contain valuable work. A completion-JSON export is not a full backup of
pads, notes and results. Follow [backup and transfer](docker-classroom.md) before
moving machines. Keep database backup, learning-volume backup and preferences distinct.

## Optional contributor files

Docker learners do not need a host `.venv`. Contributors follow
[CONTRIBUTING.md](../CONTRIBUTING.md). Interpreter paths and binary packages are
machine-specific; copy source and recreate the environment on another machine.

The [guided SQL notebook generator](guided-sql-notebooks.md) preserves editable
copies under `.learning/sql/<lesson-id>/`. It does not overwrite existing notebooks
or SQL copies. Keep those files when they contain your experiments.

Optional Serena caches, logs and memories remain local. Its portable project
configuration is a navigation convenience; AGENTS files and repository skills
contain the maintained instructions. Never commit private work records or credentials.

## Offline assets and source distribution

Installing a package does not install every pretrained model, dataset or extension.
Follow the lesson's explicit preparation, record storage locations and verify offline
use before disconnecting. Downloads made in disposable worker scratch space do not
become persistent assets. Use the documented external-project storage route.

From a prepared contributor environment, `python scripts/build_starter.py` creates
a clean source archive. It excludes Git history, credentials, learner state,
installed environments and build caches. Do not assemble a release by blindly
copying the checkout, including hidden files. Personal backups belong separately.

Before cleanup, inspect both tracked and ignored files:

```sh
git status --short
git status --ignored --short
```

Only delete resources whose ownership and purpose are established. Normal updates
need neither a global Docker prune nor deletion of learning volumes.
