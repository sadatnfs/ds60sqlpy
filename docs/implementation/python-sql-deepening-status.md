# Python and SQL deepening implementation status

Updated 22 October 2026. All 18 additive lesson sets are authored. Existing catalog IDs and the gap backlog were inspected before choosing scope, and established day lessons and the historical practice baseline remain unchanged. Agent authoring performed no Git staging, commits, pushes, Docker operations or database-engine startup.

## Authored scope

| Sequence | Stable IDs | Track order | Distinct mechanism |
| --- | --- | --- | --- |
| NumPy | python-numpy-01 through python-numpy-04 | 74-77 | Ownership/strides, axes/contractions, gather/scatter/ties, stable numerical algorithms |
| pandas | python-pandas-01 through python-pandas-04 | 78-81 | Label alignment/nullable logic, availability-time joins, grouped temporal windows, chunked global reductions |
| Algorithms | python-algo-01 through python-algo-04 | 82-85 | Complexity/hash counting, stable ordering/binary search, graphs/heaps, dynamic-programming state design |
| SQL | sql-deep-01 through sql-deep-06 | 74-79 | NULL/quantification, metric algebra, peer-aware window frames, recursive graph state, conditional writes, cohort maturity |

Each lesson has a substantive guide, answer-free learner artifact with two runnable worked examples, separate executable reference and explained solutions. There are 108 distinct progressive tasks, mirrored consistently on all four surfaces. Python guides contain approximately 1,400-1,560 words and explained solutions approximately 1,040-1,325 words. SQL guides contain approximately 1,660-1,725 words and explained solutions approximately 1,150-1,385 words. Counts describe scope; the exact inputs, expected results, counterexamples and explanations provide the teaching evidence.

SQL deep02 builds on sql-quality-01 instead of repeating its independent-child fanout lab: it teaches ratio weighting, semi-additive snapshots, bridge conservation and temporal dimensions. SQL deep05 builds on existing index/concurrency modules with predicate counterexamples, affected-row receipts, optimistic versions and payload-aware idempotency. SQL deep06 separates event occurrence, availability, observation coverage and mature cohort denominators.

## Registration and ownership

`curriculum/extensions/python-sql-deepening.json` registers only completed artifacts and extends the existing Python/SQL tracks with unique order values. It includes three learning goals and explicit stable prerequisites. Root owns the shared practice-expansion registry, generated catalog, dashboard and readers. The twelve Python targets were already registered by root; the six SQL targets and final navigation regeneration were handed off after authoring completed.

## Actual local validation

The complete candidate catalog passed the repository teaching-depth and practice counters. Every learner, guide, explained solution and executable reference has six distinct task labels and inspectable expected results. There are no em dashes or developer-specific absolute paths in the authored learner programs or extension manifest.

All twelve Python learner entrypoints and all twelve executable references ran successfully in the prepared local Python 3.12 scientific environment. Focused tests block socket connections and include independent exhaustive oracles for small knapsack/scheduling problems and duplicate-aware joins. Additional numerical checks cover aliases, empty shapes, repeated indices, stable ties, overflow-resistant normalization, log-sum-exp, cancellation, conditioning, nullable alignment, availability-time lookups, chunk boundaries, stale heap entries and cyclic paths.

The combined focused command completed with **115 passed in 4.34 seconds**:

```text
python -m pytest tests/test_python_sql_deepening.py tests/test_statistics_book.py -q -p no:cacheprovider
```

This comprises 33 deepening checks and 82 book checks. SQL tests in that suite validate artifact contracts and transaction boundaries; they do not claim live SQL execution.

## Live SQL evidence and remaining integration

Root reported that all six final SQL learner/reference pairs passed actual PostgreSQL 16 on its isolated loopback test engine, including every exact reference assertion. The receipt `work/sql-deepening-acceptance.json` contains all 12 results. The validated final deep05 includes a positive-delta guard before idempotency insertion. This authoring agent did not connect to or start a SQL engine.

