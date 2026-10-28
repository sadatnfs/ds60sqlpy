# eval-015: explained reference

The full reference is `eval-015_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Report immature labels

The missing failure label has not become a success. The report must expose incomplete outcome ascertainment.

**Expected observation:** Accuracy 1 with label coverage 0.5.

## 2. Wait for the cohort

The difference is explained by label arrival, so an unqualified early-versus-late accuracy comparison is misleading.

**Expected observation:** Accuracy 0.5 and label coverage 1.

## 3. Identical distributions

This is an exact diagnostic invariant, not proof that model quality is unchanged.

**Expected observation:** JS divergence 0.

## 4. Disjoint support

The finite maximum is a useful boundary test and differs from an unbounded one-direction KL divergence.

**Expected observation:** JS divergence is log 2.

## 5. Choose assignment units

The experimental unit should reflect how exposure and outcomes can influence one another; many rows do not create independent users.

**Expected observation:** Consider user-level assignment and cluster-aware analysis.

## 6. Investigate an alert

A changed input mix may be benign or may reveal unsupported future risk; retain outcome and operational evidence alongside drift.

**Expected observation:** Investigate composition and coverage before concluding model degradation.
