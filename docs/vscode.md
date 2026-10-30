# Optional editor and notebook workflow

The browser classroom needs no editor extension or host language toolchain. Use
VS Code to inspect source, contribute or work on an explicit external project.
Open the repository root with `code .`, or open that folder from the editor.
Windows contributors use their WSL checkout and its Linux terminal.

## Contributor Python and notebooks

Prepare the environment using [CONTRIBUTING.md](../CONTRIBUTING.md), then select
`.venv/bin/python` for Python tasks. Notebook kernel selection is separate: select
that same environment and verify it in a cell:

```python
import sys

print(sys.executable)
print(sys.version)
print(2 + 3)
```

The path must identify this checkout's environment, and the last line must print
`5`. A friendly kernel name alone is insufficient with several checkouts. Restart
the kernel after changing installed packages. Keep source notebooks unexecuted
in Git and save personal outputs separately.

`.vscode/extensions.json` contains optional Python, Ruff, notebook, PostgreSQL and
Markdown conveniences. Extensions do not install or qualify Docker runtime tools.
The repository does not ship a separate native Windows installer or devcontainer route.

## Repository tasks and formatting

Inspect `.vscode/tasks.json` for maintained task names. Classroom tasks delegate
to `./classroom`; contributor checks use the selected interpreter. The contributor
serve command runs the same HTTP interface on loopback, without provisioning workers
or synchronizing local `.learning/` files with a Docker project.

Use the shared formatter and linter:

```sh
./scripts/format-repo
./scripts/lint-repo
```

Editor format-on-save is not a substitute for the pinned release checks. New
languages need reviewed formatting, lint and runtime adapters.

## SQL, projects and tutoring

Use the classroom SQL pad for normal study. For an explicit external client,
obtain the actual port from `./classroom status` and use only the disposable
`advanced_sql_training` database. Do not assume port 5432 or commit credentials.
Complete scripts require `psql` semantics that a query editor may not reproduce.
See [guided SQL notebooks](guided-sql-notebooks.md) and [PostgreSQL in Jupyter](setup/jupyter-postgresql.md).

Multi-file C++, Java, Rust, Go, C#, Swift and web projects follow their own fixture
READMEs. Single-file pad success does not qualify an external project toolchain.

Open your coding assistant from the repository root so it discovers AGENTS files and both skills.
Use the learning skill for explanations and learner-directed practice, and the
add-learning-path skill for curriculum development. Share the actual attempt:
reference code and an unseen Docker pad are different sources.

Keep personal experiments in ignored `.learning/` or `artifacts/` locations and
back them up separately. [Documentation map](README.md) links the maintained routes.
