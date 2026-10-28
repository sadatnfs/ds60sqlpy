## Build a model whose variables have declared meanings

The first probabilistic-programming investigation fits a small regression using the actual prepared PyMC library. Its observation model is \(y_i\sim\mathcal N(a+bx_i,\sigma^2)\), with separate priors for intercept, slope and positive observation scale. The symbols identify distinct sources of variation: uncertainty about coefficients is different from the conditional noise represented by sigma.

The synthetic data contain 16 covariate values from minus one to one. Their outcomes follow an intercept .5 and slope 1.3 with a small deterministic perturbation. These known values provide a numerical check, but the fitted model is still an illustrative assumed likelihood. The data construction does not validate normal errors for an external dataset.

The prepared profile uses PyMC 5 and ArviZ 0.23 with the InferenceData object contract. This matters because newer ecosystem interfaces can use different result objects and method names. The course does not download or upgrade packages when a lesson opens.

## Worked case 1: fit real chains and retain diagnostics

The program creates a `pm.Model`, declares the three unknowns and attaches a normal likelihood to observed y. It then runs two serial chains, each with 120 warmup and 120 retained draws, a fixed seed and target acceptance .9. These bounded settings fit within the classroom budget. They are not a recommended production convergence budget.

The resulting posterior is an xarray-backed object with named chain and draw dimensions. The program calculates intercept and slope means and checks broad agreement with the known fixture. It also reports maximum R-hat, minimum bulk effective sample size and divergences for the sampled parameters. The reported values are observations from the actual run, not constants inserted into the tutorial.

An optional small trace plot displays both intercept chains. It is labeled as a short-chain illustration. Visual overlap is useful but does not replace rank-normalized diagnostics, tail effective sizes or Monte Carlo standard errors for the target quantity. Zero observed divergences is one diagnostic result, not proof that every relevant posterior region was explored.

## Worked case 2: generate future observations

Posterior predictive sampling draws observations conditional on each sampled parameter configuration. The output has dimensions two chains by 120 draws by 16 observed-design positions. The code checks this shape and compares the overall predictive mean with the observed mean.

That comparison is intentionally limited. A model can reproduce an average while missing variance, tails, dependence or a scientifically important subgroup. Predictive criticism should examine features chosen because they matter for the question, not only those the model fits most easily. The code exposes the full predictive array in the calculation so alternative summaries can be defined coherently.

Prediction at the observed covariate values is also different from forecasting at new covariates or evaluating held-out outcomes. The observed data helped fit the posterior. A posterior predictive check can reveal inadequacy, but it is not an unbiased estimate of a model-selection procedure's future performance.

## Read the diagnostic record carefully

R-hat compares within- and between-chain behavior through a modern transformed diagnostic, while effective sample size describes the information in correlated draws for particular summaries. A parameter's mean can have a different Monte Carlo precision from its extreme quantile. Review the quantities relevant to the decision rather than collapsing every diagnostic into one pass/fail badge.

The short demonstration can report warnings about chain count or effective sample size. Preserve them. A scientific continuation would use an appropriate longer run, inspect target-specific Monte Carlo error and investigate problematic geometry. Suppressing warnings or choosing a new seed until the output looks better is not a diagnostic strategy.

The code stores pointwise log-likelihood contributions for later evaluation. Their dimensions and observation unit matter. A log-likelihood entry for a repeated row is not automatically an independent predictive unit. The model-comparison tutorial revisits that contract before using information criteria or leave-one-out approximations.

## Answered scientific discussion

**Does the coefficient check establish a successful real-world regression?** It shows that the prepared inference path can recover a simple synthetic relationship within a broad tolerance. It does not establish correct modeling assumptions, calibrated uncertainty or transport to another population.

**What should be saved from a Bayesian run?** Save the model and data definitions, package versions, seeds, sampling configuration, actual diagnostics and the quantities used for interpretation. The classroom preserves submitted source and output receipts; a larger project should additionally retain the full posterior artifact in an explicitly managed storage workflow.
