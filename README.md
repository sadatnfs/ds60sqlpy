# DS60 Classroom: learn at your own pace

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is one local classroom for programming, data science, statistics, machine
learning and systems. Its opening page brings **Python, PostgreSQL, the
engineering bridge and every newer subject together**. Choose any path, review
its prerequisites, and study at a pace that fits you. Historical day numbers
are lesson labels, not deadlines.

## Build, start and open the classroom

With your local Docker engine running, open a terminal in the course folder:

```sh
./classroom
```

The command builds images locally with visible logs, starts PostgreSQL and all
ten ordinary runtime workers, checks readiness, and opens the actual local
browser address at **`/classroom`**. It works on macOS, Linux and Windows through
WSL 2. No host Python, PostgreSQL, Java, C++ compiler or Node installation is
required. Nothing is pushed to a registry.

Read the [beginner one-command setup](docs/one-command-classroom.md) for engine
installation, Windows WSL integration, storage, a smaller first build and
recovery. Windows Explorer users can run **START_DOCKER_CLASSROOM.cmd** after
WSL and engine integration are configured. Mac users can double-click
**START_DOCKER_CLASSROOM.command**.

```sh
./classroom status      # Containers and the current browser address
./classroom logs        # Recent app and database logs
./classroom stop        # Stop while preserving saved work
./classroom --no-build  # Resume using already built images
```

Initial preparation needs internet access. The normal classroom works offline
once the chosen images and fixtures are prepared. Optional pretrained-model
downloads, external services and Kubernetes cluster preparation are deliberate
lesson workflows. See [offline use](docs/setup/offline.md).

## One home, every learning path

The home page is the subject chooser. Every subject has its own color theme
and a text label, so color is never the only way to identify a path. Opening a
lesson keeps its guide, coding workspace or reading notes, and progress in the
same classroom. Use **All subjects** to change direction without opening a
second application.

| Subject | Start here | Main direction |
| --- | --- | --- |
| Python and data science | [Python](python/ds-60day/README.md) | First programs, NumPy, pandas, algorithms, analysis and delivery |
| PostgreSQL | [SQL](sql/postgres-60day/README.md) | First queries, relational reasoning, analytics, performance and operations |
| Python + PostgreSQL engineering | [Bridge](bridge/README.md) | Safe database access, transactions, testing and pipelines |
| Statistics and machine learning | [Tutorial book](courses/statistics-ml/README.md) | Theory, modeling choices, worked Python examples and interview explanations |
| C++ | [C++20](courses/cpp/README.md) | Language foundations, ownership, compilation and larger programs |
| Java | [Java](courses/java/README.md) | Objects, types, collections, concurrency and practical engineering |
| JavaScript and TypeScript | [JavaScript/TypeScript](courses/javascript-typescript/README.md) | Browser and Node concepts, types, asynchronous code and testing |
| Kubernetes | [Kubernetes](courses/kubernetes/README.md) | Workloads, configuration, networking and bounded cluster practice |
| Scala and Apache Spark | [Scala/Spark](courses/scala-spark/README.md) | Scala, distributed data processing and companion PySpark implementations |
| TensorFlow | [TensorFlow/Keras](courses/deep-learning-tensorflow/README.md) | Tensors, optimization, architectures and model workflows |
| PyTorch | [PyTorch](courses/deep-learning-pytorch/README.md) | Autograd, training state, architectures and reproducibility |
| Natural language processing | [NLP](courses/nlp/README.md) | Text representation, classical baselines, neural methods and evaluation |
| LLM mechanisms | [LLM theory](courses/llm-theory/README.md) | Tokens, Transformers, attention, generation and adaptation mechanics |
| Applied LLM systems | [Applied LLMs](courses/llm-applied/README.md) | RAG, evaluation, fine-tuning, tools and subject assistants |

The library contains **598 canonical lessons and chapters across 14 subjects**,
with 30 additional PySpark implementations. The statistics book develops all
1,005 topics in its supplied outline. The [72-chapter LLM reading route](docs/learning/llm-textbook.md)
connects mechanisms to a running subject-assistant case study; [Inside a
Transformer](docs/learning/inside-a-transformer.md) provides a connected
numerical explanation of the architecture.

