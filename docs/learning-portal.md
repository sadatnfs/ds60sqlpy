# Learning portal

`START_HERE.html` is the visual front door to the course. It is generated from
`curriculum/catalog.json`, so its 154 lesson cards link to the same guides,
learner artifacts, solutions, prerequisites, levels, and network labels used
by the command-line tools.

## Choose a mode

| Mode | Start it | Progress location | Native launch buttons |
| --- | --- | --- | --- |
| Static/offline | Double-click `START_HERE.html` | This browser's local storage | No; browser links still open every artifact |
| Private launcher | Run `scripts/learning_portal.py` | Ignored `.learning/progress.json` plus a browser copy | Yes, unless `--no-launches` is supplied |

The static file contains its styles, scripts, and catalog data. It does not
load a font, analytics script, image, or API from the internet.

## Start private launcher mode

Complete setup first, then run:

```powershell
# Windows PowerShell
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
- **Open in VS Code** on a lesson card resolves that stable catalog ID and
  opens only its cataloged learner artifact.
- **Launch Python JupyterLab** opens `python/ds-60day/notebooks`.
- **Launch PostgreSQL notebook lab** opens
  `bridge/professional/notebooks`.

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
- requires the expected `Host`, token, and same origin for writes;
- sends no cross-origin access headers;
- blocks hidden directories, environment files, progress, caches, and common
  credential/private-key names from file serving;
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
& $CoursePython -m pytest tests\test_course_guide.py tests\test_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/build_course_guide.py
.venv/bin/python scripts/build_course_guide.py --check
.venv/bin/python -m pytest tests/test_course_guide.py tests/test_portal.py
```

Browser QA should cover desktop and narrow mobile layouts, static `file://`
behavior, launcher mode, keyboard focus, filter/pagination behavior,
progress export/import, console errors, and unexpected network requests.
