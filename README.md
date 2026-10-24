# DS60 Classroom: learn at your own pace

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is one local classroom for programming, data science, statistics, machine
learning and systems. Its opening page brings **Python, PostgreSQL, the
engineering bridge and every newer subject together**. Choose any path, review
its prerequisites, and study at a pace that fits you. Historical day numbers
are lesson labels, not deadlines.

## Build, start and open the classroom

### 1. Prepare your machine

Install and start a local Docker-compatible engine with **Linux containers**,
**Docker Compose 2.28.0 or newer**, and a Bash terminal. Install Git if you want
to clone the repository; a ZIP download works without Git.

| Operating system | What to prepare | Where to run the commands below |
| --- | --- | --- |
| Windows | WSL 2 with Ubuntu, plus Docker Desktop or Rancher Desktop. Enable Linux containers and integration for your Ubuntu distribution. Rancher Desktop uses the Moby engine. | The Ubuntu/WSL terminal |
| macOS | Docker Desktop or Rancher Desktop using Moby. Start the application and wait for its engine to be ready. Bash is included with macOS. | Terminal |
| Linux | Docker Engine, its Compose plugin, Bash and permission for your normal user to access the local engine. | A terminal in your Linux session |

Follow the [beginner setup guide](docs/one-command-classroom.md) for installation
links, WSL integration and resource guidance. The course's Python, PostgreSQL,
Java, C++, Node, TensorFlow, PyTorch and Spark tools run inside Docker, so you do
not need to install those language toolchains on your machine.

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

The repository currently requires access from its owner. Sign in to a GitHub
account with repository access before cloning or downloading a ZIP. For HTTPS
cloning, use a Git credential manager or authenticated GitHub CLI; do not paste
a personal access token into the clone URL. The local classroom itself needs no
GitHub login after you have downloaded it.

Clone the repository, enter its folder, check prerequisites and launch:

```sh
git clone https://github.com/sadatnfs/ds60sqlpy.git
cd ds60sqlpy
./classroom doctor
./classroom
```

`doctor` checks the local engine and configuration without starting services.
The final command builds images locally with **visible build logs**, starts
PostgreSQL and all ten ordinary runtime workers, waits for readiness, and opens
the browser. Keep the terminal open while it works. The first build needs
internet access, several gigabytes of downloads and time to install the image
dependencies. A log step marked `CACHED` was reused from an earlier build.
Nothing is pushed to a registry.

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
readable, while other languages need their runtime profiles. Run `./classroom`
later to prepare the full ordinary set.

### 3. Open the classroom and keep your work

When startup finishes, the launcher prints the actual local address ending in
**`/classroom`** and tries to open it. If no browser opens, copy that printed URL
into your browser. Docker chooses an available local port, so use the printed
address instead of assuming a fixed port. You can retrieve it with
`./classroom status`.

Choose a subject on the opening page and follow its first lesson. Source,
notes, saved results and progress stay in named Docker volumes on your machine;
PostgreSQL has its own volume. Stopping or replacing a container preserves
those volumes.

```sh
./classroom status      # Containers and the current browser address
./classroom logs        # Recent app and database logs
./classroom stop        # Stop this classroom while preserving saved work
./classroom            # Build current sources and resume the same workspace
```

If all images for your selected profiles already exist, `./classroom --no-build`
resumes them without rebuilding or preparing downloads. A starter-only setup
uses `./classroom --starter --no-build`. After deleting images, use the normal
build command again.

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
with 30 additional PySpark implementations. The statistics book maps its chapters to 1,005 topics in the source outline. The [72-chapter LLM reading route](docs/learning/llm-textbook.md)
connects mechanisms to a running subject-assistant case study; [Inside a
Transformer](docs/learning/inside-a-transformer.md) provides a connected
numerical explanation of the architecture.

For a first SQL course, start with `sql-start-01`, `sql-start-02` and
`sql-start-03`, then continue to `sql-01`. The classroom keeps this on-ramp
ahead of schema and operations topics.

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

The optional [MCP tutor](docs/mcp-tutor.md) can search content and help plan
study. It is read-only by default, reveals official solutions only on request,
and does not execute pad code. An AI tutor is optional; every lesson must explain
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
Running the classroom and developing its application are separate setup paths.
Optional native notebook, SQL and editor workflows are documented under
[setup](docs/setup/offline.md) and [dependency profiles](docs/dependency-profiles.md).

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
learning resources retain their own licenses. See [CONTRIBUTING.md](CONTRIBUTING.md)
for content attribution, verification and how to report a reproducible problem.