Prerequisites and estimated durations help you choose your next step. They do
not impose a deadline or lock you into one subject. Read slowly, revisit a
chapter, switch paths or combine them. A saved completion marker records your
choice; running a sample or opening an answer does not certify mastery.

## Read, code and keep your work

Mathematical explanations render as typeset equations, including fractions,
subscripts, vectors and matrices. Fenced code examples carry language-aware
syntax highlighting. Both work from bundled local rendering resources without
an external CDN. Code remains selectable so you can copy an example into its
appropriate workspace.

C++ and Java compile in Docker workers. JavaScript runs in Node.js, and
TypeScript is checked and compiled before execution. Python, TensorFlow,
PyTorch and Spark use their declared profiles. Each lesson explains its own
execution contract: a SQL script, a notebook, a standalone program and a
reading chapter are different artifacts. Follow the capability notice and
preparation steps, especially for disposable SQL schemas and optional cluster
operations.

Programming lessons combine explanations, worked examples, practice,
progressive hints and separate solutions. The statistics/ML book is a tutorial
with fully worked examples and answered interview discussions, without exams
or a hidden-solution gate. Reading, code, prediction and notes stay within one
subject workspace. See [the classroom guide](docs/classroom-experience.md).

The standard classroom saves learner work in named Docker volumes. Rebuilding
or replacing containers does not erase that work. Keep these volumes when
cleaning images, and use the documented export/backup workflow before moving
to a different machine or storage configuration. Earlier host-folder launchers
retain their own `.learning` state; they are compatibility alternatives, not
an additional required classroom. See [persistence and transfer](docs/one-command-classroom.md).

## Optional tools and compatibility routes

The static [START_HERE.html](START_HERE.html) remains an offline reading library.
Native VS Code/Jupyter workflows remain available for learners who deliberately
prepare those tools. Existing `/learn` and `/journeys` links are compatibility
entrypoints into the unified classroom; new documentation uses `/classroom`.

The optional [Codex MCP tutor](docs/mcp-tutor.md) can search content and help plan
study. It is read-only by default, reveals official solutions only on request,
and does not execute pad code. Codex is optional; every lesson must explain
its topic without requiring an agent.

The [implementation checkpoint](docs/implementation/CHECKPOINT.md) records
current acceptance evidence and explicit platform limits. Historical test
counts describe the version tested, not a guarantee about every future edit.
The [curriculum map](docs/curriculum-map.md) and generated catalog describe the
Python, SQL and bridge inventory; authored module manifests retain the newer
subjects' stable IDs.

## Optional native development setup

Run commands from the repository root - the directory containing this README.

### 1. Install prerequisites

The recommended compatibility baseline is:

- Python 3.12
- PostgreSQL 16 or newer
- PostgreSQL 17 for the canonical automated environment
- Current Visual Studio Code with the recommended extensions

Follow the guide for your operating system:

- [Windows](docs/setup/windows.md)
- [macOS](docs/setup/macos.md)
- [Linux](docs/setup/linux.md)

### 2. Set up the Python environment

Windows PowerShell:

```powershell
# Easiest guided route: double-click START_DS60.cmd in File Explorer.
#
# Recommended on a new Windows machine, including when Anaconda or PostgreSQL
# is installed but not on PATH:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\scripts\bootstrap_windows.ps1

$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\course.py doctor
```

The discovery bootstrap leaves PATH process-local by default, installs
IPython, JupyterLab, Jupyter Notebook, ipykernel, and the course dependency
profile, registers `Python (ds60sqlpy)`, and verifies `psql` without connecting
to a database. A standard `venv` puts Python under `.venv\Scripts`; the
Anaconda fallback creates a conda prefix whose interpreter is
`.venv\python.exe`. Resolve `$CoursePython` once per PowerShell window and
reuse it for the commands below. See the
[one-command Windows bootstrap guide](docs/setup/windows-bootstrap.md).
Use the smaller historical `scripts\setup.ps1` only when a supported Python is
already discoverable and you specifically want its standard-`venv`
`.venv\Scripts\python.exe` layout; do not run it over a conda-prefix `.venv`.

