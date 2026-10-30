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

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
