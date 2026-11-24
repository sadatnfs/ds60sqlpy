---
phase: 04-worked-examples-practice
type: verification
status: passed
requirements: [CURR-03, CURR-04]
---

# Phase 4 verification: worked examples and practice

## Success criteria

| # | Criterion | Result | Evidence |
| --- | --- | --- | --- |
| 1 | Every authored lesson has a substantive, accurate worked example with explanation and interpretation appropriate to its subject, including a suitable non-code artifact where execution is not the learning objective. | PASS | Live `curriculum/coverage-matrix.json`: 1838 lessons, 0 gaps, minimum 2 fenced examples and minimum 1050 guide words per lesson. All 360 non-runnable lessons (348 `reading-check`, 11 `module-check`, 1 `k8s-readiness-v1`) carry at least 2 fenced non-code artifacts such as plans, manifests, tables, logs or derivations, each followed by an interpretation (decision D3). The accuracy spot-check covered 37 tracks (about 75 lessons) and ran every changed Python, C and C++ block. It found 10 issues: 1 factual, 3 misleading and 6 cosmetic. Every factual, misleading and spacing issue is fixed in the authoring sources; see "Spot-check" below. |
| 2 | Every practice lesson progresses from supported reasoning or modification toward independent application and includes a solution or feedback that explains its reasoning. | PASS | All 1365 practice lessons have at least 6 exercises and a solution of at least 700 words. Their exercises move from guided reading or modification to independent tasks, and each solution covers approach, correctness, a plausible wrong approach and how to verify the result (decision D4). The `thin-guide`, `few-examples` and `thin-solution` ceilings in `tests/test_coverage_matrix.py` are 0. The templated-prose ratchet fell from 970529 to 835280 words, and the matrix enforces that it cannot rise. |

## Spot-check

The report is in `work/spotcheck-0403/report.md` (not committed).

- **Automated runs:**
  - C and C++: 166 of 168 blocks compile and run. The other 2 are cpp-002's intentional exit-code demonstration.
  - Python: 387 blocks match their stated output.
  - statistics-ml: 24 of 24 experiment blocks match when run with their example prefix.
  - No Example B duplicates its Example A.
- **Fixed:**
  - spark-deploy-008: the zip is now deterministic, and the stated hash `71643e7b37ffcc2e` is reproducible.
  - apache-015: the worked case code, prose and output now agree.
  - tf-009: Example A counts and asserts its 3 updates; Example B's prose matches its arithmetic.
  - k8s-056: the key term now says `externalTrafficPolicy: Local` "can preserve" the client source IP.
  - Missing spaces fixed in llm-applied, llm-theory, java-020 and spark-008.
- **Not fixed:** about 345 decimals without a leading zero ("0.5" written as ".5") and some missing comma spacing are spread across many generators. They are cosmetic and listed as known issues.

## Commands

```bash
.venv/bin/python scripts/build_lesson_readers.py
.venv/bin/python scripts/build_coverage_matrix.py --check
.venv/bin/python scripts/check_modules.py
.venv/bin/python scripts/check_walkthroughs.py --check
.venv/bin/python scripts/sync_example_fences.py --check
.venv/bin/python scripts/record_inline_format_parity.py --verify
.venv/bin/python -m pytest -n 6 -q tests/test_phase2_format_policy.py tests/test_format_repo.py \
  tests/test_lesson_reader.py tests/test_walkthroughs.py tests/test_module_ui.py \
  tests/test_coverage_matrix.py tests/test_track_qualification.py tests/test_catalog.py \
  tests/test_lesson_depth_audit.py
node scripts/check_classroom_ui.mjs
DS60_FORMAT_IMAGE=ds60-formatting:893716821-765 ./scripts/format-repo --check --language cpp
```

## Results

- **Targeted pytest:** 314 passed, 40 xfailed. The xfails are the Phase 5 track-qualification ratchets owned by 05-05.
- **Coverage matrix:** "Coverage matrix is current", 0 gaps, 835280 templated words.
- **Other gates:**
  - Walkthroughs: 96 across 32 tracks.
  - Example fences: 0 changed.
  - Inline-format parity: 275 guides verified, and presentation parity prints `0 Counter()`.
  - Classroom UI: 110 of 110 checks.
  - Ruff, ruff format and mypy are clean.
- **cpp formatting:** "Formatting checks passed" after the 76 cpp guide fences were formatted. The cpp generator still emits unformatted code, so run `format-repo --language cpp` after regenerating that track.

## Known limits

- **Templated prose (D6):** 835280 words are measured and ratcheted, not rewritten.
- **Not executed:**
  - 20 Python blocks need libraries the check environment does not have: torch, jax, tensorflow, polars and pyspark.
  - The Java, R, Julia, Go, Rust and .NET examples were checked by reading only.
  - apache-015 was checked against equivalent plain Python logic because datafusion is not installed.
- **Hand-patched outputs:** the k8s-056 and java-020 fixes were applied to their generated outputs by hand. Their builders need the prettier and tree-sitter tools in the formatter image, and the authoring sources hold the same text.
