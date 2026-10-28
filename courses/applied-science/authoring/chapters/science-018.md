## Uncertainty must enter before the decision is chosen

A decision can be optimized for expected cost, worst-case cost, a risk measure or a constrained service requirement. These objectives can recommend different actions even when they use the same scenarios. The appropriate objective comes from the decision context, not from which method produces a favorable number.

This tutorial reuses the inventory loss from the forecasting route. Demand scenarios are 2,3,4,12 with probabilities .4,.3,.2,.1. Underage costs four and overage costs one. The decision is an integer quantity from zero through twelve. The finite scenario table makes every alternative directly inspectable.

Expected loss is \(\sum_s p_sL(q,d_s)\). A minimax decision minimizes \(\max_sL(q,d_s)\). The latter does not use the scenario probabilities; it protects against the worst listed outcome. A scenario omitted from the list is not protected merely because the objective is called robust.

## Worked case 1: expected-cost and minimax decisions

The expected-cost decision is four. The minimax decision is ten, balancing the shortage loss at demand twelve against the surplus loss at demand two. The program evaluates the entire discrete action grid, verifies both choices and compares their worst-case costs.

The minimax decision can have a larger expected cost. That is not a contradiction: it is optimizing a different criterion. Whether the extra protection is worth its expected cost depends on consequences, risk tolerance and the credibility of the scenario set. A report should display the tradeoff instead of calling one quantity universally optimal.

Scenario probabilities may be estimated from sparse history or supplied by experts. Treat them as assumptions with provenance. Sensitivity analysis can vary their values, the cost ratio and the candidate action set. A precise optimizer output does not eliminate uncertainty in any of those inputs.

## Worked case 2: compute the value of perfect information

With perfect information about demand before ordering, the action could be chosen separately for each scenario. The **expected value of perfect information** is the optimized expected cost without that information minus the expected optimized cost with it:

\[
\operatorname{EVPI}=\min_q\sum_s p_sL(q,d_s)
-\sum_s p_s\min_qL(q,d_s).
\]

The code verifies that this difference is nonnegative. In this particular grid, exact demand quantities are available as actions, so a perfectly informed decision can avoid shortage and surplus loss. This makes EVPI a transparent upper bound on the value of an information source that is less than perfect, under the same model and costs.

EVPI is not the expected value of a particular forecast or experiment. That requires modeling what the information will reveal, how decisions will respond and what obtaining it costs. A noisy signal can be valuable, but its value may be far below the perfect-information benchmark.

## Extend carefully to multi-stage decisions

A one-period inventory problem ignores carryover, lead times, action-dependent demand and competition for shared resources. Adding these mechanisms can require dynamic or multi-stage optimization. The information available at each stage must be explicit; a model that lets an early decision depend on a future scenario is using perfect foresight accidentally.

Sample-average approximation uses a finite scenario sample to approximate an expectation. The chosen decision can overfit that sample. Evaluate it on independent scenarios or repeated samples and report stability of both value and action. A small improvement in estimated value can correspond to a large, unstable change in selected action near a decision boundary.

Risk measures also require interpretation. A tail-risk criterion depends on how the tail is represented and on the chosen level. Worst-case optimization over an overly broad uncertainty set can produce impractical conservatism; an overly narrow set can miss the important failure. The phrase robust should be accompanied by the exact set or distributional assumptions.

## Answered scientific discussion

**Does EVPI tell us how much to pay for a model?** It is an upper bound under the supplied decision model. The actual model's information quality, latency, implementation costs and effects on behavior require a separate analysis.

**Why show both policies when only one will be deployed?** Their difference reveals the consequences of the risk objective. A decision maker can then discuss the underlying tradeoff rather than treating the solver's chosen action as a value judgment made by mathematics.
