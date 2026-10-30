# nlp-005 through nlp-024 authoring sources

These explicit lesson bodies, worked snippets, fixtures and reference programs reproduce the authored advanced handoff. They use no external corpus or model download. The source text is original teaching material; primary references are linked in each guide. Root-owned nlp-001 through nlp-004 artifacts and manifest entries are preserved. The entry point merges only nlp-005 through nlp-024 into canonical lessons.json.

Prepare Python and the [pinned shared formatting toolchain](../../../../docker/formatting/README.md), including Ruff 0.16.0 for Python fences and the locked syntax parsers needed by any other supported fence languages. Then run from the repository root:

```sh
python courses/nlp/authoring/advanced/build_all.py
```

The command writes guides, learners, solutions, fixture ledgers and canonical lessons.json entries for nlp-005 through nlp-024. Its five batch files run in their existing order, followed by enhance.py. The author writes generated Markdown through `scripts.format_inline_code.canonical_markdown` in memory. The later enhancer applies the same hook immediately before its guide, answer and related-track writes, so newly inserted worked traces are canonical too. Python learner/reference files, fixture JSON and manifest assembly retain their existing writers.

The shared policy must explicitly admit each generated Markdown path. Unsupported snippets, transcripts and protected regions retain their bytes with preservation diagnostics. Missing prepared tools/parsers or genuine formatting failures stop generation; there is no silent fallback or automatic download. No new --check mode is provided.

Generation does not run examples or certify a runtime. The unchanged `python -m pytest tests/test_nlp_advanced.py` command executes guide snippets, reference checks and AST-based negative controls offline in the prepared environment. Those assertions remain authoritative. Regenerate shared readers through the normal root integration workflow after intentional changes.

Learner sources preserve incomplete functions. Executable answers remain under solutions/. Handcrafted vectors, tiny attention layers, lexical extraction and vote aggregation are labeled by their actual mechanisms. They do not claim pretrained-model quality, broad multilingual coverage or a production authorization service.

## Shared maintenance gates

Use [CONTRIBUTING](../../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
