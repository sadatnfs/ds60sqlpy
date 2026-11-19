## Incomplete event times contribute probabilities

A censored observation is not an event occurring at the censoring time. If an event time \(T\) is observed exactly, its likelihood contribution is a density \(f(t)\). If follow-up ends at \(c\) before an event is observed, the contribution is the survival probability \(S(c)=P(T>c)\). These represent different information.

For an exponential model with rate \(\lambda\), \(S(t)=\exp(-\lambda t)\). With event indicator \(\delta_i\), the likelihood and maximum-likelihood estimate are

\[
L(\lambda)=\prod_i\lambda^{\delta_i}\exp(-\lambda t_i),
\qquad \widehat\lambda=\frac{\sum_i\delta_i}{\sum_i t_i}.
\]

The numerator counts observed events and the denominator counts exposure time. A formula based only on the average recorded duration incorrectly treats every censoring time as a failure.

## Worked case 1: use the actual event indicators

The five observed durations are 1,2,4,5,8, with events only at 1,2 and 5. There are three events and 20 exposure units, so the exponential rate estimate is .15. Treating all five durations as event times gives .25. The program checks both values and keeps the naive estimate explicitly labeled as a contrasting incorrect analysis.

The rate has units of events per time. Changing time from years to months should divide the numerical rate by twelve while leaving model probabilities for equivalent durations unchanged. This unit check is useful when combining datasets or interpreting a model's scale parameter.

An exponential model assumes a constant hazard over time. That may be implausible for aging equipment, learning processes or early post-treatment risk. Correct handling of censoring does not make the exponential family appropriate. Model selection requires examining the mechanism and the features of survival that matter for the decision.

## Worked case 2: add delayed entry and a Weibull alternative

For left-truncated observations with entry times \(e_i\), conditioning on survival to entry divides each contribution by \(S(e_i)\). In the exponential model, the estimate becomes observed events divided by \(\sum_i(t_i-e_i)\). The program supplies valid entry times and verifies that the reduced exposure changes the rate. An entry time at or after the observed endpoint is rejected.

A Weibull distribution adds shape \(k>0\) and scale \(s>0\). Its log survival is \(-(t/s)^k\), and its log hazard is \(\log k-\log s+(k-1)(\log t-\log s)\). The code supplies an analytic gradient and fits both positive parameters on a log scale, using the event contribution \(\delta_i\log h(t_i)\) plus log survival for every row. It records optimizer status and gradient norm, and checks that the fitted likelihood is at least as good as the exponential starting point, since the exponential model is the Weibull case \(k=1\).

An **accelerated failure-time** (AFT) model lets a covariate multiply the time scale. With a binary covariate \(x_i\), the program sets \(\log s_i=b_0+b_1x_i\), so every quantile of the treated survival distribution is \(e^{b_1}\) times the corresponding control quantile; \(e^{b_1}\) is the time ratio. With cumulative hazard \(H_i=(t_i/s_i)^k\), the derivative of the negative log likelihood with respect to each log scale is \(k(\delta_i-H_i)\), and the chain rule multiplies it by 1 for \(b_0\) and by \(x_i\) for \(b_1\). The code supplies that analytic gradient to the optimizer.

The fixture makes the answer checkable. Control durations are 1, 2, 3, 5 and 7 with events at 1, 2 and 5; treated durations are exactly twice as long with the same censoring pattern. For a fixed shape \(k\), the scale MLE of one group is \(\left(\sum_i t_i^k/\sum_i\delta_i\right)^{1/k}\), so doubling every duration doubles the scale and the fitted time ratio is exactly 2 whatever shape is estimated. The program asserts that ratio and compares \(e^{b_0}\) with the closed-form control scale, about 5.63 at the fitted shape of about 1.29.

A Weibull AFT model is also a proportional-hazards model: \(h(t\mid x)=kt^{k-1}e^{-k(b_0+b_1x)}\), so the same coefficient gives the hazard ratio \(e^{-kb_1}=2^{-k}\), about 0.41 here. Treated units fail at a lower instantaneous rate because their time scale is stretched. The two summaries describe one fitted model, but their coefficients are not interchangeable without this derivation, and outside the Weibull family (including its exponential special case) an AFT model generally has no proportional-hazards form.

## Diagnostics and numerical safeguards

Positive parameters are represented by exponentiating unconstrained optimization variables. Extreme values can still create overflow or poor conditioning. Use meaningful time units, inspect the objective and check sensitivity to starting values. An optimizer success flag is useful but does not establish a well-identified or scientifically adequate model.

Compare predicted survival with appropriate empirical summaries and examine where discrepancies occur. Early-time agreement can coexist with poor tail behavior, which matters for warranty, retention or reliability decisions. Evaluate uncertainty for the quantity actually used: survival at a horizon, restricted mean time, event probability or another stated target.

The example has five observations and only three events. It is designed to verify likelihood accounting, not to choose a reliable tail model for an external population. With sparse events, priors, simpler models or explicit uncertainty may be more defensible than a highly flexible family. Later Bayesian tutorials revisit the same censoring logic with posterior computation.

## Answered scientific discussion

**Does censoring mean that the missing event time can be imputed by the follow-up duration?** No. The observed information is an inequality. Treating the lower bound as an exact event systematically changes the likelihood.

**Can a lower AIC compensate for an incorrect censoring mechanism?** It compares fitted predictive descriptions under the likelihoods supplied. It cannot validate the observation process or the causal meaning of a covariate. A well-defined likelihood starts with correct data semantics.
