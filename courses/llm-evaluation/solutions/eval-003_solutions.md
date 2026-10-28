# eval-003: explained reference

The full reference is `eval-003_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Separate a missing dimension

Inapplicable is not the same as failure. The score is 2 divided by 2, while criterion coverage must be reported separately.

**Expected observation:** Score 1.0 with one applicable dimension.

## 2. Add a critical failure

A weighted mean cannot turn a known access violation into an acceptable result.

**Expected observation:** The response is not admitted.

## 3. Reject malformed labels

An explicit label contract prevents accidental coercion of pass/fail fields into ordinal categories.

**Expected observation:** The validator rejects it.

## 4. Retain reviewer disagreement

The final operational label is a new observation with a reason, not a replacement for disagreement evidence.

**Expected observation:** Both original labels remain in the ledger.

## 5. Change the rubric version

A version change can alter category boundaries. Reannotation or a defensible crosswalk is required before aggregation.

**Expected observation:** Adjudication rejects the mixed versions.

## 6. Construct a proxy counterexample

The counterexample exposes a validity failure in a citation-marker metric even when annotators can apply it consistently.

**Expected observation:** Formatting succeeds while evidence support fails.
