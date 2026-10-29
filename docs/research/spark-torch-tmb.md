# Custom likelihoods, automatic differentiation, Spark and TMB

Research and implementation snapshot: 2026-10-29.

Spark can support custom maximum-likelihood models with PyTorch or TMB when the
objective has a valid decomposition and each worker has a prepared numerical
environment. We implemented both paths. The independent R-free package is the
primary framework; the R/TMB companion is an optional reference and compatibility
path. Spark schedules data work; Torch or TMB
computes local derivatives; a driver can combine numeric summaries and optimize
one shared parameter vector. Separately, TorchDistributor launches actual Torch
and Lightning training processes. These are different execution designs.

The central limit is mathematical: arbitrary storage partitions are not
independent statistical units. A covariance edge, shared latent effect or global
normalizer can invalidate a naive sum of partition likelihoods. No compiler,
UDF or AD library repairs a factorization that changes the model.

This report answers the seven requested research questions, identifies the
historical sources inspected, and maps the findings to actual source. The new
material comprises 20 custom-likelihood PyTorch chapters, 38 advanced Spark
chapters and 48 TMB chapters. All three subjects now pass shared catalog and
prerequisite admission. Source implementation, local native execution,
classroom/browser integration and final publication are separate stages. The
new phase's final shared integration and release are still pending.

## 1. How Spark can fit custom maximum-likelihood models

Start by defining the observation unit and the parameters it shares with other
units. Four patterns cover many useful designs:

| Pattern | Mathematical target | Appropriate computation | Incorrect shortcut |
| --- | --- | --- | --- |
| Independent models | Separate parameter vector for each group | Fit each complete group and retain separate diagnostics | Average fitted coefficients and call that the global MLE |
| Shared additive model | One parameter vector, sum of independent contributions | Evaluate loss and gradient per partition, combine them, update one driver vector | Update a different parameter vector independently in each partition |
| Group-separable latent model | Common fixed parameters, independent latent blocks | Integrate each complete block at the same fixed parameters, then sum marginal contributions | Optimize shared hyperparameters separately by group |
| Coupled model | Cross-unit covariance, shared states or nonlocal objective terms | Preserve the coupled block or use a justified specialized algorithm | Drop cross-partition terms and retain the original model's name |

For an additive weighted negative log likelihood, our implemented contract is

\[
L(\theta)=\sum_{p=1}^{P}\sum_{i\in I_p}w_i\ell_i(\theta)
 +\frac{\lambda}{2}\|\theta\|^2,
\qquad
\nabla L(\theta)=\sum_p g_p(\theta)+\lambda\theta.
\]

With lambda zero this is an unpenalized weighted objective; a nonzero penalty
changes the estimation target. Integer frequency weights can represent repeated
observations. Survey, importance or other fractional weights need their own
inferential interpretation rather than being silently treated as ordinary
independent replicates.

Each worker returns a row count, total weight, loss sum and gradient sum. The
driver validates partition completeness and the exact parameter digest before
combining results. The penalty is added once. For a weighted mean, the combined
data loss and gradient are divided by the global weight sum before the penalty
is applied. This makes the meaning of lambda explicit.

For example, partitions with counts one and three and sums one and nine have a
global mean of 2.5. Averaging their local means yields two. The same error can
appear in Spark aggregates, Arrow batches and DDP ranks. Repartitioning must not
silently change the statistical objective.