`START_DS60.cmd` is the day-to-day Windows entry point; the PowerShell command
above is the lower-level setup tool. The launcher reuses a ready environment
without reinstalling packages. Before its first download it clearly labels the
connected setup and asks you to type `SETUP`. It never asks for a database
credential and never creates, drops, or resets database data.

macOS or Linux:

```bash
bash scripts/setup.sh
.venv/bin/python scripts/course.py doctor
```

The Windows workflow intentionally does not require activating the virtual environment. In VS Code, select the interpreter inside `.venv`.

Core setup installs notebook, data, and quality tooling. Before later machine-learning and production lessons, install the larger optional groups while connected:

Windows PowerShell:

```powershell
& .\scripts\bootstrap_windows.ps1 -Profile Advanced
```

macOS or Linux:

```bash
bash scripts/setup.sh --advanced
```

The advanced profile includes machine learning, production, Python/PostgreSQL
bridge, professional data tooling, PostgreSQL notebook magics, deep-learning,
natural-language-processing, and geospatial packages. It can take substantially
longer and may use platform-specific wheels, so install it when the catalog
shows that you need it. Catalog labels are not all literal package extras; use the
[dependency-label mapping](docs/dependency-profiles.md) before choosing a
targeted install.

### 3. See what is ready

```text
python scripts/course.py catalog
python scripts/course.py validate
```

If `python` does not resolve to the repository environment, use
`.venv/bin/python` on macOS/Linux or `& $CoursePython` on Windows. In a new
PowerShell window, rerun the resolver from step 2 first.

To use the progress dashboard and launcher:

```powershell
# Windows PowerShell
& $CoursePython scripts\learning_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/learning_portal.py
```

The server binds only to `127.0.0.1`, chooses a free port, uses a per-session
request token, and accepts no arbitrary commands or paths. Use
`--no-launches` for progress synchronization without native launch buttons.

### 4. Start a lesson

Python:

1. Read [Python Day 1 companion guide](python/ds-60day/companion-guides/day01_setup_and_repl.md).
2. Open [Python Day 1 notebook](python/ds-60day/notebooks/day01_setup_and_repl.ipynb) in VS Code.
3. Attempt exercises before opening [the worked solution](python/ds-60day/solutions/day01_setup_and_repl/day01_solutions.md).

SQL:

Start with the three `sql-start` labs in catalog order before the historical
Day 1 exercises; each uses a small fixture and a plain-language query model.

1. Complete [SQL setup](sql/postgres-60day/README.md).
2. Open the private course portal with `START_DS60.cmd` on Windows or
   `scripts/learning_portal.py` with the repository interpreter on macOS/Linux.
3. Open [SQL Day 1](lesson-pages/sql-01.html), read its guide, and choose
   **Create/open guided SQL notebook**. The generated learner workspace is
   ignored under `.learning/sql/sql-01/` and preserves your edits.
