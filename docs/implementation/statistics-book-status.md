# Statistics book implementation status

Updated 22 October 2026. Work occurs directly in the user repository; no staging, commits, pushes, Docker operations or changes to the original supplied outline.

## Current checkpoint

The source outline has 40 numbered sections and 1,005 bold method bullets. `courses/statistics-ml/source-outline.md` is a byte-preserved copy. `manifest.json` and `coverage.json` map every method to stable chapter and topic IDs. Chapter IDs are `statistics-001` through `statistics-040`; topic headings use `stat-SS-NN` so Markdown renderer anchors resolve directly.

Chapters 1-24 have authored first-pass explanations for every source bullet, complete offline programs, numerical expectations and answered interview discussions. Core regression, experiment, causal, Bayesian, ensemble and PCA chapters include initial derivations. This is not yet a claim of final requested book depth: an additional case-study and detailed-method pass is underway for chapters 1-24. A second writer owns chapters 25-40 and their examples; completion of those files must be checked rather than inferred from the manifest.

The user explicitly requested no exams or problem sets. Tutorial examples are complete demonstrations, and interview questions have explanatory answers. There are no hidden answer or exercise-completion requirements.

## Execution evidence

Chapter programs 1-22 ran successfully in the prepared local Python 3.12 scientific environment: NumPy 2.4.6, pandas 2.3.3, SciPy 1.18.0, scikit-learn 1.9.0 and statsmodels 0.14.6. Each program uses tiny local fixtures, deterministic seeds where random behavior is demonstrated, a main guard and meaningful numerical assertions. No data/model downloads or cloud calls occurred.

On this restricted macOS process, joblib emitted one physical-core discovery warning and fell back to logical cores; the chapter assertions still passed. This warning is environmental, not a model-convergence failure. Chapters 23-40 and the final all-book regression suite remain to be checked after authoring and revisions complete. No Docker, Windows or Linux execution claim is made by these local tests.

## Remaining work

- Expand the first-pass chapter treatments with longer connected case studies, derivations, diagnostics, method comparisons and interpretation, especially foundations 1-10 and core model families.
- Finish and validate the second writer's chapters 25-40.
- Verify all 1,005 topic anchors, method-body coverage, local links, source digest, declared dependencies and every standalone program.
- Add focused book contract tests and update this checkpoint with final counts and actual validation results.
- Keep root-owned catalog, reader and classroom integration separate from content execution evidence.
