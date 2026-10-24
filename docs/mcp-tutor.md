# Use the local course tutor through MCP

The optional DS60 MCP server lets the AI tutor read the local curriculum, plan a path,
open the exact lesson, and provide progressive hints. MCP is the connection
protocol between the AI tutor and this local Python process. You can also learn
without it using the course application, JupyterLab, and checked-in guides.

The adapter uses standard input/output pipes. It opens no listening port,
connects to no remote service, and does not execute Python, SQL, or shell
commands. All teaching content comes from the selected repository. The
adapter works offline after installation; the AI model used by the AI tutor has its
own runtime and connectivity requirements. This repository does not bundle an
AI model.

## Use a repository assistant without MCP

An assistant that can read this checkout can use the repository's
[learning companion skill](../.agents/skills/guide-ds60sqlpy-learning/SKILL.md)
directly. It covers every registered subject and gives prerequisite-aware,
progressive guidance from the actual lesson. MCP is optional for that workflow.
The learner classroom continues to run through Docker; no additional host
Python installation is required just to read the skill and course files.

Ask it to read your current attempt, explain one mechanism, and give the next
useful hint. Keep saved drafts and notes intact. A tutor should not mark a lesson
complete merely because an example ran. The statistics/ML tutorial provides its
worked answers directly and does not require exams or hidden-solution gates.

To resume the classroom, use `./classroom` for normal reuse of saved containers
and images, or `./classroom resume` to prohibit builds and pulls. Supply the same
custom `--project NAME` if one was used. `./classroom --rebuild` deliberately
installs updated source files. The tutor must distinguish these startup settings
from your Docker learning volume and must not reset either to fix an error.

## Install the optional adapter

The following setup is an additional host-side integration for a stdio client;
it is not required by the Docker classroom. Run normal OS setup first. Install the extra into the same course interpreter
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

## Connect any compatible MCP client

Choose a client that supports local **stdio** servers. In that client's MCP
settings, add a server named `ds60-tutor` with these values:

| Setting | Value |
| --- | --- |
| Transport | `stdio` |
| Command | The absolute path to the course Python interpreter printed during setup |
| Arguments | The absolute path to `scripts/mcp_server.py`, then `--repo`, then the absolute repository directory |
| Working directory, if requested | The repository root |

Enter arguments as separate values, not as one shell command. The client must
start the interpreter on the same machine or execution environment that holds
the repository. A Windows client cannot directly launch a Linux executable
inside WSL without an explicit WSL launch configuration. Keep the interpreter,
script and repository paths in the same environment.

A JSON representation of the server values is shown below. This is an
illustration of the command and argument fields, not a universal client
configuration file. Use the wrapper and settings location documented by your
chosen client, and replace every placeholder with a real absolute path.

```json
{
  "command": "ABSOLUTE_PATH_TO_COURSE_PYTHON",
  "args": [
    "ABSOLUTE_PATH_TO_REPOSITORY/scripts/mcp_server.py",
    "--repo",
    "ABSOLUTE_PATH_TO_REPOSITORY"
  ]
}
```

Do not include shell quote characters inside a JSON argument. A path containing
spaces remains a single argument. In JSON, Windows backslashes need escaping;
forward slashes are accepted in ordinary Python file paths on Windows.

Refresh the client's server list after saving its settings. The server should
advertise the course tools described below. Installing the Python extra does
not change any client configuration. If the checkout moves, recreate its
virtual environment and update the interpreter, script and repository paths.

