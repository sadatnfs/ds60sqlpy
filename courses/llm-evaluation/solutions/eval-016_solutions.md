# eval-016: explained reference

The full reference is `eval-016_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Change one constraint

Changing one policy input cannot erase the other failures. The reference then constructs a separate all-pass input only to check the decision-rule logic; it does not invent improved observed model outcomes.

**Expected observation:** Only the coverage gate passes; quality, critical cases and latency still fail.

## 2. Keep a missing protocol result

A missing confirmation is reported as an unresolved condition rather than silently accepted.

**Expected observation:** The protocol gate fails.

## 3. Preserve a critical failure

The policy gives this condition independent force; a favorable mean effect cannot cancel it.

**Expected observation:** The critical-case gate fails even if quality improves.

## 4. Interpret zero incidents

The expression 1-alpha^(1/n) assumes independent representative Bernoulli trials. It is separate from the actual authored held-out ledger, which contains one critical failure, and supplies no real-population estimate.

**Expected observation:** Finite observations do not imply zero population risk.

## 5. Detect an artifact edit

Integrity helps reconstruct evidence but is separate from authentication and scientific validity.

**Expected observation:** Verification rejects the old digest.

## 6. Write a bounded memo

A useful memo identifies the decision, its supporting limits and a concrete next assessment without claiming universal quality or safety.

**Expected observation:** State no-go, all four failing conditions and the independent evidence needed next.
