# DS60 Classroom: learn at your own pace

[![Course validation](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml/badge.svg)](https://github.com/sadatnfs/ds60sqlpy/actions/workflows/ci.yml)

DS60 is one local classroom for programming, data science, statistics, machine
learning and systems. Its opening page brings **Python, PostgreSQL, the
engineering bridge and every newer subject together**. Choose any path, review
its prerequisites, and study at a pace that fits you. Historical day numbers
are lesson labels, not deadlines.

The supported product runs entirely in **Linux Docker containers**. Windows
uses WSL 2, macOS uses its Docker engine's Linux environment, and Linux uses a
local Docker engine. Native Windows backends and native executable bundles are
retained historical tooling, outside the supported delivery and release gates.

## Start or resume the classroom

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
Java, C, C++, Go, C#, Rust, Swift, Node, TensorFlow, PyTorch and Spark tools run inside Docker, so you do
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
On a new project, the final command prepares PostgreSQL and all sixteen ordinary
runtime workers. It builds **only missing images**, with visible logs, starts the
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
./classroom status      # Containers and the current browser address
./classroom logs        # Recent app and database logs
./classroom stop        # Pause this classroom and keep saved work
./classroom             # Resume; prepare only missing images if necessary
./classroom resume      # Resume strictly without building or pulling
./classroom --rebuild   # Deliberately build updated sources and restart services
```

`resume` and `--no-build` are equivalent. They fail with an actionable message
if a needed image is unavailable; they never start a download or build. Use
ordinary `./classroom` after deleting an image to prepare the missing image.
After downloading updated course sources or pulling repository changes, use
`./classroom --rebuild` to put those changes inside the images. A normal resume
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
same classroom. Use **All subjects** to change direction without opening a
second application.

| Subject | Start here | Main direction |
| --- | --- | --- |
| Python and data science | [Python](python/ds-60day/README.md) | First programs, NumPy, pandas, algorithms, analysis and delivery |
| PostgreSQL | [SQL](sql/postgres-60day/README.md) | First queries, relational reasoning, analytics, performance and operations |
| Python + PostgreSQL engineering | [Bridge](bridge/README.md) | Safe database access, transactions, testing and pipelines |
| Statistics and machine learning | [Tutorial book](courses/statistics-ml/README.md) | Theory, modeling choices, worked Python examples and interview explanations |
| C | [C17](courses/c/README.md) | Memory, pointers, representation, compilation and reliable systems programs |
| C++ | [C++20](courses/cpp/README.md) | Language foundations, ownership, compilation and larger programs |
| Go | [Go](courses/go/README.md) | General-purpose programs, concurrency, services and Kubernetes-oriented engineering |
| C# | [C# and .NET](courses/csharp/README.md) | Types, collections, LINQ, async programming and application design |
| Rust | [Rust and Arrow](courses/rust/README.md) | Ownership, traits, concurrency, systems design and columnar data |
| Swift | [Swift](courses/swift/README.md) | Language, concurrency and app architecture, with explicit Apple-platform project boundaries |
| Docker | [Docker](courses/docker/README.md) | Images, Dockerfiles, Compose, networking, data, security and recovery |
| Java | [Java](courses/java/README.md) | Objects, types, collections, concurrency and practical engineering |
| JavaScript and TypeScript | [JavaScript/TypeScript and D3](courses/javascript-typescript/README.md) | Browser and Node concepts, types, async code and a 24-lesson D3 visualization specialization |
| Kubernetes | [Kubernetes](courses/kubernetes/README.md) | Workloads and a deep 24-lesson networking/operations extension, with bounded owned-cluster practice |
| Scala and Apache Spark | [Scala/Spark](courses/scala-spark/README.md) | Scala, distributed data processing and companion PySpark implementations |
| TensorFlow | [TensorFlow/Keras](courses/deep-learning-tensorflow/README.md) | Tensors, optimization, architectures and model workflows |
| PyTorch | [PyTorch](courses/deep-learning-pytorch/README.md) | Autograd, training state, architectures and reproducibility |
| Natural language processing | [NLP](courses/nlp/README.md) | Text representation, classical baselines, neural methods and evaluation |
| LLM mechanisms | [LLM theory](courses/llm-theory/README.md) | Tokens, Transformers, attention, generation and adaptation mechanics |
| Applied LLM systems | [Applied LLMs](courses/llm-applied/README.md) | RAG, evaluation, fine-tuning, tools and subject assistants |
| GPU computing and CUDA | [CUDA, Python and GPU Spark](courses/cuda/README.md) | GPU architecture, C++ kernels, Python, PyTorch/TensorFlow and RAPIDS/Spark, with portable CPU study paths |
| Web development | [HTML, CSS and PHP](courses/web-development/README.md) | Semantic pages, responsive layouts, accessibility, browser interactions and server-side applications |

The library contains **1,110 canonical lessons and chapters across 22 subjects**,
with separately saved language and framework variants. The statistics book maps its chapters to 1,005 topics in the source outline. The [72-chapter LLM reading route](docs/learning/llm-textbook.md)
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

### Optional Docker Hub distribution

Local builds remain the default. After the owner has published a matching
release and architecture, a learner can download the images instead:

```sh
./classroom --from-hub YOUR_DOCKERHUB_USER --tag 0.4.0
```

Replace the placeholder with the actual publisher's Docker Hub namespace. The
project remembers that choice; later `./classroom resume` still performs no
builds or pulls. No public image release is implied by the command above.
See [building, testing, publishing and pulling images](docs/dockerhub.md) for
step-by-step instructions, account authentication, architecture tags and the
disabled-by-default manual GitHub publication workflow.

To install this source release locally with visible build logs:

```sh
./classroom --all --local-build --tag 0.4.0 --rebuild
```

Keep your existing `--project NAME` on every command when using a custom project.

### Reading and execution

Mathematical explanations render as typeset equations, including fractions,
subscripts, vectors and matrices. Fenced code examples carry language-aware
syntax highlighting. Both work from bundled local rendering resources without
an external CDN. Code remains selectable so you can copy an example into its
appropriate workspace.

C, C++, Go, C#, Rust, Swift and Java compile in Linux Docker workers. JavaScript
uses Node for server-side lessons and an isolated browser preview for the D3
specialization. TypeScript is checked and compiled before Node execution.
Python, TensorFlow, PyTorch and Spark use their declared profiles.

HTML and CSS render in an isolated offline browser preview, including inline
JavaScript interactions. PHP runs in its own CLI worker with PDO SQLite. Real
HTTP sessions and multi-file applications use the web subject's separate,
loopback-only Docker project. The pad and the web server are explicitly different
execution environments.

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
to a different machine or storage configuration. Earlier host-folder launchers
retain their own `.learning` state; they are compatibility alternatives, not
an additional required classroom. See [persistence and transfer](docs/one-command-classroom.md).

## Optional tools and compatibility routes

The static [START_HERE.html](START_HERE.html) remains an offline reading library.
Host VS Code/Jupyter instructions remain as compatibility references for people
who deliberately prepare them. They are outside the supported Docker product;
native Windows environments and executable bundles are not release targets. Existing `/learn` and `/journeys` links are compatibility
entrypoints into the unified classroom; new documentation uses `/classroom`.

To use an assistant as a study companion, open this repository in your coding
assistant and ask it to use the
[learning companion skill](.agents/skills/guide-ds60sqlpy-learning/SKILL.md).
For example: "Help me resume my saved Go lesson. Read my current attempt, explain
one concept at a time and give hints before solutions. Keep my notes and progress."
The skill covers every subject and distinguishes reading, coding and external
project workflows. It can also help diagnose startup without reinstalling tools
or resetting your workspace. Share only the source and outputs you want reviewed.

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
Format maintained code across the repository with `./scripts/format-repo`, or
check formatting without changing source files with `./scripts/format-repo --check`.
Run `./scripts/lint-repo` for read-only static source checks.
The commands use a dedicated Docker toolchain, so contributors do not need every
language compiler on their host. See [the formatting workflow](CONTRIBUTING.md#format-the-repository)
for generation order, coverage and optional pre-commit checks.
Running the classroom and developing its application are separate setup paths.
Use Linux or WSL 2 for the validated contributor environment. Historical host
notebook, SQL and editor recipes remain under [setup](docs/setup/offline.md) and
[dependency profiles](docs/dependency-profiles.md), outside the product support contract.

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
