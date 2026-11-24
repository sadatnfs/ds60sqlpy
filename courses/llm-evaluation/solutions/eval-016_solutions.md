# eval-016: explained reference

`eval-016_reference.py` asserts each answer below, from *Change one constraint* to *Write a bounded memo*, on the authored decision memo and artifact digest fixture only. Before applying a conclusion to other data, recheck the assumption that *Preserve a critical failure* tests.

## 1. Change one constraint

Changing one policy input cannot erase the other failures. The reference then constructs a separate all-pass input only to check the decision-rule logic; it does not invent improved observed model outcomes.

**Approach.** Copy the packet from `fixture()`, set `coverage` to 0.9 and call `decide`. All other inputs stay as authored.

**Why it holds for this fixture.** Coverage 0.9 now exceeds the required 0.85, so that gate passes. The quality gate still fails (lower bound -0.25 is below 0.02), the critical gate fails (one critical error) and latency fails (160 ms above 150). The failed list is `["quality", "critical_cases", "latency"]`.

**A tempting wrong approach.** Treating the coverage fix as progress toward go without addressing the others is the mistake. Each gate is independent, and the reference's later all-pass packet is a logic check on invented values, not an improved model.

**How to verify.** The reference asserts `decide(p)["failed"] == ["quality", "critical_cases", "latency"]` after setting coverage 0.9. Updating the other three inputs then makes the decision `go`.

**Expected observation:** Only the coverage gate passes; quality, critical cases and latency still fail.

## 2. Keep a missing protocol result

A missing confirmation is reported as an unresolved condition rather than silently accepted.

**Approach.** Set `protocol_frozen` to `None` in the packet and call `decide`. The gate expression is `packet["protocol_frozen"] is True`.

**Why it holds for this fixture.** `None is True` is false, so the protocol gate fails and appears in the failed list. An unconfirmed protocol freeze is handled exactly like a failed one.

**A tempting wrong approach.** Using a truthiness test such as `bool(packet["protocol_frozen"])` would still fail for `None` here, but would accept strings like `"pending"`. The identity check accepts only an explicit `True`.

**How to verify.** The reference asserts `"protocol_frozen" in decide(p)["failed"]` after setting it to `None`.

**Expected observation:** The protocol gate fails.

## 3. Preserve a critical failure

The policy gives this condition independent force; a favorable mean effect cannot cancel it.

**Approach.** Set `critical_failures` to 1, then raise `effect_lower` above the minimum effect, and call `decide`.

**Why it holds for this fixture.** The critical gate is `critical_failures == 0`, so it fails regardless of quality. The authored ledger has exactly one critical error, `operations-3`, where the baseline was correct and the candidate was wrong.

**A tempting wrong approach.** Combining all gates into one weighted score would let a strong quality improvement offset the critical error. This policy deliberately gives the critical gate independent force.

**How to verify.** Case A asserts `packet["critical_failures"] == 1`. Change `effect_lower` to 0.03 alone and confirm `critical_cases` is still in the failed list.

**Expected observation:** The critical-case gate fails even if quality improves.

## 4. Interpret zero incidents

The expression \(1-\alpha^{1/n}\) assumes independent representative Bernoulli trials. It is separate from the actual authored held-out ledger, which contains one critical failure, and supplies no real-population estimate.

**Approach.** For a hypothetical campaign with zero failures in n = 200 independent trials, the one-sided 95 percent upper bound on the failure rate is 1 - 0.05 to the power 1 / 200.

**Why it holds for this fixture.** That evaluates to about 0.0149, which is above 0. Zero observed failures in 200 trials is consistent with a true failure rate up to roughly 1.5 percent. The formula requires independent, representative trials.

**A tempting wrong approach.** Reporting "zero failures, so risk is zero" is the mistake. Also, applying this bound to the authored ledger would be wrong twice: the ledger has one critical failure, and its rows are not representative trials.

**How to verify.** Case B asserts `0 < upper < 0.02` for `upper = 1 - 0.05 ** (1 / 200)`. Compute it yourself and state that it describes a hypothetical campaign, not this packet.

**Expected observation:** Finite observations do not imply zero population risk.

## 5. Detect an artifact edit

Integrity helps reconstruct evidence but is separate from authentication and scientific validity.

**Approach.** Compute `digest(packet)` before any change, then edit `coverage` to 0.95 on a deep copy and call `verified_packet(changed, original_digest)`.

**Why it holds for this fixture.** `digest` hashes a canonical JSON encoding with sorted keys, so any value change produces a different SHA-256. The function raises `Evidence artifact changed`, and the original packet still has coverage 0.75.

**A tempting wrong approach.** Treating a matching digest as proof the evidence is correct is the mistake. A digest shows the bytes did not change since sealing; it does not show who sealed them or that the numbers inside were valid.

**How to verify.** Case B checks that the mutated copy is rejected and that `original["coverage"] == 0.75`. The exercise checks also confirm key order does not affect the digest and different values do.

**Expected observation:** Verification rejects the old digest.

## 6. Write a bounded memo

A useful memo identifies the decision, its supporting limits and a concrete next assessment without claiming universal quality or safety.

**Approach.** Write three sentences: the decision, the failing conditions with their numbers, and the next assessment needed.

**Why it holds for this fixture.** A bounded memo might read: "Decision: no-go for candidate-v1 under desk-eval-v1. Quality lower bound is -0.25 against a 0.02 minimum, coverage is 0.75 against 0.85, one critical error occurred and maximum latency is 160 ms against 150 ms. Next, collect a new held-out set with more than two families after fixing the critical case and latency."

**A tempting wrong approach.** Summarizing as "the candidate is not better" is too vague, and "the candidate is worse" is unsupported: the estimate is 0 with an interval from -0.25 to 0.25 over only two families.

**How to verify.** Check the memo against `decide(fixture())`: it must list all four failed gates (quality, coverage, critical cases, latency) and must not claim anything beyond the two synthetic families.

**Expected observation:** State no-go, all four failing conditions and the independent evidence needed next.
