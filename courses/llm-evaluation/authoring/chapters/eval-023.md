## Relative rewards provide a comparison signal

Group-relative methods compare several responses to the same prompt. For an outcome-reward group \(r_1,\ldots,r_G\), a common normalization subtracts the group mean and divides by a stated standard-deviation convention. This removes a learned value baseline from that part of the mechanism, but it does not remove the need for meaningful rewards or independent evaluation.

This lesson uses population standard deviation within each authored group. Other implementations may use a sample correction or an epsilon; these choices change advantage scales and should be recorded. Groups are formed by prompt. Combining rewards from unrelated prompts before normalization defines a different comparison and can mix prompt difficulty with response quality.

For a nonconstant group,

\[
\widehat A_i=\frac{r_i-\bar r}{\sqrt{G^{-1}\sum_j(r_j-\bar r)^2}}.
\]

The centered advantages sum to zero. That does not imply that the policy gradient is zero, because each advantage multiplies a different score-function or probability-ratio derivative. The value of a centered objective at the old policy and its derivative are different objects.

## Worked case A: constant groups and invariances

The group 0,1,2,3 has nonzero relative signal, with mean-zero, unit-variance advantages under the stated convention. A common reward shift or positive scaling preserves those advantages when the variance remains numerically resolved. A constant group yields zero advantages by an explicit policy, preventing division by zero.

Both an all-correct group and an all-incorrect group can be constant. Record raw pass rates and group variability as well as normalized advantages. Zero relative signal does not establish that the task is solved. A separate KL regularizer can still produce an update when the reward term is zero.

{{WORKED_A}}

## Worked case B: the KL sampling distribution matters

For positive distributions \(p\) and \(q\), define the pointwise quantity \(k(a)=q(a)/p(a)-\log(q(a)/p(a))-1\). It is nonnegative. Its expectation under \(a\sim p\) equals \(D_{KL}(p\Vert q)\), because the ratio term averages to one. Sampling under a different old policy generally gives another expectation.

The code enumerates two actions and compares the exact current-policy expectation, an old-policy average and an importance-corrected old-policy average. This is a value-estimator identity under explicit support assumptions. It does not prove that differentiating any sampled expression gives an unbiased KL gradient.

{{WORKED_B}}

## Length and group weighting

An outcome advantage may be assigned to every generated token in a response. Averaging per response and then per group gives responses equal total weight; averaging all token terms together gives longer responses more weight. The reference shows a two-token response with advantage-1 and a four-token response with advantage+1. Their response-average term is zero while their token-average term is one third at unit ratios.

That difference is a modeling decision, not a formatting detail. State how prompts, responses and tokens are weighted, where masks apply, and whether end-of-sequence and truncated positions contribute. Preserve the old policy used to generate the group separately from any reference policy used for regularization.

## Interpretation and practical limits

The lesson computes GRPO-related mechanisms; it does not train a large reasoning model. The paper introduced a family of objectives and supervision choices, while later implementations can alter normalization and loss details. Use the exact declared algorithm and source when comparing runs.

Inspect constant groups, reward scale, response length, support coverage, clipping and actual held-out task behavior. A small positive sampled KL penalty is not a safety certificate, and a high raw reward can reflect exploitation of a flawed judge. Independent evaluation and a reproducible decision packet remain required after policy optimization.
