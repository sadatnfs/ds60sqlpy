# TMB 1.9.25 public API reference

This maintained inventory comes from the exact pinned CRAN source archive NAMESPACE and manual signatures. Descriptions and cautions are original course prose. It maps every explicit export and registered S3 method to a substantive chapter. Internal helpers are not silently promoted to a supported public API.

The package declares 30 explicit exports. Generic dispatch additionally exposes `as.list.sdreport` and `confint.tmbprofile`; other registered methods also appear among the exports. `GK` is documented but not exported in this pinned package. An inventory row describes teaching coverage, not a runtime pass.

| Function | Surface | Chapter | Purpose |
| --- | --- | --- | --- |
| `benchmark` | exported | [tmb-039](guides/tmb-039.md) | Measure selected model operations across thread counts. |
| `checkConsistency` | exported | [tmb-031](guides/tmb-031.md) | Compare a model simulator and likelihood using score-based diagnostics. |
| `compile` | exported | [tmb-037](guides/tmb-037.md) | Compile an original C++ template through the R toolchain. |
| `config` | exported | [tmb-037](guides/tmb-037.md) | Inspect or change a loaded model DLL configuration. |
| `dynlib` | exported | [tmb-037](guides/tmb-037.md) | Construct a platform-specific model library filename. |
| `FreeADFun` | exported | [tmb-037](guides/tmb-037.md) | Release objective-associated native memory. |
| `gdbsource` | exported | [tmb-038](guides/tmb-038.md) | Run an R reproducer under a native debugger. |
| `MakeADFun` | exported | [tmb-026](guides/tmb-026.md) | Construct objective, gradient and related R interfaces from a loaded template. |
| `newton` | exported | [tmb-035](guides/tmb-035.md) | Solve a differentiable inner problem using generalized Newton steps. |
| `newtonOption` | exported | [tmb-035](guides/tmb-035.md) | Inspect or set an objective inner-optimizer configuration. |
| `normalize` | exported | [tmb-033](guides/tmb-033.md) | Normalize a suitably flag-controlled latent process contribution. |
| `oneStepPredict` | exported | [tmb-032](guides/tmb-032.md) | Construct conditional one-step-ahead residual diagnostics. |
| `openmp` | exported | [tmb-039](guides/tmb-039.md) | Read or set model-library native thread count and experimental autopar mode. |
| `plot.parallelBenchmark` | exported | [tmb-039](guides/tmb-039.md) | Display timing or speedup from a benchmark result. |
| `plot.tmbprofile` | exported | [tmb-029](guides/tmb-029.md) | Display a computed one-dimensional likelihood profile. |
| `precompile` | exported | [tmb-037](guides/tmb-037.md) | Prepare TMB library precompilation support. |
| `print.backtrace` | exported | [tmb-038](guides/tmb-038.md) | Format the debugger backtrace object. |
| `print.checkConsistency` | exported | [tmb-031](guides/tmb-031.md) | Print an existing simulation-consistency diagnostic. |
| `print.sdreport` | exported | [tmb-028](guides/tmb-028.md) | Print an existing uncertainty report. |
| `Rinterface` | exported | [tmb-025](guides/tmb-025.md) | Generate an R-side skeleton from a C++ template. |
| `runExample` | exported | [tmb-025](guides/tmb-025.md) | List or run installed package examples with explicit process/workspace options. |
| `runSymbolicAnalysis` | exported | [tmb-036](guides/tmb-036.md) | Configure specialized sparse factorization analysis paths. |
| `sdreport` | exported | [tmb-028](guides/tmb-028.md) | Calculate local uncertainty for parameters and derivative-aware reports. |
| `SR` | exported | [tmb-034](guides/tmb-034.md) | Describe an integration grid for sequential reduction. |
| `summary.checkConsistency` | exported | [tmb-031](guides/tmb-031.md) | Extract detailed joint/marginal simulation-consistency summaries. |
| `summary.sdreport` | exported | [tmb-028](guides/tmb-028.md) | Select fixed, random or reported uncertainty rows. |
| `template` | exported | [tmb-025](guides/tmb-025.md) | Create a minimal C++ authoring scaffold. |
| `tmbprofile` | exported | [tmb-029](guides/tmb-029.md) | Compute a profile or slice for a parameter or linear contrast. |
| `tmbroot` | exported | [tmb-030](guides/tmb-030.md) | Find profile-likelihood confidence endpoints by root solving. |
| `TMB.Version` | exported | [tmb-037](guides/tmb-037.md) | Report TMB package and native ABI compatibility information. |
| `confint.tmbprofile` | registered-s3 | [tmb-029](guides/tmb-029.md) | Extract confidence crossings from an existing profile curve. |
| `as.list.sdreport` | registered-s3 | [tmb-028](guides/tmb-028.md) | Restore parameter or report estimates/errors into shaped lists. |
| `GK` | documented-not-exported | [tmb-034](guides/tmb-034.md) | Describe settings for an alternative Gauss-Kronrod integration path. |

