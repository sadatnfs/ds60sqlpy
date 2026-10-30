# DS60 Classroom

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is a local classroom for programming, data science, statistics, machine
learning and systems. **All subjects use one browser interface** with lessons,
code editors, worked examples and saved progress. Prerequisites identify the
knowledge used by each lesson; historical day numbers are stable lesson labels.

The supported product runs entirely in **Linux Docker containers**. Windows
uses WSL 2, macOS uses its Docker engine's Linux environment, and Linux uses a
local Docker engine. One shared launcher prepares the classroom and its
selected runtimes on all three host platforms.

Use the [documentation map](docs/README.md) to find installation, learning,
backup, tutoring and contributor guides. The repository includes dedicated
skills for guiding a learner and adding a new language or subject.

## Start or resume the classroom

### 1. Prepare your machine

Install and start a local Docker-compatible engine with **Linux containers**,
**Docker Compose 2.28.0 or newer**, and a Bash terminal. Install Git if you want
to clone the repository; a ZIP download works without Git.

| Operating system | What to prepare                                                                                                                                                        | Where to run the commands below  |
| ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Windows          | WSL 2 with Ubuntu, plus Docker Desktop or Rancher Desktop. Enable Linux containers and integration for your Ubuntu distribution. Rancher Desktop uses the Moby engine. | The Ubuntu/WSL terminal          |
| macOS            | Docker Desktop or Rancher Desktop using Moby. Start the application and wait for its engine to be ready. Bash is included with macOS.                                  | Terminal                         |
| Linux            | Docker Engine, its Compose plugin, Bash and permission for your normal user to access the local engine.                                                                | A terminal in your Linux session |

Follow the [beginner setup guide](docs/one-command-classroom.md) for installation
links, WSL integration and resource guidance. The course's Python, PostgreSQL,
Java, C, C++, Go, C#, Rust, Swift, R, Julia, Node, PHP, JAX, PyMC, Stan,
Polars, dbt, TensorFlow, PyTorch and Spark tools run inside Docker. You do not
need to install those language toolchains on your machine.

Check your engine from that terminal before continuing:

```sh
docker info
docker compose version
bash --version
```

`docker info` must connect successfully to a Linux-container engine. The Compose
version must be at least 2.28.0. If a command is unavailable or cannot connect,
finish the engine installation or WSL integration before starting the course.

### 2. Get the course and start it

A public copy can be cloned or downloaded as a ZIP without a GitHub login.
If this repository or a fork is restricted, sign in with an account that has
access.
For authenticated HTTPS cloning, use a Git credential manager or GitHub CLI;
do not paste a personal access token into the clone URL. The local classroom
needs no GitHub login after you have downloaded it.

Clone the repository, enter its folder, check prerequisites and launch:

```sh
git clone https://github.com/sadatnfs/ds60sqlpy.git
cd ds60sqlpy
./classroom doctor
./classroom
```

