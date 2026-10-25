# nlp-005 through nlp-024 authoring sources

These explicit lesson bodies, worked snippets, fixtures and reference programs reproduce the authored advanced handoff. They use no external corpus or model download. The source text is original teaching material; primary references are linked in each guide. Root-owned nlp-001 through nlp-004 artifacts and manifest entries are preserved. The entry point merges only nlp-005 through nlp-024 into canonical lessons.json.

From the repository root, `python courses/nlp/authoring/advanced/build_all.py` writes the guides, learners, solutions, fixture ledgers and canonical lessons.json entries for nlp-005 through nlp-024. It authors files but does not run examples or certify a runtime. Run `python -m pytest tests/test_nlp_advanced.py` in the prepared environment to execute guide snippets, reference checks and negative controls offline. Regenerate the shared readers through the normal root integration workflow after intentional changes.

Learner sources preserve incomplete functions. Executable answers remain under solutions/. Handcrafted vectors, tiny attention layers, lexical extraction and vote aggregation are labeled by their actual mechanisms. They do not claim pretrained-model quality, broad multilingual coverage or a production authorization service.

## Shared maintenance gates

Use [CONTRIBUTING](../../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