4. If you prefer the terminal, run the complete lesson with error-stop behavior:

   ```text
   psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/postgres-60day/day01_select_where_orderby.sql
   ```

   That command uses the current operating system's PostgreSQL role and
   authentication defaults. A native Windows installation normally needs the
   `-h localhost -U postgres` flags from the
   [Windows setup guide](docs/setup/windows.md#option-a-native-postgresql).
   Before opening a guided notebook against native Windows PostgreSQL, also
   complete the guide's non-interactive local-authentication step; the notebook
   will never stop in a hidden password prompt.

5. Attempt the exercises before opening [the worked solution](sql/postgres-60day/solutions/day01_solutions.md).
6. Follow the generated catalog order: complete
   [relational design](sql/professional/companion-guides/sql_found_01_relational_design.md)
   between Days 15 and 16, then
   [versioned migrations](sql/professional/companion-guides/sql_found_02_versioned_migrations.md)
   between Days 39 and 40.

`sql/postgres-60day/00_setup.sql` is a destructive reset of the disposable `training` schema. Never run it against a database that contains data you care about.

Python + PostgreSQL engineering bridge:

1. Complete at least Python Day 15 and SQL Day 15.
2. Read the [bridge guide](bridge/README.md).
3. Open [Bridge Day 1](bridge/lessons/day01_config_logging_cli.py) and its
   [companion guide](bridge/companion-guides/day01_config_logging_cli.md).
4. Run it with the repository interpreter; live-database work is optional and
   uses `DS60_DATABASE_URL`.

## Learn with Codex

Codex is optional. The lessons, examples, and local tools remain usable without it.

This repository includes the repo-local skill `$guide-ds60sqlpy-learning`. Try:

```text
Use $guide-ds60sqlpy-learning to assess my level and guide me through the next Python, SQL, or bridge lesson. Give hints before solutions.
```

The tutor should adapt commands to your operating system, inspect your actual
work, and avoid opening official solutions until you ask. Every companion
guide ends with a lesson-specific prompt; the same exact prompt is copyable
from its generated reader and from the lesson selector in `START_HERE.html`.
See [Learning with Codex](docs/learning-with-codex.md).

## What is in the repository

```text
python/
  PYTHON_TRAINING.md
  ds-60day/
    notebooks/
    companion-guides/
    solutions/
  professional/
sql/
  ADVANCED_SQL_60DAY_PLAN.md
  postgres-60day/
    00_setup.sql
    day*.sql
    companion-guides/
    solutions/
  professional/
bridge/
  lessons/
  companion-guides/
  solutions/
  tests/
  professional/
curriculum/catalog.json
scripts/
docs/
.agents/skills/guide-ds60sqlpy-learning/
```

The maintained content has learner artifacts, companion guides, and runnable
solutions for all 60 lessons in both main tracks, eight engineering bridge
lessons, and 40 named foundation/professional/specialization modules. The
generated catalog indexes 186 learning modules and reports their exact artifact
paths.

Every lesson also has a checked exercise-enrichment target. The immutable
historical baseline lives in `curriculum/practice_baseline.json`; new lessons
are registered separately in `curriculum/practice_expansion.json`. The target for each
learner artifact, guide, and every explanatory solution artifact is at least
`max(6, 2 × audited baseline)`. Run `python scripts/audit_practice.py` or read
the generated [practice coverage report](docs/practice-coverage.md).
The companion [lesson depth report](docs/lesson-depth-report.md) checks the
self-contained beginner-teaching contract, explanatory solution floor,
historical Python notebook depth, and per-lesson Codex prompts. These automated
checks are minimums; runnable examples and technical explanations still
receive human and execution review.

## Documentation

- [Curriculum map](docs/curriculum-map.md)
- [Portable guided course portal](START_HERE.html)
- [Portal modes, progress, and launcher security](docs/learning-portal.md)
- [Professional and specialization paths](docs/professional-paths.md)
- [VS Code workflow](docs/vscode.md)
- [One-command Windows bootstrap](docs/setup/windows-bootstrap.md)
- [Offline use](docs/setup/offline.md)
- [PostgreSQL in Jupyter](docs/setup/jupyter-postgresql.md)
- [Practice coverage](docs/practice-coverage.md)
- [Lesson depth report](docs/lesson-depth-report.md)
- [Curriculum design references](docs/curriculum-design-references.md)
- [Local environments and caches](docs/local-files-and-caches.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Validation](docs/validation.md)
- [Content authoring](docs/content-authoring.md)
- [Contributing](CONTRIBUTING.md)

## Continuous validation

The badge at the top reflects `.github/workflows/ci.yml`. Every push and pull
request runs locked core checks on Ubuntu (Python 3.11 and 3.12), Windows
(3.12), and macOS (3.12), exercises the learner bootstrap, and executes the
complete learner/solution SQL sequence against PostgreSQL 17. A scheduled or
manual job also verifies every optional dependency group on Windows, Ubuntu,
and macOS. See [Validation](docs/validation.md) for the exact local
equivalents and the difference between structural, smoke, and full execution
evidence.

## Scope and expectations

The Python track is strongest as a practical Python-for-data-science path; it
is not a substitute for the complete Python language reference. The SQL track
targets PostgreSQL. The bridge adds focused application-engineering practice,
not a full distributed-systems or database-administration program. Treat lesson
objectives and the generated catalog view - not a promise to teach
“everything” - as the contract.

Progress matters more than the 60-day label. A good session ends with runnable work, an explanation in your own words, and one small note about what to revisit.

## License

See [LICENSE](LICENSE).