This checkout targets release 1.3.0. To use prebuilt images, first verify a
completed full publisher and fresh-pull acceptance for that release, then use
its matching source or starter with
`./classroom --all --from-hub sadatnfs --tag 1.3.0`.
See [Docker Hub distribution](#optional-docker-hub-distribution) for historical
evidence, current availability, selective installation and saved versions.

`doctor` checks the local engine and configuration without starting services.
In local-build mode, the final command prepares PostgreSQL and the ordinary
CPU and language runtime workers. It builds **only missing images**, with visible logs, starts the
services, waits for readiness and opens the browser. Keep the terminal open while
it works. First preparation needs internet, several gigabytes of downloads and
time to install image dependencies. Nothing is pushed to a registry.

**Returning to study? Run the same `./classroom` command.** It remembers the
project's selected profiles, reuses local images and starts existing containers
without rebuilding images. If Docker changes an automatically assigned browser
port on restart, the launcher recreates only the app from its existing image to
use that address; your volumes and worker containers are retained. Interrupted
first preparation also keeps the selection and completed images, so the next
start prepares only what is still missing.

**Using a ZIP instead:** download the repository ZIP or a complete starter ZIP,
extract it fully, and open a terminal in the extracted folder containing
`classroom`. Run `./classroom doctor`, then `./classroom` there. If extraction
removed executable permissions, use `bash classroom doctor` and `bash classroom`.
After the prerequisites above are ready, Windows users can also double-click
**START_DOCKER_CLASSROOM.cmd**; Mac users can double-click
**START_DOCKER_CLASSROOM.command**.

For a smaller first build, replace the last command with:

```sh
./classroom --starter
```

This prepares the app, PostgreSQL and Python Core. The full library remains
readable, while other languages need their runtime profiles. Later `./classroom`
starts remember this smaller selection. Use `./classroom --all` when you want to
prepare the full ordinary set, or choose specific profiles from the
[launcher guide](docs/one-command-classroom.md#useful-variations).

### 3. Open the classroom and keep your work

When startup finishes, the launcher prints the actual local address ending in
**`/classroom`** and tries to open it. If no browser opens, copy that printed URL
into your browser. Docker chooses an available local port, so use the printed
address instead of assuming a fixed port. You can retrieve it with
`./classroom status`. Automatic ports can change after a stop/start. For a stable
address, configure fixed ports as described in the
[startup guide](docs/one-command-classroom.md#ports-and-saved-work).

Choose a subject on the opening page and follow its first lesson. Source,
notes, saved results and progress stay in named Docker volumes on your machine;
PostgreSQL has its own volume. Stopping or replacing a container preserves
those volumes.

```sh
./classroom status                  # Containers and the current browser address
./classroom logs                    # Recent app and database logs
./classroom stop                    # Pause this classroom and keep saved work
./classroom                         # Resume; prepare only missing images if necessary
./classroom resume                  # Resume strictly without building or pulling
./classroom --local-build --rebuild # Install changed local sources deliberately
```

`resume` and `--no-build` are equivalent. They fail with an actionable message
if a needed image is unavailable; they never start a download or build. Use
ordinary `./classroom` after deleting an image to prepare the missing image.
After downloading updated course sources or pulling repository changes, use
`./classroom --local-build --rebuild` to put those changes inside local images. A normal resume
deliberately keeps using the existing installation.

The ignored `.classroom/<project>/` directory remembers profile, registry and
port choices. Your code, notes, history and database live in Docker volumes,
not in that settings directory. Existing projects created before selection
tracking can recover their profile selection from their own worker containers.

Reuse the same Compose project to return to the same saved work. If you choose
`--project NAME`, supply that same name on later start, status and stop commands.
Keep the learning and database volumes when cleaning containers or images;
removing volumes deletes the state they contain. See
[backup and transfer](docs/one-command-classroom.md) before moving machines.

The ordinary classroom works offline after its images and fixtures are
prepared. Optional pretrained-model downloads, external services and Kubernetes
cluster preparation are explicit lesson workflows. For errors, profiles and
recovery, read the [one-command guide](docs/one-command-classroom.md) and
[offline-use guide](docs/setup/offline.md).

## One home, every learning path

The home page is the subject chooser. Every subject has its own color theme
and a text label, so color is never the only way to identify a path. Opening a
lesson keeps its guide, coding workspace or reading notes, and progress in the
same classroom. Use **All learning paths** to change direction without opening a
second application.

| Subject                         | Start here                                                                  | Main direction                                                                                                                       |
| ------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Python and data science         | [Python](python/ds-60day/README.md)                                         | First programs, NumPy, pandas, algorithms, analysis and delivery                                                                     |
| PostgreSQL                      | [SQL](sql/postgres-60day/README.md)                                         | First queries, relational reasoning, analytics, performance and operations                                                           |
| Python + PostgreSQL engineering | [Bridge](bridge/README.md)                                                  | Safe database access, transactions, testing and pipelines                                                                            |
| Statistics and machine learning | [Tutorial book](courses/statistics-ml/README.md)                            | Theory, modeling choices, worked Python examples and interview explanations                                                          |
| Applied scientific methods      | [Applied Science](courses/applied-science/README.md)                        | Causal identification, forecasting, survival, ranking, optimization and evidence synthesis                                           |
| Bayesian computation            | [PyMC, ArviZ and Stan](courses/bayesian-computing/README.md)                | Generative models, actual posterior fitting, diagnostics, predictive checks and decisions                                            |
| Polars                          | [Polars data engineering](courses/polars/README.md)                         | Expressions, lazy plans, Arrow, temporal joins and validated feature publication                                                     |
| dbt                             | [dbt and DuckDB](courses/dbt/README.md)                                     | Real models, tests, snapshots, incremental data, contracts and controlled publication                                                |
| ML engineering                  | [ML engineering](courses/ml-engineering/README.md)                          | Features, experiment tracking, model decisions, serving, monitoring and rollback                                                     |
| Data and ML Engineering         | [Engineering tutorial book](courses/data-ml-engineering/README.md)          | 72 chapters connecting data contracts, storage, streaming, features, model delivery and the complete LLM request-to-SSE lifecycle    |
| Apache and open-data platforms  | [Platform tutorials and workshops](courses/apache-data-platforms/README.md) | 88 units covering Arrow, DataFusion, Ballista, Airflow, Kafka, Iceberg, Flink, Cassandra, Pinot, Hive, Atlas and Delta Sharing       |
| LLM evaluation                  | [Evaluation and alignment](courses/llm-evaluation/README.md)                | Sampling, annotation, uncertainty, retrieval, preference models, DPO, PPO and GRPO                                                   |
| Julia                           | [Julia scientific computing](courses/julia/README.md)                       | Language, dispatch, data analysis, numerical methods, differentiation and concurrency                                                |
| R                               | [R programming and statistics](courses/r/README.md)                         | Language foundations, data workflows, S3/S4/R6/S7, statistical modeling and plotting                                                 |
| JAX                             | [JAX numerical computing](courses/jax/README.md)                            | Arrays, automatic differentiation, JIT, transformations, optimization and scientific models                                          |
| DAX                             | [Offline DAX](courses/dax/README.md)                                        | Semantic models, filter context, measures, time intelligence and worked reference tables                                             |
| Data visualization              | [Plotly in Python and JavaScript](courses/data-visualization/README.md)     | Shared data semantics, uncertainty, interactive controls, accessibility and export                                                   |
| C                               | [C17](courses/c/README.md)                                                  | Memory, pointers, representation, compilation and reliable systems programs                                                          |
| C++                             | [C++20](courses/cpp/README.md)                                              | Language foundations, ownership, compilation and larger programs                                                                     |
| Go                              | [Go](courses/go/README.md)                                                  | General-purpose programs, concurrency, services and Kubernetes-oriented engineering                                                  |
| C#                              | [C# and .NET](courses/csharp/README.md)                                     | Types, collections, LINQ, async programming and application design                                                                   |
| Rust                            | [Rust and Arrow](courses/rust/README.md)                                    | Ownership, traits, concurrency, systems design and columnar data                                                                     |
| Swift                           | [Swift](courses/swift/README.md)                                            | Language, concurrency and app architecture, with explicit Apple-platform project boundaries                                          |
| Docker                          | [Docker](courses/docker/README.md)                                          | Images, Dockerfiles, Compose, networking, data, security and recovery                                                                |
| Java                            | [Java](courses/java/README.md)                                              | Objects, types, collections, concurrency and practical engineering                                                                   |
| JavaScript and TypeScript       | [JavaScript/TypeScript and D3](courses/javascript-typescript/README.md)     | Browser and Node concepts, types, async code and a 24-lesson D3 visualization specialization                                         |
| Kubernetes                      | [Kubernetes](courses/kubernetes/README.md)                                  | Workloads and a deep 24-lesson networking/operations extension, with bounded owned-cluster practice                                  |
| Scala and Apache Spark          | [Scala/Spark](courses/scala-spark/README.md)                                | Scala, distributed data processing and companion PySpark implementations                                                             |
| Advanced Spark modeling         | [Advanced Spark](courses/advanced-spark-modeling/README.md)                 | Custom likelihoods, bounded distributed fitting, Scala extensions, Catalyst and Spark/PyTorch integration                            |
| Custom likelihoods              | [PyTorch modeling](courses/custom-likelihood-pytorch/README.md)             | Likelihood construction, automatic differentiation, optimization, uncertainty and numerical diagnostics                              |
| TMB modeling                    | [R and C++ with TMB](courses/tmb-modeling/README.md)                        | Compiled models, random effects, Laplace approximation, public APIs and C++ authoring families                                       |
| TensorFlow                      | [TensorFlow/Keras](courses/deep-learning-tensorflow/README.md)              | Tensors, optimization, architectures and model workflows                                                                             |
| PyTorch                         | [PyTorch](courses/deep-learning-pytorch/README.md)                          | Autograd, training state, architectures and reproducibility                                                                          |
| Natural language processing     | [NLP](courses/nlp/README.md)                                                | Text representation, classical baselines, neural methods and evaluation                                                              |
| LLM mechanisms                  | [LLM theory](courses/llm-theory/README.md)                                  | Tokens, Transformers, attention, generation and adaptation mechanics                                                                 |
| Applied LLM systems             | [Applied LLMs](courses/llm-applied/README.md)                               | RAG, evaluation, fine-tuning, tools and subject assistants                                                                           |
| GPU computing and CUDA          | [CUDA, Python and GPU Spark](courses/cuda/README.md)                        | GPU architecture, C++ kernels, Python, PyTorch/TensorFlow and RAPIDS/Spark, with portable CPU study paths                            |
| Web development                 | [HTML, CSS and PHP](courses/web-development/README.md)                      | Semantic pages, responsive layouts, accessibility, browser interactions and server-side applications                                 |
| Python web development          | [HTTP, Flask, FastAPI and Django](courses/python-web/README.md)             | Shared HTTP foundations, independent framework branches, APIs, databases, authentication, streaming and real Docker service projects |

The engineering book includes separately owned [data-product](courses/data-ml-engineering/projects/data-product/README.md)
and [inference-service](courses/data-ml-engineering/projects/inference-service/README.md)
workshops with their own persistent state. Apache library examples run in the
ordinary `data-platforms-python` worker; distributed services use explicit
project preparation. The [platform qualification ledger](courses/apache-data-platforms/authoring/ENVIRONMENTS.md)
records actual runtime scope and separately prepared Atlas/Delta Sharing routes.
Opening a chapter does not start those services or install their dependencies.

The [scientist roadmap](docs/scientist-roadmap.md) connects the statistics,
experimentation, data engineering and ML routes, showing what each adds and
where external systems or hardware are still required.

The catalog lists canonical lessons, tutorial chapters and separately saved
language/framework variants. The current inventory is shown in the classroom
and can be checked with `python scripts/check_modules.py --json`. The statistics book maps its chapters to 1,005 topics in the source outline. The [72-chapter LLM reading route](docs/learning/llm-textbook.md)
connects mechanisms to a running subject-assistant case study; [Inside a
Transformer](docs/learning/inside-a-transformer.md) provides a connected
numerical explanation of the architecture.

For a first SQL course, start with `sql-start-01`, `sql-start-02` and
`sql-start-03`, then continue to `sql-01`. The classroom keeps this on-ramp
ahead of schema and operations topics.

Prerequisites and estimated durations support study planning. Access is not
restricted by completion markers. Each subject retains its own drafts, notes
and results when you change courses.

Mathematics is compiled from explicit TeX during the image build, with bundled
fonts and accessible MathML. Lesson prose uses textbook typography. Tagged code
blocks remain highlighted and copyable. The classroom needs no font or math CDN.
DAX uses an offline editor and fixed, hand-derived reference tables; it has no
Run operation. JAX and Bayesian examples run on CPU in their dedicated profiles.
Python, R and Julia charts, plus bounded data tables and JSON reports, can be
retained with their exact run source. JavaScript Plotly examples run in the
isolated browser preview. See [plotting](docs/plotting.md) for limits
and [textbook rendering](docs/textbook-rendering.md) for the authoring contract.

## Read, code and keep your work

### Optional Docker Hub distribution

The [historical 1.1.0 publisher](https://github.com/sadatnfs/ds60sqlpy/actions/runs/40961726148)
completed from [source `59a0d116`](https://github.com/sadatnfs/ds60sqlpy/tree/59a0d116a1759d5d509718c52c4f3439e1986644),
promoting App and all 25 ordinary workers as combined Linux AMD64/ARM64 images.
Its native worker/scientific gates and App/Core fresh-pull/stop/resume checks
passed. The later all-module audit accepted 19 native groups and retained 19
failed groups. An authenticated metadata check on October 30 returned HTTP 404
for the old App tag. Those records describe historical results, not current
availability or acceptance of this later source.

For a completed full 1.3.0 publication, use the matching source or starter:

```sh
./classroom --all --from-hub sadatnfs --tag 1.3.0
```

Ordinary startup uploads nothing. For a new Hub selection, omitting `--tag`
resolves the app's `latest` alias to a concrete release, requires a matching
checked-in app version, and saves that version. App tags are `:1.3.0` and
`:latest`; distinct worker tags include `:1.3.0-worker-r-statistics` and
`:1.3.0-worker-python-core`. Docker selects the native architecture. Tags starting
`ci-` are publication staging candidates, not learner releases. Hub mode never
falls back to local builds. The [complete subject/profile/image mapping](docs/dockerhub.md#subjects-runtime-profiles-and-canonical-images)
explains which runtime serves each subject and how to select only needed workers.

The independent [Spark/TMBad package](packages/spark-tmbad/README.md) was added
after the historical 1.1.0 publisher's source. Use each independent package's
own version, installation guide and qualification records; a classroom image
version does not imply package acceptance. Saved learner selections retain
their pin until an explicit update.

For a partial publication, select only its available workers. For example, an
app/Core plus JavaScript and TypeScript publication is installed with:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

`--all` requires every ordinary worker at the selected app release and fails
if a partial publication omitted one. Use `--tag VERSION` to select a default
release explicitly. Repeat `--image-tag PROFILE=VERSION` to choose a particular
Hub image, including `app`; for example, `--image-tag app=1.0.0` and
`--image-tag javascript-node=1.0.0`. `VERSION` may also be `latest` for an
individual profile. The launcher resolves it to a concrete version and checks
the published worker's profile, platforms and source revision before saving it.
Selected workers must share the app's qualified source revision. Current CI
binds one checked-in version to each revision, so its releases do not support
mixing worker images from different versions. The launcher also requires any
different patch versions to stay in the app's major.minor line. Missing or
incompatible images stop startup with the project volumes retained.
Use `--image-tag javascript-node=default --rebuild` to clear a saved worker
pin and return that worker to the app's version.

A same-namespace saved Hub project keeps its pinned release when you repeat
`--from-hub USER` without `--tag`. Use `--tag latest --rebuild` to choose a newer
completed release deliberately. Later bare `./classroom resume` never builds,
pulls or follows a moving latest tag.

For a completed full release, download without starting services with
`./classroom pull --all --from-hub YOUR_DOCKERHUB_USER --tag 1.3.0`.
For a partial release, use only its published profiles.
For an existing project, switching image source/layout or applying an update
requires the same command without `pull` and with `--rebuild`. In Hub mode
that pulls and applies images without compiling. Keep the same custom
`--project NAME` to retain its volumes. Images do not carry saved progress;
moving machines needs a separate learning/database backup.

#### Publish through GitHub Actions

The full publication workflow builds and pushes only for a push to `main`
whose HEAD commit message contains `[publish-docker]`. The targeted
workflow accepts `[build-test-ALIAS]` on a branch for native qualification
without uploading, and `[publish-ALIAS]` on `main` for a partial
versioned release. Use exactly one Docker marker in the HEAD message.
Configure the two repository Actions secrets `DOCKERHUB_USERNAME` and
`DOCKERHUB_TOKEN` for publication. No extra enable variables or
protected-environment setup is required.

For a smaller native check, `[build-test-js]` builds and qualifies the
JavaScript and TypeScript group without publishing. `[publish-js]` publishes
App, Core and that group from a marked `main` commit after its gates pass.
Profile names such as `javascript-node` are aliases for their complete
qualification group. See [targeted image checks and partial publication](docs/targeted-images.md)
for accepted markers, version rules and the selected-profile install command.

After staging and validating the reviewed release changes on `main`:

```sh
git commit -m "Release the reviewed version [publish-docker]"
git push origin main
```

Native AMD64 and ARM64 jobs build and qualify the app, Core and worker groups.
Commit-specific staging uploads precede final promotion. Only the complete
successful checks allow versioned worker tags, then the app version, followed
by latest aliases with app `latest` last. Small receipts record the evidence;
large Docker archives are not transferred through Actions artifacts.

The version comes from checked-in source. An incompatible existing version is
refused; changes after publication need a coherent new patch version such as `1.1.1`.
The first upload can be large, and later runs reuse unchanged layers where
available. Account pull limits, fair use and runner capacity still apply.
A workflow configuration or staging upload does not prove final publication.
For published full versions, the [read-only module audit](docs/dockerhub.md#audit-every-published-module-without-republishing)
checks canonical pulls and selected setup using the exact original source,
without rebuilding or publishing images.

#### Publish an existing local image set manually

The local publisher remains a separate, single-architecture route. If this
machine needs authentication, the operator runs:

```sh
docker login
```

Preview already built and tested images without uploading:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.3.0
```

After reviewing the mapping, explicitly upload:

```sh
./classroom publish --to-hub YOUR_DOCKERHUB_USER --tag 1.3.0 --push
```

This requires the complete ordinary local set by default. It checks all
selected images before tagging/pushing and does not build, log in, create
another architecture or publish combined manifests. Prepare missing images
with `./classroom build --all --local-build --tag 1.3.0`, then qualify them.

Manual tags include architecture, such as `1.3.0-lab-arm64`. A matching-architecture
learner selects that layout explicitly:

```sh
./classroom --all --from-hub YOUR_DOCKERHUB_USER --tag 1.3.0 --architecture-tags
```

An ARM64-only Mac publication does not supply AMD64 tags for a typical
Windows/WSL machine. See [Docker Hub distribution](docs/dockerhub.md) for
complete account, tag, lifecycle, compatibility and publication instructions.

### Reading and execution

Mathematical explanations render as typeset equations, including fractions,
subscripts, vectors and matrices. Fenced code examples carry language-aware
syntax highlighting. Both work from bundled local rendering resources without
an external CDN. Code remains selectable so you can copy an example into its
appropriate workspace.

C, C++, Go, C#, Rust, Swift and Java compile in Linux Docker workers. JavaScript
uses Node for server-side lessons and an isolated browser preview for the D3
specialization. TypeScript is checked and compiled before Node execution.
Python, TensorFlow, PyTorch, Spark, Polars and dbt use their declared profiles.
Julia runs with its prepared scientific packages. Stan compiles native model
source and samples two short seeded chains; its diagnostic output requires
interpretation, not just a successful exit code.

HTML and CSS render in an isolated offline browser preview, including inline
JavaScript interactions. PHP runs in its own CLI worker with PDO SQLite. Real
HTTP sessions and multi-file applications use the web subject's separate,
loopback-only Docker project. The pad and the web server are explicitly different
execution environments.

For dbt, beginner SQL-model variants accept one SQL/Jinja model in a fixed
project. Complete dbt projects and the [local ML service](courses/ml-engineering/projects/local-system/README.md)
have separate, explicit Docker workflows and storage. They do not create a
multi-file editor or long-running server inside an ordinary pad. Stan models
with a separate JSON data file use the [complete project fixture](courses/bayesian-computing/projects/normal-mean/README.md).

Turn on **Live preview** in an HTML/CSS or browser JavaScript/D3 workspace to
see edits after a short pause. Switch between desktop, tablet and phone widths,
inspect the console, and pause or stop the preview whenever you need. Automatic
updates preserve your draft without filling run history; use Run or explicitly
save an observation when you want a durable result.

The 128-chapter CUDA subject is useful on CPU-only machines: read the theory,
save reasoning and run small CPU models. Selected C++, CuPy, PyTorch and
TensorFlow variants can use optional NVIDIA workers after explicit setup and
a real device probe. GPU images are excluded from `--all`; Apple, AMD and Intel
GPUs are not made CUDA-compatible by Docker. See the
[platform and evidence guide](docs/cuda-classroom.md), including non-CUDA options.

D3 7.9.0 is bundled locally. Its 24 lessons render real SVG or Canvas charts in
the classroom, including accessible controls, brushing, zooming and dashboards.
The preview has an opaque origin and blocks external connections. Its saved
console results are clearly labeled browser observations, not independent
server verification. Viewing a saved observation preserves your current source
and does not rerun it.

The Swift Linux worker teaches portable language and Foundation behavior.
SwiftUI, UIKit and Apple app signing require the explicitly documented macOS
and Xcode project route. Docker itself is taught through complete reading and
practice lessons plus a disposable host project; the classroom never receives
the Docker engine socket. Advanced Kubernetes controllers, load balancers,
policy enforcement and dual-stack labs require named, separately prepared
owned capabilities. Each lesson explains its own
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
to a different machine or storage configuration. An older host-folder `.learning` backup remains separate until you
deliberately transfer and verify it; startup does not merge storage routes. See [persistence and transfer](docs/one-command-classroom.md).

## Offline reading and optional study tools

The static [START_HERE.html](START_HERE.html) remains an offline reading library.
The complete source folder contains its linked readers and fixtures. Static
pages do not launch a compiler or database. Existing `/learn` and `/journeys`
bookmarks lead into the unified classroom; use `/classroom` for new bookmarks.

A separately prepared contributor environment can use VS Code or Jupyter for
specific notebook and multi-file project work. Those workflows are described
where a lesson needs them and do not replace Docker onboarding.

To use an assistant as a study companion, open this repository in your coding
assistant and ask it to use the
[learning companion skill](.agents/skills/guide-ds60sqlpy-learning/SKILL.md).
For example: "Help me resume my saved Go lesson. Read my current attempt, explain
prerequisite concepts clearly and give hints before solutions. Keep my notes and progress."
The skill covers every subject and distinguishes reading, coding and external
project workflows. It can also help diagnose startup without reinstalling tools
or resetting your workspace. Share only the source and outputs you want reviewed.

The optional [MCP tutor](docs/mcp-tutor.md) can search content and help plan
study. It is read-only by default and does not execute pad code. Practice references
require an explicit reveal request; the statistics tutorial exposes its worked
answers directly. An AI tutor is optional; every lesson must explain
its topic without requiring an agent.

The [implementation checkpoint](docs/implementation/CHECKPOINT.md) records
the maintained architecture and explicit verification boundaries. Use the
workflow result for the exact revision when checking CI status.
The [curriculum map](docs/curriculum-map.md) and generated catalog describe the
Python, SQL and bridge inventory; authored module manifests retain the newer
subjects' stable IDs.

## Develop and contribute

Developers who modify Python application code or content generators should read
[CONTRIBUTING.md](CONTRIBUTING.md). It explains the locked Python environment,
focused checks, grouped parallel tests, source ownership and generated readers.
Format maintained code across the repository with `./scripts/format-repo`, or
check formatting without changing source files with `./scripts/format-repo --check`.
Run `./scripts/lint-repo` for read-only static source checks.
The commands use a dedicated Docker toolchain, so contributors do not need every
language compiler on their host. See [the formatting workflow](CONTRIBUTING.md#format-the-repository)
for generation order, coverage and optional pre-commit checks.
Running the classroom and developing its application are separate setup paths.
Use Linux or WSL 2 for the validated contributor environment. Optional notebook, SQL and editor workflows are documented in
[contributor setup](CONTRIBUTING.md), [notebook guidance](docs/setup/jupyter-postgresql.md)
and [dependency profiles](docs/dependency-profiles.md). The ordinary learner
classroom continues to use Docker.

To add a lesson or subject, start with the
[curriculum extension playbook](docs/curriculum-extension-playbook.md) and the
[repository authoring skill](.agents/skills/add-learning-path/SKILL.md).
The skill covers learning progression, manifests, runtime boundaries, offline
examples, browser delivery and saved-work verification. New subjects join the
same classroom instead of creating another application.

## Project boundaries

DS60 runs trusted local learning code on your own machine. It is not intended
as a public multi-user code-execution service. Keep its ports on loopback and
use the provided disposable training database. Runtime limits and cleanup help
contain mistakes; they do not make arbitrary untrusted programs safe.

The repository is licensed under [Apache 2.0](LICENSE). Dependencies and linked
learning resources retain their own licenses. Bundled D3 7.9.0 uses its
[ISC license](src/ds60sqlpy/assets/vendor/LICENSE.d3.txt). See [CONTRIBUTING.md](CONTRIBUTING.md)
for content attribution, verification and how to report a reproducible problem.
