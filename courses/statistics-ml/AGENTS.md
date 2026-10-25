# Statistics and machine learning book authoring

This is an explanatory tutorial book. Its learning mode has no exams or problem sets. Do not add exercise counts, graded tasks, official solution gates, or automatic mastery claims. Interviews are answered discussions. Runnable demonstrations are complete worked examples, not submissions.

Preserve source-outline.md byte-for-byte. Every bold method in its 40 numbered sections has a stable topic ID in coverage.json. Preserve IDs and chapter anchors when improving prose. The original outline remains the scope reference; the book prose must explain mechanisms, assumptions, selection, failure modes and interpretation rather than merely reproduce definitions.

Examples use tiny deterministic offline fixtures, standard library and declared NumPy, pandas, SciPy, scikit-learn or statsmodels APIs. Optional scientific packages and pretrained models are not imported by default. Every script has a main guard and numerical assertions. No network requests, shell commands, credentials or downloads in examples. Reading does not require a runtime. Do not use em dashes.


After styling standalone examples, run `python scripts/sync_example_fences.py`
before rebuilding readers. The helper updates only this book's manifest-linked
complete Python fences after proving AST equivalence, including literal values.
Use `--check` to detect drift without writing. A missing or ambiguous match
requires reviewing the chapter and example together; never overwrite unrelated
or intentionally invalid teaching snippets. The full formatter runs this step.

Chapters, examples, manifest and coverage are maintained sources. Keep the
shared renderer, source-prose normalizer and statistics fence synchronizer as
separate owners. Use [the book's guide](README.md) and focused tests before
changing coverage. Link related NLP/LLM/framework/CUDA explanations without
turning the tutorial into mandatory exercises or equating code execution with
statistical validity.
