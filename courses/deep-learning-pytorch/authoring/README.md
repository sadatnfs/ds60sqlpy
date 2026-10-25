# PyTorch course authoring sources

The original topic specifications and renderer generate all 36 bundles while preserving reviewed track IDs, prerequisites and paired TensorFlow IDs. Run `python courses/deep-learning-pytorch/authoring/build.py` from the repository root. Authoring uses the Python standard library and does not import PyTorch or execute training.

`specs.py` owns the literal fixtures, helpers, exercise programs, basic concepts and framework comparisons. `depth_reviews.py` owns the foundation review, shared prose corrections and review-matrix builder. `depth_reviews_advanced.py` supplies the independently reviewed advanced chapters through the same callback. `render.py` publishes guides, learner worksheets, executable references and explained solutions. Edit these durable sources before regenerating; direct edits to generated artifacts will be detected by the regeneration test.

Each topic contains mechanism and shape/state reasoning, three worked examples, six distinct exercise checks, a framework comparison, answered interviews, method-selection decisions and topic-specific diagnosis. The review additions include analytic extensions that are identified separately from executed checks. The machine-readable `review_matrix.json` records concrete findings, paired-guide review and whether executable or worked code changed. Its completion is a source-review claim, not a runtime receipt.

Worked Examples A-C execute sequentially in one scratch file. Imports, helpers and initial fixture state appear in A, while later blocks may reuse or mutate earlier state. Reproduce all three as one fresh program. The separate reference contains all six exercises. The focused tests compare their Python syntax trees so displayed calculations cannot silently drift from reference setup or the first three exercises.

Run the focused host checks with the repository's prepared development interpreter:

```text
python -m pytest tests/test_pytorch_lessons.py -q
```

The host suite checks all 36 bundles, paired links, practice contracts, exact regeneration, worked/reference parity and bounded child programs. Actual numerical reference tests are opt-in through `DS60_TEST_TORCH=1` inside the separately prepared PyTorch runtime. A host skip does not establish execution. Changes to reference behavior or worked programs require new parent-owned prepared-worker receipts. These authoring tools do not download data or models, install packages, change shared runtime definitions or modify learner state.

## Unified classroom presentation

Author mathematical expressions with explicit LaTeX `\( ... \)` and standalone
`\[ ... \]` delimiters. Tag every fenced code example with its actual language.
After regenerating older prose sources, run `python scripts/normalize_lesson_prose.py --write`
from the repository root before rebuilding HTML readers. The reviewed
`curriculum/math-prose.json` registry preserves this migration across regeneration;
it does not change executable fences, notebook code or the supplied statistics
outline. The public learner entrypoint is `/classroom`, shared by every subject.
See [the content contract](../../../docs/content-authoring.md) for the rendering
and subject-theme requirements.

Generators read and write UTF-8 explicitly and publish LF newlines on every OS.
The regeneration test also simulates Windows text defaults and compares exact
artifact bytes; do not normalize away a mismatch in the assertion.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
