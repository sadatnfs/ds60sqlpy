## Positivity determines what can be learned

Weighting creates a comparison population by changing the contribution of observed units. It cannot manufacture an unobserved treatment option. Let \(e(x)=P(A=1\mid X=x)\). Identification of a population average effect requires \(0<e(x)<1\) throughout the target support, together with the other causal assumptions. **Practical overlap** asks whether the available sample actually contains useful comparisons, even when the theoretical probabilities are nonzero.

For binary treatment, an inverse-probability score is

\[
\phi_i=\frac{A_iY_i}{e(X_i)}-\frac{(1-A_i)Y_i}{1-e(X_i)}.
\]

Its average targets an additive population effect under the identification assumptions. These are probability weights attached to treatment assignment. Survey inclusion weights, censoring weights and transport weights represent different mechanisms and must be derived separately before being multiplied together.

## Worked case 1: exact balance in a finite population

The program builds 100 records across two covariate strata. Treatment probabilities are .2 and .8. Outcomes follow \(Y=1+4X+2A\), so the known intervention effect is two everywhere. The raw treated and control groups have different covariate compositions. Inverse-probability weighting nevertheless recovers two exactly because the fixture repeats each cell in its stated probability proportion.

This is an arithmetic oracle, not a finite-sample guarantee. Randomly drawn samples generally produce variation around the target. Estimating the propensity introduces another source of uncertainty. A correctly coded weight formula cannot rescue an unmeasured confounder, incorrectly recorded treatment or inconsistent outcome definition.

Inspect the largest weights and the covariate distributions that they represent. For positive weights \(w_i\), a commonly used concentration summary is

\[
n_{\mathrm{eff}}=\frac{(\sum_i w_i)^2}{\sum_i w_i^2}.
\]

It equals the actual sample size when all weights are equal. In the second numerical check, weights \([1,1,1,50]\) produce an effective size below two. Four rows therefore provide little balanced averaging. This quantity is a diagnostic of weight concentration, not a universal variance formula for every estimator or sampling design.

## Worked case 2: overlap weighting changes the target

Suppose the first stratum has population mass .8 and treatment probability .1, while the second has mass .2 and probability .6. Their treatment effects are four and one. Weighting target strata in proportion to \(p(x)e(x)(1-e(x))\) emphasizes regions where either treatment is plausible. The program compares this overlap-population effect with the original population effect and verifies that they differ.

This difference is not an estimator malfunction. The target has changed. Overlap weighting can answer a useful question about the population in clinical or operational equipoise, but it should not be presented as the original population effect with a numerical stabilization trick. Likewise, removing units with extreme estimated propensities changes the represented population. A threshold chosen after observing the desired effect is an additional analyst decision.

Clipping very large inverse weights may reduce variance while introducing bias. The tradeoff depends on which units are clipped and how their outcomes differ. Keep the unclipped and clipped analyses, the fraction of affected units, and a statement of the modified procedure. Renormalizing weights separately within treatment groups produces a different finite-sample estimator even when it approaches a similar large-sample target.

## An operational overlap review

Plot propensity distributions by treatment, but do not stop at a histogram. Examine important covariate combinations, treatment availability, extreme-weight units and weighted balance. A classifier that perfectly separates treatment groups may indicate poor overlap rather than a superior causal model. Conversely, a poorly fitted propensity model may appear to create overlap by flattening real differences.

Define a failure policy before estimating the effect. Possible responses include narrowing the target population, collecting data on missing comparisons, changing the scientific question or reporting partial identification. Returning a number for every input is not a desirable requirement when the necessary comparisons do not exist.

The program rejects probabilities of zero or one explicitly. It does not silently replace them with a small epsilon. An epsilon avoids division by zero computationally while hiding the exact scientific failure. Numerical stability and identification are separate properties.

## Answered scientific discussion

**Can outcome regression solve a positivity violation?** A fitted model can extrapolate into missing cells, but the result then relies on its extrapolation assumptions. That may be an informed modeling decision; it is not the same evidence as an observed comparison.

**Should effective sample size replace the original count in a confidence formula?** Not automatically. The estimator, estimated weights, dependence structure and design determine the uncertainty calculation. Use the concentration measure to reveal influential contributions, then derive or resample the actual analysis procedure at the correct unit.
