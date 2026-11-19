# Durable Go authoring

The source of every published Go lesson is the original specification in:

- `foundations.py`: lessons 001-016.
- `composition.py`: lessons 017-032.
- `systems.py`: lessons 033-048.
- `render.py`: teaching layout, one-file program assembly and manifest derivation.

Every case stores its task, expected observation, executable code and explanatory
answer. A lesson stores its original mechanism explanation, syntax anatomy,
vocabulary, primary source and any external-workflow boundary. IDs are derived
from the stable ordered sequence, so append new lessons or introduce an explicit
identity field before inserting within the sequence. Never renumber existing
lessons as a cosmetic edit.

Prepare Python and the [pinned shared formatting toolchain](../../../docker/formatting/README.md)
before authoring. Go generation requires `gofmt` from Go 1.27.3 and the
shared toolchain's locked syntax parsers. Any other supported language
fences also require their prepared formatter/parser. Run from the repository
root:

```sh
python courses/go/authoring/build.py
```

The renderer uses `gofmt` to publish readable, deterministic Go source. Each
generated guide and explanatory-answer Markdown document also passes through
`scripts.format_inline_code.canonical_markdown` in memory immediately before
its normal write. The shared policy must explicitly admit that generated
output path. Unsupported snippets, transcripts and protected regions retain
their bytes with preservation diagnostics. Missing prepared tools/parsers or
a genuine formatting failure stop generation; there is no silent fallback
or automatic download.

Generation does not execute references, fetch dependencies or contact clusters. It rebuilds
`track.json`, `lessons.json`, all guides, starter pads, executable references and
explanatory solutions. The prepared client-go project under `fixtures/` is directly
authored and is not overwritten by the renderer.

After generation, run the shared module and rendering checks documented in the
root contributor guide. Execute all references in the prepared Go Docker worker,
including compile-error and bounded-execution checks supplied by the platform.
A local `go run` pass is useful during authoring but must be reported separately
from worker and browser acceptance.

Do not hide implementation answers in starter pads. They contain the task and
expected observations only. Supporting helper declarations in guides are
teaching material; the complete six-case reference remains a separate reveal.
Use raw Python string literals for embedded Go code so escapes and struct tags
survive regeneration exactly.

## Outcomes and derived practice

`outcomes.py` holds one specific, observable outcome per lesson ID (and an
optional minutes override for larger lessons); the renderer refuses a missing or
templated outcome. The published `lab` and `verification` fields both come from
the first independent investigation (case 3).

Exercises 1 and 2 are not copies of the worked examples. `variants.py` derives
them from the worked cases: exercise 1 changes one input of worked example 1 and
asks for a prediction, exercise 2 shows a one-token regression of worked example 2
to diagnose. Every `Verify` line and hint names that case's own check and a
one-token edit that was executed and observed to make the check fail. Those
observations live in `variants.json` and are refreshed after any case change:

```sh
python courses/go/authoring/qualify_variants.py
```

It needs a local Docker engine and the prepared `ds60sqlpy-worker-go` image. It
compiles each candidate mutant offline with the classroom's fixed import
configuration, first confirms that every unmodified reference passes, keeps
records for unchanged cases, and prefers an edit to real computation over an edit
to a check's own comparison, then an edit that fails the case's main (last) check.
Rendering never executes code; it stops with a clear message if a case
changed after its record was made.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
