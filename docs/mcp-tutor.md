# Use the local course tutor through MCP

The optional DS60 MCP server lets Codex read the local curriculum, plan a path,
open the exact lesson, and provide progressive hints. MCP is the connection
protocol between Codex and this local Python process. You can also learn
without it using the course application, JupyterLab, and checked-in guides.

The adapter uses standard input/output pipes. It opens no listening port,
connects to no remote service, and does not execute Python, SQL, or shell
commands. All teaching content comes from the selected repository. The
adapter works offline after installation; the AI model used by Codex has its
own runtime and connectivity requirements. This repository does not bundle an
AI model.

## Install the optional adapter

Run normal OS setup first. Install the extra into the same course interpreter
while connected. It uses the official Python MCP SDK v2; old `FastMCP` examples
from SDK v1 are not this adapter's interface.

Windows PowerShell, from the repository root:

```powershell
$CourseRoot = (Resolve-Path .).Path
$CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
    (Resolve-Path .\.venv\Scripts\python.exe).Path
} else {
    (Resolve-Path .\.venv\python.exe).Path
}
& $CoursePython -m pip install -e ".[mcp]"
$McpScript = Join-Path $CourseRoot "scripts\mcp_server.py"
& $CoursePython $McpScript --help
```

macOS/Linux:

```bash
CourseRoot="$(pwd -P)"
"${CourseRoot}/.venv/bin/python" -m pip install -e ".[mcp]"
"${CourseRoot}/.venv/bin/python" "${CourseRoot}/scripts/mcp_server.py" --help
```

Expect help showing the required `--repo` argument and the optional
`--allow-progress-writes` flag. The installed `ds60-mcp` entry point provides
the same server, but an absolute Python path is easier to diagnose in a client
configuration and works with both Windows environment layouts.

If you use exact locked synchronization later, remember to retain `--extra mcp`
in that synchronization. Standard Core setup intentionally does not require
this optional integration.

## Add it to Codex

The commands below register a local server in your Codex MCP configuration.
Run them yourself when you want that integration. They use absolute paths so
the server starts correctly even if Codex's working folder differs.

Windows PowerShell, using the variables above:

```powershell
codex mcp add ds60-tutor -- $CoursePython $McpScript --repo $CourseRoot
codex mcp get ds60-tutor
```

macOS/Linux:

```bash
codex mcp add ds60-tutor -- "${CourseRoot}/.venv/bin/python" "${CourseRoot}/scripts/mcp_server.py" --repo "$CourseRoot"
codex mcp get ds60-tutor
```

The installed Codex CLI's `codex mcp add --help` documents the `NAME -- COMMAND`
stdio form used here. `codex mcp list` shows configured servers. Restart or
refresh the Codex client if it does not immediately discover a new server.
The CLI must be installed and on PATH to use these commands. No configuration
file is changed by merely installing the Python extra or reading this guide.

You can inspect the equivalent local configuration with
`codex mcp get ds60-tutor`. The executable must be a real absolute interpreter
path; `~`, an activated shell assumption, or a Python name found only in one
terminal can fail when a desktop client starts the process. If you move the
repository, recreate its environment and update this registration.

## Begin a learning conversation

For example, tell Codex:

```text
Use the ds60-tutor MCP server. List the learning paths, then help me plan
Python foundations for five hours each week. Start with the first pending
lesson. Explain the guide, ask me to predict a result, and wait for my attempt.
Give one hint at a time. Do not open an official solution unless I explicitly
ask to compare it. Ask me to explain my result from memory before completion.
```

For a specific lesson:

```text
Use ds60-tutor for python-01. Read the actual guide and learner artifact.
Ask what I think the first example will do, then wait for my attempt.
If I am stuck, give one hint. Use my observed result to help me explain why
it works. Keep official solutions closed unless I ask for a comparison.
```

These prompts guide the AI host. The server supplies local evidence and
structured operations; it does not itself generate a model response, run your
exercise, grade your explanation, or infer mastery from a page view.

## Available teaching operations

| Tool | Purpose |
| --- | --- |
| `course_paths` | Available goals and saved completion IDs |
| `course_plan` | Expand named paths or lesson IDs into a pending prerequisite plan |
| `course_lessons` | Search IDs, titles, levels, phases, and dependency groups |
| `course_lesson` | Guide, learner artifact, missing prerequisites, and session evidence |
| `course_hint` | One numbered progressive hint, with a general prompt if the guide has none |
| `course_solution` | Official explanatory solution, only with explicit `reveal: true` |
| `course_session` | Read locally saved evidence for the current lesson |

