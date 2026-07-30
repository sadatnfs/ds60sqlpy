# Learning with Codex

Codex can act as a tutor, reviewer, debugger, and study planner for this repository. It is optional: all course content and local execution should remain usable without Codex.

Codex itself may require a network connection even when a lesson does not. “Offline course” and “online tutor” are separate capabilities.

## Start Codex in the repository root

Open the directory containing `README.md`. From there, Codex can discover:

- Root and track-specific `AGENTS.md` guidance
- The generated `curriculum/catalog.json` lesson index
- The `$guide-ds60sqlpy-learning` repo-local skill
- The environment doctor and validation commands

If Codex starts inside a nested lesson directory, tell it to work from the repository root.

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
Use $guide-ds60sqlpy-learning to start sql-found-01 before SQL Day 1. Make me
state the grain and invariants before I write DDL.
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

1. Identify your operating system, track, experience, and current lesson.
2. Run or interpret `python scripts/course.py doctor`.
3. Read only the relevant catalog entry, guide, and learner artifact.
4. Check prerequisites with a few short questions.
5. Explain the lesson in plain language.
6. Ask you to predict output or write an attempt.
7. Use a progressive hint ladder.
8. Run or inspect your actual code/query.
9. Finish with a short retrieval quiz and a next step.

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
- Do not put passwords, personal data, API keys, or proprietary datasets in prompts or notebooks.
- Do not ask Codex to connect a course reset command to a workplace database.

A useful local progress note records:

- Lesson ID
- Date attempted
- What you can explain without notes
- Exercise status
- One misconception or blocker
- Next review date

The course CLI can keep a minimal ignored progress record:

```text
python scripts/course.py progress show
python scripts/course.py progress complete python-01 --notes "Can explain values, variables, and the selected kernel."
```

Use the stable lesson ID printed by `catalog`. Codex should ask before marking a lesson complete and should base completion on your explanation or working attempt—not on merely opening the file.

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
