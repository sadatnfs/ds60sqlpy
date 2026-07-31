# Learning portal

`START_HERE.html` is the visual front door to the course. It is generated from
`curriculum/catalog.json`, so its 154 lesson cards link to the same guides,
learner artifacts, solutions, prerequisites, levels, and network labels used
by the command-line tools.

## Choose a mode

| Mode | Start it | Progress location | Native launch buttons |
| --- | --- | --- | --- |
| Static/offline | Double-click `START_HERE.html` | This browser's local storage | No; use rendered reading pages |
| Private launcher | Double-click `START_DS60.cmd` on Windows, or run `scripts/learning_portal.py` | Ignored `.learning/progress.json` plus a browser copy | Yes, unless `--no-launches` is supplied |

The dashboard displays a prominent mode banner beneath its hero. Do not infer
the mode from the URL or button styling: **You are in portable reading mode**
means native apps cannot start, while **Private launcher mode is active**
means the authenticated loopback bridge is ready.

The static file contains its styles, scripts, and catalog data. It does not
load a font, analytics script, image, or API from the internet.

Static mode is a reader and setup guide. Browsers cannot execute a `.py`,
`.ipynb`, or `.sql` lesson safely just by opening its source. On Windows,
`START_DS60.cmd` is therefore the recommended front door: it prepares and
checks the environment before enabling the portal's fixed VS Code and
JupyterLab actions.

Setup, documentation, and incidental SQL links open generated pages under
`reference-pages/`, not raw Markdown or SQL. In static mode, use the lesson
reader's **Track completion on the course dashboard** link and mark the card
on `START_HERE.html`. The per-lesson completion checkbox appears only in
private launcher mode, where the dashboard, reader, CLI, and Codex can share
the ignored progress file.

## Start private launcher mode

Complete setup first, then run:

```powershell
# Windows PowerShell
# Or simply double-click START_DS60.cmd, which performs readiness checks first.
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\learning_portal.py
```

The resolver supports both the standard `venv` layout and the Anaconda
conda-prefix fallback. Reuse `$CoursePython` for later Windows commands in the
same PowerShell window.

```bash
# macOS/Linux
.venv/bin/python scripts/learning_portal.py
```

The command chooses a free loopback port, prints the private URL, and opens the
default browser. Keep that terminal open; press `Ctrl+C` to stop the server.
Jupyter inherits `PATH` and `DS60_DATABASE_URL` from this terminal. Native
Windows PostgreSQL users should complete the
[password-file handoff](setup/windows.md#let-the-guided-notebook-authenticate-without-a-hidden-prompt)
and start the portal from that configured PowerShell window; the portal never
asks for or stores a database password.

Useful options:

```text
--no-browser   print the URL without opening a browser
--no-launches  synchronize progress but disable native process actions
--port 8765    request a particular loopback port
```

You can also choose **Terminal → Run Task → Course: Learning portal** in
Visual Studio Code.

## What can be launched

Every native action is mapped in course code; the browser never supplies a
shell command or unrestricted filesystem path.

- **Open repository in VS Code** opens only the repository root.
- **Open notebook** on a Python/bridge notebook card starts JupyterLab with
  that exact cataloged learner notebook.
- **Open SQL workspace** on a SQL card creates and opens that lesson's guided
  notebook directly.
- **Open in VS Code** on a lesson reader resolves that stable catalog ID plus
  its guide, learner, or indexed solution selector.
- **Open exact notebook** starts JupyterLab with that cataloged `.ipynb`.
- **Create/open guided SQL notebook** creates an ignored, editable notebook
  and SQL copy for that stable SQL lesson, then starts JupyterLab with that
  exact notebook. It never accepts a browser-supplied path or command.
- **Launch Python JupyterLab** opens `python/ds-60day/notebooks`.
- **Open PostgreSQL magics lab** opens `bridge/professional/notebooks`. This is
  the JupySQL `%sql`/`%%sql` integration lab, not the normal way to run a full
  lesson script.

VS Code needs its `code` launcher. If it is unavailable, open the repository
with **File → Open Folder**. Jupyter actions require the repository `.venv`;
run setup first if the portal reports that it is missing.

## Progress and portability

A completion check means the learner can explain the concept and produce a
working attempt—not merely that a file was opened.

Private launcher mode and these CLI commands share
`.learning/progress.json`:

```powershell
# Windows PowerShell
& $CoursePython scripts\course.py progress show
& $CoursePython scripts\course.py progress complete python-01 --notes "Evidence"
```

```bash
# macOS/Linux
.venv/bin/python scripts/course.py progress show
.venv/bin/python scripts/course.py progress complete python-01 --notes "Evidence"
```

The progress directory is intentionally ignored. Use **Export progress** to
create a JSON backup before changing browsers or making a source-only USB
copy. **Import progress** validates stable lesson IDs before replacing the
local completion set. Setup-checklist state remains browser-local.

## Local security boundary

The private launcher:

- binds only to `127.0.0.1`, never a LAN or public interface;
- generates a new in-memory request token for each session;
- requires the exact loopback `Host` for every request, plus the session token
  and same origin for API writes;
- sends no cross-origin access headers;
- serves only `START_HERE.html`, generated lesson readers, and generated
  reference pages; raw repository source, hidden directories, environment
  files, progress, caches, and credential/private-key files are not exposed;
- limits JSON request size;
- allows only the fixed actions listed above.

This boundary is defense in depth for a learner convenience tool. Do not
modify it to accept arbitrary commands, paths, remote binding, or credentials.

## Maintainer workflow

Edit `scripts/build_course_guide.py`, never `START_HERE.html` directly:

```powershell
# Windows PowerShell
& $CoursePython scripts\build_course_guide.py
& $CoursePython scripts\build_course_guide.py --check
& $CoursePython scripts\build_lesson_readers.py
& $CoursePython scripts\build_lesson_readers.py --check
& $CoursePython -m pytest tests\test_course_guide.py tests\test_lesson_reader.py tests\test_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/build_course_guide.py
.venv/bin/python scripts/build_course_guide.py --check
.venv/bin/python scripts/build_lesson_readers.py
.venv/bin/python scripts/build_lesson_readers.py --check
.venv/bin/python -m pytest tests/test_course_guide.py tests/test_lesson_reader.py tests/test_portal.py
```

Browser QA should cover desktop and narrow mobile layouts, static `file://`
behavior, launcher mode, keyboard focus, filter/pagination behavior,
progress export/import, generated local-reference navigation, the mode-specific
completion control, console errors, and unexpected network requests.
