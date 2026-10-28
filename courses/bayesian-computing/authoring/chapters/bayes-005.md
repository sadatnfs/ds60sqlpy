## Posterior uncertainty becomes a decision through loss

Inference describes uncertainty under a model. A decision additionally requires actions and consequences. A Bayes action minimizes posterior expected loss, or equivalently maximizes posterior expected utility. A probability threshold such as 95% is not a universal decision rule; it represents a particular choice of consequences or constraints when it is justified at all.

The example considers an action that costs five units and produces eight units of benefit on success. Its success probability has a Beta(10,4) posterior. Under the stated linear utility, expected net benefit is \(8\mathbb{E}[p\mid y]-5\). The action is preferred when this quantity is positive.

This is a decision model for a named future action. It does not establish that a success probability estimated under an unrelated old policy is the causal success probability after a new intervention. Transport, intervention effects and changing selection require their own scientific assumptions.

## Worked case 1: compare expected utility with a posterior probability

The posterior mean probability is 10/14. Expected net benefit is therefore positive. The program also calculates the probability that the unknown net-benefit parameter is positive, using the threshold \(p>5/8\). These are two distinct summaries.

Requiring the latter probability to exceed a chosen level would introduce a different decision rule. It might be appropriate under a justified risk constraint, but it should not be silently substituted for maximizing the stated expected utility. A decision maker should be able to identify which objective produced the recommendation.

The same reasoning generalizes to several actions and a nonlinear loss. In that case, plugging a posterior mean parameter into the utility function can differ from averaging utility over the posterior. Retain the full relevant uncertainty when consequences are nonlinear, asymmetric or constrained.

## Worked case 2: calculate posterior expected regret

Regret compares the chosen action with the action that would have been selected if the uncertain parameter were known. The program integrates the loss from choosing the action when its net benefit is negative and the loss from waiting when its net benefit is positive.

The expected regret of acting is smaller. The difference between the expected regrets equals the expected net benefit, providing an independent identity check for this two-action setup. Both quantities are integrated over the same posterior and use the same cost and benefit definitions.

Expected regret is not the same as the probability of making the wrong action. A rare but very large loss can matter more than a common small loss. Reporting only the probability that one action is better can hide the magnitude of the consequences. The program keeps both probability and utility summaries so that distinction can be inspected.

## Separate parameter uncertainty, future noise and model uncertainty

Uncertainty about p is not the same as the randomness of a future success conditional on p. A predictive calculation integrates both when appropriate. If the benefit itself is uncertain or depends on another outcome, the joint model should represent that dependence rather than multiplying unrelated mean values.

The posterior is conditional on the model. A decision can be highly sensitive to prior assumptions, missing outcome mechanisms or a poorly modeled tail. Sensitivity analysis should vary scientifically plausible alternatives and show whether the action changes. A precise Monte Carlo average cannot remove those uncertainties.

Constraints can change the optimal policy. A budget, safety requirement or fairness condition may exclude an action that otherwise has positive expected utility. Define those constraints explicitly. Do not encode every normative requirement as an unexplained penalty coefficient and then call the selected result objective.

## Answered scientific discussion

**Should the lower bound of a credible interval determine every action?** That is one possible conservative rule, but its relationship to costs and risk must be stated. Expected-utility optimization and chance constraints are different decision frameworks.

**What does the small exact example establish?** It verifies the posterior-risk calculation under a transparent beta model and fixed consequences. A real deployment should also preserve the data boundary, intervention assumptions, operational costs, uncertainty assessment and a plan for updating or reversing the decision when evidence changes.