The [MCP stdio transport specification](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#stdio)
defines the process and pipe boundary. It does not require a specific client
brand, settings filename or command-line registration tool.

## Begin a learning conversation

For example, tell the AI tutor:

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

## Read the authored subject library

Four additional read-only operations expose the authored subject library,
including languages, systems, deep learning, NLP, LLMs and statistics. Their
counts come from the curated module manifests.
Canonical lesson counts exclude language variants. `planned_count` covers the
full design, including the authored subset; `unwritten_count` identifies the
remaining planned lessons.

| Tool | Purpose |
| --- | --- |
| `module_subjects` | Subject summaries and authored/design counts |
| `module_lessons` | Paginated canonical metadata, authored lessons by default |
| `module_lesson` | One authored guide and checked-in learner artifact |
| `module_solution` | Curated solution documents after explicit `reveal: true` |

For example, ask the AI tutor:

```text
Use ds60-tutor module_subjects, then module_lessons with subject scala-spark
and status authored. Read spark-013@pyspark through module_lesson for the
PySpark variant. Explain the guide, ask me to predict the NULL behavior, and
wait for my attempt. Give one progressive hint from the guide. Keep official
solutions closed until I explicitly request a comparison.
```

`module_lessons` defaults to twenty results and accepts at most fifty. Keep
subject, status, query and limit unchanged when following `next_cursor`.
An explicit `status: "planned"` or `status: "all"` returns labelled design
metadata. Planned placeholders have no authored guide/source read through
`module_lesson`. A canonical lesson can list a curated variant ID, such as
`spark-013@pyspark`, without counting that variant as another lesson.

The module tools read checked-in content. They do not read saved classroom pads,
construct job services, probe runtime availability, start a worker, execute
source, or record mastery. Their `runtime_status` is always `not_probed`;
a runtime profile name describes the lesson's intended backend. Use the local
application and its host preparation instructions for experiments, then share
your own attempt and observations with the tutor.

Guide and solution documents have a 96000-byte tutor read limit; learner source
has a 48000-byte limit, and a response has a 384000-byte bound. Oversized content
is rejected explicitly instead of silently truncating a lesson. Only curated
relative content paths can be read, and each read repeats the content-path
check. Solutions have a separate reveal-gated response and are never read by
normal module guide, index or search calls.

All four module tools remain read-only when `--allow-progress-writes` enables
the separate legacy evidence tools. An older checkout without expansion plans
keeps its original course tools; module tools are not advertised there,
and a direct request reports their unavailability. No worker, network service,
engine session or module progress file is needed to read an authored guide.

## Optional local evidence and progress writes

By default the adapter advertises no mutation tools and creates no progress
files. If you want the AI tutor to save your own evidence, add
`--allow-progress-writes` to the server command when registering it. For an
existing registration, inspect the saved command and arguments in your client
settings, then add `--allow-progress-writes` as one final argument only when
you want that behavior.

With that flag, two additional tools are available:

- `course_save_evidence`: save learner-authored notes for `read`, `predict`,
  `attempt`, `compare`, or `explain` in `.learning/coaching.json`.
- `course_complete`: require `confirmed: true`, nonempty saved prediction,
  attempt, and explanation, plus recorded prerequisites, before writing
  `.learning/progress.json`.

These are the course application's local evidence and progress files. Existing
notes in other phases are preserved. Completion is explicitly labelled
learner-confirmed self-report, not automatic grading. Ask an AI tutor to save only
your actual attempt and explanation, with your consent. Keep credentials and
private workplace data out of course notes. Neither tool edits a lesson,
starts a process, resets a database, or executes the learner's code.

## Diagnose a connection failure

1. Inspect your client's saved server configuration: executable, script,
   arguments and absolute repository path must all point to this checkout.
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
& $CoursePython -m pytest tests\test_mcp_server.py tests\test_module_mcp.py -q
```

```bash
# macOS/Linux
.venv/bin/python -m pytest tests/test_mcp_server.py tests/test_module_mcp.py -q
```

Tests cover a client/server stdio handshake, legacy and module discovery, lesson/guide reads,
prompts, solution gating, pagination, opt-in writes, evidence prerequisites,
invalid requests, bounded module reads, variants, and clean protocol stdout. Module
tests additionally forbid worker/service construction, source subprocesses,
and progress-file access during a real stdio exchange. The client session runs with
network connect/bind calls forbidden in the POSIX server process. Windows
runs the same stdio exchange without that audit guard because its event loop
may use an internal socket pair. This proves the adapter protocol in the tested environment; it does not prove that a specific
MCP client installation is configured, that an AI taught well, or that a learner
mastered the material. No user configuration is modified by these tests.

The implementation follows the official
[SDK v2 low-level server API](https://py.sdk.modelcontextprotocol.io/advanced/low-level-server/)
for explicit schemas, structured tool results, and caller validation. The
[SDK pagination guide](https://py.sdk.modelcontextprotocol.io/advanced/pagination/)
describes protocol list cursors. Client configuration is separate from the
server protocol; verify it with the documentation for your chosen client.

## Maintainer evaluation

`docs/mcp-tutor-evaluation.xml` contains ten independent read-only tutoring
questions with verified stable answers. The matching
`tests/test_mcp_tutor_evaluation.py` exercises real adapter searches,
prerequisite plans, lesson resources and prompts, and checks that these
operations create no learner-state files. This checks the adapter's evidence
and interface. It is separate from evaluating an AI model's teaching quality
with actual learners.

## Expanded-library protocol acceptance

The real stdio tests enumerate the current subject and canonical lesson
manifests, page through discovery, and read representative language and
statistics guides. Tutorial content retains its learning mode without exams
or solution gates. Default tools provide neither code execution nor progress
mutation. The tests reject false solution reveals and disabled write calls,
and audit unexpected network access, child processes and learner-state writes.
Run these tests against the exact checkout being released. Passing protocol
tests does not establish that an individual client is configured correctly or
that a learner has mastered the material.