## benchmark

```r
benchmark(obj, n = 10, expr = NULL, cores = NULL)
```

Measure selected model operations across thread counts.

Typical use: Use after numerical parity to time a named objective, gradient or custom expression.

Cautions: Report cold/warm scope, repetitions and thread policy; timing is not correctness.

Read [tmb-039](guides/tmb-039.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `benchmark` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## checkConsistency

```r
checkConsistency(
  obj,
  par = NULL,
  hessian = FALSE,
  estimate = FALSE,
  n = 100,
  observation.name = NULL
)
```

Compare a model simulator and likelihood using score-based diagnostics.

Typical use: Check joint score centering and inspect approximation effects on marginal scores.

Cautions: Requires matching SIMULATE code; beta API; repeated estimation can be expensive.

Read [tmb-031](guides/tmb-031.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `checkConsistency` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## compile

```r
compile(
  file,
  flags = "",
  safebounds = TRUE,
  safeunload = TRUE,
  openmp = isParallelTemplate(file[1]),
  libtmb = TRUE,
  libinit = TRUE,
  tracesweep = FALSE,
  framework = getOption("tmb.ad.framework"),
  supernodal = FALSE,
  longint = FALSE,
  eigen.disable.warnings = TRUE,
  max.order = NULL,
  ...
)
```

Compile an original C++ template through the R toolchain.

Typical use: Build a source-identified library with explicitly chosen framework and flags.

Cautions: Compiler success is not a load, optimizer or uncertainty pass; flags and ABI matter.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `compile` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## config

```r
config(..., DLL = getUserDLL())
```

Inspect or change a loaded model DLL configuration.

Typical use: Read the selected DLL configuration while diagnosing runtime behavior.

Cautions: Option names and meaning can be internal/version-sensitive; do not expose arbitrary mutation.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `config` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## dynlib

```r
dynlib(name)
```

Construct a platform-specific model library filename.

Typical use: Pass the resulting filename to a deliberately scoped native load.

Cautions: A filename does not establish compatible architecture or source identity.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `dynlib` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## FreeADFun

```r
FreeADFun(obj)
```

Release objective-associated native memory.

Typical use: Retire an objective in a process with explicit object ownership.

Cautions: This is not deletion of source or learner state and is not arbitrary safe concurrent DLL unloading.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `FreeADFun` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## gdbsource

```r
gdbsource(file, interactive = FALSE)
```

Run an R reproducer under a native debugger.

Typical use: Diagnose a minimal crash using matching source and debug symbols.

Cautions: Needs a prepared debugger and permissions; backtraces can contain sensitive input/environment details.

Read [tmb-038](guides/tmb-038.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `gdbsource` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## MakeADFun

```r
MakeADFun(
  data,
  parameters,
  map = list(),
  type = c("ADFun", "Fun", "ADGrad"[!intern && (!is.null(random) || !is.null(profile))]),
  random = NULL,
  profile = NULL,
  random.start = expression(last.par.best[random]),
  hessian = FALSE,
  method = "BFGS",
  inner.method = "newton",
  inner.control = list(maxit = 1000),
  MCcontrol = list(doMC = FALSE, seed = 123, n = 100),
  ADreport = FALSE,
  atomic = TRUE,
  LaplaceNonZeroGradient = FALSE,
  DLL = getUserDLL(),
  checkParameterOrder = TRUE,
  regexp = FALSE,
  silent = FALSE,
  intern = FALSE,
  integrate = NULL,
  ...
)
```

Construct objective, gradient and related R interfaces from a loaded template.

Typical use: Declare named data/parameters and deliberate map, random, profile and integration choices.

Cautions: Some options change the statistical target; data shapes, framework and parameter ordering must agree.

Read [tmb-026](guides/tmb-026.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `MakeADFun` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## newton

```r
newton(
  par,
  fn,
  gr,
  he,
  trace = 1,
  maxit = 100,
  tol = 1e-08,
  alpha = 1,
  smartsearch = TRUE,
  mgcmax = 1e+60,
  super = TRUE,
  silent = TRUE,
  ustep = 1,
  power = 0.5,
  u0 = 1e-04,
  grad.tol = tol,
  step.tol = tol,
  tol10 = 0.001,
  env = environment(),
  ...
)
```

Solve a differentiable inner problem using generalized Newton steps.

Typical use: Study gradient/Hessian-based inner optimization with explicit tolerances.

Cautions: Indefinite curvature, scaling and approximate solves need diagnosis; one iteration is not generally enough.

Read [tmb-035](guides/tmb-035.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `newton` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## newtonOption

```r
newtonOption(obj, ...)
```

Inspect or set an objective inner-optimizer configuration.

Typical use: Save and adjust model-specific inner controls after observing a concrete failure.

Cautions: Changing outer tolerances does not replace adequate inner accuracy.

Read [tmb-035](guides/tmb-035.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `newtonOption` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## normalize

```r
normalize(obj, flag, value = 0)
```

Normalize a suitably flag-controlled latent process contribution.

Typical use: Use when a model intentionally exposes an unnormalized process without observation terms.

Cautions: Requires the correct template flag and a proper integrable process; not a generic missing-term detector.

Read [tmb-033](guides/tmb-033.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `normalize` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## oneStepPredict

```r
oneStepPredict(
  obj,
  observation.name = NULL,
  data.term.indicator = NULL,
  method = c(
    "oneStepGaussianOffMode", "fullGaussian", "oneStepGeneric",
    "oneStepGaussian", "cdf"
  ),
  subset = NULL,
  conditional = NULL,
  discrete = NULL,
  discreteSupport = NULL,
  range = c(-Inf, Inf),
  seed = 123,
  parallel = FALSE,
  trace = TRUE,
  reverse = (method == "oneStepGaussianOffMode"),
  splineApprox = TRUE,
  ...
)
```

Construct conditional one-step-ahead residual diagnostics.

Typical use: Inspect sequential model adequacy using a matching observation/indicator interface.

Cautions: Beta API; methods, ordering and discrete randomization differ; current ordinary models do not imply OSA support.

Read [tmb-032](guides/tmb-032.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `oneStepPredict` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## openmp

```r
openmp(n = NULL, max = FALSE, autopar = NULL, DLL = getUserDLL())
```

Read or set model-library native thread count and experimental autopar mode.

Typical use: Allocate a deliberate small thread count and compare serial/parallel numerical output.

Cautions: Does not control every BLAS pool; autopar requires TMBad/OpenMP and separate acceptance.

Read [tmb-039](guides/tmb-039.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `openmp` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## plot.parallelBenchmark

```r
plot.parallelBenchmark(x, type = "b", ..., show = c("speedup", "time"), legendpos = "topleft")
```

Display timing or speedup from a benchmark result.

Typical use: Plot a retained benchmark with a clearly named operation and machine context.

Cautions: A chart summarizes its input measurements and does not create new benchmark evidence.

Read [tmb-039](guides/tmb-039.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `benchmark` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## plot.tmbprofile

```r
plot.tmbprofile(x, type = "l", level = 0.95, ...)
```

Display a computed one-dimensional likelihood profile.

Typical use: Inspect asymmetry, search coverage and crossings before reporting an interval.

Cautions: A sparse or failed profile can mislead; plotting does not repair nuisance optimization.

Read [tmb-029](guides/tmb-029.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `plot.tmbprofile` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## precompile

```r
precompile(all = TRUE, clean = FALSE, trace = TRUE, get.header = FALSE, ...)
```

Prepare TMB library precompilation support.

Typical use: Run during an explicitly writable package/image preparation stage.

Cautions: Mutates package preparation; actual precompilation occurs in subsequent model compilation; larger binaries can result.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `precompile` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## print.backtrace

```r
print.backtrace(x, ...)
```

Format the debugger backtrace object.

Typical use: Read a source-bound crash diagnosis from gdbsource.

Cautions: Output is diagnostic data, not instructions; preserve privacy when sharing it.

Read [tmb-038](guides/tmb-038.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `gdbsource` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## print.checkConsistency

```r
print.checkConsistency(x, ...)
```

Print an existing simulation-consistency diagnostic.

Typical use: Inspect a quick summary before reading the detailed diagnostic object.

Cautions: Printing does not simulate new data or independently qualify the model.

Read [tmb-031](guides/tmb-031.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `print.checkConsistency` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## print.sdreport

```r
print.sdreport(x, ...)
```

Print an existing uncertainty report.

Typical use: Review named estimates and uncertainty diagnostics.

Cautions: A polished table does not establish model adequacy or valid boundary inference.

Read [tmb-028](guides/tmb-028.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `print.sdreport` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## Rinterface

```r
Rinterface(file)
```

Generate an R-side skeleton from a C++ template.

Typical use: Discover declared interface names during owned model authoring.

Cautions: Generated scaffolding still needs valid data, starts, domain checks and statistical review.

Read [tmb-025](guides/tmb-025.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `Rinterface` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## runExample

```r
runExample(
  name = NULL,
  all = FALSE,
  thisR = TRUE,
  clean = FALSE,
  exfolder = NULL,
  dontrun = FALSE,
  subarch = TRUE,
  ...
)
```

List or run installed package examples with explicit process/workspace options.

Typical use: Explore an API in a disposable preparation directory.

Cautions: Examples may compile and run code; understand cleanup options and retain dependency licensing.

Read [tmb-025](guides/tmb-025.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `runExample` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## runSymbolicAnalysis

```r
runSymbolicAnalysis(obj, method = c("CHOLMOD", "incomplete"), ...)
```

Configure specialized sparse factorization analysis paths.

Typical use: Investigate ordering/fill-in or a deliberately tested incomplete-factorization experiment.

Cautions: CHOLMOD features can require special builds; incomplete methods are experimental and need error checks.

Read [tmb-036](guides/tmb-036.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `runSymbolicAnalysis` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## sdreport

```r
sdreport(
  obj,
  par.fixed = NULL,
  hessian.fixed = NULL,
  getJointPrecision = FALSE,
  bias.correct = FALSE,
  bias.correct.control = list(sd = FALSE, split = NULL, nsplit = NULL),
  ignore.parm.uncertainty = FALSE,
  getReportCovariance = TRUE,
  skip.delta.method = FALSE
)
```

Calculate local uncertainty for parameters and derivative-aware reports.

Typical use: Propagate curvature and delta-method uncertainty for a defined estimand.

Cautions: Boundary, weak-identification and approximation limits remain; dense report covariance can be large.

Read [tmb-028](guides/tmb-028.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `sdreport` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## SR

```r
SR(x, discrete = FALSE)
```

Describe an integration grid for sequential reduction.

Typical use: Prepare a documented grid compatible with an explicit MakeADFun integration design.

Cautions: Grid measure, support and truncation affect the target/accuracy; not a universal scalable integrator.

Read [tmb-034](guides/tmb-034.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `SR` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## summary.checkConsistency

```r
summary.checkConsistency(object, na.rm = FALSE, ...)
```

Extract detailed joint/marginal simulation-consistency summaries.

Typical use: Interpret score behavior and estimated approximation bias with replicate counts.

Cautions: A large experiment can detect small Laplace approximation error; avoid treating every p-value as a universal pass.

Read [tmb-031](guides/tmb-031.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `summary.checkConsistency` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## summary.sdreport

```r
summary.sdreport(
  object,
  select = c("all", "fixed", "random", "report"),
  p.value = FALSE,
  ...
)
```

Select fixed, random or reported uncertainty rows.

Typical use: Extract named estimates and standard errors for the intended result table.

Cautions: Optional p-values require a defensible null and regular inference assumptions.

Read [tmb-028](guides/tmb-028.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `summary.sdreport` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## template

```r
template(file = NULL)
```

Create a minimal C++ authoring scaffold.

Typical use: Begin an original objective in an owned scratch source file.

Cautions: A template has no complete statistical meaning until the density, schema and checks are supplied.

Read [tmb-025](guides/tmb-025.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `template` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## tmbprofile

```r
tmbprofile(
  obj,
  name,
  lincomb,
  h = 1e-04,
  ytol = 2,
  ystep = 0.1,
  maxit = ceiling(5 * ytol / ystep),
  parm.range = c(-Inf, Inf),
  slice = FALSE,
  adaptive = TRUE,
  trace = TRUE,
  ...
)
```

Compute a profile or slice for a parameter or linear contrast.

Typical use: Reoptimize nuisance parameters across a scientifically meaningful target range.

Cautions: A slice is not a profile; convergence, range coverage and regular likelihood assumptions matter.

Read [tmb-029](guides/tmb-029.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `tmbprofile` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## tmbroot

```r
tmbroot(
  obj,
  name,
  target = 0.5 * qchisq(0.95, df = 1),
  lincomb,
  parm.range = c(NA, NA),
  sd.range = 7,
  trace = FALSE,
  continuation = FALSE
)
```

Find profile-likelihood confidence endpoints by root solving.

Typical use: Solve a stated NLL-rise equation with a justified domain and target.

Cautions: Default chi-square calibration is asymptotic and can fail at boundaries or under non-identification.

Read [tmb-030](guides/tmb-030.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `tmbroot` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## TMB.Version

```r
TMB.Version()
```

Report TMB package and native ABI compatibility information.

Typical use: Record compatibility metadata beside source/compiler/architecture identity.

Cautions: A matching TMB ABI alone does not guarantee cross-platform binary compatibility.

Read [tmb-037](guides/tmb-037.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `TMB.Version` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## confint.tmbprofile

```r
confint.tmbprofile(object, parm, level = 0.95, ...)
```

Extract confidence crossings from an existing profile curve.

Typical use: Use confint(profile, level=...) after inspecting profile shape and domain coverage.

Cautions: Uses the computed curve and interpolation; unresolved crossings remain unresolved.

Read [tmb-029](guides/tmb-029.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `confint.tmbprofile` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## as.list.sdreport

```r
as.list.sdreport(x, what = "", report = FALSE, ...)
```

Restore parameter or report estimates/errors into shaped lists.

Typical use: Use the as.list generic instead of guessing flattened output positions.

Cautions: Registered S3 dispatch is public usage even though the method is not an explicit NAMESPACE export.

Read [tmb-028](guides/tmb-028.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `as.list.sdreport` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## GK

```r
GK(...)
```

Describe settings for an alternative Gauss-Kronrod integration path.

Typical use: Read the documented helper while comparing integration designs.

Cautions: Documented in 1.9.25 but not exported by its NAMESPACE; no stable TMB::GK or classroom runtime promise is made.

Read [tmb-034](guides/tmb-034.md). Source: [TMB manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf), `GK` entry. See [qualification](QUALIFICATION.md) for actual executed boundaries.

## Native execution coverage

The original nine-model compiler acceptance and the bounded public API probe
exercise most ordinary APIs on native Linux ARM64. The machine-readable inventory
records each entry's exact execution scope. `runExample` is exercised only as an
example listing; `SR` only constructs a descriptor; `config` and `newtonOption`
are read without arbitrary mutations. Experimental TMBad/autopar, specialized
SuiteSparse and alternate integration modes are separate capabilities.

`normalize`, `oneStepPredict`, `precompile`, `runSymbolicAnalysis`, `gdbsource` and
its backtrace printing are taught with their real contracts but are not claimed
as executed native acceptance here. GK remains explicitly non-exported. A
mathematical companion or an API signature is not a substitute for those probes.
