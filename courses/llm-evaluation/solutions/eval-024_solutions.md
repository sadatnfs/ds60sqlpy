# eval-024: explained reference

`eval-024_reference.py` asserts each answer below, from *Recover behavior value* to *Audit the final claim*, on the authored importance sampling and self-normalization fixture only. Before applying a conclusion to other data, recheck the assumption that *Remove behavior support* tests.

## 1. Recover behavior value

This is a basic estimator invariant under the constructed log.

**Approach.** Call `estimate(log, b, b, q)` on the 40-event log with counts `[[16, 4], [6, 14]]`.

**Why it holds for this fixture.** Target equals behavior, so every weight is 1. IPS becomes the plain mean reward: 16 rewards of 1 in context 0 plus 14 in context 1 give 30 / 40 = 0.75. The effective sample size is 40 squared over 40 = 40.

**A tempting wrong approach.** Expecting some difference between IPS and the observed mean is a sign of a weighting bug. This check catches swapped numerator and denominator.

**How to verify.** The reference asserts `np.isclose(same["ips"], 0.75)` and `same["weight_ess"] == 40`.

**Expected observation:** All weights are 1 and the mean observed reward is 0.75.

## 2. Evaluate a useful target

Known counterfactual outcomes make this value inspectable only in the authored environment; real evaluations need data and assumptions.

**Approach.** Call `estimate` with target `[[0.9, 0.1], [0.1, 0.9]]` and the exact outcome table `[[1, 0], [0, 1]]` as the outcome model.

**Why it holds for this fixture.** The target puts 0.9 on the rewarded action in each context, so its value is 0.9 in each. With an exact outcome model, every DR residual is zero and each term equals p[c] dot q[c] = 0.9, so the estimate is 0.9.

**A tempting wrong approach.** Treating this as a demonstration that DR works in practice is the mistake. Here the outcome model is the true table by construction; a real model would be estimated and wrong somewhere.

**How to verify.** The reference asserts `np.isclose(estimate(log, b, [[0.9, 0.1], [0.1, 0.9]], q)["dr"], 0.9)`.

**Expected observation:** The target value is 0.9.

## 3. Remove behavior support

A value model may extrapolate there, but that is a different identifying assumption and not justified by overlap-based evaluation alone.

**Approach.** Call `policies([[1, 0], [0.5, 0.5]], [[0.5, 0.5], [0.5, 0.5]])`. The behavior never takes action 1 in context 0, yet the target does half the time.

**Why it holds for this fixture.** The weight for that action would be 0.5 / 0, and the log contains no examples of it. The helper raises `Target has unsupported actions` before any estimate is computed.

**A tempting wrong approach.** Filling in the missing action's value from an outcome model and reporting the estimate as off-policy evaluation is the mistake. That value rests entirely on model extrapolation, a different and stronger assumption.

**How to verify.** The reference raises `Missing support accepted` if this call returns. Also check that an empty log raises.

**Expected observation:** The helper rejects the target.

## 4. Use a zero outcome model

This algebraic check separates the correction structure from a claim that the supplied model is correct.

**Approach.** Call `estimate` on case B's log with the outcome model set to all zeros, and compare its DR value with IPS.

**Why it holds for this fixture.** With q = 0, each DR term is 0 + w times (r - 0) = w times r, which is exactly the IPS term. The DR estimate reduces to IPS algebraically.

**A tempting wrong approach.** Reading DR as automatically better is the mistake. Its benefit depends on the outcome model; with a useless model it is plain IPS with the same variance.

**How to verify.** Case B asserts `np.isclose(estimate(log, behavior, target, [[0, 0], [0, 0]])["dr"], result["ips"])`.

**Expected observation:** The doubly robust expression reduces to ordinary importance sampling.

## 5. Interpret self-normalization

Self-normalization changes the estimator. A useful variance tradeoff should not be described as exact finite-sample unbiasedness.

**Approach.** Compute IPS and SNIS on case B's log, counts `[[18, 2], [10, 10]]`, with target `[[0.5, 0.5], [0.8, 0.2]]`.

**Why it holds for this fixture.** Weights are 0.625, 2.5, 2.667 and 0.286. The weighted rewards sum to 18 times 0.625 + 10 times 0.286, about 14.11, so IPS is about 0.353. The weights sum to about 45.77, so SNIS is about 0.308. The effective sample size is about 22.9 of 40.

**A tempting wrong approach.** Describing SNIS as unbiased because it often has lower variance is the mistake. Dividing by the realized weight sum introduces finite-sample bias; the tradeoff should be stated as such.

**How to verify.** Case B asserts IPS and SNIS differ, DR equals 0.35 with the exact model, and `weight_ess < len(log)`.

**Expected observation:** Their finite-sample values differ.

## 6. Audit the final claim

A complete alignment decision needs independent task utility, support, uncertainty and critical-condition evidence, not only a favorable training reward or off-policy point estimate.

**Approach.** If many policies were scored on one log and the best was picked, treat that log as selection evidence, as in eval-013, and evaluate the chosen policy on a new protected log or experiment.

**Why it holds for this fixture.** Choosing the maximum of many noisy estimates adds optimism. Off-policy estimates are also limited by support and effective sample size, so the selected value overstates what a fresh assessment would show.

**A tempting wrong approach.** Reporting the winning off-policy estimate as the expected deployed value is the mistake. A full decision also needs task utility, uncertainty and the critical-case gates from eval-016.

**How to verify.** No reference assertion covers this task. Record how many policies were compared on the log and confirm the final assessment data share no events with it.

**Expected observation:** Treat that log as selection evidence and obtain a protected final assessment.
