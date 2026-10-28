## Multiple estimates can carry shared information

Several effects from one study may share participants, controls, instruments or outcome measurements. Treating them as independent can make the evidence appear more precise than it is. The correlation does not disappear because the estimates occupy separate spreadsheet rows.

If a vector of estimates \(\mathbf y\) shares a common mean under a specified model and has covariance \(\mathbf V\), generalized least squares gives

\[
\widehat\mu=\frac{\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf y}
{\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf{1}},\qquad
\operatorname{Var}(\widehat\mu)=
\left(\mathbf{1}^{\mathsf T}\mathbf V^{-1}\mathbf{1}\right)^{-1}.
\]

The covariance matrix is part of the statistical model. It must represent the dependencies and the scale of the estimates. A matrix chosen for numerical convenience should not be presented as measured sampling covariance.

## Worked case 1: retain the same mean, change the uncertainty

Two effect estimates are .4 and .6, with variance .04 each. Treating them as independent gives a mean of .5 and variance .02. When their covariance is .03, the mean remains .5 but its variance rises to .035. The code checks both exact results.

The unchanged point estimate can make the independence error easy to miss. A chart displaying only effect values would look identical under the two models, while an interval and resulting decision could change substantially. Review uncertainty calculations even when an alternative model leaves the central estimate stable.

Perfect or near-perfect dependence can make the covariance matrix singular or poorly conditioned. Two identical reported estimates do not provide two independent measurements. Possible responses include selecting a prespecified estimate, aggregating within study, using a multivariate model or applying an appropriate cluster-robust method with enough independent clusters. An arbitrary tiny diagonal jitter changes the model and should be justified rather than hidden.

## Worked case 2: make a missing-study scenario explicit

The visible effects are .3,.5,.7, giving a mean of .5. Adding two hypothetical missing effects of -.2 and -.1 lowers the arithmetic mean to .24. The program labels this as a sensitivity scenario. It does not estimate the missing studies or demonstrate that they exist.

The usefulness of the scenario depends on its interpretation. It might ask how many negative findings of a particular scale would alter a decision, or how selection could differ by study precision. A credible analysis should connect those assumptions to the review process, registration records, outcome reporting and subject-matter knowledge.

Funnel asymmetry, small-study effects and publication bias are related but distinct. Heterogeneity, measurement differences or design quality can also produce patterns associated with study size. A diagnostic plot should motivate investigation rather than automatically label every asymmetric pattern as a missing-publication mechanism.

## Organize a reproducible synthesis ledger

Use a stable study identifier and retain all candidate outcomes, their eligibility decisions and shared samples. Record how one estimate was selected when multiple versions exist. The unit resampled for uncertainty should reflect the independent evidence source; resampling individual effects from the same study as if they were independent can reproduce the original mistake.

If correlations are unknown, sensitivity analysis across scientifically plausible values may be more transparent than pretending independence. For a small number of studies, asymptotic robust-variance approximations may also be unreliable. The uncertainty procedure and the effective number of independent clusters belong in the report.

Keep observed evidence separate from imputed or hypothetical evidence. A machine-readable column identifying scenario status prevents an illustrative missing-study row from being mistaken for an extracted real result later. Likewise, preserve the difference between a study's reported standard error and one reconstructed under additional assumptions.

## Answered scientific discussion

**Can we simply average several outcomes within each study?** Sometimes that defines a meaningful composite, but the scientific target, outcome scales and within-study covariance must support the combination. Averaging is not a universal way to remove dependence.

**Does a sensitivity scenario that leaves the decision unchanged prove robustness?** It establishes stability under that stated scenario. Other selection mechanisms, stronger dependence or different effect definitions can still matter. A defensible conclusion names the alternatives examined and the assumptions left unresolved.
