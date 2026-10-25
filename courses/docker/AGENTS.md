# Docker curriculum guidance

Read the root AGENTS.md and the add-learning-path skill. This subject is host-only reading/practice: the browser saves worksheets and renders commands, but never receives a Docker socket or executes engine commands. Windows commands use Bash inside WSL 2 with a Linux-container engine.

The durable source is authoring/chapters.py, rendered by authoring/build.py. Preserve docker-001 through docker-042 and regenerate after edits. Each lesson has two worked examples, six progressive evidence tasks, separate answer-free worksheets and explanatory solutions. Keep runtime observations distinct from synthetic diagrams and model validation.

The compose-lab fixture is a single-process standard-library teaching server with a persistent counter. It is not a public service or a safely replicated database. Keep host publication on loopback, non-root execution, read-only root, resource bounds and project-scoped cleanup. Preserve volumes by default. Never use global prune, ambient remote contexts, privileged mode or an engine socket to make a lesson appear executable.

Do not use em dashes. Do not add private credentials, host identifiers or fabricated runtime receipts. New fixtures need an inventory entry and separate actual engine qualification by the integrating agent.

Use [the subject authoring guide](authoring/README.md) for regeneration and
[the module contract](../../docs/implementation/ADDING_A_MODULE.md) for shared
runtime integration. Root guidance owns common formatting, saved-work and
publication rules; subject changes must preserve those boundaries.
