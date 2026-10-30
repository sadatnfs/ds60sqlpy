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
