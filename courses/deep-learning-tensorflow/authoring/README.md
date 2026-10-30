# ML lesson authoring sources

These original topic specifications and renderer maintain the completed TensorFlow and LLM lesson bundles. They are authoring tools, not learner runtime dependencies. The existing first eight TensorFlow and first nine LLM lessons remain independently authored and are preserved.

Run from the repository root with a prepared Python interpreter:

```text
python courses/deep-learning-tensorflow/authoring/build.py
```

The renderer writes only the two ML course guides, learner worksheets, separate solutions and authored manifests. It does not change active catalog registration, runtime qualification, learner state or the shared practice registry. Each topic specification contains its own mechanism explanation, API anatomy, six concrete exercises, arithmetic expectations and explanatory solution code. After editing, run the focused ML tests and the relevant prepared runtime references.

The original executable worked examples now have a standalone fresh-process contract. Each ordinary later block includes the required preceding fixture setup; a topic can supply explicitly independent `worked_examples` and focused `preamble` text. `llm010.py` contains the reviewed position/normalization derivation and readable reference. The renderer's `guides_only=True` mode repairs guide presentation without rewriting already-qualified reference programs. `tests/test_ml_module_lessons.py` executes each core worked program in a new process and exposes explicit opt-in TensorFlow/Torch cases. Exact Docker qualification inventories can be generated under ignored `work/` with source and guide hashes.

## Prose review layers

`depth_reviews_tf.py` supplies the 26 topic-specific derivation and diagnosis
additions. Their durable explanations and focused content tests are authoritative. The
`tf.py` hook applies them after the executable specifications are registered.
Use `write_all(only=set(DEPTH_NOTES), guides_only=True)` for a prose-only pass
and compare all Python fences and learner/reference hashes before and after.
Do not infer executable changes from a Markdown file hash alone.

`depth_reviews_llm.py` supplies the reviewed theory prose for llm-012 through llm-015 and llm-017 through llm-042;
llm-010, llm-011 and llm-016 retain their dedicated detailed mechanism modules. The hook also
repairs selected prose spelling without touching executable exercise code.
Reading chapters have written reasoning instructions and text examples, while
executable worked examples retain their declared standalone contracts. Keep runtime evidence in immutable source-bound JSON receipts or current CI
artifacts. [The maintained checkpoint](../../../docs/implementation/CHECKPOINT.md)
records architectural constraints rather than past session counts.

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
