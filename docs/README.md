# Documentation map

DS60 has one Docker classroom and one maintained source tree. Historical day
numbers identify lessons; they do not limit your pace or the number of subjects.

## Learn or return to saved work

1. Read the [front README](../README.md) for supported hosts and the subject directory.
2. Follow [one-command setup](one-command-classroom.md), then [first success](setup/first-success.md).
3. Use the [classroom guide](classroom-experience.md) for pads, live previews, results and language switching.
4. Choose a route with [placement and pacing](learning-paths.md), the [scientist roadmap](scientist-roadmap.md), lesson prerequisites and subject READMEs.
5. Consult [troubleshooting](troubleshooting.md) for an observed failure and [storage boundaries](local-files-and-caches.md) before cleanup.

Windows uses [WSL 2](setup/windows.md); [macOS](setup/macos.md) and [Linux](setup/linux.md)
use the same Linux-container product. [Docker basics](docker-beginners.md) explains
prerequisites. [Manual Compose and backup](docker-classroom.md) covers transfer.
Normal startup is `./classroom`; strict return is `./classroom resume`.

## Understand an execution environment

- [Runtime profiles](modules-runtime.md) and [dependency labels](dependency-profiles.md) distinguish languages, package sets and prepared workers.
- [CUDA preparation](cuda-classroom.md) explains CPU study, optional NVIDIA execution and GPU evidence.
- [Offline use](setup/offline.md) and [source readers](lesson-readers.md) separate prepared execution, reading and optional downloads.
- [Python package customization](docker-profiles.md) covers deliberate app-image extras.
- [Docker Hub distribution](dockerhub.md) covers CI publication on marked main commits, combined release tags, manual architecture tags, pulling and safe resume.
- [Guided SQL notebooks](guided-sql-notebooks.md), [PostgreSQL in Jupyter](setup/jupyter-postgresql.md) and [editor use](vscode.md) are optional prepared workflows.

## Learn with a coding assistant

Start with [AI tutoring](learning-with-an-ai-tutor.md). The repository's
[learning skill](../.agents/skills/guide-ds60sqlpy-learning/SKILL.md) guides placement,
explanation, progressive hints and review across all subjects. [MCP tutoring](mcp-tutor.md)
provides read-only curriculum tools by default. It does not execute code or
implicitly read private Docker pads. Tutorial books expose worked explanations;
practice lessons keep attempts and reference solutions separate.

## Develop or add a subject

Start with [CONTRIBUTING.md](../CONTRIBUTING.md), [AGENTS.md](../AGENTS.md) and the
[repository tour](repository-tour.md). The [checkpoint](implementation/CHECKPOINT.md)
describes current architecture. [Validation](validation.md) lists exact local and
CI gates and distinguishes source checks, execution and platform qualification.

Use the [authoring skill](../.agents/skills/add-learning-path/SKILL.md),
[extension playbook](curriculum-extension-playbook.md), [module contract](implementation/ADDING_A_MODULE.md)
and [content contract](content-authoring.md) for progression, durable sources,
registration, runtime preparation and browser acceptance. Read the closest subject
AGENTS file and authoring README. Derive IDs/counts from loaders, not another list.

The [curriculum map](curriculum-map.md), [gap backlog](curriculum-gap-backlog.md)
and [design references](curriculum-design-references.md) support teaching decisions.
Generated [practice coverage](practice-coverage.md) and [depth reports](lesson-depth-report.md)
are maintained outputs. The [founding subject plans](expansion/README.md) remain active
metadata; the former prototype application has been removed.

## Python applications and APIs

The [Python web route](learning/python-web.md) connects the original Python
foundations to HTTP, Flask, FastAPI and Django. Choose one framework branch after
the shared foundations, then use the owned service lab for actual browser,
PostgreSQL, WebSocket and SSE behavior. Short coding-pad programs terminate;
persistent servers have their own explicit Docker lifecycle.

## Connected textbook routes

The [LLM textbook route](learning/llm-textbook.md) connects mechanisms and applied
systems. [Inside a Transformer](learning/inside-a-transformer.md) gives a numerical
explanation. [Professional routes](professional-paths.md) deepen Python, SQL and
cross-language engineering. All subject entrances are in the front README and
classroom chooser.

## Numerical, statistical and visualization extensions

[JAX](../courses/jax/README.md) covers CPU numerical transformations and explicit
optional accelerator workflows. [R](../courses/r/README.md) adds statistical
programming and graphics. [DAX](../courses/dax/README.md) is an offline source and
worked-reference course. The [statistics tutorials](../courses/statistics-ml/tutorials/README.md)
connect experimentation, learning theory and scientific analysis to executable
cases. [Data visualization](../courses/data-visualization/README.md) pairs Python
and JavaScript implementations.

See [textbook rendering](textbook-rendering.md) for TeX and typography and
[plotting](plotting.md) for captured figures, interactive charts and saved results.

## Applied science and engineering routes

[Applied Science](../courses/applied-science/README.md) and
[Bayesian Computing](../courses/bayesian-computing/README.md) provide complete
worked tutorial answers. [Julia](../courses/julia/README.md),
[Polars](../courses/polars/README.md), [dbt](../courses/dbt/README.md),
[ML engineering](../courses/ml-engineering/README.md) and
[LLM evaluation](../courses/llm-evaluation/README.md) add distinct programming and
applied-system progressions. The [scientist roadmap](scientist-roadmap.md) maps
these to the earlier recommendations and explains prerequisites and limits.

The [Data and ML Engineering book](../courses/data-ml-engineering/README.md)
connects these foundations through 72 worked chapters, including the complete
LLM request, model loading, scheduling, decoding and SSE response lifecycle.
[Apache and open-data platforms](../courses/apache-data-platforms/README.md)
provides 88 tutorials and separately prepared service workshops. Its
[qualification ledger](../courses/apache-data-platforms/authoring/ENVIRONMENTS.md)
distinguishes actual library/service checks from prepared external routes.
Delta Sharing is included as an open data protocol rather than an Apache project.

Separate owned projects cover [dbt configuration](../courses/dbt/projects/retail/README.md),
[a real local ML service](../courses/ml-engineering/projects/local-system/README.md),
[data-product ingestion and publication](../courses/data-ml-engineering/projects/data-product/README.md),
[LLM inference and streaming](../courses/data-ml-engineering/projects/inference-service/README.md)
and [Stan with JSON data](../courses/bayesian-computing/projects/normal-mean/README.md).
Their instructions explain preparation, saved outputs and cleanup independently
of ordinary classroom pads.


## Advanced modeling research

The [Spark, PyTorch and TMB report](research/spark-torch-tmb.md) maps the modeling
questions to the new chapters, implementation and runtime evidence. The
[Brad Bell and native AD review](research/brad-bell-autodiff.md) covers the pinned
repository survey and explains the direct C++ experiment's scope. Explore the
[independent Spark likelihood package](../packages/spark-likelihood/README.md)
and the [standalone native AD example](../examples/native-ad-core/README.md)
through those reports. The native experiment is a serial C++ demonstration;
it does not implement a Spark/TMBad connector.
