# Documentation map

DS60 has one Docker classroom and one maintained source tree. Historical day
numbers identify lessons; they do not limit your pace or the number of subjects.

## Learn or return to saved work

1. Read the [front README](../README.md) for supported hosts and the subject directory.
2. Follow [one-command setup](one-command-classroom.md), then [first success](setup/first-success.md).
3. Use the [classroom guide](classroom-experience.md) for pads, live previews, results and language switching.
4. Choose a route with [placement and pacing](learning-paths.md), lesson prerequisites and subject READMEs.
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
- [Docker Hub distribution](dockerhub.md) covers publishing, pulling, architecture tags and the protected manual workflow.
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

## Connected textbook routes

The [LLM textbook route](learning/llm-textbook.md) connects mechanisms and applied
systems. [Inside a Transformer](learning/inside-a-transformer.md) gives a numerical
explanation. [Professional routes](professional-paths.md) deepen Python, SQL and
cross-language engineering. All subject entrances are in the front README and
classroom chooser.