Every SQL script checks `current_database()`, requires the disposable `advanced_sql_training` target, creates temporary fixtures, uses a 15-second statement timeout and ends with ROLLBACK. Reference cases use independent savepoints and exact JSON row-set comparisons that reject false and NULL assertions. SQL deep05 is a single-session state/receipt model; it does not claim a complete multi-session or distributed-delivery proof.

Remaining root-owned integration: register the six SQL practice targets, regenerate catalog/dashboard/readers after final prose revisions, and run integrated journey/runtime checks. Live SQL reference execution is complete. Local Python success does not establish Windows/Linux or Docker acceptance, and script success does not certify learner mastery.

## Expert review follow-through

A further adversarial review found and repaired intermediate-overflow cases in row/column centering and weighted means. Means now scale before summing, weights normalize before contraction, and an unrepresentable centered or squared-distance result is rejected explicitly. Reference checks include uniform 1e308 values, large finite weights and an out-of-range centered result. Row normalization already scales before computing norms.

The review also found that nullable pandas Boolean reductions can skip an unknown value, allowing a naive isfinite().all() check to miss missing measurements. Group-share and prior-window contracts now reject missing amounts explicitly, while category summaries deliberately preserve missingness and reject nonnumeric or infinite known values. These are distinct policies, not a global fill-with-zero rule. All 33 deepening checks passed again after these changes.

The review retained independent oracles for dynamic programming and duplicate-aware joins, exact SQL row sets, explicit conditional-write receipts, and the separation between cohort maturity and event availability. The optional coaching text remains supplemental; the substantive mechanism explanations, worked examples, counterexamples and boundary contracts are present in each guide and reference.

The numeric comparison review also added opposite-sign 1.7e308 cases. Tolerance comparisons now scale the inputs before subtracting, preventing an overflowed difference and overflowed tolerance from both becoming infinity and falsely comparing equal. The same counterexample is taught in Scala008.

## Repository integration repair, 23 October 2026

The broader repository run exposed missing established SQL heading/navigation and exercise-parity records. All six guides now use the exact required sections, linked prerequisite and learner artifacts, concrete next links, and task-specific Inputs/evidence, Expected result/shape and Verify contracts shared verbatim across guide, learner comments and explained reference. The six SQL executable references remain byte-identical to the versions accepted on PostgreSQL 16. SQL guides now contain about 2,130-2,240 whitespace words, with about 1,590-1,865 in explained references.

The 24 new Python learner/reference programs and three owned content test files pass Ruff check and formatting. Strict MyPy passes the 12 references and three tests; pandas uses the repository's existing narrow import-untyped convention rather than a global type-check exclusion. Array returns retain their declared ndarray contract, optional values are narrowed before arithmetic, mutable container types are explicit, and invalid-type boundary calls have only a local documented suppression. The 72 displayed implementations, 72 assertion snippets and 24 worked demonstrations were synchronized to executable source after formatting. Authoring scratch generators predate these direct final quality repairs and must not overwrite the frozen Python artifacts without reapplying and validating them.

The final focused integration command covering SQL contract parity, repository checks, the book, Python/SQL deepening and current Spark content passed **244 tests in 3.48 seconds**. Root also reported all 40 book examples and 12 earlier Python references passing actual offline Core Docker. The Python quality repair changes file hashes, so a fresh root-owned receipt is required for exact final-byte runtime qualification; the local executable checks pass.

## Final-source runtime receipt readback

The receipt work/python-deepening-final-acceptance.jsonl contains 12 successful Core Docker runs after the broad quality repair. A subsequent pandas04 boundary review rejected mixed string/integer customer identities explicitly instead of allowing incidental sorting errors. Its learner contract, guide, explained implementation and negative control were synchronized. The new work/pandas-id-boundary-acceptance.jsonl records a successful Core Docker run with a source hash matching that final pandas04 reference. The other 11 references retain their earlier accepted hashes.

The latest combined focused suite passes **205 tests** across the book, deepening lessons and the complete Spark content. The six SQL executable references remain unchanged from the accepted PostgreSQL versions. Source and displayed Python code are semantically aligned after the Markdown formatter and identity-boundary repairs. Root has registered all 18 additions; shared generated outputs and broader classroom delivery remain parent-owned.
