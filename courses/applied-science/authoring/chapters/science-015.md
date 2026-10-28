## Logged behavior is selected by a policy

Historical outcomes are observed under the actions chosen by a logging policy. If that policy prefers one item or treatment, its observed mean reward is not generally the value of another policy. Off-policy evaluation uses the logging mechanism and explicit support assumptions to estimate what a proposed policy would do.

Let \(p(a\mid x)\) be the logging probability, \(q(a\mid x)\) the target-policy probability and \(R\) the observed reward. An inverse-propensity estimate is

\[
\widehat V_{\mathrm{IPS}}=\frac{1}{n}\sum_i
\frac{q(A_i\mid X_i)}{p(A_i\mid X_i)}R_i.
\]

Every action used by the target must have positive logging probability in the relevant contexts. Accurate logging probabilities also need to correspond to the actual action-selection process, including eligibility, exploration and overrides. An undocumented business rule can invalidate a nominal propensity stored by a model service.

## Worked case 1: recover a new policy's value

The logging policy chooses action A 80% of the time and B 20%. Their known rewards are .2 and .8. The observed logging mean is .32. A target policy choosing each action equally has value .5. The program represents the logging population with exact repeated proportions and recovers .5 using the probability ratio.

This calculation distinguishes two values that are often confused: the performance of the policy that generated the log and the performance of the proposed policy. A dataset can accurately describe the former while being inadequate for the latter because of limited support or large importance weights.

The function rejects a target-positive action with zero logging support. Replacing a zero propensity with an epsilon would produce an arbitrary finite number without creating evidence. Support may also be practically weak when probabilities are merely very small; examine weight concentration, effective sizes and behavior by context rather than checking only for exact zeros.

## Worked case 2: clipping and doubly robust correction

Clipping the importance ratio at 1.5 reduces the influence of the rarely logged high-reward action. In this fixture, the resulting estimate is below .5. The code checks that direction explicitly. Clipping can reduce variance in a random sample, but it changes the expectation. It should be presented as a stated bias-variance tradeoff and accompanied by sensitivity analysis.

The program also supplies an imperfect reward model with predictions .3 and .7. It combines the model's target-policy average with an importance-weighted residual correction. The result is again .5 because the logging probabilities are correct. This is a concrete doubly robust calculation, not a claim that an arbitrary model and arbitrary weights are jointly safe.

In observational settings, reward-model fitting and evaluation should be separated, often using cross-fitting or a clearly held-out design. Reusing the evaluation rewards to overfit the nuisance model can undermine finite-sample behavior. A doubly robust formula does not remove the need for identification, support and honest model-selection boundaries.

## Build an evaluation ledger

Store the context, eligible action set, selected action, exact logging probability, reward definition, attribution window and model/policy version. A probability before a deterministic eligibility filter may not be the probability of the action actually delivered. If users receive multiple actions or influence each other, a simple single-action contextual-bandit estimand may be inappropriate.

Report uncertainty at the correct independent unit, such as a user or session. Examine whether delayed rewards are complete and whether missing outcomes depend on action. Self-normalized importance estimates, clipping and alternative nuisance models are distinct estimators with different finite-sample properties. Record them rather than presenting all as the same IPS method.

Offline evidence should lead to a bounded deployment decision, such as a controlled experiment with guardrails, rather than an automatic claim of online benefit. Changes in user behavior, catalog eligibility, feedback loops and serving latency can invalidate the historical environment assumed by an offline calculation.

## Answered scientific discussion

**Can a deterministic historical policy evaluate every new policy?** No. If it never chose an action in a context, that outcome is not identified from the log without additional modeling assumptions or new exploration.

**Does unbiasedness guarantee a useful estimate?** An unbiased estimator can have enormous variance when it relies on rare actions. Diagnose both identification and uncertainty before using its point estimate to make a deployment decision.