The implementation uses Spark's public partition and aggregation mechanisms;
these distribute a supplied calculation rather than deriving its statistical
validity. Spark also offers a built-in logistic estimator, useful as a reference
for supported models but not as an interface for every arbitrary likelihood.
See the [Spark 4.0.1 programming guide](https://spark.apache.org/docs/4.0.1/rdd-programming-guide.html)
and [LogisticRegression API](https://spark.apache.org/docs/4.0.1/api/scala/org/apache/spark/ml/classification/LogisticRegression.html).

The first complete examples deliberately have strong oracles:

- Stable binary logistic loss uses
  \(\operatorname{softplus}(z)-yz\), where
  \(\operatorname{softplus}(z)=\max(z,0)+\log(1+e^{-|z|})\).
  We compare analytic gradients, finite differences and actual Spark reduction.
- Nonlinear Gaussian regression uses
  \(\mu(t)=a\exp(-bt)+c\), with positive rate and scale represented explicitly.
  The likelihood includes the log-scale normalization. One public Spark example
  profiles linear parameters over a finite rate grid; the combined Torch
  project fits a continuous four-parameter objective and compares with a
  separate NumPy/SciPy calculation. The grid fit is not described as a
  continuous global optimizer.
- The AR(1) example retains the initial-state density and every transition.
  Restarting the stochastic process at each physical partition produces a
  different likelihood, which the counterexample demonstrates.

Repeated optimization actions have real costs. Cache immutable input when useful,
return small summaries, limit native library threads, and measure scheduling,
conversion, arithmetic and reduction separately. A cache is not a transactional
snapshot: lost partitions can be recomputed from lineage. Pure task evaluation
also avoids counting retried side effects as extra observations.

For group fits, Spark 4.0.1's `applyInPandas` performs a shuffle and loads complete
groups. A check inside the pandas function cannot prevent memory exhaustion
that occurred while materializing a giant group. `mapInPandas` instead provides
an iterator of transport batches; a transport batch is not a statistical group.
These boundaries are documented in the versioned
[grouped pandas API](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.GroupedData.applyInPandas.html)
and [mapInPandas API](https://spark.apache.org/docs/4.0.1/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.mapInPandas.html).

Implemented teaching: [asm-001](../../courses/advanced-spark-modeling/guides/asm-001.md)
through [asm-012](../../courses/advanced-spark-modeling/guides/asm-012.md),
[asm-018](../../courses/advanced-spark-modeling/guides/asm-018.md), and
[asm-037](../../courses/advanced-spark-modeling/guides/asm-037.md).

## 2. What “native automatic differentiation in Spark” means

There are three distinct claims:

1. **Spark executes derivative formulas.** Yes. A SQL expression, Scala
   aggregate or partition function can compute an analytic gradient.
2. **A derivative engine runs inside Spark tasks.** Yes. Our original Scala
   dual-number example performs bounded forward-mode AD in JVM task code.
   The prepared Torch and TMB projects perform genuine local AD inside their
   respective numerical processes.
3. **Spark automatically differentiates an arbitrary DataFrame program through
   joins, shuffles, UDFs and materialization.** The inspected Spark 4.0.1 public
   APIs do not provide that general facility. Our implementation does not claim
   to add it.

The distinction is visible at the serialization boundary. A Torch tensor graph
or TMB native tape can produce a numeric gradient. Once that gradient and loss
are returned as ordinary numbers, they are evidence from an evaluation, not a
portable global reverse-mode graph. Wrapping a collected scalar in a new tensor
with gradients enabled does not reconnect it to the original distributed data.

The dual-number lesson implements \(a+b\varepsilon\), with
\(\varepsilon^2=0\), for addition, multiplication and exponential. It correctly
propagates derivatives through compositions such as \(x^2+e^x\). That is real AD
for its supported operations. It does not differentiate a Spark scheduler,
discrete top-k selection or arbitrary third-party function. PyTorch's own
[autograd mechanics](https://docs.pytorch.org/docs/2.9/notes/autograd.html)
explains its graph-based local derivative mechanism; Spark's
[expression source](https://github.com/apache/spark/blob/v4.0.1/sql/catalyst/src/main/scala/org/apache/spark/sql/catalyst/expressions/Expression.scala)
describes a query-expression execution interface, a different abstraction.

Implemented teaching: [asm-024](../../courses/advanced-spark-modeling/guides/asm-024.md)
and [asm-025](../../courses/advanced-spark-modeling/guides/asm-025.md).
Their complete Scala sources execute in the ordinary prepared Spark profile.

## 3. Custom likelihood modeling in PyTorch

PyTorch is useful for classical statistical optimization as well as neural
networks. A model can produce one normalized negative log-likelihood term per
observation, then use autograd and a conventional optimizer. The main work is
specifying the probability model correctly: support, normalizing terms,
parameter constraints, observation dependence and the prediction target.

The new [20-chapter route](../../courses/custom-likelihood-pytorch/README.md)
starts with observation/parameter/likelihood distinctions and proceeds through
Gaussian and nonlinear models, logistic and count likelihoods, censoring,
heteroskedasticity, mixtures and correlated residuals. It then develops
penalties, identifiability, optimizer closures, curvature, prediction and
uncertainty. All 20 programs are complete original float64 CPU examples.

Two frequently missed details receive explicit treatment:

- Estimating a Gaussian scale requires the log-scale normalization as well as
  the squared residual. Increasing scale must not make every observation
  artificially favorable for free.
- Reparameterizing an optimizer variable, such as \(\sigma=\exp(s)\), requires
  the chain rule but does not automatically add a likelihood Jacobian. A
  transformed probability density is a different question, where a Jacobian
  can be required.

Mixtures use stable log-sum calculations. Censored observations contribute
probability mass over an unobserved range, not an imputed observation at the
censoring threshold. Correlated panels retain their joint structure. These are
modeling decisions that AD faithfully differentiates, whether they are right
or wrong.

The route checks analytic scores and finite differences, inspects Hessians and
profiles, and distinguishes convergence from identification. PyTorch's
[gradcheck documentation](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.gradcheck.gradcheck.html)
provides a numerical derivative-testing mechanism; passing it does not establish
that the scientific model or confidence interval is valid. Closure-based
optimization also has an explicit evaluation contract, described by the
[LBFGS API](https://docs.pytorch.org/docs/2.9/generated/torch.optim.LBFGS.html).

Chapter map: `clp-001` through `clp-004` establish likelihood and derivative
contracts; `clp-005` through `clp-012` implement distinct distributions and
dependence structures; `clp-013` through `clp-016` cover estimation diagnostics;
`clp-017` through `clp-020` cover prediction, uncertainty, distributed scaling and
a nonlinear panel dossier. See the course's
[validation record](../../courses/custom-likelihood-pytorch/VALIDATION.md) for
actual numerical execution and the limitations of supplied covariance and
plug-in prediction examples.

## 4. Spark with PyTorch, TorchDistributor and Lightning

We implemented the independent distribution
[`ds60-spark-likelihood`](../../packages/spark-likelihood/README.md), imported as
`ds60_spark_likelihood`, for bounded custom maximum-likelihood estimation. Its pure
core imports neither the classroom nor R. Spark, Torch, SciPy and training extras
are prepared explicitly. The historical application namespace contains thin
compatibility aliases, not a second implementation. Low-dimensional driver
optimization and general neural-network training remain distinct interfaces.

| Component | Responsibility |
| --- | --- |
| [contracts.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/contracts.py) | Finite numeric contracts, parameter digests, complete partition accounting and one global reduction/penalty |
| [torch_backend.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/torch_backend.py) | Bounded CPU float64 batches, one per-observation loss, local autograd and detached summaries |
| [spark_backend.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/spark_backend.py) | Explicit DataFrame/RDD boundary, owned derived cache and partition evaluation |
| [optimization.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/optimization.py) | Optional SciPy L-BFGS-B, bounded calls, status, trace and raw/bound-aware gradient diagnostics |
| [models.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/models.py) | Original logistic, normal, nonlinear Gaussian and Poisson-exposure models |
| [unit_backend.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/unit_backend.py) and [spark_units.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/spark_units.py) | Distinct bounded complete-unit losses, membership/order identities and whole-unit weighting |
| [registry.py](../../packages/spark-likelihood/src/ds60_spark_likelihood/registry.py) | Trusted named factories, explicit parameter/features/prediction metadata and source/configuration/live-code fingerprints |
| [DataFrame and ML guide](../../packages/spark-likelihood/docs/DATAFRAME-ML.md) | Explicit column mapping, shared versus separate fits, Estimator/Model, response-free transform and JSON/Pipeline persistence |

The package bounds parameters at 64, partition summaries at 4,096 and local
batches at 8,192 rows. Those limits express its teaching and driver-memory scope.
The model must be deterministic and additive across its declared observation
units. A callable that depends on batch composition violates the contract even
if its return tensor has the expected shape.

A complete-unit callback returns one joint loss for a whole independent group;
it is not a scalar shortcut through the per-row batching interface. The exact
Gaussian random-intercept model integrates the latent intercept with Torch
linear algebra and matches an independent rank-one oracle. Its declared prediction
is a marginal new-group mean, not an inferred existing-group latent effect.
The original [Gamma-Poisson custom model](../../packages/spark-likelihood/docs/gamma-poisson.md)
proves non-Gaussian extensibility through ordinary registration: groups share a
Gamma-distributed latent rate, exposures enter the conditional Poisson law, and
a closed-form integral supplies the joint NLL. It is not a generic Laplace engine.

Review found that subtracting large Gamma log-normalizers could produce zero loss
and score at log shape/rate 100 despite the correct zero-count loss being three.
The repaired example uses a bounded integer rising-factorial identity and stable
log-domain products. Zero and nonzero count cases at log shape/rate 40, 100 and
300 match the independent Poisson limit. Its explicit total-count and numerical
bounds are documented rather than silently clipped during optimization.

Model identity also includes callable defaults, keyword defaults, direct JSON
constants and normalized live bytecode, with Python minor compatibility. Replacing
a named code object changes identity even when its source file is unchanged;
relocating source paths alone does not. Trusted code/configuration remain a
requirement. Direct package JSON loading does not import an artifact-selected
model, while upstream Spark Pipeline metadata can import stage classes and must
come from a trusted source.

The [combined project](../../courses/advanced-spark-modeling/projects/spark-torch/README.md)
prepares Spark 4.0.1, Torch 2.9.1 CPU, Lightning 2.6.1 and the required conversion
libraries together. The ordinary Spark and Torch pads remain separate images.
Its fixed cases cover global logistic and nonlinear fits, independent group
fits, actual Arrow batches, TorchDistributor, Lightning and sampler coverage.
The additional `standalone-package` case builds evidence from the installed wheel,
compares declared/packaged/installed source hashes, probes actual executor imports
and exercises numerical, complete-unit, prediction and all 33 DataFrame/ML checks.
The sealed native ARM64 workshop passed those checks alongside the original cases.
This is local CPU evidence; the final new-version hosted native jobs remain a
separate release gate.

TorchDistributor has a different job. Inspection of Spark's exact
[v4.0.1 source](https://github.com/apache/spark/blob/v4.0.1/python/pyspark/ml/torch/distributor.py)
confirmed public `run` and private `_train_on_dataframe`; the latter is not a
public interface taught here. `run` launches the training function. That function
still owns its model, data loader, optimizer and result contract.

Our one-process baseline and two-rank CPU case use `local_mode=True`, so Torch's
launcher runs on the driver machine. This is actual process coordination, but
not a remote Spark executor training deployment. The unequal-rank case uses
four observations on one rank and two on the other. For local gradient sums
\(g_r\), global observation count N and world size R, ordinary DDP averaging of
local losses scaled by \(R/N\) yields \(\sum_r g_r/N\). Unweighted averaging of
local mean losses would generally be wrong. The
[DDP contract](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html)
also makes input sharding the application's responsibility.

The sampler audit demonstrates why five observations across two equal-length
rank samplers can produce six assignments with padding or four with dropping.
It records IDs rather than assuming an epoch covers each row once. The
[DistributedSampler documentation](https://docs.pytorch.org/docs/2.9/data.html#torch.utils.data.distributed.DistributedSampler)
explains padding, dropping and epoch-dependent shuffling.

Lightning organizes the training loop, device handling and strategy. It must
use a compatible process topology instead of independently spawning another
full world inside every already launched rank. Our actual two-rank Lightning
case checks the numerical update and unique row coverage on a divisible fixture.
This does not qualify arbitrary Trainer configurations, checkpoint recovery or
GPU placement. See the [Trainer contract](https://lightning.ai/docs/pytorch/stable/common/trainer.html)
and the project's pinned implementation rather than assuming that a moving
`stable` documentation page has the exact installed version.

A later sealed-image acceptance found a separate failure after the Lightning
numerical result was written: both ranks aborted during interpreter shutdown.
Inspection of Spark 4.0.1's
[`torch_run_process_wrapper.py`](https://github.com/apache/spark/blob/v4.0.1/python/pyspark/ml/torch/torch_run_process_wrapper.py)
confirmed that this version waits for its child but does not propagate the
child's return code on normal wrapper completion. A serialized result plus a
zero wrapper exit therefore did not establish successful rank shutdown in this
case. The integration repair adds explicit process-group teardown and a narrowly
version/source-hash-checked preparation patch for exit propagation. The repaired
sealed offline launcher then passed with exit zero, 12 accepted observations and
no fatal diagnostics on native ARM64. A deliberately failing worker exited with
code seven after serializing a result, and the launcher correctly raised instead
of accepting that result. Lightning completed cleanly with explicit teardown.
That historical source-bound receipt also covers one/two ranks, Arrow batch
bounds one/three, MLEs, group fits and cleanup. The subsequent canonical-package
integration preserved those cases and passed 13 top-level observations, including
the new installed-wheel gate. Exact image/source identities remain in the retained
qualification receipts, rather than becoming mutable installation instructions. This is a specific observed version/integration
defect and tested repair, not a general claim that Spark or Lightning cannot
train correctly or that remote-cluster behavior has been qualified.

Implemented teaching: [asm-026](../../courses/advanced-spark-modeling/guides/asm-026.md)
through [asm-030](../../courses/advanced-spark-modeling/guides/asm-030.md), supported
by [clp-019](../../courses/custom-likelihood-pytorch/guides/clp-019.md).
The restart chapter defines a review contract; the current fixtures do not
claim exact mid-epoch or remote-cluster recovery.

## 5. TMB/adcomp, R/C++, rpy2 and Spark integration

TMB's architecture fits this problem well. An author writes a C++ template for
the objective, R constructs callable value/derivative functions with `MakeADFun`,
and an optimizer such as `nlminb` performs estimation. `REPORT`, `ADREPORT` and
`sdreport` serve different reporting and uncertainty roles. Selected latent
variables can be integrated through a Laplace approximation. These mechanisms
are documented by the [TMB introduction](https://kaskr.github.io/adcomp/Introduction.html)
and the authors' [methodology paper](https://www.jstatsoft.org/article/view/v070i05).
The introduction currently displays an older documentation build, so our exact
API inventory is tied to installed TMB 1.9.25 rather than that header.

TMB differentiates supported operations expressed with its templated numeric
`Type`; converting a parameter-dependent value to an ordinary double or calling
an external routine without a derivative interface can break that computation.
The prepared project qualifies the CppAD route. TMBad-specific capabilities and
specialized internal integration options have separate preparation boundaries.
TMB's OpenMP accumulation is parallelism within a prepared numerical process,
not Spark distribution. The documented
[parallel accumulator](https://kaskr.github.io/adcomp/structparallel__accumulator.html)
has a restricted accumulation contract, and the course checks one/two-thread
parity before treating parallel execution as evidence. The current
[TMB 1.9.25 manual](https://cran.r-project.org/web/packages/TMB/TMB.pdf) is the
reference for installed R API details and distinguishes simulation diagnostics,
profiles, inner solvers and reporting methods.

The [48-chapter TMB route](../../courses/tmb-modeling/README.md) includes nine
original compiled models and 48 base-R mathematical companions. Native C++/TMB
compilation remains a separate project capability. The public API reference
maps the installed namespace's 30 exports, nine registered S3 methods and an
explicitly labeled non-exported documented helper. It does not say every
specialized facility was exercised merely because its name was inventoried.
Eight additional chapters, `tmb-041` through `tmb-048`, teach C++ data/container
contracts, density and sparse/separable families, stable branches and custom
atomic derivatives. Five original native probes test those families separately.
See [CPP-API-FAMILIES.md](../../courses/tmb-modeling/CPP-API-FAMILIES.md),
[API-REFERENCE.md](../../courses/tmb-modeling/API-REFERENCE.md),
[api-inventory.json](../../courses/tmb-modeling/api-inventory.json) and
[QUALIFICATION.md](../../courses/tmb-modeling/QUALIFICATION.md).

### When group Laplace contributions can be summed

For complete independent latent groups conditional on shared theta,

\[
p(y\mid\theta)=\prod_g\int\exp[-f_g(\theta,u_g)]du_g.
\]

At a suitable inner mode with positive-definite latent Hessian,

\[
\widetilde L_g(\theta)=f_g(\theta,\hat u_g)
 +\frac12\log|H_g|-\frac{q_g}{2}\log(2\pi).
\]

Evaluate all terms at the same theta, then sum their marginal values and outer
derivatives. Shared hyperparameter priors or penalties also need a deliberate
once-only placement. Integrating latent effects is different from maximizing
the joint density over them. A conditional derivative at a frozen inner mode
is not automatically the derivative of the complete marginal objective.

For Gaussian random intercepts the integral is Gaussian, so the Laplace result
has an exact independent oracle. For non-Gaussian latent models it is generally
an approximation. Correct derivatives of that approximation do not establish
its accuracy for the original integral.

A coupled two-variable Hessian makes the limit concrete:

\[
H=\begin{bmatrix}2&1\\1&2\end{bmatrix},\quad
|H|=3,\quad |H_{11}|\,|H_{22}|=4.
\]

The independent-block curvature term is wrong by
\(\tfrac12\log(4/3)\), about 0.14384, before accounting for a potentially wrong
inner mode. A spatial field or global latent state crossing partitions therefore
needs its coupling retained. Complete connected components, sparse centralized
solves within memory, state-space methods or a specialized distributed solver
are possible alternatives. Arbitrary partition-local Laplace calls are not.

### The implemented Spark/TMB boundary

The [Spark/TMB project](../../courses/advanced-spark-modeling/projects/spark-tmb/README.md)
contains a reusable prepared-model package,
[`spark_tmb`](../../courses/advanced-spark-modeling/projects/spark-tmb/spark_tmb/),
as well as fixed numerical cases. Trusted model source is registered and compiled
during preparation. Runtime requests contain a model ID, validated numerical
data and parameters. They do not accept arbitrary C++ source, R expressions,
compiler flags or library paths.

Registry v2 contains the original normal and random-intercept models plus
prediction-enabled normal-location and linear-regression templates. It declares
independent rows or complete groups, scalar/fixed-size-vector parameter blocks,
canonical flattened coordinate names, bounded data fields and an optional indexed
random vector. Response-free prediction/report semantics must be explicitly
registered; a likelihood does not automatically define a forecast. The schema
currently uses bounded numeric data vectors and explicit parameter blocks, not
an arbitrary matrix/object bridge. Preparation binds source,
compiled library, registry and R/TMB/Matrix/architecture identities. An R process
loads the compatible library, creates its own native objective, evaluates or
fits it, returns detached results and exits. Live R external pointers, DLL
handles and tapes are never serialized through Spark.

`SparkTMBObjective.evaluate(theta)` returns one shared additive objective.
`fit_independent_units(initial)` returns distinct fitted models. The unit ledger
checks identifiers, counts and data hashes; it cannot discover that the author
incorrectly declared correlated units independent. The bounded interface accepts
at most 4,096 observations and 64 fixed parameters per unit payload, with an
explicit bound on grouped latent structure. See
[REGISTERING-MODELS.md](../../courses/advanced-spark-modeling/projects/spark-tmb/REGISTERING-MODELS.md)
for the actual extension contract.

The fixed `global-normal-fit` example uses model-specific exact conditional
updates derived from AD scores. It is not labeled a general nonlinear optimizer.
The reusable evaluator supplies a boundary a separately prepared driver
optimizer can consume when the objective assumptions hold. The optional reference
also includes explicit DataFrame mappings, real ML fit/transform/persistence and
a Scala/JVM route through the same validated prepared-model protocol. It consumes
the standalone package's pure contracts without importing Torch. These R-bound
reference capabilities are qualified separately from the primary R-free package.

The `rpy2-frame` case separately checks real pandas-to-R conversion and a
compiled regression fit. Scoped converters keep conversion policy local;
column order, missing values, factor indices and time zones remain explicit
schema concerns. Conversion can copy data and is not a zero-cost transport for
an entire massive Spark table. This follows the official
[rpy2 pandas guide](https://rpy2.github.io/doc/latest/html/pandas.html).

Implemented teaching: `tmb-001` through `tmb-024` develop compiled modeling,
latent integration, prediction and the bridge; `tmb-025` through `tmb-040` deepen
the public API, profiles, diagnostics, sparse solvers, lifetime, debugging and
parallelism. [asm-031](../../courses/advanced-spark-modeling/guides/asm-031.md)
through [asm-035](../../courses/advanced-spark-modeling/guides/asm-035.md) connect
those mechanisms to actual Spark decomposition and its counterexamples.

## 6. Where PyMC fits

PyMC is a strong complementary modeling and posterior-inference environment.
Its custom-distribution interface can define a log probability, and predictive
sampling requires an appropriate generative definition as well. A custom
likelihood is not automatically a complete predictive model. The inspected
[current CustomDist documentation](https://www.pymc.io/projects/docs/en/stable/api/distributions/custom.html)
is newer than the classroom's pinned PyMC 5.28.5 runtime, so runnable code must
follow the installed version's API, not a moving documentation label.

The target matters more than the library name. With observations one and three,
known observation variance one and a normal prior with mean zero/variance one,
the MLE of the mean is two. The posterior mean is four-thirds and posterior
variance is one-third. The difference is intended prior information, not a
framework disagreement. MAP, posterior mean, MLE and a Laplace marginal estimate
are different quantities.

Spark may prepare data or orchestrate independent chains, but parallel chains
do not make one chain's joint likelihood partition-additive. Likewise, replacing
an exact full gradient with an arbitrary minibatch gradient changes the inference
algorithm. A specialized stochastic method requires its own justification.

[asm-036](../../courses/advanced-spark-modeling/guides/asm-036.md) develops this
comparison and connects to the existing [Bayesian route](../../courses/bayesian-computing/README.md).
The synthesis contains an analytic comparison, not a claim that identical
Torch, TMB and PyMC programs were all newly executed side by side for every
custom model. Use a small matched probabilistic model when doing that comparison.

## 7. Advanced Spark mechanisms implemented beyond library estimators

We implemented public APIs before introducing engine internals:

| Mechanism | Lessons | Actual source and evidence |
| --- | --- | --- |
| Typed Scala `Aggregator`, encoders and merge laws | asm-013 | Compiled count/sum aggregate, identity and empty-input cases |
| Registered SQL UDAF | asm-014 | Compiled weighted summary with seen/accepted counts and null policy |
| Native expression versus scalar UDF | asm-015 | Executed null/value comparison and plan inspection |
| Custom Transformer | asm-016 | Schema rejection, parameter copying and saved/loaded parity |
| Custom Estimator and fitted Model | asm-017 | Training-only learned mean, leakage counterexample and fitted-model persistence |
| Analyzed, optimized and physical plans | asm-019 | Actual printed plans and executed output invariants |
| Whole-stage code generation | asm-020 | Actual generated source and equivalent mode-on/mode-off results |
| Extension lifecycle and custom expression | asm-021, asm-022 | Compiled exact-version project, input checks and evaluated/generated parity |
| Restricted optimizer rule | asm-023 | Typed two-node-to-one-node rewrite plus boundary/null output checks |
| Bounded JVM forward AD | asm-024, asm-025 | Original dual-number implementation and explicit global-tape boundary |

The [UDAF API](https://spark.apache.org/docs/4.0.1/sql-ref-functions-udf-aggregate.html)
and [ML pipeline contract](https://spark.apache.org/docs/4.0.1/ml-pipeline.html)
provide reusable public structures. They do not guarantee that a custom merge
law, schema policy or saved artifact is correct; the examples test those
behaviors directly.

The [Catalyst project](../../courses/advanced-spark-modeling/projects/catalyst/README.md)
is intentionally pinned to Spark 4.0.1, Scala 2.13 and JDK 17.
`SparkSessionExtensions` explicitly disclaims source and binary stability in its
[versioned API](https://spark.apache.org/docs/4.0.1/api/scala/org/apache/spark/sql/SparkSessionExtensions.html).
The stable-softplus expression has separate evaluated and generated paths. The
optimizer rule removes a duplicate nonnegative BIGINT clamp, whose idempotence
is proved over the actual supported domain. It does not apply speculative
real-number identities to arbitrary floating expressions.

A first probe revealed that a local literal table was being folded away before
code generation. The final probe uses range-backed columns and checks actual
typed expression counts. This illustrates why “compiled successfully” and
“executed the intended engine path” are separate evidence.

## Historical repositories inspected and attribution decisions

The following immutable revisions were inspected on the report date. Repository
names, source links and mathematical ideas are retained; historical deployment
paths and workplace metadata are not imported into the classroom.

| Repository and revision | Concrete inspected files and finding | Use in this classroom |
| --- | --- | --- |
| [AFModel at 5362baf5](https://github.com/sadatnfs/AFModel/tree/5362baf5aa909d9792e0aeef2b9d17c8670841b9) | `AFModel.cpp` contains Gaussian panel terms with fixed/group effects and autoregressive/moving-average options; `run_model.R` constructs `MakeADFun`, calls `nlminb` and `sdreport` | Historical architecture in tmb-021 and the original synthetic panel dossier in tmb-024; no claim to reproduce every historical branch |
| [adcomp at ee2aebea](https://github.com/kaskr/adcomp/tree/ee2aebea75ccb96ccfb242732165a113cd3ec6d9) | TMB DESCRIPTION identifies 1.9.25; NAMESPACE and official API documentation distinguish exports, methods, compilation, differentiation and inference | Prepared dependency and exact-version public API teaching |
| [PyMB at 6c70da82](https://github.com/kforeman/PyMB/tree/6c70da82bbca9e6ae33cd3349cba89a45de7fc42) | `PyMB/model.py` uses global NumPy conversion activation, R loading and TMB calls | Historical bridge comparison in tmb-022/023; new scoped conversion and prepared-model protocol |
| [ar.matrix at c8f75efb](https://github.com/nmmarquez/ar.matrix/tree/c8f75efb08d5ea926aee5817cce22a940f03efa0) | `Q.AR1.R` constructs sparse autoregressive precision; `simGMRF.R` uses an eigensystem with a tolerance | Precision/recurrence and singularity discussion; independent original AR1 oracle |
| [TMBstanEX at 76f4c5b2](https://github.com/nmmarquez/TMBstanEX/tree/76f4c5b20891b91a9471edcc27c194f875f5bed7) | `ar1ex.cpp` defines a latent AR1/GMRF observation model with hyperpriors; `model_run.R` invokes TMB optimization and tmbstan | A useful research comparison for latent optimization versus posterior sampling; not a qualified dependency |
| [tmb_inla_sim at 47065f8b](https://github.com/nmmarquez/tmb_inla_sim/tree/47065f8bc692638670e7d8c7b8f0d7f4848d0538) | `spde.cpp` constructs sparse spatial precision and a separable temporal/spatial latent model with binomial observations | Concrete motivation for the coupled-latent limits in asm-035; no copied source or binaries |
| [us_county_forecasting at 118a58f3](https://github.com/nmmarquez/us_county_forecasting/tree/118a58f35b5bea3119346b70bde746057d98169f) | `simulations/conditional_ar.R` contains conditional autoregressive simulation and sparse Cholesky use | Context for spatial simulation and precision modeling, not an executed classroom workflow |

The nmmarquez inventory contained 85 public repositories at inspection time.
The table is a relevance-selected source inspection, not a claim that every file
in all 85 repositories was reviewed. In particular, the `ar.matrix` README's
broad Cholesky description should not be substituted for the inspected
`simGMRF.R` implementation, which uses eigenvalues and a tolerance. Similarly,
comments about comparing inference approaches in TMBstanEX do not establish
identical priors, algorithms or current compatibility. None of these historical
applications was installed or executed as part of this research report.

License evidence comes from actual package/source files, not solely GitHub's
license badge:

- AFModel's package declares MIT plus a license file, with an
  [MIT license text](https://github.com/sadatnfs/AFModel/blob/5362baf5aa909d9792e0aeef2b9d17c8670841b9/AFModel/LICENSE.md).
- TMB's [DESCRIPTION](https://github.com/kaskr/adcomp/blob/ee2aebea75ccb96ccfb242732165a113cd3ec6d9/TMB/DESCRIPTION)
  declares GPL-2. Installed dependency licenses remain applicable; the
  classroom's top-level license does not replace them.
- PyMB's [LICENSE](https://github.com/kforeman/PyMB/blob/6c70da82bbca9e6ae33cd3349cba89a45de7fc42/LICENSE)
  is GPL-2.0. No implementation source was copied into the classroom.
- `ar.matrix` has no recognized GitHub license badge at the inspected snapshot,
  but its [DESCRIPTION](https://github.com/nmmarquez/ar.matrix/blob/c8f75efb08d5ea926aee5817cce22a940f03efa0/DESCRIPTION)
  explicitly declares GPL greater than or equal to 2.
- No license declaration was found in the inspected TMBstanEX,
  tmb_inla_sim or us_county_forecasting trees. Their inclusion here is limited to
  source links and original conceptual analysis, not vendoring code or data.

The classroom's prose, synthetic data, models and adapters are original. Optional
runtime distribution must retain the actual dependency notices and applicable
source-availability materials. This report is a source-attribution record, not
a claim that the historical projects or installed dependencies share one license.

## What has actually been demonstrated

The evidence below is local native Linux ARM64 evidence from the bounded
fixtures. The supported runtime sources are checked in; final shared release
acceptance remains distinct.

| Surface | Observed result | Limit |
| --- | --- | --- |
| Custom PyTorch course | All 20 programs executed; 24 independent numerical tests passed under Torch 2.9.1 CPU | No Spark, DDP, GPU or scale inference from those tests |
| Public advanced Spark examples | 12 PySpark programs and nine compiled Scala programs executed; 29 focused host tests passed | Spark local[2], tiny fixtures; modeled retry delivery is not injected executor failure |
| Catalyst project | Real compilation, generated/evaluated parity, null/type/arity checks and the intended optimizer rewrite passed | Exact Spark/Scala/JDK combination only |
| Combined Spark/Torch objective | Unequal and empty partition layouts agreed with analytic oracles; caller-owned cache was preserved | Low-dimensional additive objective, immutable-input assumption |
| Nonlinear Spark/Torch fit | Forty rows across partitions 13/13/14; maximum fitted-parameter difference from separate serial objective about 4.49e-8 | A local numerical comparison, not proof of the global optimum or performance |
| TorchDistributor | Actual one-rank and two-rank CPU launches; gradient about -1/6 and one-step parameter about 1/60; six unique IDs retained | `local_mode=True` on one host, no GPU or remote executors |
| Lightning and launch failure handling | Actual two-rank update and six-row coverage; repaired sealed run exits cleanly and rejects a worker exit seven after result serialization | Exact prepared local CPU image; no arbitrary-strategy, remote-cluster or restart qualification |
| Arrow batches | Seventeen IDs preserved under actual batch bounds one and three, with identical transformed values | Small conversion fixture only |
| TMB course | Forty-eight base-R companions, nine compiled native models, five additional C++ family probes and bounded public-API probes recorded in its ledger | Some specialized TMBad, debugger, OSA and normalization surfaces are taught but not fully executed |
| Spark/TMB registered models | Actual local Spark tasks invoked compiled normal and Gaussian random-intercept models; finite-difference/analytic checks and independent fits produced receipts | The reusable registry has bounded payloads and complete-unit assumptions; final combined-project acceptance is recorded separately |
| Rendering | All 38 advanced Spark guides and 205 mathematical expressions passed the actual offline renderer | Not a browser or saved-progress acceptance claim |

The public Spark receipt is
[qualification-public.json](../../courses/advanced-spark-modeling/qualification-public.json).
The PyTorch course retains its [validation ledger](../../courses/custom-likelihood-pytorch/VALIDATION.md),
and the TMB course retains its [qualification ledger](../../courses/tmb-modeling/QUALIFICATION.md).
The combined projects' checks and source-bound logs must be consulted for the
exact revision used. A later source edit does not inherit a previous receipt.
The report does not infer success from earlier failed launcher attempts or from
an image existing locally. The six Spark/TMB cases have actual local receipts;
final source hardening and sealed-image qualification remain a separate gate
at this snapshot.

The shared lesson/catalog admission, prerequisite graph, read-only MCP discovery
and three-track source packaging checks pass. Temporary-state tests also confirm
separate drafts survive reopening without overwriting existing work. Final
integration still needs generated readers and compiled-TeX inventory, actual
browser rendering and Docker saved-state acceptance,
coherent release checks and the separately authorized publication path. Native
AMD64, remote-cluster performance, production fault recovery and GPU execution
are not established by this ARM64 work.

## Suggested reading route and extension choices

For a Spark practitioner new to custom modeling, start with `clp-001` through
`clp-007`, then `asm-001` through `asm-012`. Those chapters establish what the
optimizer is minimizing and which parts can be distributed. Continue through
the public Scala extension chapters before the optional Catalyst project.

For the TMB route, read `tmb-001` through `tmb-009`, then latent-model chapters
`tmb-012` through `tmb-018`, followed by `asm-031` through `asm-035`. Use the
historical AFModel comparison to understand architectural choices, then build
an original model through the prepared registry instead of importing an old
application wholesale. Chapters `tmb-025` through `tmb-040` provide the deeper
API and diagnostic route. Continue through `tmb-041` to `tmb-048` for the C++
model-authoring families and native derivative checks.

For neural or more general Torch customization, follow `asm-026` through
`asm-030` after the serial likelihood route. Choose the additive driver adapter
for small shared parameter vectors and expensive distributed data passes. Choose
a training runtime when replicated large parameter vectors, collective updates
or accelerators justify it. Preserve an explicit data-delivery and epoch
contract in either case.

The next justified extensions would be a qualified real-cluster deployment,
measured repeated-evaluation performance, controlled retry/recovery experiments,
and a specialized coupled solver if a concrete model demands one. These are
new acceptance tasks. The current examples provide the mathematical and runtime
boundaries needed to design them without claiming they are already complete.


## Release qualification for these scientific projects

The full publication workflow now requires a dedicated native scientific gate
after all ordinary workers qualify. It uses same-run immutable Spark/Torch/R/Java
bases on AMD64 and ARM64, with serial project preparation within each architecture.
It retains the primary installed-wheel and training checks, optional Spark/TMB
reference and Scala bridge, and standalone TMB public API/C++ probes. The
[validation guide](../validation.md#standalone-modeling-and-native-scientific-publication)
describes exact receipt and promotion boundaries. Local compiled/library execution
does not mean those hosted jobs or the final release have already completed.

The [Brad Bell and native automatic-differentiation report](brad-bell-autodiff.md)
separately examines CppAD, TMBad and the R-free native experiment. A native AD proof
does not establish full compatibility with TMB's R API, a generic distributed
Laplace engine or a production Spark backend.
