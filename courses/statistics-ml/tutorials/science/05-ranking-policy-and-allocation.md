# A ranking score, a policy value and a resource decision

Tutorial ID: `statistics-science-005`. Prerequisites: `statistics-032`, `statistics-017`, `statistics-036`, `statistics-022`. Complete program: [science_05.py](examples/science_05.py).

## Evaluate order at the query level

Four candidates have relevance grades 3,2,0,1. A proposed ranking returns candidate indices 1,0,3,2. Discounted cumulative gain weights gain \(2^{r}-1\) by \(1/\log_2(k+1)\) at rank k. Dividing by the ideal ordering gives NDCG, approximately .843 in this fixture. Report the gain convention, cutoff, tie handling and query averaging; changing them changes the number.

A query with no relevant candidates needs an explicit convention. Pooling all candidates into one global ranking does not evaluate query-specific retrieval. Relevance judgments can also be missing or biased toward previously exposed items.

## Logged clicks reflect the historical policy

The second fixture has two context types and two actions. The historical policy chooses action one with probability .2 and action zero with probability .8. Matching the action to context gives reward probability .7; a mismatch gives .3. The new policy always matches context, so its known synthetic value is .7.

Inverse propensity scoring uses

\[
\widehat V(\pi)=\frac1n\sum_i
\frac{\mathbf1\{A_i=\pi(X_i)\}Y_i}{p_{\rm log}(A_i\mid X_i)}.
\]

Each observed matching action represents similar opportunities that the logger did not choose. The worked estimate is about .663 with SE .0285. The rare action has larger weights and contributes more variance. The code's proximity to the oracle is checked against a declared sampling tolerance; that does not validate a future logger's propensity records.

If the logger never chooses an action in a relevant context, no finite inverse weight can identify its value from those logs. Estimated propensities, delayed rewards, policy changes and repeated users all need additional care. Evaluating a policy on the same data used to learn it also creates selection bias; this example's policy is specified independently.

## Convert value into constrained allocation

Three interventions have expected benefits 3,1.8,2 and costs 2,1,2. With budget three and each available at most once, the linear allocation model selects the first two, yielding expected benefit 4.8. Here the optimum happens to be integral even though the solver permits fractions. If partial intervention is meaningless and a fractional optimum appears, an integer model is needed rather than rounding without checking feasibility.

Now subtract uncertainty allowances 1.5,.2,.1 from benefits. The conservative objective selects the second and third. Those allowances are declared scenarios, not automatically simultaneous confidence bounds. A scientifically defensible robust decision must explain how uncertainty was estimated and why that protection criterion matches the costs of error.

Fairness, capacity, eligibility and intervention effects can all constrain the decision. High predicted response is not necessarily high incremental benefit. A scoring model that predicts purchases among people who would buy anyway may be useless for choosing incentives.

**Answered discussion: Does higher NDCG prove higher business value?** It supports ordering under the relevance definition. Causal effects of changed exposure, user adaptation and shared-resource interference require additional evaluation. Connect offline ranking evidence to a credible online experiment before claiming incremental impact.

Related route: [experimentation](../experimentation/README.md). Sources: [scikit-learn ranking metrics](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.ndcg_score.html), [SciPy linear programming](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).
