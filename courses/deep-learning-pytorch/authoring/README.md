# PyTorch course authoring sources

The original topic specifications and renderer generate all 36 bundles while preserving reviewed track IDs, prerequisites and paired TensorFlow IDs. Run `python courses/deep-learning-pytorch/authoring/build.py` from the repository root. Authoring uses Python and the pinned Ruff formatter from the repository quality environment. It does not import PyTorch or execute training.

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

## Canonical displayed code

The owner renderer passes Markdown through the shared guarded fence formatter
before writing it. Python fences use the pinned Ruff tool already present in
the Core quality environment, with independent AST, literal and comment guards.
Missing tools fail explicitly; generation never installs a dependency or runs
framework examples. Formatting configuration comes from the renderer's stable
source root even when a regeneration test uses a temporary output directory.

For a formatting-only publication pass, run this directory's normal `build.py`
with `--markdown-only`. That mode writes guides and explanatory solutions while
preserving standalone learner/reference programs, plans, manifests and review
ledgers. Normal full generation retains its existing scope. After generation,
apply the maintained prose normalizer and the shared reader/TeX pipeline.

Historical execution and frozen-artifact receipts remain unchanged. Changed
Python fence layout needs the separate self-verifying
`curriculum/inline-format-parity.json` binding from a retained pre-format source
snapshot. Its verifier preserves non-code spans, fence identities, Python AST
values/type comments and ordered comments before exposing historical bytes for
old hash assertions. This is static formatting parity, not new execution.
