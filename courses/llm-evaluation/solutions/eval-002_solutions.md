# eval-002: explained reference

`eval-002_reference.py` asserts each answer below, from *Split paraphrases* to *Audit an empty partition*, on the authored group splits and temporal split fixture only. Before applying a conclusion to other data, recheck the assumption that *Reject a delayed label* tests.

## 1. Split paraphrases

Row-level randomization can leak family-specific information. Entire groups must stay together under this protocol.

**Approach.** Build two rows with the same `family` value and different `split` values, then call `validate_split`. The function remembers the first split seen per family with `setdefault` and raises `Family leakage` when a later row disagrees.

**Why it holds for this fixture.** In case A the rows `m1` and `m2` are both metrics questions. Moving `m2` to test means a near copy of a training question is scored as held out, so the test score partly measures memorization of the metrics family rather than transfer to new families.

**A tempting wrong approach.** Shuffling rows and splitting 80/20 by row is the usual default and is exactly what fails here. With only two metrics rows, a random row split puts them in different partitions half of the time, and nothing in the score would show it.

**How to verify.** Run worked case A: it copies the rows, sets `broken[1]["split"] = "test"`, and asserts the raised message equals `Family leakage`. The valid version returns `{"metrics": "train", "policy": "test"}`.

**Expected observation:** Family validation fails.

## 2. Include cutoff equality

Boundary inclusion is a protocol choice. Here both observations are available at the cutoff and the validator uses an inclusive rule.

**Approach.** Call `training_ids` with one row whose `event` and `label_available` both equal the cutoff, 10. The filter uses `<=` for both times, so the row is kept.

**Why it holds for this fixture.** The stated protocol says data available at the cutoff instant may be used. Both the request and its label exist at day 10, so including the row does not use any information from after the boundary.

**A tempting wrong approach.** Switching to `<` to be "safe" quietly changes the protocol and drops every boundary row. That is not leakage, but it shrinks the training set and makes results differ from a pipeline that follows the written inclusive rule, so two teams would disagree without knowing why.

**How to verify.** The reference asserts `training_ids([{"id": "x", "event": 10, "label_available": 10}], 10) == ["x"]`. If you change the policy to exclusive, update the written protocol and this assertion together.

**Expected observation:** The row is eligible under the stated inclusive policy.

## 3. Reject a delayed label

The target was unknown at deployment, so using it in training would be retrospective leakage.

**Approach.** Use one row with `event` 9, `label_available` 11 and cutoff 10. The event passes the cutoff test but the label time does not, so the row is excluded.

**Why it holds for this fixture.** At day 10 the outcome for this request was still unknown. A model trained at day 10 could not have seen that label, so a historical evaluation that includes it trains on information that did not exist at decision time.

**A tempting wrong approach.** Filtering only on `event <= cutoff` is the common mistake. Worked case B shows its effect: that rule returns `["a", "b"]` while the correct rule returns `["a"]`, because row `b` had its event at day 8 but its label only at day 12.

**How to verify.** The reference asserts `training_ids([{"id": "x", "event": 9, "label_available": 11}], 10) == []`. Printing the case B comparison shows the two filters side by side.

**Expected observation:** The row is excluded.

## 4. Separate normalization from meaning

A digest equality test is not a semantic paraphrase detector. Its known false negatives should be documented.

**Approach.** Call `fingerprint("rate")` and `fingerprint("rates")` and compare the digests. The function casefolds and collapses whitespace before hashing, so only those differences are normalized away.

**Why it holds for this fixture.** The two strings differ by one character after normalization, and SHA-256 maps any byte difference to an unrelated digest. The fingerprint is designed to catch exact duplicates up to case and spacing, and it does that: `"A B"` and `"a\n b"` match.

**A tempting wrong approach.** Using fingerprint equality as the contamination check and declaring the split clean is the error. Paraphrases, plurals and reordered clauses all pass as different, so a test set could contain a lightly edited training question and the digest audit would report no overlap.

**How to verify.** The reference asserts `fingerprint("rate") != fingerprint("rates")` and `fingerprint("A B") == fingerprint("a\n b")`. Document the first result as a known false negative of the exact-match detector.

**Expected observation:** The fingerprints differ.

## 5. Version the retrieval corpus

A later correction can change answer correctness and evidence. Preserve snapshot identity rather than silently substituting current content.

**Approach.** Record a corpus version identifier with each evaluation run. When a document is corrected after the cutoff, store the correction as a new version and keep the version that was available at the cutoff for historical evaluation.

**Why it holds for this fixture.** Retrieval answers are graded against the evidence the system could retrieve. If the corrected document replaces the old one, a historical answer that was correct against the old text can be graded wrong, or an answer can cite evidence that did not exist yet.

**A tempting wrong approach.** Evaluating against the current live corpus is convenient and silently mixes time periods. The same rule as `training_ids` applies: content available after the cutoff must not influence an evaluation that claims to describe behavior at the cutoff.

**How to verify.** There is no numerical assertion for this task. Check your explanation by naming the snapshot ID used for the run and confirming that the corrected document's availability time is later than the cutoff, so it belongs only to later evaluations.

**Expected observation:** Historical evaluation uses the earlier available version.

## 6. Audit an empty partition

The split guard accepts no conflicting groups, but a separate coverage gate must reject an empty final assessment.

**Approach.** Create rows that all share one split, for example every family in `train`, and call `validate_split`. It returns a mapping with no conflicts and raises nothing, even though there is no test data.

**Why it holds for this fixture.** `validate_split` checks two properties only: unique IDs and one split per family. An empty test partition satisfies both, as does an empty row list: `validate_split([])` returns `{}`. The guard was never meant to check coverage.

**A tempting wrong approach.** Treating a passing `validate_split` as proof the evaluation is ready is the mistake. A coverage gate, like the `label_coverage` gate from eval-001, must separately require that the final partition contains enough families and labeled rows to support the stated claim.

**How to verify.** The reference asserts `validate_split([]) == {}` to document that the guard accepts emptiness. Add your own check, such as counting families mapped to `test`, and confirm it raises when the count is zero.

**Expected observation:** Grouping validation alone is insufficient for an evaluation.
