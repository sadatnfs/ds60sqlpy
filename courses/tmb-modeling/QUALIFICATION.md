# TMB qualification ledger

This ledger separates mathematical companions, compiled code and future surfaces.
Evidence is from native Linux ARM64 only unless another architecture is named.

| Layer | Status | Meaning |
| --- | --- | --- |
| Original source | Implemented | 48 guides, 48 base-R companions, nine original C++ templates, fixed R API/JSON protocol, lazy Python bridge. |
| Host algebra and input contract | Passed | Eight standard-library tests cover Gaussian gradients/ML, censored Weibull values, AR1 precision, Laplace normalization, coupling and row identity. |
| Native C++ preparation | Passed | All nine templates compiled under R4.6.1/TMB1.9.25/Matrix1.7.6/RcppEigen0.3.4.0.2, CppAD, Linux ARM64. |
| Native numerical acceptance | Passed | Gaussian values/gradients/ML, regression oracle, Gaussian latent integration and gradient, AR1 dense oracle, count/censor terms, nonlinear/panel fits, Hessian/sdreport and actual OpenMP one/two-thread parity. |
| Base-R companions | Passed | All 48 final formatted companion scripts executed successfully under native Linux ARM64 R4.6.1. |
| Python/rpy2 bridge | Passed on native ARM64 | Actual pandas/rpy2/TMB regression and invalid-frame rejection passed in the separately prepared combined runtime with Python3.12, NumPy2.2.6, pandas2.2.3, rpy2 meta3.6.9/rinterface3.6.7/robjects3.6.6. |
| Spark/TMB integration | Separate project | R-only acceptance does not qualify Spark task decomposition, retries or distributed performance. |
| Ordinary classroom pad | R companions only | The R statistics pad can run base-R companion scripts. Multi-file native TMB compilation is an owned project capability. |
| C++ authoring families | Passed on native ARM64 | Five original templates compiled under TMB1.9.25/CppAD and passed dense/precision/scale/separable oracles, extreme-logit mixture checks, conditional branch crossings and custom atomic value/gradient/Hessian checks. |
| Public API probe | Passed on native ARM64 | Exact export inventory, map/report methods, version/config/lifetime, profile/interval oracles, simulation diagnostic, sparse Newton/options, SR descriptor, authoring/listing helpers and benchmark plotting exercised. |
| Specialized API processes | Taught, not fully executed | normalize/OSA require template conventions; gdb, precompile, specialized symbolic analysis and TMBad/autopar require separate preparation. |
| AMD64, multi-node, GPU | Not established here | No AMD64 emulation or GPU execution was performed on the ARM Mac. |

The first panel acceptance correctly failed: nlminb reported relative convergence
but the absolute gradient was 1.99456e-4, above the unchanged 1e-4 requirement.
Curvature was positive definite, with eigenvalues about 8 to 308754. A bounded
small Newton refinement reduced the maximum gradient to about 2.01e-9 while
preserving the raw optimizer status and initial diagnostic. Tightening nlminb's
relative tolerance alone did not repair the residual gradient and was not used
as a substitute for diagnosis. The source now retains refinement metadata.

Do not present prepared-but-unexecuted surfaces as passing. Keep the exact source
hashes and logs with release evidence. Subsequent code changes need appropriate
new checks; a historical green row does not qualify modified code automatically.

The additional public API probe initially rejected a diagonal Matrix Hessian
representation in the raw Newton helper. The corrected test constructs a genuine
symmetric compressed sparse matrix and verifies the known quadratic optimum.
This is a helper representation requirement, not a change to a statistical
model. The native probe verifies all 30 exports against the actual installed
namespace; the maintained reference additionally covers nine registered S3
methods and the explicitly non-exported documented GK helper.

The C++ family probes used a native aarch64 Linux GNU C++20 compiler, TMB1.9.25,
CppAD, serial compilation and `-O1 -g0`. The exact tested source lives in
`projects/tmb-cpp-api/models`; the numerical driver is `check.R`. No source
changes were needed after the first five-template compile. This qualifies the
small stated operations, not every private density/AD helper or higher-order
combination.

A peer review strengthened the C++ family acceptance without changing any C++
source: SEPARABLE now compares all state, correlation and log-scale derivative
directions against an independent dense covariance oracle at two finite-difference
step sizes. The mixture compares every logit, mean and log-scale derivative to
an independent stable R likelihood at logits -1000, -3, 0, 2 and 1000, again at
two step sizes. These checks passed using the exact retained compiled artifacts.
The two profile/covariance teaching companions now print their promised contrasting
interval and incorrect-precision outputs, and both revised scripts passed.
