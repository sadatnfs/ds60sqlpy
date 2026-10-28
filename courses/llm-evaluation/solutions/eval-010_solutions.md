# eval-010: explained reference

The full reference is `eval-010_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Answer everything

The policy pays 5 twice and averages over all four eligible requests.

**Expected observation:** Coverage 1, accuracy 0.5 and cost 2.5.

## 2. Abstain on everything

The operational cost remains defined because every eligible request incurs the abstention cost.

**Expected observation:** Coverage 0, missing conditional accuracy and cost 0.4.

## 3. Check equality

Boundary behavior matters for reproducibility and should be written into the policy contract.

**Expected observation:** The request is answered.

## 4. Derive the probability cutoff

The derivation assumes calibrated correctness probabilities and zero cost for correct answers. It does not justify using 0.92 on an arbitrary score.

**Expected observation:** The calibrated-probability cutoff is 0.92.

## 5. Inspect subgroup coverage

Differences can reflect calibration, difficulty or selection. Preserve group definitions and uncertainty before attributing them to a model mechanism.

**Expected observation:** Report each eligible count, coverage and cost.

## 6. Protect the final set

A test failure can guide development, but the same labels cannot remain untouched evidence for the modified policy.

**Expected observation:** Use it as a diagnosis and collect a new final assessment after changes.
