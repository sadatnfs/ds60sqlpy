# Curriculum design references

This course is original material, but its teaching structure should learn from
successful beginner resources. The sources below were reviewed on 2026-07-30.
They are design references, not content to copy. DS60 remains PostgreSQL 16+,
Python 3.11–3.12, local-first, Windows-friendly, and runnable after one
connected bootstrap.

## Patterns adopted from established tutorials

### Python's official tutorial: explain, run, observe, contrast

The [Python control-flow tutorial](https://docs.python.org/3/tutorial/controlflow.html)
introduces a construct with a small runnable example, shows the actual output,
then immediately explains a boundary or contrast. Its `for` section, for
example, contrasts Python iteration with index-oriented loops, warns about
mutating a collection during iteration, shows several `range` boundaries, and
explains why a `range` object is iterable rather than a stored list.

DS60 applies that pattern by requiring:

- a plain-language definition before syntax;
- a bounded example and expected output;
- a second example that changes one meaningful condition;
- an explicit edge case or nearby concept comparison; and
- an explanation of the runtime or memory behavior when it matters.

The official tutorial documents the current Python release, while DS60 targets
Python 3.11–3.12. Authors must verify that adopted syntax exists in the course
baseline rather than copying version-current examples blindly.

### CS50P: concrete setup, progressive revision, and evidence

[CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/)
separates lectures, short focused explanations, source code, problem sets, and
a final project. Its
[loop notes](https://cs50.harvard.edu/python/notes/2/) begin with repeated
statements, expose an infinite-loop failure, explain how to interrupt it, and
revise the program in small steps. Its problem specifications provide concrete
files, commands, assumptions, sample behavior, and tests rather than only a
topic label.

DS60 applies that pattern by requiring:

- exact “where to type and how to run” instructions;
- a progression from a deliberately limited first version to a better one;
- error symptoms and recovery, including how to stop unsafe or stuck work;
- exercises with supplied inputs, constraints, expected behavior, and
  verification cases;
- separate solutions revealed after an honest attempt; and
- cumulative projects that assess correctness, design, explanation, and
  testing rather than syntax recall alone.

### PostgreSQL's official tutorial: start from the system and show results

The [PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial.html)
puts installation, architecture, database creation, and database access before
query syntax. Its
[querying chapter](https://www.postgresql.org/docs/current/tutorial-select.html)
names the parts of `SELECT`, shows commands and tabular results, explains
aliases and predicates, and calls out nondeterministic ordering. Its
[join chapter](https://www.postgresql.org/docs/current/tutorial-join.html)
explains the row-pairing mental model, displays unmatched-row behavior, then
distinguishes that conceptual model from the physical implementation.

DS60 applies that pattern by requiring:

- a visible database/client/server mental model before lesson queries;
- the disposable `advanced_sql_training` safety boundary in every run path;
- query anatomy and logical row grain before clause-by-clause detail;
- expected result columns, representative rows, or invariant counts;
- explicit treatment of `NULL`, ties, ordering, time zones, and transactions;
- conceptual explanations labeled as models rather than universal physical
  execution claims; and
- a guided notebook that keeps the SQL source, `psql` transcript, reset
  confirmation, and recovery steps in one learner workspace.

### SQLBolt: concept and practice on the same page

[SQLBolt](https://sqlbolt.com/lesson/select_queries_introduction) places a
brief table/row mental model, a syntax shape, and interactive exercises on the
same lesson page. It also keeps the next lesson gated behind active work.

DS60 cannot safely turn a static `file://` page into a database client, so it
adapts the useful part of that pattern:

- the rendered reader keeps the guide, learner preview, and optional solution
  together;
- the private portal adds a fixed **Create/open guided SQL notebook** action;
- the generated notebook preserves an editable learner copy and runs it
  through a catalog-restricted `psql -f` path; and
- completion means explaining and demonstrating the objective, not merely
  opening the page.

### Exercism: concept scope, prerequisites, stubs, tests, and hints

The [Exercism concept-exercise specification](https://exercism.org/docs/building/tracks/concept-exercises)
separates a concept introduction, task instructions, hints, starter
implementation, tests, exemplar, and maintainer-facing design notes. Its
[syllabus guidance](https://exercism.org/docs/building/tracks/syllabus)
organizes focused concept exercises by prerequisite relationships and
distinguishes learning a concept from later fluency practice.

DS60 applies that pattern by:

- keeping stable prerequisites in the catalog instead of assuming day-number
  proximity;
- separating guides, answer-free learner artifacts, hints, and explanatory
  solutions;
- giving exercises a starter input or scaffold plus an independent
  verification method;
- naming what a lesson teaches and what remains out of scope; and
- following concept introduction with additional debugging, edge-case, and
  transfer practice rather than treating the first passing answer as fluency.

### The Carpentries: align objectives, practice, and formative evidence

The Carpentries'
[lesson-development guidance](https://carpentries.github.io/lesson-development-training/instructor/key-points.html)
uses objectives to focus and chunk a lesson, aligns exercises with those
objectives, and treats formative assessment as feedback about both learner
progress and misconceptions. Its
[exercise-design guidance](https://carpentries.github.io/lesson-development-training/instructor/formative-assessment.html)
emphasizes selecting an exercise format that actually demonstrates the stated
objective rather than counting activity for its own sake.

DS60 therefore requires:

- observable objectives using actions such as trace, implement, compare,
  diagnose, and justify;
- a topic-specific expected result or verification contract for each exercise;
- prediction and evidence checkpoints during the lesson, not only a final
  solution reveal;
- debugging tasks that expose likely misconceptions; and
- human review for alignment, because word, example, and exercise counts
  cannot prove that an assessment measures the intended skill.

### Official Codex guidance: goal, context, boundaries, and done

The [Codex prompting guide](https://learn.chatgpt.com/docs/prompting) recommends
giving a clear goal, relevant context, desired output, and important
boundaries. The
[Codex `AGENTS.md` guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
explains that repository and nested instruction files provide durable,
scope-specific guidance. Repeated workflows belong in a skill rather than in
an ever-longer one-off prompt.

Every DS60 lesson therefore includes an optional **Ask Codex about this
lesson** prompt that:

- identifies the stable lesson ID and exact guide and learner-artifact paths;
- invokes the checked-in `guide-ds60sqlpy-learning` tutoring skill;
- names the lesson outcome and assumed prerequisite boundary;
- keeps `solutions/` closed until the learner asks or completes an attempt;
- requests explanation, prediction, learner evidence, progressive hints, and
  retrieval practice; and
- defines success as a runnable attempt plus an explanation in the learner's
  own words.

The prompt is a convenience, not missing curriculum. A learner must be able to
complete the lesson without Codex or an internet connection.

## DS60 lesson sequence

Each Python and SQL lesson now follows this default sequence:

1. **Orient** — outcome, motivation, prerequisites, and run location.
2. **Model** — vocabulary, mental model, syntax or query anatomy.
3. **Observe** — first runnable example and expected output/result shape.
4. **Contrast** — second example, boundary, common mistake, or alternative.
5. **Predict** — state what will happen before execution.
6. **Practice** — guided change, independent construction, debugging, edge
   case, and transfer.
7. **Verify** — assertions, test cases, row-grain/count checks, or bounded
   expected output.
8. **Explain** — retrieval questions and a short learner explanation.
9. **Extend** — next lesson, optional reference, or Codex coaching prompt.

This sequence is enforced partly by
[`scripts/audit_lesson_depth.py`](../scripts/audit_lesson_depth.py). The audit
is deliberately only a floor. It cannot determine whether an analogy is
accurate, an example is illuminating, or six exercises are genuinely distinct;
human review and execution remain required.
