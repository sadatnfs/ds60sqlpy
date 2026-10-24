# Statistics book implementation status

Updated 22 October 2026. Agent work occurred directly in the user repository without staging, commits, pushes, Docker operations or modification of the original supplied outline.

## Authored result

- 40 complete tutorial chapters under `courses/statistics-ml/chapters/`.
- All 1,005 bold method bullets in the supplied 40-section outline mapped one-to-one in `coverage.json` to explicit method explanations and stable Markdown topic headings.
- 97,117 whitespace-delimited words across chapter files, including code; this count is a scope measure, not a teaching-quality proof.
- 40 standalone executable chapter programs containing 126 named functions other than main. The functions include demonstrations and supporting computational routines.
- 118 interview questions with explanatory answers.
- Chapter-specific theory, assumptions, selection guidance, failure modes, mathematical derivations, numerical interpretation and extended cases. Core regression, experiments, causal inference, Bayes, ensembles, PCA, validation, uncertainty and forecasting receive connected worked treatments.
- Applied LLM connections cover extraction as measurement, embeddings, grounded synthesis, SFT/LoRA, retrieval and answer evaluation, point-in-time data and accountable domain-assistant workflows. Links point to existing applied-course guides.

The user explicitly requested no exams or problem sets. This is a tutorial book with complete demonstrations and answered interviews, not a graded exercise track. Reading markers do not certify mastery. Specialized methods have explanatory coverage; the book does not claim a production implementation of every research estimator.

## Scope and provenance

`courses/statistics-ml/source-outline.md` is byte-identical to the original supplied source. SHA-256:

```text
146945b484305436b8cdee1fd3eb90b6689c3b32397321f20b2a77b15ae1f938
```

`manifest.json` records repository-relative paths, prerequisites, levels, time estimates, actual imported scientific dependencies and tutorial mode. Chapter IDs are `statistics-001` through `statistics-040`; topic IDs use `stat-SS-NN` in original source order. Repeated method names in different source sections keep separate IDs and contexts. All 1,005 labels and their exact order are checked against the preserved outline.

## Actual validation evidence

The focused command completed with **82 passed in 2.14 seconds**:

```text
python -m pytest tests/test_statistics_book.py -q -p no:cacheprovider
```

The test suite checks source digest and exact method coverage, stable topic headings, nonempty substantive method bodies, answered interviews, no exercise/exam headings, local link resolution, declared core imports, main guards, numerical assertions and verbatim equality between embedded chapter code and standalone programs. Every one of the 40 programs executed with socket connections blocked. No dataset/model downloads or cloud calls occurred. All chapter text and programs were checked for the user's no-em-dash rule.

Execution environment: local macOS arm64 Python 3.12, NumPy 2.4.6, pandas 2.3.3, SciPy 1.18.0, scikit-learn 1.9.0 and statsmodels 0.14.6. The test sets a process-local joblib CPU-count hint to avoid a restricted-macOS physical-core discovery warning. It does not suppress numerical or model-convergence warnings.

This establishes source, structural and local executable-example correctness for this environment. It does not establish Windows/Linux or Docker execution, production statistical validity, or learner mastery. Root-owned catalog/reader/classroom tests provide separate integration evidence. Default programs require only the prepared scientific core; optional XGBoost, PyMC/Stan, NetworkX and other ecosystems are discussed without automatic imports or installation.

## Maintenance

Preserve source-outline.md and stable topic IDs. Revise original chapter Markdown and example programs together, then run the focused suite and root-owned reader/catalog checks. Do not infer broad estimator validity from a tiny demonstration. Keep assumptions, uncertainty limits and claims of actual runtime acceptance explicit.

## Current-source Docker receipt readback

The standardized receipt work/statistics-all-acceptance.jsonl contains 40 successful Core Docker runs. A direct SHA-256 comparison on 23 October 2026 matches every receipt to the current corresponding chapter example. The combined focused suite, including all 82 book checks, also passes. This is executable-demonstration acceptance, not a claim of learner mastery or exhaustive empirical validation of every discussed method.
