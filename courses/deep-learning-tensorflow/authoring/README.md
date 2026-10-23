# ML lesson authoring sources

These original topic specifications and renderer maintain the completed TensorFlow and LLM lesson bundles. They are authoring tools, not learner runtime dependencies. The existing first8 TensorFlow and first9 LLM lessons remain independently authored and are preserved.

Run from the repository root with a prepared Python interpreter:

```text
python courses/deep-learning-tensorflow/authoring/build.py
```

The renderer writes only the two ML course guides, learner worksheets, separate solutions and authored manifests. It does not change active catalog registration, runtime qualification, learner state or the shared practice registry. Each topic specification contains its own mechanism explanation, API anatomy, six concrete exercises, arithmetic expectations and explanatory solution code. After editing, run the focused ML tests and the relevant prepared runtime references.

The original executable worked examples now have a standalone fresh-process contract. Each ordinary later block includes the required preceding fixture setup; a topic can supply explicitly independent `worked_examples` and focused `preamble` text. `llm010.py` contains the reviewed position/normalization derivation and readable reference. The renderer's `guides_only=True` mode repairs guide presentation without rewriting already-qualified reference programs. `tests/test_ml_module_lessons.py` executes each core worked program in a new process and exposes explicit opt-in TensorFlow/Torch cases. Exact Docker qualification inventories can be generated under ignored `work/` with source and guide hashes.

## Prose review layers

`depth_reviews_tf.py` supplies the 26 topic-specific derivation and diagnosis
additions recorded in `docs/implementation/tensorflow-depth-review.md`. The
`tf.py` hook applies them after the executable specifications are registered.
Use `write_all(only=set(DEPTH_NOTES), guides_only=True)` for a prose-only pass
and compare all Python fences and learner/reference hashes before and after.
Do not infer executable changes from a Markdown file hash alone.

`depth_reviews_llm.py` supplies the reviewed theory prose for012-015 and017-042;
010,011 and016 retain their dedicated detailed mechanism modules. The hook also
repairs selected prose spelling without touching executable exercise code.
Reading chapters have written reasoning instructions and text examples, while
executable worked examples retain their declared standalone contracts. The
current content/evidence checkpoint is `docs/implementation/ml-content-status.md`.

## Unified classroom presentation

Author mathematical expressions with explicit LaTeX `\( ... \)` and standalone
`\[ ... \]` delimiters. Tag every fenced code example with its actual language.
After regenerating older prose sources, run `python scripts/normalize_math_prose.py --write`
from the repository root before rebuilding HTML readers. The reviewed
`curriculum/math-prose.json` registry preserves this migration across regeneration;
it does not change executable fences, notebook code or the supplied statistics
outline. The public learner entrypoint is `/classroom`, shared by every subject.
See [the content contract](../../../docs/content-authoring.md) for the rendering
and subject-theme requirements.