`course_lessons` returns at most 50 lessons per page. Use its `next_cursor`
with exactly the same query, track, and limit. For example:

```json
{"query": "pandas", "track": "python", "limit": 10}
```

Follow-up requests add `"cursor": "THE_RETURNED_CURSOR"` to those same filters.
No results is a valid response. Changing filters requires starting a new search.

Resources expose `ds60://course/paths` and
`ds60://course/lesson/LESSON_ID`. The latter contains only the checked-in guide.
Resource enumeration is paginated too. The `coach_lesson` prompt accepts a
stable `lesson_id` and optional `request` and starts the same guide-first
coaching loop. Solutions have no resource URI; they require the gated tool.

The solution flag is an explicit protocol acknowledgement. The AI host must
still respect the learner's actual request; it should never set the flag just
to bypass a request for hints.

## Optional local evidence and progress writes

By default the adapter advertises no mutation tools and creates no progress
files. If you want Codex to save your own evidence, add
`--allow-progress-writes` to the server command when registering it. For an
existing registration, inspect it with `codex mcp get ds60-tutor`, then replace
it deliberately with `codex mcp remove ds60-tutor` and the matching `add`
command ending in `--allow-progress-writes`.

With that flag, two additional tools are available:

- `course_save_evidence`: save learner-authored notes for `read`, `predict`,
  `attempt`, `compare`, or `explain` in `.learning/coaching.json`.
- `course_complete`: require `confirmed: true`, nonempty saved prediction,
  attempt, and explanation, plus recorded prerequisites, before writing
  `.learning/progress.json`.

These are the course application's local evidence and progress files. Existing
notes in other phases are preserved. Completion is explicitly labelled
learner-confirmed self-report, not automatic grading. Ask Codex to save only
your actual attempt and explanation, with your consent. Keep credentials and
private workplace data out of course notes. Neither tool edits a lesson,
starts a process, resets a database, or executes the learner's code.

## Diagnose a connection failure

1. Run `codex mcp get ds60-tutor` and inspect the executable, script, and
   absolute repository path.
2. Run that interpreter with `-m pip show mcp` and check it reports SDK v2.
3. Run the script with `--help`. A missing SDK message means the package was
   installed into a different interpreter or removed by an exact sync.
4. Launching the script with `--repo` in a terminal normally appears to wait:
   it is waiting for protocol messages from a client. Press `Ctrl+C` to stop.
5. Run the integration tests below, then inspect client/server stderr if
   discovery still fails. Application messages must never be printed to stdout
   because stdout carries MCP JSON-RPC.

The server refuses relative or nested `--repo` paths, unknown lesson IDs,
arbitrary resource/file paths, unknown tool arguments, invalid pagination
cursors, and progress calls when writes are disabled. It does not require a
database credential or a listening web service.

## Verification and source references

Run the real protocol tests with the optional SDK installed:

```powershell
# Windows, after resolving the interpreter
& $CoursePython -m pytest tests\test_mcp_server.py -q
```

```bash
# macOS/Linux
.venv/bin/python -m pytest tests/test_mcp_server.py -q
```

Tests cover a client/server stdio handshake, discovery, lesson/guide reads,
prompts, solution gating, pagination, opt-in writes, evidence prerequisites,
invalid requests, and clean protocol stdout. The client session runs with
network connect/bind calls forbidden in the POSIX server process. Windows
runs the same stdio exchange without that audit guard because its event loop
may use an internal socket pair. This proves the adapter protocol in the tested environment; it does not prove that a specific
Codex installation is configured, that an AI taught well, or that a learner
mastered the material. No user configuration is modified by these tests.

The implementation follows the official
[SDK v2 low-level server API](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)
for explicit schemas, structured tool results, and caller validation. The
[SDK pagination guide](https://py.sdk.modelcontextprotocol.io/advanced/pagination/)
describes protocol list cursors. The current local Codex CLI help was checked
for the registration commands above.

## Maintainer evaluation

`docs/mcp-tutor-evaluation.xml` contains ten independent read-only tutoring
questions with verified stable answers. The matching
`tests/test_mcp_tutor_evaluation.py` exercises real adapter searches,
prerequisite plans, lesson resources and prompts, and checks that these
operations create no learner-state files. This checks the adapter's evidence
and interface. It is separate from evaluating an AI model's teaching quality
with actual learners.
