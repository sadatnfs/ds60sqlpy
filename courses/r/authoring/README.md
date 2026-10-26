# Authoring the R curriculum

The sixty `units/r-*.json` records are the durable source. Each includes a title,
level, direct prerequisites, observable outcome, mechanism, vocabulary, syntax
explanation, two standalone worked programs, six varied tasks, hints, a starter,
a complete reference, explained answers and primary references.

Edit those records and preserve every stable ID. Each worked program and reference
must start from its own local input in a fresh R process. The reference uses
meaningful assertions and ends with its own `r-XXX reference checks passed` marker.
That marker describes the explicit checks, not a universal correctness verifier.
A starter supplies inputs and incomplete work, with no unconditional failure just
to force the learner to edit it. Do not include installation or download calls.

From the repository root, in the prepared contributor environment:

```bash
python3 courses/r/authoring/build.py
python3 courses/r/authoring/build.py --check
PYTHONPATH=src python3 -m pytest tests/test_r_content.py tests/test_r_advanced_content.py
python3 courses/r/authoring/check_references.py --workers 2 --report /tmp/ds60-r-reference-checks.json
```

All sixty units are required before the assembler publishes admission. It emits
the Markdown code fences and complete references from the same source fields.
Format R source fields with the pinned styler contract, verify parsed-expression
identity, and regenerate. Formatting only an emitted reference without updating
its JSON source creates drift. Use repository lint/format checks and coordinate
shared reader generation after this subject is frozen.

The reference checker uses the existing image for the repository release, resolves
it to an image ID, and runs starters, references and worked programs with networking
disabled. It never builds or pulls an image and never mounts learner data. Its
read-only containers have bounded CPU, memory and process counts plus an owned
temporary filesystem. Cleanup addresses only the current UUID-named container,
including after a timeout. The JSON report binds each actual source hash to its
observed exit, output and marker. Use `--image` for an explicitly selected local
image when qualifying a different prepared version. Base plotting and explicit `print(ggplot_object)` or
`print(plotly_object)` need the worker's actual figure-capture path in addition to
plain Rscript checks. Browser display, keyboard interaction and saved-result
readback remain separate integration checks. Keep at most two figures per run.

Tests should preserve input and output contracts, failure cases and independent
numerical expectations. Statistical examples must distinguish descriptive,
predictive and causal claims. Tiny synthetic model checks are not production
model acceptance. Optional package projects and bounded parallel operations must
state their actual process/filesystem boundary rather than promise unsupported
behavior from the classroom pad.
