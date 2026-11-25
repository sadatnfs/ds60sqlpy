# Durable Java authoring

`specs.py` contains the original teaching cases, `render.py` assembles the
published artifacts, and `build.py` is the normal entrypoint. Preserve the
existing java-001 through java-036 identities, prerequisites, six exercise
contracts, answer-free starters and separate checked references. Directly
authored multi-file fixtures remain under their existing ownership.

Use the [prepared contributor formatting toolchain](../../../docker/formatting/README.md),
including its locked Python parsing dependencies, Prettier 3.6.2 and
prettier-plugin-java 2.7.7. Run from the repository root inside that environment:

```sh
python courses/java/authoring/build.py
```

The command is unchanged. Before writing a guide or explanatory solution, the
renderer passes its completed Markdown through the shared in-memory
`canonical_markdown` adapter. The adapter checks ownership, parsing, protected
literal values and idempotence. It changes only admitted fence bodies and
reports explicitly preserved fragments or transcripts. Missing prepared tools
are errors, with no silent raw-output fallback or automatic download. The
generator does not compile or execute Java.

The renderer retains its existing UTF-8/backslashreplace serialization before
those guards. In particular, authored Python surrogate code units become the
same Java Unicode escapes that the previous file writer produced. This does
not replace literal contents with a visually similar string. Standalone Java
solutions and starter files keep their existing assembly and normal shared
source-formatting route.

There is no separate builder `--check` mode. Hash the generated artifacts, rerun
the command in the same prepared environment and compare hashes. Follow the
normal source formatting step, then the read-only Java fence check:

```sh
python scripts/format_inline_code.py --check --language java
```

Run the Java publication contracts in `tests/test_java_lessons.py`. Actual JDK
qualification uses the explicitly prepared Java 21 environment, with assertions
enabled; preserve H2 and other declared fixture boundaries. Existing checks for
source literals, child-JVM environment and separate diagnostic output remain
unchanged. A generation or formatter pass is not compiler, runtime or learner
mastery evidence.

## Outcomes and derived practice

`outcomes.py` holds one specific, observable outcome per lesson ID; the renderer
refuses a missing outcome or one that merely repeats the mental model. The
published `lab` and `verification` fields both come from exercise 3, the first
authored investigation. Required work never runs inside an `assert` statement:
store the result first and assert on the stored value, so a launch without `-ea`
still performs every operation.

Exercises 1 and 2 are derived from Examples A and B instead of repeating them:
exercise 1 changes one input of Example A and asks for a prediction, exercise 2
presents a one-token regression (or an edited assertion) in the code that
Example B adds. Every `Verify` line names that exercise's own assertion and a
one-token edit that was executed and observed to make that assertion fail, and
the hints for exercises 1 and 2 walk through that edit, or through an executed
example defect when the exercise asks the learner to inject one. The renderer
locates the edit in the formatted snippet that learners see, so it calls the
same `canonical_markdown` adapter on the six
exercise fences. The observations live in `variants.json` and are refreshed
after any exercise change:

```sh
python courses/java/authoring/qualify_variants.py
```

It needs a local Docker engine and the prepared `ds60sqlpy-worker-java21` image.
Each mutant is compiled with the classroom `javac` flags and run with `-ea`,
offline and without a repository mount. Unmodified references must pass first,
and a mutant counts only when the targeted exercise's own assertion fails; a
timeout, compile error or other exception is not counted. Edits outside an
assertion are preferred. Rendering never executes code and stops with a clear
message if an exercise changed after its record was made.

## Lesson-specific teaching text and the shared study guide

Operating instructions that are the same for every lesson (classroom and native
JDK steps, how the six exercises are built, the hint routine, failure triage,
when to open solutions, moving on and evidence levels) live once in
[`../STUDY-GUIDE.md`](../STUDY-GUIDE.md); every guide and explanatory solution
links to its anchors instead of repeating them.

The per-lesson prose for how to run, prediction, pitfalls, the six progressive
hints, retrieval and the after-comparison follow-up lives in `teaching.txt`, one
`== java-NNN` block per lesson with one `field: text` line per field.
`teaching.py` loads it into `TEACHING` and refuses a duplicate lesson or a
missing, duplicate or unknown field. Each hint is a three-rung ladder whose
sentences start with `First`, `Then` and `Finally,` (no other sentence may start
with a sequencing word), so the classroom can reveal one rung at a time. Write
every field about that lesson's own code and failure modes; text that would
still be true after swapping in another lesson's topic belongs in the study
guide.

Use [CONTRIBUTING](../../../CONTRIBUTING.md) and the
[validation guide](../../../docs/validation.md) for shared checks. Refresh shared
readers only after the owner-generated content passes its checks; never edit
generated HTML or weaken publication assertions to hide drift.
