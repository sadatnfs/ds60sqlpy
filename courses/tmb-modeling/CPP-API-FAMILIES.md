# C++ model-authoring API families

This map complements the [R API inventory](API-REFERENCE.md). It covers model-authoring families from the pinned TMB1.9.25 headers and their statistical/execution contracts. It does not claim every private Eigen, CppAD or TMBad implementation symbol is a stable public teaching API. Original small [C++ family probes](projects/tmb-cpp-api/README.md) remain separate from the core likelihood project.

| Family | Interfaces | Chapters |
| --- | --- | --- |
| typed-data | `DATA_SCALAR`, `DATA_VECTOR`, `DATA_MATRIX`, `DATA_ARRAY`, `DATA_INTEGER`, `DATA_IVECTOR`, `DATA_FACTOR`, `DATA_SPARSE_MATRIX` | [tmb-002](guides/tmb-002.md), [tmb-041](guides/tmb-041.md) |
| typed-parameters | `PARAMETER`, `PARAMETER_VECTOR`, `PARAMETER_MATRIX`, `PARAMETER_ARRAY`, `Type`, `vector<Type>`, `matrix<Type>`, `array<Type>` | [tmb-002](guides/tmb-002.md), [tmb-026](guides/tmb-026.md), [tmb-041](guides/tmb-041.md) |
| reports-and-simulation | `REPORT`, `ADREPORT`, `SIMULATE` | [tmb-009](guides/tmb-009.md), [tmb-018](guides/tmb-018.md), [tmb-019](guides/tmb-019.md), [tmb-031](guides/tmb-031.md), [tmb-045](guides/tmb-045.md) |
| univariate-probability | `dnorm`, `dpois`, `dbinom`, `dgamma`, `dnbinom2`, `pnorm`, `lgamma` | [tmb-003](guides/tmb-003.md), [tmb-011](guides/tmb-011.md), [tmb-042](guides/tmb-042.md) |
| stable-probability | `logspace_add`, `logspace_sub`, `logit`, `invlogit` | [tmb-004](guides/tmb-004.md), [tmb-042](guides/tmb-042.md), [tmb-046](guides/tmb-046.md) |
| multivariate-and-sparse | `density::MVNORM`, `density::GMRF`, `density::UNSTRUCTURED_CORR` | [tmb-015](guides/tmb-015.md), [tmb-036](guides/tmb-036.md), [tmb-043](guides/tmb-043.md) |
| density-composition | `density::AR1`, `density::SCALE`, `density::VECSCALE`, `density::SEPARABLE` | [tmb-015](guides/tmb-015.md), [tmb-044](guides/tmb-044.md) |
| ad-safe-control | `CppAD::CondExpGt`, `CppAD::CondExpLt`, `CppAD::CondExpEq`, `parameter transforms`, `data-controlled branches` | [tmb-004](guides/tmb-004.md), [tmb-027](guides/tmb-027.md), [tmb-046](guides/tmb-046.md) |
| atomic-extensions | `TMB_ATOMIC_VECTOR_FUNCTION`, `forward values`, `reverse adjoints`, `higher derivatives` | [tmb-006](guides/tmb-006.md), [tmb-027](guides/tmb-027.md), [tmb-047](guides/tmb-047.md) |
| parallel-and-lifecycle | `parallel_accumulator<Type>`, `CppAD`, `TMBad`, `OpenMP`, `native ABI`, `sparse factorization` | [tmb-005](guides/tmb-005.md), [tmb-020](guides/tmb-020.md), [tmb-027](guides/tmb-027.md), [tmb-035](guides/tmb-035.md), [tmb-037](guides/tmb-037.md), [tmb-038](guides/tmb-038.md), [tmb-039](guides/tmb-039.md), [tmb-048](guides/tmb-048.md) |

## typed-data

R-side shape, finite-value, index and sparse-representation contracts precede native access.

Evidence boundary: Original nine-model project covers vectors/matrices/integer indices; array/sparse family probes are separate.

## typed-parameters

Flat parameter order and free dimension depend on declarations and map/random/profile construction.

Evidence boundary: Scalar/vector parameters executed in original likelihoods; array parameters executed in the separable family probe.

## reports-and-simulation

Keep deterministic estimands, diagnostic readback and generative simulation distinct.

Evidence boundary: Original normal SIMULATE and multiple report/sdreport paths executed.

## univariate-probability

Check the actual family parameterization, support and log-density flag; not every helper has the same conventions.

Evidence boundary: Normal/Poisson/censor original models executed; other listed families require their own native tests.

## stable-probability

Stable arithmetic does not change invalid domains or remove identifiability problems.

Evidence boundary: Original stable-mixture template passed independent value and full logit/mean/log-scale gradient oracles at logits -1000, -3, 0, 2 and 1000 with two step sizes. logspace_sub and other transforms retain separate mathematical examples.

## multivariate-and-sparse

Distinguish covariance from precision, normalization from penalty and proper from intrinsic fields.

Evidence boundary: MVNORM and GMRF compiled value/gradient equivalence passed against a dense oracle. UNSTRUCTURED_CORR remains explained but not claimed executed.

## density-composition

Scale Jacobians and array-axis ordering are part of the statistical target.

Evidence boundary: AR1/SCALE passed in the original model. SCALE/VECSCALE have independent value/gradient oracles. SEPARABLE state, row/column correlation and log-scale gradients matched an independent dense Kronecker oracle at two step sizes.

## ad-safe-control

Avoid invalid arithmetic in candidate expressions and distinguish branch changes from mathematical nonsmoothness.

Evidence boundary: Censor data branch executed; CondExpGt parameter-crossing probe compiled and matched positive/negative value and gradient references.

## atomic-extensions

A correct first derivative does not establish higher-order latent-model support.

Evidence boundary: Original quartic atomic compiled under CppAD and matched analytic values, gradients and Hessians at three points. This does not qualify every custom atomic or framework.

## parallel-and-lifecycle

Separate arithmetic, compilation, process ownership, threading and experimental framework evidence.

Evidence boundary: Original CppAD/OpenMP model passed; TMBad/autopar and specialized debugging/factorization remain separate.

## Related correlation construction

`density::UNSTRUCTURED_CORR` constructs an unconstrained-parameter correlation family documented in the density header. Its vector length determines the dimension, and its implied covariance can be paired with VECSCALE for marginal standard deviations. It is not the same as filling arbitrary off-diagonals: a valid correlation matrix must be positive definite. This related helper is explained here; a new compiled lesson using it needs a dimension, covariance and derivative oracle before a runtime claim.

Primary source: [typed density families](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/tmbutils/density.hpp), [convenience arithmetic](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/convenience.hpp), [atomic macro](https://github.com/kaskr/adcomp/blob/master/TMB/inst/include/atomic_macro.hpp). Exact reviewed header hashes are in `cpp-api-families.json`.

## Native family acceptance

All five original family templates compiled and executed on Linux ARM64. The
checks compare covariance/precision and scale-composed densities with dense
formulas, verify separable column-major array ordering, cross parameter branches
on an existing tape, evaluate extreme mixture logits and compare a custom
atomic's first and second derivatives to exact formulas. These source-bound
results are separate from the broad family inventory and from untested TMBad,
GPU or specialized sparse configurations.
