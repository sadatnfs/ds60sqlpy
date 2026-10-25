# Choose the runtime a lesson needs

A subject is a learning path. A runtime profile is the prepared environment
that executes an artifact. Several subjects can share one profile, and one
subject can contain reading lessons and multiple language variants.

Start with `./classroom` for the saved selection. A new project prepares all
sixteen ordinary workers. For a smaller installation:

```sh
./classroom --starter
```

This prepares the app, PostgreSQL and Python Core while keeping the complete
library readable. Choose additional profiles or the full ordinary set:

```sh
./classroom --profile cpp20 --profile php-cli
./classroom --all
```

An explicit profile list replaces the remembered selection with Core plus
those names. It does not stop unselected workers already running. To reduce
the active set, stop the classroom before starting the smaller selection.
Always repeat your custom `--project NAME` if you use one.

## Ordinary worker profiles

| Profile | Source contract | Typical use |
| --- | --- | --- |
| `python-core` | Python source / supported notebook-style cells | Python, NumPy, pandas, statistics, NLP and CPU models |
| `cpp20` | `main.cpp`, C++20 | C++ language and bounded systems examples |
| `c17` | `main.c`, C17 | C, memory and POSIX examples |
| `go` | `main.go` with prepared standard library | Go programs and offline controller models |
| `csharp-dotnet` | `Program.cs` in a fixed .NET project | C# language and application-core examples |
| `rust-stable` | `main.rs` with prepared Arrow dependencies | Rust and columnar data |
| `swift-linux` | `main.swift` with an explicit entry point | Portable Swift and Foundation |
| `java21` | `Main.java` with public `Main` | Java and prepared JVM libraries |
| `javascript-node` | `main.mjs` | Node JavaScript |
| `typescript-node` | `main.mts`, strict NodeNext checking | TypeScript compiled for Node |
| `tensorflow-cpu` | Python with prepared TensorFlow | TensorFlow/Keras CPU lessons |
| `llm-torch-cpu` | Python with prepared PyTorch | PyTorch and tensor-based LLM CPU lessons |
| `scala-jvm` | `Main.scala` with `object Main` | Scala language foundations |
| `spark-local-scala` | Scala application in local Spark | Scala/Spark batch and bounded streaming |
| `spark-local-python` | Python application in local Spark | PySpark variants |
| `php-cli` | `main.php` with PDO SQLite | PHP language and application-core examples |

PostgreSQL is included with the classroom, not an additional worker flag.
HTML/CSS and browser JavaScript/D3 use the bundled preview and need no separate
compiler worker. Their `html-browser` and `javascript-browser` labels are not
launcher `--profile` selections.

A ready worker establishes its declared runtime is available. Read each
lesson's package, fixture and resource requirements before treating that as
evidence for a larger project. Run does not install dependencies.

## Optional GPU and cluster environments

NVIDIA profiles `cuda-cpp`, `cuda-python`, `pytorch-cuda` and
`tensorflow-cuda` are excluded from ordinary startup and `--all`. They need
explicit device selection and compatible hardware, driver and container
support. Follow [CUDA setup](cuda-classroom.md) and the selected variant's
instructions. CPU workers remain CPU environments on a GPU-equipped host.

Kubernetes uses a separately prepared owned cluster and scoped capabilities.
The classroom receives neither the engine socket nor an ambient cluster
configuration. Follow [Kubernetes setup](modules-runtime.md#prepare-and-run-the-owned-kubernetes-lab).

Real web servers, multi-file C++ projects, Apple app development, long model
training and larger Spark clusters are explicit project workflows. A
single-source pad does not implicitly provide their additional capabilities.

## Optional Python package sets for local builds

The app and Python Core worker use locked Core extras: notebooks, data,
bridge, quality, professional and SQL notebooks. Advanced Python lessons
can declare additional package groups.

| Package group | Examples of additional libraries |
| --- | --- |
| `ml` | XGBoost, LightGBM, SHAP, LIME, pmdarima, imbalance tools, Numba |
| `production` | FastAPI, Dask, MLflow, Prefect, Pydantic, Uvicorn |
| `deep-learning` | PyTorch and torchvision for the relevant Python examples |
| `nlp` | Transformers, datasets, evaluate, spaCy, accelerate |
| `geo` | GeoPandas, geodatasets, contextily, NetworkX |
| `advanced` | All five groups above |
| `mcp` | Optional stdio tutoring adapter dependency |

These package groups differ from worker names. For example, `tensorflow-cpu`
selects a dedicated worker, while `DS60_DOCKER_PROFILES=ml` changes packages
installed in a locally built app/Core image.

Preserve existing settings when adding `DS60_DOCKER_PROFILES` to your ignored
`.env` file, then rebuild deliberately. An explicit one-command example is:

```sh
DS60_DOCKER_PROFILES=ml ./classroom --starter --local-build --rebuild
```

That assignment applies to that command. Retain the group in your settings
for later rebuilds if needed. Only declared extras from `uv.lock` are installed;
package-source strings and arbitrary installer arguments are rejected.

Published Hub images have the publisher's prepared package set. Editing a
local build setting does not add packages to a pulled image. Use the release's
capability contract or make a deliberate local build.

## Resources and offline use

A container's memory limit is different from the engine VM's available memory.
`DS60_LAB_MEMORY` controls the app container; worker limits and total engine
allocation are separate. Choose fewer profiles when RAM or disk is constrained.

Package installation does not download every model, tokenizer or dataset.
Prepare assets through the lesson's workflow and keep their storage separate
from temporary job files. The named learning volume preserves classroom work;
it does not automatically preserve arbitrary temporary caches or checkpoints.

See [offline preparation](setup/offline.md), [image distribution](dockerhub.md)
and [the launcher guide](one-command-classroom.md) for the corresponding steps.
