# Learning with an AI tutor

The Docker classroom is the main learning environment. An AI tutor is an
optional companion for explanation, debugging, retrieval practice and planning.
All lessons must remain usable without an account, a hosted model or an AI
assistant. A tutor's network and privacy requirements are separate from the
course's offline-after-setup behavior.

## Start the classroom

From the repository root on macOS, Linux or Windows through WSL 2, run:

```bash
./classroom
```

The launcher builds the prepared runtimes, starts the services and prints the
actual browser address. Open `/classroom`, choose any subject, and use its
lesson list to follow a sequence or revisit a topic. The same interface serves
Python, SQL, the engineering bridge, programming languages, Kubernetes, deep
learning, NLP, LLMs and statistics. Prerequisites describe what a lesson assumes;
they do not force every learner to study at the same pace.

The guide, code pad, notes and results stay together. Follow the lesson's runtime
notice: an orientation or theory lesson may intentionally have no Run button.
C++ and Java compile in their prepared workers; JavaScript and TypeScript use
the documented Node runtime. Browser DOM examples have a separate browser
workflow because Node does not provide a browser document.

The launcher reuses local named Docker volumes. Returning to the same project
restores progress and saved work. Keep that project name when restarting, and
preserve its volumes. A progress JSON export is not a complete backup of pads,
notes, database state, job history or saved run receipts. Read
[the classroom guide](docker-classroom.md) before moving a learner's work.

For static reading, open [`START_HERE.html`](../START_HERE.html). It includes
rendered lesson and reference pages, math and syntax highlighting, but does not
execute code. Its browser-local completion state is separate from Docker data.
Prepared native editor and Jupyter workflows remain available under
[the optional application modes](offline-app.md).

## Give the tutor the right context

Open an AI coding assistant in the repository root, or connect a compatible
MCP client using [the optional course tutor adapter](mcp-tutor.md). The local
adapter reads the course and plans a path; it does not run learner code or
bundle a language model.

Ask the assistant to read:

- Root and subject-specific `AGENTS.md` instructions.
- The current catalog or module manifest, using stable lesson IDs.
- The exact guide and learner artifact for the chosen lesson.
- The repo-local `guide-ds60sqlpy-learning` skill.
- Your current attempt and the actual result you observed.

If a client does not discover skills automatically, provide the path
`.agents/skills/guide-ds60sqlpy-learning/SKILL.md`. Some clients support the
`$guide-ds60sqlpy-learning` shorthand used in lesson prompts; others need the
file to be opened explicitly. The learning sequence is independent of that
client feature.

Every ordinary programming guide ends with **Ask an AI tutor about this
lesson**. Copy that lesson-specific prompt so the tutor receives the stable ID,
paths, prerequisites and solution boundary. Read the lesson first. A tutor may
adapt an explanation, but it must not compensate for missing curriculum.

## Use the learning loop

1. **Explain:** read the guide and describe the objective in your own words.
2. **Predict:** state what a worked example will produce before running it.
3. **Attempt:** change the code or write your own solution in the correct pad.
4. **Inspect:** compare the actual output with the lesson's expected behavior.
5. **Ask for one hint:** describe the mismatch and the smallest relevant code.
6. **Compare:** explicitly request the official solution when ready, then explain
   why it works and how it differs from your attempt.
7. **Retrieve:** close the example and explain or rebuild the key idea from memory.

A successful process exit, copied reference or completion check is not proof of
understanding. Save your reasoning as well as your output. For the statistics
and machine learning tutorial book, use the worked examples and answered
interview discussions. It has no exam or mandatory exercise submission; its
read marker records reading rather than mastery.

A useful starting prompt is:

```text
Use the guide-ds60sqlpy-learning skill for the lesson I selected.
Read its actual guide and learner artifact. Ask which prerequisite ideas I
already understand. Explain one new idea, ask me to predict an example, then
wait for my attempt. Give one hint at a time. Keep official solutions closed
until I explicitly ask to compare them. Use my observed output as evidence,
and ask me to explain the result from memory before marking completion.
```

## Ask for help without losing the learning

For an error:

```text
Here is my lesson ID, the relevant code, the exact error and what I expected.
Help me find the first mismatch between my mental model and the program.
Explain unfamiliar error terms, then suggest one small diagnostic step.
Do not replace the whole solution or automatically rerun a destructive step.
```

For SQL:

```text
Help me reason about the starting row grain, joins, grouping, NULL behavior
and final ordering. Ask me to predict the rows before proposing a query.
Use only the disposable advanced_sql_training database. Explain whether a
statement changes state before asking me to run it.
```

For a compiled language:

```text
Explain the source filename, entry point, compile step and runtime step for
this lesson's prepared profile. Distinguish compiler errors from runtime
errors. Use the first diagnostic and the documented language version to
help me make one small correction, then inspect the new result.
```

For a theory chapter:

```text
Define every symbol in this chapter's main equation. Work through a small
numerical example, explain the assumptions, then give a case where the
method would be misleading. Connect the result to the accompanying Python
example without treating a toy demonstration as a production model.
```

## Protect work and keep evidence honest

- Keep pads, notes and saved results in the learner's own project. Do not ask an
  assistant to overwrite another learner's files or reset their progress.
- Paste only the smallest relevant example and output. Keep credentials,
  private datasets, connection strings and personal material out of tutor chats.
- Use the exact source and result from the same run. A past receipt must not be
  mistaken for output from a newly edited pad.
- A tutor should explain a proposed setup or reset action before running it.
  The SQL training database is disposable; another database is not a substitute.
- Installing an AI client is optional. Do not add hosted API dependencies to a
  lesson that is meant to run offline.
- Completion should reflect your own explanation and attempt. MCP progress
  writes are disabled by default and require an explicit server opt-in.

For a blocked environment, record the missing dependency or runtime separately
from the lesson's correctness. A reading lesson still works without a compiler,
while a compilation claim needs an actual compiler result.

## Plan a sustainable route

Choose a weekly time budget and a concrete outcome, then ask the tutor to expand
that outcome into prerequisites. Alternate new topics with retrieval of earlier
ones. If a lesson feels too fast, return to its prerequisite and ask for a
smaller example. If it feels familiar, demonstrate the concept on a new input
before skipping ahead.

The classroom supports switching subjects without mixing their pads or results.
Use that freedom deliberately: Python and SQL reinforce data reasoning; C++,
Java and JavaScript expose different runtime models; Scala and Spark introduce
distributed data work. Statistics, deep learning and LLM chapters connect those
implementation skills to assumptions, measurement and evaluation.

## Continue without an AI tutor

Follow the guide, run the worked examples, attempt the exercises where present,
and compare the separate explanations. Use the expected results and common
mistakes to diagnose your work. Record questions for later, and review the
linked primary references. The checked-in course is the source of truth.
