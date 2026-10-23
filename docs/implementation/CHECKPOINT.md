# Maintained implementation checkpoint

This file describes the architecture and continuation boundaries of the current
source. It is not a record of a particular developer's machine, test session or
hosted CI run. Use [validation](../validation.md) and the workflow results for
the exact revision being reviewed.

## Delivered application structure

`/classroom` provides one home and workspace for all registered subjects.
`/`, `/learn`, `/journeys` and `/journey-preview` are compatibility aliases for
that shell. The old independent Python/SQL and module pages are retired.
Subject selection, search, themes, lesson navigation, code or reading workspace,
notes and progress belong to this shared interface.

The directory combines the historical Python, PostgreSQL and engineering bridge
catalog with authored module subjects and the statistics/ML tutorial. Identity
and prerequisite metadata are derived from the loaders. Inspect the current
inventory rather than copying a past count:

```sh
python scripts/course.py catalog
python scripts/check_modules.py --json
```

Historical day labels, canonical lesson IDs and language variants remain stable.
The legacy catalog and module manifests are separate authoring contracts that
share one learner experience. See [ADDING_A_MODULE.md](ADDING_A_MODULE.md) before
choosing where an extension belongs.

## Presentation and learning modes

The shared renderer provides offline MathML and syntax highlighting. Reviewed
prose normalization runs before reader generation; copying a code block must
preserve source characters. The generated static library remains available
without the application server. Design-preview templates are developer tools,
not a second live classroom.

Practice lessons have progressive exercises, hints and separate solutions.
The statistics book is a theory-and-code tutorial with directly available
worked examples and answered interview discussions. Reading markers and
learner-confirmed completion do not certify understanding.

## Runtime and storage boundaries

The shared `./classroom` launcher builds local images, starts the selected
profiles, waits for readiness and opens the actual loopback address. Its default
includes the ordinary CPU and language workers. Windows uses WSL 2 with an
integrated Linux-container engine. Host compilers and databases are unnecessary
for the ordinary classroom route.

The app preserves Python/SQL pads, coaching phases and immutable run receipts.
Module lessons preserve source, notes, variants and job history through their
own storage adapter. Viewing a saved result is read-only. Reconnection must not
replay a job whose outcome is unknown, and a receipt-save failure must not hide
a successful execution.

Named Compose volumes hold learning state and PostgreSQL data. Reuse the same
project name to resume that workspace. Keep volumes when replacing containers
or removing images, and follow the documented backup workflow before moving
machines. Private runtime sessions and credentials are separate from portable
learner exports.

Kubernetes operations require deliberately prepared, owned local resources.
Pretrained models, GPU experiments, external APIs and longer-running services
have separate preparation and capability requirements. A small offline example
demonstrates its mechanism; it does not prove model quality, production capacity
or safety on arbitrary infrastructure.

## Where to make changes

| Change | Maintained source |
| --- | --- |
| Classroom behavior and styles | `src/ds60sqlpy/assets/classroom.*`, `classroom.py`, `lab.py` |
| Module content and admission | `courses/<subject>/`, `modules.py`, `module_extensions.py` |
| Worker execution | `module_jobs.py`, `worker_operations.py`, reviewed adapters, `docker/workers/` |
| Legacy identity and planner | `catalog_builder.py`, `curriculum/extensions/`, `catalog.py`, `study_plan.py` |
| Rendering | `lesson_reader.py`, `reader_math.py`, `reader_content.py` |
| Local build/start | `classroom`, `scripts/classroom.sh`, `compose.classroom.yaml` |
| Tutoring integration | `mcp_server.py`, repository learning skill |
| Future authoring | [Add a learning path skill](../../.agents/skills/add-learning-path/SKILL.md), [content contract](../content-authoring.md) |

Python filenames without a full path are under `src/ds60sqlpy/`.

## Continue and qualify a change

1. Read root and subject guidance; inspect current changes and the selected
   source generator before editing its output.
2. Implement one coherent change, preserving IDs, saved-work namespaces and
   the distinction between content registration and runtime capability.
3. Run focused behavioral checks, relevant reference programs and generated
   document checks. Review a changed learner flow in the browser.
4. Run the grouped parallel suite and applicable CI gates. Keep structural
   checks, live runtime receipts and target-platform results distinct.
5. Record actual commands, revision and environment in release or CI artifacts.
   Do not copy a historical success count into a claim about a new revision.
6. Clean only the resources created for the check and retain learning volumes.

No file here implies that a background process, acceptance project or automation
is running. Discover current runtime state through `./classroom status` and the
container engine before acting on it. No claim of Windows, Linux, architecture
or optional-runtime acceptance follows merely from a Dockerfile or workflow.
