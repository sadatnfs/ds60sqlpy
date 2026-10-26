# Maintaining the offline DAX course

The durable teaching records are `part01.py` through `part10.py`. Each supplies six
distinct units with mechanism teaching, expression anatomy, at least two named
worked cases and six varied practice tasks with hints and explained answers.
`progression.py` owns direct prerequisite edges and chapter-specific starter pads.
`fixtures.py` owns the tiny original models, including the complete date dimension.
`build.py` emits all admitted Markdown, DAX, JSON and CSV artifacts deterministically.

From the repository root:

```bash
python3 courses/dax/authoring/build.py
python3 courses/dax/authoring/build.py --check
PYTHONPATH=src python3 -m pytest tests/test_dax_content.py
```

Use the prepared contributor environment for pytest and repository formatting.
The generator needs only the Python standard library and never executes DAX or
uses a network connection. Shared reader generation happens after subject sources
are frozen. Preserve source literals during prose or formatting work.

The `reference-results.json` contract is version 1, track `dax`, with one record
per lesson. Each record names an owned reference path and model path, their actual
SHA-256 values, `evidence: hand-derived`, and bounded named cases. Cases contain
plain-text context and trace, typed columns, primitive cells and an explicit note.
Allowed column types are number, integer, text, boolean and ISO date. JSON null
represents DAX BLANK. Maximums are six cases, twelve columns and one hundred rows.

Model JSON identifies each CSV's exact hash, typed columns, grain, key and explicit
relationships. Keep the deliberately broken unknown-member model distinct from
the clean retail model. Metadata for role policies and preview calendars is an
offline specification, not evidence that the classroom installed an engine model.

Add a changed-context or edge case before broadening a formula's claimed domain.
Reconcile results independently from fixture rows. Retain feature/version notes,
source links and the distinction between semantic, security and performance proof.
The focused tests check these boundaries and representative numerical oracles;
they deliberately do not pretend to be a DAX interpreter.
