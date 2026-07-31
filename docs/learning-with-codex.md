# Learning with Codex

Codex can act as a tutor, reviewer, debugger, and study planner for this repository. It is optional: all course content and local execution should remain usable without Codex.

Codex itself may require a network connection even when a lesson does not.
“Offline course” and “online tutor” are separate capabilities.

## Choose the right front door

| Situation | Start here | What it provides |
| --- | --- | --- |
| New or returning Windows learner | Double-click `START_DS60.cmd` | Discovers or prepares the repository environment, runs readiness checks, and opens the authenticated private portal |
| macOS/Linux learner after setup | Run `scripts/learning_portal.py` with the repository interpreter | Opens the same private portal with exact VS Code and JupyterLab actions |
| Source-only USB or no local server | Double-click [`START_HERE.html`](../START_HERE.html) | Fully static dashboard and rendered lesson readers; progress stays in that browser |

The Windows launcher asks before a connected first setup. It never requests or
stores a database credential and never resets PostgreSQL. Keep its terminal
open while learning; `Ctrl+C` stops the private portal.

Manual private-portal commands are:

```powershell
# Windows PowerShell
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython scripts\learning_portal.py
```

```bash
# macOS/Linux
.venv/bin/python scripts/learning_portal.py
```

The private launcher binds only to `127.0.0.1`. It can open the repository,
exact cataloged artifacts, exact notebook lessons, and catalog-restricted
guided SQL notebooks; it cannot accept arbitrary commands or paths. Pass
`--no-launches` if you want file-backed progress with every native process
action disabled.

Static mode remains useful without Python or a server, but a browser cannot
safely execute Python, notebooks, or SQL. Its optional `vscode://` link is a
best-effort handoff to a registered VS Code installation. If it does not work,
open the repository in VS Code and use the catalog path printed on the lesson
page.

## Start Codex in the repository root

Open the directory containing `README.md`. From there, Codex can discover:

- Root and track-specific `AGENTS.md` guidance
- The generated `curriculum/catalog.json` lesson index
- The `$guide-ds60sqlpy-learning` repo-local skill
- The environment doctor and validation commands

If Codex starts inside a nested lesson directory, tell it to work from the repository root.

## Use one rendered lesson page

Every **Start lesson** link opens
`lesson-pages/<lesson-id>.html`, a deterministic page generated from the
checked-in companion guide, learner artifact, and solutions. Markdown is
rendered as HTML, notebook cells receive a read-only notebook view, and Python
or SQL receives a readable source listing. The browser is for reading; edit
and run the actual artifact in VS Code or JupyterLab.

Setup, documentation, and other local Markdown/SQL links open generated
`reference-pages/` HTML, so they remain readable instead of becoming raw text
tabs. In static mode, return to `START_HERE.html` to mark completion; the
lesson-page checkbox is reserved for private launcher mode, where progress can
be synchronized safely.

Use this sequence with Codex:

1. Read the **Guide** tab and state the objective in your own words.
2. Predict what the first example will do.
3. Open the real **Learner artifact** and make an honest attempt.
4. Ask for one progressive hint at a time.
5. Open a **Solution** tab only after the attempt, then explain the difference.

Every Python, SQL, and bridge companion guide ends with
**Ask Codex about this lesson**. That block is not a generic “explain this”
prompt: it carries the stable lesson ID, exact guide and learner paths,
prerequisite boundary, topic-specific goals, safe run boundary, no-solutions
rule, evidence loop, and mastery condition. The rendered reader presents the
same contract in a dedicated copy panel, and the `START_HERE.html` lesson
selector embeds that exact guide-authored prompt as well. Prefer that lesson
prompt over rewriting file paths and context by hand.

The prompt is intentionally last. Read the definitions, examples, expected
observations, exercises, and troubleshooting first. If the lesson itself does
not make sense without Codex, report that as a curriculum defect; the coach is
there to adapt questions and hints, not to supply missing course material.

In private mode, the reader's buttons resolve only that stable lesson ID and
its cataloged files. For a Python notebook, choose **Open this notebook in
JupyterLab** or open it in VS Code and select `Python (ds60sqlpy)`. For a
Python source lesson, open the exact `.py` file in VS Code and run it with the
repository interpreter.

For a normal SQL lesson, choose **Create/open guided SQL notebook**. The
launcher creates an ignored notebook plus editable SQL copy under
`.learning/sql/<lesson-id>/` and opens that exact notebook in JupyterLab. It
preserves existing learner edits. The notebook runs the complete course script
through a fixed, non-shell `psql -f` path so `psql` meta-commands continue to
work; database preparation remains a separate, explicitly confirmed reset of
only `advanced_sql_training`. Use `bridge-jupyter-01` instead when the learning
objective is short JupySQL `%sql`/`%%sql` exploration. See
[Guided SQL lesson notebooks](guided-sql-notebooks.md).

## Use the tutor skill

Explicit invocation is the most predictable starting point:

```text
Use $guide-ds60sqlpy-learning to assess my current level and guide me through the next lesson.
```

You can also ask:

```text
Use $guide-ds60sqlpy-learning. I am on a new Windows machine and have never programmed. Help me verify setup, then start Python Day 1.
```

