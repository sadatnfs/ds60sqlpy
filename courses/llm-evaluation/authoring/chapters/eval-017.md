## Preferences define a different target from correctness

A preference label states that one response was chosen over another under a particular prompt, rubric and annotator context. It may reflect correctness, usefulness, style or an undesired shortcut. A reward model trained from preferences inherits that target. It is not automatically a correctness model or a universal measure of human welfare.

The Bradley-Terry model assigns scalar scores and converts a score difference into a comparison probability. The logistic function is \(\sigma(z)=1/(1+\exp(-z))\); it maps a real score difference to a number between zero and one. For preferred response \(a\), alternative \(b\), reward function \(r\) and logistic function \(\sigma\),

\[
P(a\succ b\mid x)=\sigma(r(x,a)-r(x,b)).
\]

For a positive comparison, the negative log likelihood is \(\log(1+\exp(-(r_a-r_b)))\). A numerically stable softplus calculation is preferable to taking the logarithm of a probability that may round to zero. The code uses `logaddexp` and checks extreme score differences.

## Worked case A: reward offsets are unidentified

Adding the same constant to both responses leaves their score difference and preference probability unchanged. If comparisons occur only within a prompt, the offset can be different for each prompt. A reward level from one prompt should therefore not be interpreted as directly comparable with a level from another merely because both came from one pairwise objective.

The gradient of one positive-comparison loss with respect to the two scores sums to zero. The data inform a relative difference, not a common translation. The reference verifies this analytically and with finite differences.

{{WORKED_A}}

## Worked case B: empirical preference rates and inconsistent cycles

Three wins and one loss for the same pair produce a maximum-likelihood difference of \(\log 3\), giving a probability of three quarters. The label frequency is uncertain in a finite sample; the fitted probability is not a certainty that the response is better in every context.

A strict cycle A preferred to B, B to C and C to A cannot all be satisfied by a single deterministic scalar ordering. Such labels need not be corrupt: they may represent stochastic choices, multiple criteria or heterogeneous annotators. A scalar probabilistic model can still fit a compromise, but its interpretation and residual failures matter.

{{WORKED_B}}

## Comparison design and data quality

A disconnected comparison graph permits separate shifts for disconnected components. More comparisons inside one component do not identify its offset relative to another. Choose comparison coverage to support the questions you intend to answer. Keep prompt identity, candidate identity, display order, labeler/rubric version and ties or abstentions in the ledger.

Ties require a declared treatment. Assigning half a binary win to each side is one scoring convention, not a universal model of indifference. Missing or inapplicable comparisons should not be silently encoded as ties. Position and length biases from earlier units can become learned reward shortcuts if they are present in the training labels.

## From a fitted reward to an optimization signal

Optimization searches for responses with high predicted reward. It can discover regions where the model extrapolates poorly, especially when the reward predictor was trained on a narrow response distribution. Keep reward-model validation separate from policy evaluation, and test shifted candidate distributions as training changes the policy.

The finite examples expose the likelihood, identifiability and numerical behavior before any neural training. They do not claim that a scalar reward captures all relevant preferences or that preference optimization improves factual accuracy. The next unit fits a small real PyTorch reward model and tests a deliberate length shortcut on a held-out comparison.
