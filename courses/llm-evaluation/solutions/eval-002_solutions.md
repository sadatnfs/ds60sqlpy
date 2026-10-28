# eval-002: explained reference

The full reference is `eval-002_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Split paraphrases

Row-level randomization can leak family-specific information. Entire groups must stay together under this protocol.

**Expected observation:** Family validation fails.

## 2. Include cutoff equality

Boundary inclusion is a protocol choice. Here both observations are available at the cutoff and the validator uses an inclusive rule.

**Expected observation:** The row is eligible under the stated inclusive policy.

## 3. Reject a delayed label

The target was unknown at deployment, so using it in training would be retrospective leakage.

**Expected observation:** The row is excluded.

## 4. Separate normalization from meaning

A digest equality test is not a semantic paraphrase detector. Its known false negatives should be documented.

**Expected observation:** The fingerprints differ.

## 5. Version the retrieval corpus

A later correction can change answer correctness and evidence. Preserve snapshot identity rather than silently substituting current content.

**Expected observation:** Historical evaluation uses the earlier available version.

## 6. Audit an empty partition

The split guard accepts no conflicting groups, but a separate coverage gate must reject an empty final assessment.

**Expected observation:** Grouping validation alone is insufficient for an evaluation.
