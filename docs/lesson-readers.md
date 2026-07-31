# Offline lesson readers

Every catalog entry has a generated page under `lesson-pages/`. Start from
[`START_HERE.html`](../START_HERE.html), choose **Start lesson**, and use one
page for the complete learning sequence:

1. read the rendered companion guide;
2. open the real learner artifact in VS Code or Jupyter and do the work;
3. return to the readable preview when you need context; and
4. compare the rendered solutions only after an honest attempt.

The reader tabs never send a `.md`, `.ipynb`, `.py`, or `.sql` file directly
to the browser. Markdown becomes semantic HTML, notebook Markdown and code
cells become a read-only notebook preview, and Python/SQL source becomes an
escaped, line-numbered listing. Notebook outputs are never executed while the
pages are built or viewed. Untrusted rich HTML output is not reproduced.

Local Markdown and SQL links that are not themselves cataloged lesson
artifacts route to deterministic pages under `reference-pages/`. This includes
setup guides, curriculum documentation, README/AGENTS guidance, and linked SQL
support files. Those reference pages recursively rewrite their own local
Markdown/SQL links, so navigation never falls back to a raw source tab.

## Static and guided modes

The same reader URL works in both portal modes:

| Mode | Reader URL shape | Run controls |
| --- | --- | --- |
| Static/USB | `lesson-pages/<lesson-id>.html` over `file://` | A best-effort `vscode://file` link derived in the browser from the current repository location |
| Guided launcher | `/lesson-pages/<lesson-id>.html` on `127.0.0.1` | Allowlisted exact-artifact VS Code and notebook JupyterLab actions |

Static pages cannot safely start arbitrary native processes. The VS Code link
uses the official file URL handler and may require a browser confirmation. If
the operating system has not registered that handler, open the repository
folder in VS Code and use the catalog path printed beside the artifact.

In static mode, mark completion on `START_HERE.html`. Browser handling for
separate `file://` documents is not consistent enough to promise that a lesson
page checkbox and dashboard share one storage boundary, so the reader shows a
clear **Track completion on the course dashboard** link instead. In private
launcher mode, the tokenized lesson reader may show its own checkbox because
it writes to the same ignored `.learning/progress.json` boundary as the
dashboard and CLI.

Guided launcher mode is the recommended experience for a new learner after
setup. The server injects its in-memory token into each served reader. A reader
can then request only these fixed, catalog-resolved actions:

- open the guide, learner artifact, or indexed solution in VS Code; and
- open the exact cataloged learner notebook in JupyterLab; or
- create an ignored, editable guided notebook for a cataloged SQL lesson and
  open that notebook in JupyterLab.

Every Python and SQL reader also has an **Ask Codex about this lesson** panel.
It contains a read-only, copy-ready prompt built from that exact catalog entry:
stable ID, title, guide and learner paths, prerequisites, execution safety,
solution boundary, progressive coaching loop, and evidence-based done
condition. This is optional coaching context; the rendered guide before it
must still define and demonstrate the concept completely.

On Windows, double-click `START_DS60.cmd` rather than trying to make a static
browser page start local software. It performs readiness checks and reopens
the same course guide in authenticated loopback mode. SQL lesson run cards can
then request only the fixed `jupyter-sql` action for their own stable lesson
ID; the launcher generates the notebook under `.learning/sql/`.

The browser never supplies a shell command or unrestricted filesystem path.
See [Learning portal](learning-portal.md) for startup and security details.

## Offline and portability contract

Each lesson page embeds all of its CSS, JavaScript, guide content, learner
preview, and solution previews. Rendered references embed their own CSS and
source content. Neither surface loads a remote font, stylesheet, script,
image, or analytics service. Known links between catalog artifacts are
rewritten to the corresponding reader and section; for example, a guide's
learner-notebook link becomes `python-01.html#learner`.

The pages are generated from checked-in source artifacts. Do not edit the HTML
under `lesson-pages/` or `reference-pages/` by hand.

## Maintainer workflow

Generate and verify the readers:

```powershell
# Windows PowerShell (reuse $CoursePython from the setup/bootstrap guide)
& $CoursePython scripts\build_lesson_readers.py
& $CoursePython scripts\build_lesson_readers.py --check
& $CoursePython -m pytest tests\test_lesson_reader.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/build_lesson_readers.py
.venv/bin/python scripts/build_lesson_readers.py --check
.venv/bin/python -m pytest tests/test_lesson_reader.py
```

`src/ds60sqlpy/lesson_reader.py` is the renderer and
`scripts/build_lesson_readers.py` is its command-line entry point. The generator
escapes source content, blocks unsafe Markdown URL schemes, resolves paths
inside the repository, follows only the deterministic closure of local
Markdown/SQL links reachable from the course entry points, and removes only
obsolete generated `.html` files from the selected output directories.
