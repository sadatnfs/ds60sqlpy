# Research and implementation map

The probability derivations, synthetic data and explanatory text in this course are original. No third-party repository implementation or dataset was copied. Academic references provide context; official API references establish executable library contracts. Reading a reference is not execution evidence.

| Question | Added chapters | Executable checks |
| --- | --- | --- |
| Can Torch fit a custom likelihood rather than a neural prediction loss? | clp-001 through clp-010 | Bernoulli, Gaussian, nonlinear decay, logistic, exposure-count, censoring and heteroskedastic objectives with analytic or distribution oracles |
| Can we differentiate nonstandard and dependent observation models? | clp-011, clp-012, clp-016 | Mixture marginalization, Cholesky panel likelihood, analytic Hessian and deliberately detached gradient failure |
| How do priors, constraints and weak identification change the answer? | clp-004, clp-013, clp-014 | Parameter-versus-density Jacobian distinction, penalty duplication, rank deficiency and nuisance-refitted profiles |
| What should be reported beyond coefficients? | clp-015, clp-017, clp-018, clp-020 | Closure accounting, prediction estimands, cluster sandwich, exact empirical bootstrap and a reproducible panel dossier |
| What changes when the objective is distributed? | clp-002, clp-013, clp-019, clp-020 | Global numerator/mass contracts, one global penalty, unequal-rank averaging correction and sampler padding audit |

Primary API references checked for this implementation:

- [PyTorch 2.9 autograd mechanics](https://docs.pytorch.org/docs/2.9/notes/autograd.html): the executed tensor graph determines derivatives.
- [Distribution APIs](https://docs.pytorch.org/docs/2.9/distributions.html): independent density comparisons use Normal, Bernoulli, Poisson, LogNormal, MixtureSameFamily and MultivariateNormal.
- [L-BFGS](https://docs.pytorch.org/docs/2.9/generated/torch.optim.LBFGS.html): closures may be reevaluated; final loss is recomputed after updates.
- [Gradcheck](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.gradcheck.gradcheck.html): float64 and appropriate differentiability assumptions matter.
- [Functional Hessian](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.functional.hessian.html) and [Cholesky](https://docs.pytorch.org/docs/2.9/generated/torch.linalg.cholesky.html): small-matrix curvature and covariance calculations are checked against independent formulas.
- [DDP](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html) and [DistributedSampler](https://docs.pytorch.org/docs/2.9/data.html#torch.utils.data.distributed.DistributedSampler): averaging and sample membership must match the declared objective.

Foundational inferential references include [White (1982)](https://doi.org/10.2307/1912526) on misspecified likelihood estimation and [Efron (1979)](https://doi.org/10.1214/aos/1176344552) on bootstrap inference. Chapter 18 derives its tiny mean-example arithmetic directly, distinguishes iid from cluster resampling, and does not present a few-cluster example as validated asymptotic coverage.

The conclusion is deliberately scoped: Torch provides the derivatives and numerical linear algebra needed to construct and audit custom likelihoods. Correct model specification, independent units, constraints and inferential interpretation remain the author's responsibility. Spark integration is possible only when the distributed execution preserves the intended objective and data units; this course supplies local mathematical oracles for that separate integration work.
