# eval-003: explained reference

`eval-003_reference.py` asserts each answer below, from *Separate a missing dimension* to *Construct a proxy counterexample*, on the authored rubric and construct validity fixture only. Before applying a conclusion to other data, recheck the assumption that *Reject malformed labels* tests.

## 1. Separate a missing dimension

Inapplicable is not the same as failure. The score is 2 divided by 2, while criterion coverage must be reported separately.

**Approach.** Pass a criteria dictionary such as `{"a": 2, "b": None}` to `rubric_score`. The function drops `None` entries, validates the remaining labels and divides their sum by twice their count.

**Why it holds for this fixture.** Only one criterion applies and it earned the maximum level 2, so the score is 2 / (2 times 1) = 1.0. Worked case A does the same with `format: None` and still scores 1 over three applicable dimensions.

**A tempting wrong approach.** Treating `None` as 0 is the tempting shortcut and gives 2 / 4 = 0.5, punishing a response for a criterion that did not apply to its question. A format criterion for a free-text answer is not a failure; it is outside the rubric's scope for that item.

**How to verify.** The reference asserts `rubric_score({"a": 2, "b": None}) == 1`. Report coverage next to it: one of two dimensions applied. If every dimension is `None`, `rubric_score` raises `No applicable rubric dimensions`.

**Expected observation:** Score 1.0 with one applicable dimension.

## 2. Add a critical failure

A weighted mean cannot turn a known access violation into an acceptable result.

**Approach.** Call `admit` with all criteria at level 2 and `access_ok` set to `False`. The function requires both `rubric_score(...) >= 0.75` and `access_ok is True`.

**Why it holds for this fixture.** Quality is perfect, so the score is 1.0 and clears the threshold. The access check is a separate gate combined with `and`, so a known violation blocks admission no matter how high the rubric score is.

**A tempting wrong approach.** Folding access into the weighted rubric, for example as a fourth criterion scored 0, gives (2 + 2 + 2 + 0) / 8 = 0.75, which passes the 0.75 threshold. A known access violation would then be admitted by averaging.

**How to verify.** Worked case A asserts `admit(criteria, True)` and `not admit(criteria, False)`. The exercise checks also assert `not admit({"a": 2}, None)`, because an unknown access result is not `True`.

**Expected observation:** The response is not admitted.

## 3. Reject malformed labels

An explicit label contract prevents accidental coercion of pass/fail fields into ordinal categories.

**Approach.** Call `rubric_score({"a": True})`. The validator tests `type(v) is not int`, and the type of `True` is `bool`, so the label is rejected with `Invalid rubric label`.

**Why it holds for this fixture.** In Python, `True == 1` and `isinstance(True, int)` are both true. An `in (0, 1, 2)` test alone would accept it as level 1. The exact type check makes a pass/fail field that was pasted into a rubric column fail loudly.

**A tempting wrong approach.** Using `isinstance(v, int)` or relying on `v in (0, 1, 2)` lets `True` through as level 1. A column of Boolean pass flags would then be silently read as "partial credit" on an ordinal scale and averaged with real rubric levels.

**How to verify.** The reference loops over `{"a": None}`, `{"a": 3}` and `{"a": True}` and fails with `Invalid rubric admitted` if any is accepted. All three must raise `ValueError`.

**Expected observation:** The validator rejects it.

## 4. Retain reviewer disagreement

The final operational label is a new observation with a reason, not a replacement for disagreement evidence.

**Approach.** Call `adjudicate` with the two case B labels, final label 1 and a reason. The function appends a new record that names the original annotators in `parents` and keeps the input list intact.

**Why it holds for this fixture.** Annotators `a` and `b` gave 1 and 2. The adjudicated record has label 1, `parents == ["a", "b"]` and the reason text. Because the function returns `records + [...]`, the original two-row list still has length 2 and the label 2 is still visible.

**A tempting wrong approach.** Overwriting `b`'s label with 1 makes the item look like perfect agreement. Any later agreement statistic, like the kappa in eval-004, would then be computed on edited data and overstate reliability.

**How to verify.** Worked case B asserts `len(labels) == 2`, `len(resolved) == 3`, `resolved[-1]["parents"] == ["a", "b"]` and `resolved[1]["label"] == 2`. An empty reason or fewer than two originals raises `ValueError`.

**Expected observation:** Both original labels remain in the ledger.

## 5. Change the rubric version

A version change can alter category boundaries. Reannotation or a defensible crosswalk is required before aggregation.

**Approach.** Build two records for item `q`, one with `rubric` set to `v1` and one with `v2`, then call `adjudicate`. The function collects the set of rubric versions among the originals and raises `Mixed rubric versions` if it has more than one element.

**Why it holds for this fixture.** A version change can move category boundaries; for example, v2 might demote answers without units from level 2 to level 1. Labels from v1 and v2 are then not measurements on the same scale, and a final label could not say which scale it uses.

**A tempting wrong approach.** Averaging or majority voting across versions looks like it uses all the data, but it mixes scales. The resulting label might match neither rubric's definition, and later analysis would not be able to reconstruct which boundary produced it.

**How to verify.** The reference builds exactly these two rows and fails with `Mixed versions admitted` if no error appears. To combine versions legitimately, reannotate under one version or apply a documented crosswalk before adjudicating.

**Expected observation:** Adjudication rejects the mixed versions.

## 6. Construct a proxy counterexample

The counterexample exposes a validity failure in a citation-marker metric even when annotators can apply it consistently.

**Approach.** Write a response that includes a citation marker, such as a bracketed reference number, pointing at a passage that does not support the claim. Score it twice: once with a format check that looks for markers, once with an evidence check that asks whether the passage supports the claim.

**Why it holds for this fixture.** The format check passes because the marker is present and well formed. The evidence check fails because the passage is irrelevant. Both checks can be highly reliable between annotators, which shows that reliability does not establish that a metric measures what the claim needs.

**A tempting wrong approach.** Accepting the citation-marker metric because annotators agree on it is the mistake. Agreement measures consistency of applying the rule, not whether the rule tracks evidence support. A model could learn to emit markers without retrieval and still score well.

**How to verify.** There is no assertion in the reference for this task. Verify by recording both scores for your counterexample: format criterion at level 2, evidence criterion at level 0. If both come out the same, the evidence criterion is not defined tightly enough.

**Expected observation:** Formatting succeeds while evidence support fails.
