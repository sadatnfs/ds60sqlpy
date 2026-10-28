## A trained policy changes the observed distribution

A deployed policy determines which responses or actions are observed. If a new policy would choose different actions, its value cannot generally be estimated by averaging the old policy's observed rewards. Off-policy evaluation uses information about the logging process and, optionally, an outcome model to estimate a new policy's value under stated assumptions.

For context \(X\), logged action \(A\), observed reward \(R\), behavior probability \(b(A\mid X)\) and target policy \(\pi(A\mid X)\), the importance weight is \(w=\pi(A\mid X)/b(A\mid X)\). An ordinary importance estimate averages \(wR\). A self-normalized estimate divides the weighted reward sum by the weight sum; it can have a different finite-sample bias/variance tradeoff.

With an outcome estimate \(\widehat q(x,a)\), a contextual-bandit doubly robust value uses

\[
\widehat V_{DR}=\frac1n\sum_i\left[\sum_a\pi(a\mid X_i)\widehat q(X_i,a)
+\frac{\pi(A_i\mid X_i)}{b(A_i\mid X_i)}
\left(R_i-\widehat q(X_i,A_i)\right)\right].
\]

This unit treats one-step contextual decisions. Long trajectories require additional treatment of sequential probabilities and dependence; multiplying many ratios can create severe variance. The name doubly robust does not remove overlap, consistency, correct target-population weighting or appropriate nuisance-fitting assumptions.

## Worked case A: reconstruct a known finite value

Two contexts occur equally often. Their behavior policies are[0.8,0.2] and[0.3,0.7], while the target policies are[0.5,0.5] and[0.8,0.2]. The authored reward table favors action 0 in the first context and action 1 in the second. Exact target value is 0.35. A constructed log with action counts matching the behavior proportions gives that same importance estimate.

{{WORKED_A}}

## Worked case B: finite logs and an outcome model

A second possible log has different realized action counts while retaining the same behavior propensities. Ordinary and self-normalized estimates differ. With the known synthetic reward table as its outcome model, the doubly robust expression returns 0.35 because its residuals are zero and contexts remain balanced. In a real study, that counterfactual reward table is not known; it must be learned or otherwise justified and independently assessed.

{{WORKED_B}}

## Support and data provenance

Every action assigned positive target probability needs positive behavior probability in the relevant context. A missing action cannot be recovered by a finite inverse weight. The helper rejects that support failure. Very small propensities can also make estimates unstable even when support is technically positive. Report weight concentration and sensitivity, and do not hide large weights by clipping without explaining the changed estimator.

The conditional reward law must also remain applicable under the target policy. A policy that changes service congestion, future user behavior or tool availability can violate a one-step transfer assumption even when the logged ratios are correct.

Logged probabilities must describe the policy that actually generated each action. An empirical action frequency is not automatically the correct propensity when the logging policy used private context, adaptive routing or changing versions. Retain behavior-policy identity, available context, action probability, outcome availability and eligibility. If nuisance models are estimated from the same data, consider appropriate sample separation or cross-fitting rather than assuming a fitted residual correction is automatically unbiased.

## Close the alignment loop

Keep preference-training reward distinct from the task utility used for final evaluation. A policy can optimize a proxy while making the independently defined task worse, as the earlier PyTorch counterexample showed. Assess the frozen policy using new task families, valid uncertainty, coverage and critical-policy conditions. Evaluating many candidate policies on the same log and choosing the best consumes that log for selection.

The authored log makes a known answer available for mathematical checking. Its point estimates do not justify a real release or a confidence claim for an external population. A final memo should state the target policy and population, logging and support assumptions, outcome definition, estimator, uncertainty procedure, selection history and unresolved risks. Where those requirements are unmet, the correct result can be more evidence required.
