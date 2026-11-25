# Durable C authoring

Original teaching specifications live in:

- `foundations.py`: c-001 through c-014.
- `composition.py`: c-015 through c-028.
- `systems.py`: c-029 through c-042.
- `render.py`: publication layout, checked program assembly and metadata.

Each case contains a concrete task, expected observation, C source and reasoning.
Each lesson contains a mechanism explanation, vocabulary, syntax anatomy, primary
source and any platform or prepared-project boundary. Preserve the stable order:
IDs are currently derived from position. Add an explicit identity field before
inserting new chapters within the route; do not renumber saved lesson identities.

Use the [prepared contributor formatting toolchain](../../../docker/formatting/README.md),
including Python, clang-format 21.1.8 and its locked parsing dependencies.
From that environment, run the existing command at the repository root:

```sh
python courses/c/authoring/build.py
```

The formatter must be on PATH, or set `C_LESSON_FORMATTER` to an explicit formatter
command for standalone C programs and snippets. Markdown publication also uses
the shared `canonical_markdown` guard and its pinned formatter on PATH;
`C_LESSON_FORMATTER` does not replace that parsing/literal-preservation contract.
Missing prepared tools fail explicitly. No generator installs a formatter or
falls back to unformatted Markdown. Generation writes UTF-8/LF guides, answer-free starters, executable
references, explanations and manifests. It does not execute learner code, install
dependencies or modify the separately authored stats project.

Use raw Python strings for embedded C so null characters, newlines, character
literals and preprocessor syntax survive generation exactly. The renderer formats
complete C programs and snippets; source validity still requires compiler checks.

After generation, run shared module/rendering gates and execute every reference
in the actual c17 worker. During authoring, a prepared compiler can check with:

```sh
cc -std=c17 -Wall -Wextra -Wpedantic -pthread main.c -lm -o lesson
./lesson
```

For memory-sensitive changes, separately compile and run with supported address
and undefined-behavior sanitizers. Keep the compiler version, source identity,
exit result and diagnostic distinct from ordinary runtime receipts. Do not weaken
assertions, hide warnings or execute a known invalid access merely to obtain a
demonstration.

The first two cases are worked examples; the remaining cases extend, debug,
bound or transfer the mechanism. Supporting helper code is teaching material.
The complete six-case reference and explanations remain a separate reveal.

## Outcomes and derived practice

`outcomes.py` holds one specific, observable outcome per lesson ID (plus an
optional minutes override for the capstone); the renderer refuses a missing or
templated outcome. The published `lab` and `verification` fields both come from
the first independent investigation (case 3).

Exercises 1 and 2 are derived from the worked examples rather than repeating
them: exercise 1 changes one input of worked example 1 and asks for a prediction,
exercise 2 shows a one-token regression of worked example 2 to diagnose. Every
`Verify` line and hint names that case's own CHECK and a one-token edit that was
executed and observed to make that CHECK fail. The observations live in
`variants.json` and are refreshed after any case change:

```sh
python courses/c/authoring/qualify_variants.py
```

It needs a local Docker engine and the prepared `ds60sqlpy-worker-c17` image.
Each candidate mutant is built with the classroom flags plus AddressSanitizer and
UndefinedBehaviorSanitizer, and thread lessons are also built with
ThreadSanitizer. A candidate with any sanitizer report, timeout or crash is
rejected, so practice never asks a learner to run undefined behavior. Unmodified
references must pass the same sanitized build first. Edits to real computation
are preferred over edits to a CHECK's own comparison. Rendering never executes
code and stops with a clear message if a case changed after its record was made.

`transfer.py` holds the authored, lesson-specific prose that used to be
templated: `PITFALLS` gives every lesson its own common-mistake paragraph, and
`TRANSFER` gives each lesson without reasoning notes its own transfer task
(reasoning lessons keep theirs in their notes). Each entry names that lesson's
real helpers and cases, so check it against the reference `main.c` when a case
changes. Shared operating steps (running a lesson, the always-on `CHECK`, the
exercise routine, diagnosis order and the execution boundary) live once in
[`../STUDY-GUIDE.md`](../STUDY-GUIDE.md); guides and solutions link to its
sections instead of repeating them.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.

## Canonical Markdown publication

The renderer passes each completed guide and explanatory solution through the
shared in-memory Markdown adapter before its normal write. Only admitted fenced
program bodies may change; prose, TeX, delimiters, literal values and unsupported
regions keep their documented preservation rules. Standalone C files retain the
existing assembly and formatter path, and the always-active CHECK helper remains
unchanged. The adapter does not compile or execute a lesson.

This builder has no separate `--check` flag. Verify reproducibility by hashing
its outputs, rerunning the same command in the same prepared environment and
comparing hashes. Then run the normal shared formatting/content checks. In the
prepared tool environment, the read-only fence check is:

```sh
python scripts/format_inline_code.py --check --language c
```

Inspect preserved-fragment diagnostics instead of counting those fragments as
formatted programs. Do not repair a generated guide directly or weaken a
publication/runtime assertion to satisfy formatting. Shared readers remain a
separate root-owned generation step.
