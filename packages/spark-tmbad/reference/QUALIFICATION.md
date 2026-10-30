# Qualification status

The optional reference is implemented source awaiting dependency/template and
fitted-example qualification. No glmmTMB family, custom TMB model, Docker image,
model fit, forecast study or simulation run is marked accepted by this document.
The primary native package's earlier receipts do not qualify this R reference.

Completed source and mathematical checks:

- The 65-package locked dependency graph is complete, topologically ordered and
  version-compatible with R 4.6.1 under the reviewed constraints. Exact upstream
  and CRAN archive hashes are recorded. Compatibility of metadata is not proof
  of installation or ABI compatibility.
- Pure Python tests validate source/download and registry admission boundaries,
  failed and unattempted simulation accounting, MCSE and uncertainty for a zero
  observed failure count.
- R parsing and formatting checks cover the maintained R sources and pure tests.
- Serial mathematical tests check exact orthogonal Gaussian lasso/KKT, conjugate
  Gaussian posterior moments, Gaussian conditioning/density and panel covariance.
  Additional pure tests check finite-domain quadrature/error refusal, restoration
  of mutable objective state, and beta-binomial success/failure matrix handling.
  The mutable-state and simulation-shape tests use explicit synthetic objects;
  they do not execute TMB or the upstream simulator.

The fitted-source review also repaired four specific risks: fixed quadrature
bounds without error checks, reading stale TMB state after `sdreport`, exact
floating-point equality for an unpenalized lasso intercept, and flattening
beta-binomial success/failure matrices. The pinned TMB and glmmTMB sources were
read to resolve their state and simulation contracts. These repairs still need
actual prepared-library regression checks.

Pending acceptance:

1. Install the complete locked dependency closure into a fresh independent
   library, verify actual metadata/ABI identities and retain full build logs.
2. Compile the four templates in a fresh immutable registry. Check source and
   artifact bindings, actual numerical values/gradients, failure controls and
   final runtime operation.
3. Run each maintained custom and upstream family/covariance/MAP example on its
   declared native architecture. Preserve failures and add actual observed
   outputs to the guides.
4. Run a copied-project Docker/installation proof and bounded simulation smoke.
   Larger calibration studies require their own complete replication ledger,
   failed-fit accounting and Monte Carlo uncertainty.

Until those steps pass, the case table in README is a description of source
behavior to qualify. It is not an implemented-and-tested compatibility matrix.
No AMD64, multiple-machine, Spark, GPU, generic posterior-sampler or arbitrary
upstream-model compatibility claim is made for this optional project.
