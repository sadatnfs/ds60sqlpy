# Reproducible Swift authoring

Prepare Python and the [pinned shared formatting toolchain](../../../docker/formatting/README.md),
including `swift-format from Swift 6.3.3` and the shared toolchain's locked syntax parsers.
Any other supported language fences require their prepared formatter/parser too.
Then run from the repository root:

```sh
python courses/swift/authoring/build.py
```

`foundations.py`, `composition.py` and `advanced.py` contain the original chapter
specifications, examples, task contracts and diagnosis. `render.py` writes the
published artifacts and manifests. Its central writer passes only Markdown
through `scripts.format_inline_code.canonical_markdown` in memory before the
normal write, preserving the existing final-newline rule. The shared policy must
explicitly admit each generated Markdown output path. Unsupported snippets,
transcripts and protected regions retain their bytes with preservation
diagnostics. Missing prepared tools/parsers or genuine formatting errors stop
generation; there is no silent fallback or automatic download.

The source order defines stable IDs swift-001 through swift-048. Do not reorder existing specifications or renumber them after publication. Additive work requires a reviewed stable-ID strategy. The three stages each have sixteen lessons.

To check reproducibility, hash the track, manifest, guides, learners and solutions, rerun build.py, and compare hashes. Generated HTML belongs to the shared reader generator and is never edited here. Project fixtures are directly authored source, not output of build.py.

Runtime checks are separate from generation. Every reference combines both worked scenarios with explicit invariant checks. Independent and transfer tasks can have several valid designs; explanatory solutions state the reasoning rather than promising a hidden grading engine. The profile `swift-linux` must actually compile and execute source before runtime success is claimed.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
