# Learn in one classroom

Start your local Linux-container engine, run `./classroom` in the course
folder and open the URL it prints. The `/classroom` home lets you choose any
registered subject and return to it at your own pace.

## Choose a path

| Area | Subjects |
| --- | --- |
| Programming and interfaces | Python, C, C++, Go, C#, Rust, Swift, Java, JavaScript/TypeScript with D3, HTML/CSS/PHP web development |
| Data and statistical work | PostgreSQL, the Python/PostgreSQL engineering bridge, statistics and machine learning, Scala/Apache Spark |
| Learning systems and language models | TensorFlow, PyTorch, NLP, LLM theory, applied LLM systems |
| Infrastructure and acceleration | Docker, Kubernetes, GPU computing and CUDA |

Use **All learning paths** or **Switch subject** to change direction. Subject
names and individual color themes identify the current path. Search within a
path, filter its stage or choose a lesson from the list. A filter changes what
you see; it does not erase your current draft.

Start with a beginner lesson when the vocabulary is new. Prerequisites are
helpful review links. Historical day numbers and estimated sessions are
planning aids, not deadlines. Follow a long explanation over several sittings
if useful. The [learning paths](learning-paths.md) suggest combinations, and
[the LLM textbook route](learning/llm-textbook.md) connects mechanisms with
applied systems. The statistics book also works as a reference.

## Read the explanation

A lesson puts its guide beside its coding or reading workspace. Mathematics
renders with fractions, powers and indices. Code blocks are highlighted by
language and remain copyable. Those resources are bundled locally.

Use **Focus on reading** for a wider explanation and **Show code and notes**
to return to practice. The section chooser jumps within a long guide.
Keep each example's input, expected observation and limitation together.
A tiny demonstration teaches a mechanism; its success does not establish
production scale or model quality.

Programming practice offers predictions, exercises, hints and separate
solutions. Reveal a solution when you want to compare with your attempt.
The statistics/ML tutorial gives complete worked examples and answered
discussion directly, without mandatory exams or hidden answers.

## Choose the right execution environment

The capability notice describes the selected lesson or variant. A runtime
can be unavailable while the guide and your saved source remain readable.
Follow its preparation command instead of installing tools inside the pad.

| Workspace | What a Run does |
| --- | --- |
| Python | Executes current source in a fresh process; supported notebook-style cells share state only within that Run |
| PostgreSQL | Runs a SQL snippet or the selected guarded whole-script psql workflow |
| C, C++, Go, C#, Rust, Swift, Java, Scala | Compiles the declared single-source artifact before execution |
| Node JavaScript / TypeScript | Runs Node code, or checks and compiles TypeScript before Node execution |
| HTML/CSS or browser JavaScript/D3 | Opens a separate browser preview with local inline code and bundled resources |
| PHP | Executes a fresh CLI program with prepared PDO SQLite; generated HTML is text output |
| TensorFlow, PyTorch and Spark | Uses the selected prepared CPU worker for bounded local examples |
| Reading | Saves reasoning and notes without an invented execution action |

Do not paste raw notebook JSON into a Python pad. Keep `# %%` markers in
supported notebook-style source. In SQL, distinguish ordinary statements from
psql backslash commands, and read the fixture and transaction contract first.

Compiled-language workers choose filenames and compiler arguments for you.
Read the first diagnostic, change one thing and retry. Larger multi-file
builds, interactive servers and project-specific dependencies use their
separately documented fixtures.

CUDA reading and CPU-model variants work without an NVIDIA device. Optional
NVIDIA variants require explicit setup and a real device probe. A CPU
calculation, a compiled kernel and measured GPU execution establish different
facts. Kubernetes similarly requires an explicitly owned target. Opening a
lesson does not create a cluster or download pretrained models.

## Explore in the preview studio

HTML/CSS and browser JavaScript/D3 provide an optional **Live preview** switch.
Turn it on deliberately for the current workspace. Edits refresh after a short
pause in typing, and errors appear in the console.

Use **Focus on editor & preview** to place them side by side on a wide screen;
they stack on a narrow screen. **Return to lesson layout** brings the guide
back. Desktop, Tablet, Phone and Fit to space resize the same preview without
rerunning it. **View console** moves to the output, and fullscreen changes
presentation only.

**Pause updates** keeps the last rendered version while you edit.
**Resume updates** renders the current draft. **Stop preview** closes the
frame and cancels queued updates. Leaving the lesson, viewing a past result
or reloading turns live execution off.

Automatic previews do not create saved-run records. **Run browser preview**
leaves live mode and saves its exact submitted source with its observation.
**Save observation** keeps the current rendered source/output and pauses
automatic updates. Ordinary draft saving continues independently.

The preview supports inline scripts, native HTML parsing and real browser
lifecycle events. External scripts/imports, network data, real form submission
and navigation metadata are outside its contract. Use the web course's
separate loopback server project for real HTTP sessions. Browser observations
are client-reported results, not independent backend verifier evidence.

## Save work and understand history

The classroom keeps work separate by lesson, language, variant and SQL mode.
**Save work** records the current draft and notes; ordinary edits also schedule
a save. Wait for the saved confirmation before closing. If a server save fails,
the interface tells you whether a recoverable browser draft remains. Keep a
copy until server saving is confirmed.

**Saved runs** stores the source and output from a particular execution or
explicit browser observation. Reading history does not rerun that source or
replace your current edit. A saved run can describe an older version than
the draft visible in the editor.

Python/SQL workspaces offer earlier saved pad versions where supported.
Modern module pads retain their current source and recorded run snapshots;
do not assume every keystroke creates an immutable version. Restoring or
copying earlier source differs from inspecting earlier output.

Progress markers record your learning choices. A tutorial read marker is a
bookmark. A reference run and a completion mark do not certify independent
mastery; explanation and transfer to a new case provide additional evidence.

## Return to the same learning data

```sh
./classroom stop
./classroom resume
```

Stopping keeps project volumes. Strict resume never builds or pulls. Normal
`./classroom` can prepare missing images. Install changed local sources with
`./classroom --local-build --rebuild`.

Keep the same engine and project name. Repeat a custom `--project NAME` on
each command. The learning volume stores pads, notes, history and progress;
PostgreSQL tables use another volume. The checkout's `.classroom/` directory
stores launcher preferences, not a backup of either volume.

See [startup and recovery](one-command-classroom.md) and
[backup and transfer](one-command-classroom.md#backup-and-transfer).
A source ZIP, Docker image and learning-data backup serve different purposes.

## Read offline or study with a companion

`START_HERE.html` and generated readers provide static offline reading after
the full source folder is downloaded. They cannot execute a compiler or
database from a browser file URL. Existing `/learn` and `/journeys` bookmarks
resolve to the unified classroom; use `/classroom` for new links.

An assistant can use the [learning companion skill](../.agents/skills/guide-ds60sqlpy-learning/SKILL.md)
to explain a guide and review the attempt you share. The optional
[MCP tutor](mcp-tutor.md) reads checked-in curriculum and has no code execution.
It cannot silently inspect a Docker-volume pad. Learning requires no AI service.
