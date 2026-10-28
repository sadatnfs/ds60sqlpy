## Selection is part of the system

A candidate can include a model, prompt, retrieval depth, judge, parser and abstention threshold. Choosing each component after inspecting validation outcomes creates a procedure with more opportunities to fit noise. The final score should assess the selected procedure, not only the final parameter vector or checkpoint name.

Suppose several candidates have the same underlying quality but their development estimates contain zero-mean noise. Selecting the maximum does not preserve zero-mean noise in the selected score. For observed estimates \(\widehat{q}_j=q+\varepsilon_j\), the reported development maximum is \(q+\max_j\varepsilon_j\). Even when each \(\varepsilon_j\) has mean zero, its maximum usually has positive expectation. More search opportunities can therefore improve the reported development score without improving true quality.

The issue is not that tuning is forbidden. Tuning is a useful part of development. The requirement is to distinguish the data that select the system from the data that assess the selected procedure, and to include the relevant search budget when comparing two approaches.

## Worked case A: exact selection optimism

The first program enumerates equally likely development noise values of plus or minus 0.1. With one candidate, mean selected noise is zero. With two candidates it becomes 0.05, and with four it becomes 0.0875. This is an exact constructed distribution, so its optimism is visible without simulation error. It is not a universal formula for arbitrary model searches, whose estimates can be correlated and have unequal variances.

{{WORKED_A}}

## Worked case B: inner selection, outer assessment

Two outer folds each contain an inner development comparison. The procedure chooses the development winner inside each fold and then evaluates that selected candidate using its corresponding outer outcomes. The resulting average is 0.45. Choosing the winner using those outer outcomes instead yields 0.85 on the same table, but consumes the assessment data for selection.

This small table demonstrates the information flow, not a complete fitted cross-validation implementation. In an actual workflow, preprocessing, feature construction, prompt selection and calibration must all remain inside the relevant training/development boundary. A transform learned once from the full dataset can leak information even if the final model fit is nested correctly.

{{WORKED_B}}

## Protect and version the evaluation protocol

Record candidate eligibility, tuning resources, selection metric, tie policy, stopping rule and final assessment plan before examining the final labels. Preserve a digest of the selected configuration and dataset version. Digests make later changes detectable; they do not prove that the author had no prior knowledge of the labels.

A final test can be reused as a regression suite after publication, but its role changes. If a failure motivates a new model or prompt, use development data for that iteration and acquire another independent final assessment. A succession of improvements on one repeatedly inspected benchmark does not retain the same untouched-test guarantee.

## Scientific interpretation

Nested evaluation estimates a selection procedure under its fold construction. It does not automatically certify the one final model retrained on all available development data. Temporal deployment may also require forward-chaining partitions rather than random folds, and dependent users or question families require group separation. The estimand and data-generating process determine the suitable split.

When a reported improvement disappears on a new benchmark, inspect selection history before attributing the change to a model regression. Compare candidate counts, prompt-search budgets, access to benchmark labels and shared source documents. Keep unsuccessful candidates in an experiment ledger so the selection mechanism can be reconstructed.

The reference programs provide exact counterexamples and invalid-shape guards. They show why the maximum of noisy estimates is optimistic and why outer outcomes must not choose a candidate. They do not imply that four candidates are too many, that cross-validation eliminates every bias, or that a single held-out score establishes broad generalization.