```text
Use $guide-ds60sqlpy-learning to resume SQL. Quiz me on prerequisites before recommending the next lesson.
```

```text
Use $guide-ds60sqlpy-learning to start the Python/PostgreSQL bridge. Verify
that I am ready, use fakes before a live database, and make me explain each
transaction boundary.
```

```text
Use $guide-ds60sqlpy-learning to start SQL Day 1 as a complete beginner. Teach
table, row, column, result set, row grain, SELECT, WHERE, and deterministic
ORDER BY before asking me to write a query.
```

```text
Use $guide-ds60sqlpy-learning to guide bridge-jupyter-01. Verify the selected
kernel and disposable database, keep my connection secret, and make me explain
bound parameters versus Jinja SQL rendering.
```

```text
Use $guide-ds60sqlpy-learning to choose my next professional module from the
catalog based on demonstrated prerequisites rather than the lesson number.
```

```text
Use $guide-ds60sqlpy-learning to review my current notebook. Give one hint at a time and do not open the official solution.
```

```text
Use $guide-ds60sqlpy-learning to check whether this lesson will run offline on my machine.
```

## A good tutoring session

The expected flow is:

1. Paste the lesson's own **Ask Codex about this lesson** prompt.
2. Identify your operating system, track, experience, and current lesson.
3. Run or interpret `python scripts/course.py doctor`.
4. Read only the relevant catalog entry, guide, and learner artifact.
5. Check prerequisites with a few short questions.
6. Explain the lesson in plain language.
7. Ask you to predict output or write an attempt.
8. Use a progressive hint ladder.
9. Run or inspect your actual code/query.
10. Finish with a short retrieval quiz and a next step.

The hint ladder should normally be:

1. Restate the goal and identify the misconception.
2. Give a conceptual hint.
3. Suggest pseudocode or a query shape.
4. Show a partial implementation.
5. Reveal a full worked solution only when requested or when you decide the attempt is complete.

## Ask Codex to inspect evidence

Useful debugging prompt:

```text
Inspect my selected interpreter, the exact error, and the lesson's declared dependencies before suggesting a fix. Do not assume package installation succeeded.
```

Useful SQL prompt:

```text
Run this only against the disposable advanced_sql_training database with psql -X -v ON_ERROR_STOP=1. Explain the first failing statement and keep the lesson transaction safe.
```

Useful bridge prompt:

```text
Test my solution offline with the provided fake first. If a live PostgreSQL
check would add evidence, resolve DS60_DATABASE_URL and explain the exact
rollback-safe operation before running it.
```

Useful review prompt:

```text
Compare my answer with the exercise requirements, not just the official solution. Tell me what is correct, what fails on an edge case, and the smallest next improvement.
```

## Progress and privacy

You decide whether progress is stored.

- Keep private local notes under `.learning/`; the directory is ignored.
- Ask before writing or changing a progress file.
- Treat `.learning/sql/` as learner work. A generated SQL notebook and editable
  SQL copy are preserved when reopened; do not delete them without first
  saving anything worth keeping.
- Do not put passwords, personal data, API keys, or proprietary datasets in prompts or notebooks.
- Do not ask Codex to connect a course reset command to a workplace database.

A useful local progress note records:

- Lesson ID
- Date attempted
- What you can explain without notes
- Exercise status
- One misconception or blocker
- Next review date

The course CLI and private portal share the same minimal ignored progress
record:

```text
python scripts/course.py progress show
python scripts/course.py progress complete python-01 --notes "Can explain values, variables, and the selected kernel."
```

Use the stable lesson ID printed by `catalog`. Codex should ask before marking a lesson complete and should base completion on your explanation or working attempt—not on merely opening the file.
On Windows, substitute `& $CoursePython` from the launcher block for `python`
when the repository environment is not activated.

The portal's **Export progress** button creates a portable JSON backup. In
static-file mode, import/export is also the deliberate bridge between browsers.
Never commit either the `.learning/` directory or a personal progress export.
Before making a source-only USB copy, export progress and separately preserve
any `.learning/sql/` exercises you want to resume.

## Avoid answer leakage

Say this explicitly when you want active learning:

```text
Do not read files under solutions/ until I ask. Use the learner notebook and companion guide first.
```

If you want a worked example, ask for a new analogous example before requesting the official answer.

## Use Codex for setup carefully

Codex should:

- Adapt commands to PowerShell or POSIX
- Use the repository virtual environment
- Explain what a command changes
- Preserve unrelated work
- Verify results with the course doctor

Codex should not:

- Change machine-wide security settings without explaining why
- Install into the system Python
- invent an unverified package version
- silently access the network during an offline lesson
- reset a database without resolving the exact disposable target

## Without Codex

Use the same learning loop manually:

1. Read the guide.
2. Predict and run examples.
3. Attempt exercises.
4. Use hints and documentation.
5. Compare with the separate solution.
6. Record what you can reproduce without looking.

The [curriculum map](curriculum-map.md), [troubleshooting guide](troubleshooting.md), and `python scripts/course.py catalog` provide the same navigation foundation.
