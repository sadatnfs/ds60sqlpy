## A mixture sums over unobserved membership

A finite mixture models each observation through several possible component distributions. If the component indicator is not observed, its likelihood contribution sums the weighted component densities. Stan's Hamiltonian methods require a differentiable continuous target, so discrete latent membership is often marginalized rather than declared as a sampled discrete parameter.

For two normal components with first-component weight w,

\[
p(y_i\mid\theta)=w\,\mathcal N(y_i\mid\mu_1,\sigma^2)
+(1-w)\,\mathcal N(y_i\mid\mu_2,\sigma^2).
\]

The program uses `log_mix` to compute the corresponding log density stably. Averaging component log densities would be a different calculation because the logarithm of a sum is not the sum of logarithms.

## Worked case 1: fit a marginalized two-component model

The tiny data contain one group of values near minus two and another near two. The model orders its two means and uses explicitly stated prior anchors near those two locations. The shared positive scale keeps the example compact. The weight receives a Beta(2,2) prior.

Ordering defines a label convention, while anchored priors add substantive prior information. They should not be conflated. If the scientific model instead uses symmetric exchangeable components, an ordering restriction can establish an interpretable labeling convention, but other prior choices must still match that intended model.

For each observation, the program adds the log of the weighted mixture density. This is the likelihood after integrating out its unobserved component indicator. The computation preserves uncertainty over membership rather than assigning each row permanently to whichever component currently has the larger density.

## Worked case 2: compute responsibilities and replicate observations

A generated responsibility is the posterior component probability conditional on one parameter draw and the observed value:

\[
r_{i1}=\frac{w\,\mathcal N(y_i\mid\mu_1,\sigma^2)}
{w\,\mathcal N(y_i\mid\mu_1,\sigma^2)+(1-w)\,\mathcal N(y_i\mid\mu_2,\sigma^2)}.
\]

The code computes it from log terms and the same mixture normalizer. Averaging responsibilities over posterior draws incorporates parameter uncertainty. A hard label discards that uncertainty and should not be reported as a discovered factual identity without further interpretation.

For replicated data, the program first draws a component according to the sampled mixture weight and then draws from that component. This is different from drawing at a weighted-average mean. A normal centered at that average would erase the multimodal structure the mixture was designed to represent.

## Review identifiability and model criticism

Mixtures can have multiple modes, weakly separated components and difficult geometry. Additional components can improve in-sample density while remaining poorly identified. Component-specific scales can introduce further pathologies and require careful priors and diagnostics. A model that compiles and produces draws has not automatically discovered a meaningful number of populations.

Label switching can make naive component-wise posterior means misleading in a symmetric model. Label-invariant predictions or quantities may still be meaningful, but the reporting convention must be stated. Ordering and informative anchors can change the interpretation and should be retained in the model record.

Predictive checks should examine modes, spread, tails and any features important to the scientific question. A mixture can fit a bimodal histogram while missing dependence, covariate effects or the observation process. For example, two measurement devices with different biases could produce modes without representing two substantive populations.

The short classroom chains are especially limited for multimodal problems. Inspect actual summaries and traces, compare initializations and investigate disagreement. The ordered, anchored synthetic example is intentionally approachable; it is not evidence that two short chains reliably explore arbitrary mixture posteriors.

## Answered scientific discussion

**Why not sample one integer membership per observation directly?** Stan's standard HMC target is continuous. Marginalization integrates those discrete possibilities into a differentiable likelihood when the structure permits it.

**Does a responsibility of .99 establish a real category?** It is a probability conditional on the mixture model and, before averaging, on one parameter draw. Its scientific meaning depends on whether the components represent defensible mechanisms. A high conditional number cannot establish that interpretation on its own.
