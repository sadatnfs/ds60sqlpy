## A policy is a conditional distribution over actions

For one context, a policy assigns probabilities to possible responses or actions. A language model makes many conditional token decisions, but a two-action policy is enough to expose the objective and its assumptions. This unit uses authored actions with known rewards; it does not generate natural-language answers.

Let \(p_i\) be the policy probability of action \(i\), \(q_i\) a fixed reference probability and \(r_i\) a reward. Consider

\[
J(p)=\sum_i p_i r_i-\beta\sum_i p_i\log\frac{p_i}{q_i},\qquad \beta>0.
\]

The second term penalizes divergence from the reference. The distributions must share suitable support. Assigning positive policy probability where the reference has zero probability makes this direction of KL infinite. Replacing a zero reference probability with a small positive constant changes the problem, rather than merely fixing a numerical issue.

Introducing a Lagrange multiplier for \(\sum_i p_i=1\) and setting derivatives to zero gives a normalized exponential tilt:

\[
p_i^*=\frac{q_i\exp(r_i/\beta)}{\sum_j q_j\exp(r_j/\beta)}.
\]

The implementation subtracts the maximum log weight before exponentiation. This leaves the normalized probabilities unchanged while avoiding overflow. The reference remains fixed during this calculation; it is different from the old rollout policy used later for PPO ratios.

## Worked case A: inspect the exact optimum

With rewards 1 and 0, a uniform reference and beta 1, the preferred action receives probability \(e/(1+e)\). Its regularized objective exceeds the reference objective. A second calculation compares the gradient through a softmax parameterization to central finite differences. This checks both the reward and KL derivatives rather than testing only a final scalar value.

{{WORKED_A}}

## Worked case B: a wrong reward produces a wrong policy

Suppose the proxy assigns a high score to a verbose unsupported answer, while independently defined task utility penalizes that answer. Optimizing the proxy pushes probability toward the bad action and reduces true utility. A KL penalty limits how far the policy moves for a given reward scale, but does not turn the proxy into a correct measure of the task.

{{WORKED_B}}

## Reward scale, temperature and reference choice

Multiplying all rewards and beta by the same positive factor preserves the optimal policy. Adding a common reward constant also preserves it. These invariances help diagnose implementations. Changing only the reward scale changes the tradeoff against KL and can alter the policy sharply. Report both scales when comparing training runs.

The reference distribution itself encodes a choice. A poor reference can assign too little probability to useful actions or omit them entirely. A strong reference may preserve valuable behavior, but closeness to it is not a proof of access-policy compliance, factuality or safety. Keep independent held-out and critical-condition assessments from the evaluation sequence.

## Interpretation and transfer

For an autoregressive model, sequence probabilities factor into conditional token probabilities. The context, stopping rule, mask and normalization determine which probability law the objective refers to. Summing token log ratios along a sampled response produces a sequence log ratio, but a sample average still needs the correct sampling distribution and weighting to estimate a population KL.

A real policy update should retain the reward model version, reference checkpoint, rollout policy, sampled responses and optimization configuration. Measure actual reward/utility behavior on independent cases after training. A decrease in the training loss or an increase in proxy reward is evidence about optimization, not proof that the deployed task improved.

The exact finite-action calculations here make support, derivatives and reward exploitation visible without a large model. Their closed-form optimum is a property of the stated objective. Later units compare DPO, PPO and group-relative updates while preserving these distinctions.
