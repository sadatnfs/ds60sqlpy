# Native 0.2 studies: selected priors, exact L1 and honest simulation summaries

This guide starts from linear regression, Gaussian likelihoods, gradients and
basic Spark DataFrames. It shows how to define a selected penalty, fix a known
nuisance parameter, check an analytic answer and interpret a retained study
receipt. Use the separately prepared native package project. These sim-* names
are study-design IDs, not newly registered classroom lessons or ordinary pad jobs.

The initial local Spark smoke passed sim-003 and sim-004 at replication zero,
seed 381729. Each contains weak- and strong-slope data, two methods and two
reductions, giving 16 accepted fits in total. This is one independent generated
dataset per scenario, not sixteen Monte Carlo replications. The retained
[Gaussian-prior receipt](../observed/native020-targets-arm64-v1/sim-003-r0.json),
[L1 receipt](../observed/native020-targets-arm64-v1/sim-004-r0.json) and
[source inventory](../observed/native020-targets-arm64-v1/source-inventory.json)
bind the exact executed inputs. The five additional local shards also completed: 22 method records, 21 accepted
and one beta-binomial optimizer failure retained. The [additional receipts](../observed/native020-families-arm64-v1/README.md)
bind those observations. Across those initial seven shards there are 38 method records,
not 38 independent Monte Carlo datasets.

A later, separately retained expansion now covers sim-003/004 replications 0
through 15. Its [observed aggregate](../observed/native020-targets-arm64-expanded-v1/AGGREGATE.json)
has 16 target/scenario/method/reduction groups, each with 16 independent datasets,
and all 256 fit records accepted. The earlier replication-zero examples below
remain initial-stage history. A separate eight-dataset expansion now covers the
five family/panel/independent-fit studies: 176 method records, 172 accepted and four
optimizer failures retained. Its [independently derived summary](../observed/native020-families-arm64-expanded-v1/aggregate-derived.json)
is separate from the named-target aggregate and remains bound to the older JAR
used by those actual runs. The initial one-replication examples are preserved below.

## Prepare the source and execution environment

Work from an independently copied `packages/spark-tmbad/` directory inside its
prepared Linux environment. Follow [native preparation](../../docs/PREPARATION.md)
to obtain the matching 0.2.0 Python wheel, native executable, manifest and JVM
adapter before running a study. Install the wheel noneditably. Do not put
`python/src` on PYTHONPATH for actual Spark acceptance. No study installs packages,
downloads inputs or compiles a model while fitting.

The observed environment was Linux ARM64, Python 3.12.12, Java 17.0.21 and Spark
4.0.1 with `local[2]`. It used native build
`5d3cfec94ba65f7c39711f109b09dc3ec6883bcb062e68cecb50345434a35383` and JVM SHA256
`4bc78a3be973d8e3e62eea12df2bf1e2410299b7bf39144b2f75257958814b8c`.
The complete identities are in each receipt. Another binary, JAR, fixture or
study-source revision needs its own observation. This run does not qualify
multi-host execution, managed cloud services, generic posterior inference or
the separately scheduled Torch expansion.

The maintained files are:

| Source | Role |
| --- | --- |
| [generate_extended_fixtures.py](../generate_extended_fixtures.py) | Keyed original data, explicit training/future splits and known mechanisms |
| [extended_support.py](../extended_support.py) | Independent target, density and conditional-moment calculations |
| [run_native_extended.py](../run_native_extended.py) | One bounded actual native/Spark study and replication |
| [aggregate_extended.py](../aggregate_extended.py) | Identity checks, failure accounting and dataset-level summaries |
| [native020-smoke.json](../fixtures/native020-smoke.json) | Retained fixture bundle, separate from the older smoke fixtures |

The checked fixture SHA256 is
`858a9d44b062a20dbb9df8841588d5f68c9ba9aabd27dc76cc01f98a3cdeeeb9`.
The source inventory includes the generator, helper and original shared support
hashes. New fixture generation uses a fresh path:

```sh
python3 studies/generate_extended_fixtures.py \
  --seed 381729 --replicates 2 --output /out/native020-new-fixtures.json
```

The generator bounds the bundle to 4 MiB. Replicates, covariates, observation
noise and future outcomes have explicit keys. Methods share the same retained
data. Future responses are stored only for scoring; the prediction DataFrames
contain IDs and the required future covariates, never those responses.

## The likelihood and the two reductions

Both worked studies generate 32 independent training observations and 24 future
observations from

\[
Y_i=2+b x_i+\epsilon_i,\qquad \epsilon_i\sim N(0,1),
\qquad x_i\in\{-1,1\},\quad \sum_i x_i=0,\quad \sum_i x_i^2=n=32.
\]

The weak scenario uses \(b=0.15\); the strong scenario uses \(b=1.2\).
The prepared vector is \((\beta_0,\beta_1,\log\sigma)\). We fix
`log_sigma` to zero, so the known noise standard deviation is one, and leave
the intercept unpenalized. This is a two-column design \([1,x]\). The older
four-column orthogonal calculation in run_reference.py remains a separate serial
reference; the native one-covariate descriptor has not gained extra columns.

Let \(S\) be the summed normalized data negative log likelihood, \(P\) the
selected Gaussian prior negative log density and \(Q\) the selected L1 penalty.
The named target is

\[
J(\theta)=\frac{S(\theta)+P(\theta)+Q(\theta)}{d},
\qquad d=1\text{ for sum},\quad d=W\text{ for weighted mean}.
\]

All rows here have weight one, so \(W=32\). Dividing every term preserves
the optimum; only the objective's units change. This differs from legacy
`l2_strength`, which adds an all-coordinate penalty after reduction. Nonzero
legacy L2 cannot be mixed with the named regularization block. Arbitrary weights
would require a stated weighted/power-likelihood interpretation.

## Worked study 1: a Gaussian prior centered away from zero

sim-003 compares the unpenalized likelihood with a prior
\(\beta_1\sim N(m,1/\lambda)\), where \(m=0.2\) and \(\lambda=8\).
Omit the intercept and scale from the named Gaussian block:

```python
regularization = {
    "schema_version": 1,
    "coordinate_system": "native_optimizer_parameters",
    "normalization": "summed_likelihood_target",
    "gaussian": {"beta1": {"mean": 0.2, "precision": 8.0}},
    "l1": {},
}
options = {
    "initial_parameters": [0.0, 0.0, 0.0],
    "fixed_parameters": {"log_sigma": 0.0},
    "regularization": regularization,
    "reduction": "sum",
    "max_iterations": 200,
    "gradient_tolerance": 1e-6,
    "function_tolerance": 0.0,
}
```

For this orthogonal known-scale design, the independent answer is

\[
\widehat\beta_0=\bar y,\qquad
\widehat\beta_{1,\mathrm{MLE}}=\frac{\sum_i x_i y_i}{n},\qquad
\widehat\beta_{1,\mathrm{MAP}}
=\frac{\sum_i x_i y_i+\lambda m}{n+\lambda}.
\]

Observed replication-zero values, rounded here but retained at full precision in
the receipt, are:

| Scenario | True slope | MLE slope | Named-Gaussian slope | MLE future MSE | Named-Gaussian future MSE |
| --- | --- | --- | --- | --- | --- |
| Weak | 0.15 | 0.199161687 | 0.199329350 | 0.517463653 | 0.517508750 |
| Strong | 1.2 | 1.342937153 | 1.114349722 | 0.780893159 | 0.782584375 |

In the weak case, the MLE is already close to the prior center. The prior moves
the slope slightly upward toward 0.2. In the strong case it pulls the slope
substantially downward. A nonzero-center prior does not always shrink toward
zero. The intercept estimates are approximately 1.886114538 and 2.295391334,
respectively, and are unchanged by the analytic selected-slope penalty.

The normalized Gaussian contribution is

\[
P(\beta_1)=\frac{\lambda}{2}(\beta_1-m)^2
+\frac12\log\!\left(\frac{2\pi}{\lambda}\right).
\]

Here the constant is -0.1207822376352452. It changes the reported objective even
though it changes neither the optimizer nor the score. The weak-case summed
objective is 55.4022570742 without a prior and 55.2814770855 with the named prior.
The latter being smaller is not evidence of improved prediction: its held-out
MSE is slightly larger in this one dataset. Compare methods with the same
held-out density and observations, not unlike penalized training objectives.

The actual named-Gaussian summed stationarity residuals were approximately
\(3.61\times10^{-8}\) and \(5.37\times10^{-9}\), within the declared
\(10^{-6}\) criterion. Both sum and weighted_mean matched the analytic
parameters within the predeclared comparison tolerance. This is MAP in the
native optimizer coordinates; no parameter posterior was sampled.

## Worked study 2: exact selected L1 and its KKT condition

sim-004 keeps the same two datasets and fixes the same noise scale, but uses
\(Q(\beta_1)=4|\beta_1|\). The intercept remains unpenalized. Its exact
solution is soft thresholding:

\[
\widehat\beta_1
=\operatorname{sign}(\widehat\beta_{1,\mathrm{MLE}})
\max\left\{|\widehat\beta_{1,\mathrm{MLE}}|-\frac4{32},0\right\}.
\]

The threshold is 0.125. The native options select a genuine proximal solver:

```python
regularization = {
    "schema_version": 1,
    "coordinate_system": "native_optimizer_parameters",
    "normalization": "summed_likelihood_target",
    "gaussian": {},
    "l1": {"beta1": 4.0},
}
solver = {
    "method": "proximal_gradient",
    "initial_step": 1.0 / 32.0,
    "kkt_tolerance": 1e-6,
}
```

For weighted_mean the study uses initial_step=1 because the smooth curvature
has also been divided by 32. The KKT tolerance remains in summed-target units.
The public API rejects explicit BFGS with a nonempty L1 block.

| Scenario | MLE slope | Exact/native L1 slope | L1 future MSE | L1 mean future NLL |
| --- | --- | --- | --- | --- |
| Weak | 0.199161687 | 0.074161687 | 0.499487631 | 1.168682349 |
| Strong | 1.342937153 | 1.217937153 | 0.768869549 | 1.303373308 |

Neither observed L1 slope is zero: both sample MLEs exceed the threshold. Exact
zeros require a sample slope at or below that threshold, not merely a small
generating slope. A separate pure analytic case checks that zero branch; it is
not reported as another executed Spark dataset here.

At a positive fitted slope the smooth score is -4, canceled by the L1
subgradient +4. At a zero slope the smooth score must lie within \([-4,4]\).
Use `target.stationarity`, not the raw gradient norm, to judge the fit. The
observed summed KKT residuals were about \(1.33\times10^{-14}\) and
\(7.11\times10^{-15}\). The fixed scale's raw score need not vanish because
that coordinate is not being estimated.

The weak-case summed objective is 55.9489038222, while weighted_mean reports
1.74840324444. The fitted vector is the same. Replacing L1 by a smoothed absolute
value or reusing a smooth gradient stopping rule would change this contract.
The improved held-out MSEs in these two realized cases are observations, not a
general superiority claim or a reason to select the penalty using this holdout.

## Mathematical expected risk versus one observed holdout

The one-replication improvements above need not persist on new data. Under the
stated orthogonal known-variance generator, the slope MLE has expected squared
error (1/32=0.03125). The selected Gaussian estimator has

\[
\operatorname{MSE}(\widehat\beta_{1,\mathrm{MAP}})
=\frac{n}{(n+\lambda)^2}
+\left\{\frac{\lambda(m-b)}{n+\lambda}\right\}^2.
\]

With n=32, precision 8 and center 0.2, this gives 0.0201 for the weak true slope
0.15 and 0.06 for the strong true slope 1.2. The variance reduction helps when
the center is appropriate; prior bias dominates in the strong scenario. These
are analytic repeated-sampling predictions under the stated model, not observed
Monte Carlo results or extra native fits. They explain why one favorable
realization is insufficient for an estimator comparison.

## Expanded named-target evidence: sixteen independent datasets

The expansion adds thirty new shards, sim-003 and sim-004 at replications 1..15,
and reuses the two unchanged replication-zero receipts. It does not rerun or
relabel the original stage. All 32 canonical raw-receipt hashes match the aggregate
input ledger. Training and future hashes each have sixteen distinct values within
every study/scenario; the two studies intentionally reuse matching datasets for
their method contrasts. There are 32 distinct physical training datasets across
the two scenarios, not 256 independent datasets. The
[verified identity record](../observed/native020-targets-arm64-expanded-v1/identity.json)
records these checks, and the aggregate was recomputed exactly from the raw shards.

The expanded fixture has SHA256
`cb2af656c05d58403aaa4d711ea4701cac936e5ea138cb1080a125345867ab7e`.
It was generated by the same frozen source and contains more replication indices
than the original smoke bundle. The source, prepared native/JVM artifact, installed
package and local ARM64 Spark environment match the retained identities. The
[source inventory](../observed/native020-targets-arm64-expanded-v1/source-inventory.json)
keeps that distinction explicit. This is actual local repeated-dataset execution,
not a hosted, cloud, multi-host or posterior-sampling result.

### Parameter risk, with its Monte Carlo uncertainty

The table uses summed-target results; weighted_mean fits represent the same
statistical target and do not add independent replications. Each observed slope
MSE is the average squared estimation error across sixteen independently generated
datasets. Its MCSE is the sample standard deviation of those squared errors divided
by four. The duplicated unpenalized baseline is shown only once per scenario.

| True-slope scenario | Method | Analytic expected slope MSE | Observed slope MSE | MCSE of observed MSE |
| --- | --- | --- | --- | --- |
| Weak, 0.15 | Unpenalized | 0.031250 | 0.032579 | 0.012018 |
| Weak, 0.15 | Selected Gaussian | 0.020100 | 0.020796 | 0.007620 |
| Weak, 0.15 | Selected L1 | 0.018843 | 0.020684 | 0.005148 |
| Strong, 1.2 | Unpenalized | 0.031250 | 0.033071 | 0.008876 |
| Strong, 1.2 | Selected Gaussian | 0.060000 | 0.065843 | 0.018081 |
| Strong, 1.2 | Selected L1 | 0.046875 | 0.052350 | 0.017365 |

The [analytic reference](../observed/native020-targets-arm64-expanded-v1/analytic-risk-reference.json)
uses the exact Gaussian sampling law of the OLS slope and truncated-normal moments
of soft thresholding. Its L1 values have a separately retained
[host quadrature crosscheck](../observed/native020-targets-arm64-expanded-v1/analytic-risk-crosscheck.json).
These files are mathematical reference calculations, not more native observations
or empirical Monte Carlo estimates. The observed risk values broadly follow the
expected weak-slope variance reduction and strong-slope shrinkage bias, with
substantial Monte Carlo uncertainty at sixteen datasets.

For example, the strong-slope Gaussian estimate has observed bias -0.211694 with
MCSE 0.037442, compared with analytic bias -0.2. This repeated-data result is more
informative than its favorable slope error in the single initial dataset. It
still does not prove a general ranking across other truths, prior centers,
collinearity, noise scales or tuning rules.

Because methods share data, uncertainty in a comparison uses paired dataset loss
differences. The [derived paired-risk summary](../observed/native020-targets-arm64-expanded-v1/paired-risk.json)
retains those comparisons without refitting:

| Scenario | Selected method minus unpenalized slope squared error | Mean paired difference | MCSE |
| --- | --- | --- | --- |
| Weak | Gaussian prior | -0.011783 | 0.004494 |
| Weak | L1 | -0.011895 | 0.008106 |
| Strong | Gaussian prior | 0.032772 | 0.013962 |
| Strong | L1 | 0.019279 | 0.011701 |

These MCSEs are computed from sixteen paired differences. They must not be replaced
by an independence calculation using the two methods' marginal MCSEs.

### Exact zeros, coverage and observed failures

The expanded L1 fits set the weak-slope coefficient exactly to zero in 7 of 16
datasets and the strong-slope coefficient to zero in none. The analytic weak-slope
zero probability is approximately 0.383871. The observed fraction 0.4375 is a
small-sample realization, not a precise calibration statement. The earlier
replication-zero claim that neither slope was zero remains correct for that stage.

Gaussian pointwise coverage is first averaged over each dataset's 24 future rows,
then summarized across sixteen datasets. For example, the weak-slope L1 procedure
has observed coverage 0.953125 with MCSE 0.009973; the strong-slope Gaussian-prior
procedure has coverage 0.932292 with MCSE 0.016081. These are observation-band
coverage summaries at plug-in population estimates, not parameter-posterior
coverage or simultaneous path guarantees. Sixteen datasets do not establish
nominal 95% coverage.

All sixteen attempts succeeded in each target/scenario/method/reduction group.
The reported failure-fraction point estimate is zero, but its Wilson 95% upper
bound is approximately 0.193608. Do not pool the 256 correlated method/reduction
records as if they were independent trials of one procedure.

### Reproduce the expanded source route deliberately

Generate a separate bounded fixture from the frozen source, then choose each
study/replication shard explicitly. This example selects only one new shard:

```sh
python3 studies/generate_extended_fixtures.py --seed 381729 --replicates 16 \
  --output /out/native020-sixteen-fixtures.json
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  studies/run_native_extended.py --manifest /opt/spark-tmbad/artifact.json \
  --fixtures /out/native020-sixteen-fixtures.json \
  --study sim-003 --replicate 1 --partitions 2 --output /out/sim-003-r1-new.json
```

The public expanded folder keeps the bounded aggregate, verified input identities
and source inventory, rather than duplicating every raw trace. Complete raw shards
remain in the retained run evidence. A fresh expansion needs its own source/input
identities and failure ledger; it does not overwrite either observed stage.

## Run and inspect the two qualified shards

From the copied package root, use fresh output filenames:

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  studies/run_native_extended.py --manifest /opt/spark-tmbad/artifact.json \
  --fixtures studies/fixtures/native020-smoke.json \
  --study sim-003 --replicate 0 --partitions 2 --output /out/sim-003-r0-new.json

spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  studies/run_native_extended.py --manifest /opt/spark-tmbad/artifact.json \
  --fixtures studies/fixtures/native020-smoke.json \
  --study sim-004 --replicate 0 --partitions 2 --output /out/sim-004-r0-new.json
```

Each command checks installed source and prepared artifacts, fits the planned
methods, evaluates each fitted point publicly, compares the independent target,
and predicts only the requested future rows. Its declared truth baseline uses
PreparedParameters with generator, seed and fixture provenance. Truth parameters
are not saved as a converged fit. On this holdout, known-truth MSEs were
0.507969397 and 0.792523627; finite-sample noise can make a fitted predictor's
realized error lower than truth's error without invalidating the generating model.

The receipt's `status="completed"` means all planned methods were attempted;
inspect every record's status. Unconverged fits remain failed outcomes.
Unclassified execution or artifact errors interrupt the shard and preserve its
incremental receipt. A source or data change is a new experiment, not permission
to rewrite an old receipt.

## Summaries, failures and Monte Carlo uncertainty

The initial two named-target smoke receipts can be summarized without refitting:

```sh
python3 studies/aggregate_extended.py \
  --reports studies/observed/native020-targets-arm64-v1/sim-003-r0.json \
  studies/observed/native020-targets-arm64-v1/sim-004-r0.json \
  --output /out/named-targets-one-replication-summary.json
```

That initial-stage command produces sixteen target/scenario/method/reduction groups, each with exactly one
attempted and successful replication. Bias, MSE and predictive means can be
described, but their sample-SD-based MCSE is `null`, not zero. Reductions, methods
and the two studies deliberately reuse data; they do not multiply the independent
replication count. One observed success also cannot establish a zero failure
probability; the failure summary retains its finite-sample interval.

For \(R\) independent generated datasets and dataset summaries \(q_r\),
the Monte Carlo standard error of their mean is

\[
\operatorname{MCSE}(\bar q)=s_q/\sqrt R.
\]

The aggregator refuses repeated training or future bytes under new replicate or
seed labels within a study/scenario. Generating new posterior draws for one fixed
dataset does not create repeated-data estimator evidence. It also refuses changed
targets, artifacts, source or incomplete method coverage. Large runs require a
predeclared replication count and an explicit resource plan; they are not started
by these documentation commands.

Conditional estimates use successful replications. Procedural coverage includes
all attempted replications, assigning zero coverage when no interval is returned.
If every fit fails, conditional coverage has count zero and a null mean; procedural
coverage is still zero over the attempted denominator. Gaussian pointwise bands
and the event that every band along a requested path covers are separate metrics.
The latter is not a calibrated simultaneous 95% band.

For independent-group fitting, distinguish a dataset-level procedure failure
from an individual group-fit failure. Two datasets with one failed group among
four each have two failed complete procedures but only two failed fits out of
eight. `replication_failure_fraction`, `group_fit_counts` and
`group_failure_fraction_per_dataset` preserve that distinction. Group-failure
MCSE is calculated across independent datasets, not by assuming every group or
overlapping horizon supplies an independent Monte Carlo replication.

## Observed family, panel and independent-fit smoke

The remaining local ARM64 Spark shards used the same generator, helper, driver,
artifact and fixture identities as the named-target runs. Their separate
[source inventory](../observed/native020-families-arm64-v1/source-inventory.json)
and unchanged receipts preserve the actual successful and failed outcomes:

| Study and receipt | Accepted method records / attempted | Executed scope and remaining limit |
| --- | --- | --- |
| [sim-009](../observed/native020-families-arm64-v1/sim-009-r0.json) | 4 / 4 | Pooled versus independent normal fits, equal/heterogeneous means. All eight individual group fits passed. Small-group/boundary-variance contrasts remain pending. |
| [sim-020](../observed/native020-families-arm64-v1/sim-020-r0.json) | 6 / 6 | Poisson, ZIP and hurdle fits on ordinary/structural-zero data, with model-correct log scores. This is a Poisson subset of broader composition studies. |
| [sim-022](../observed/native020-families-arm64-v1/sim-022-r0.json) | 3 / 4 | Binomial/beta-binomial contrasts. Beta-binomial on binomial truth failed its optimizer gate and has no fitted prediction result. COM-binomial remains unimplemented. |
| [sim-024](../observed/native020-families-arm64-v1/sim-024-r0.json) | 4 / 4 | Gaussian/fixed-df Student-t fits on Gaussian/contaminated data. Broader Gamma/lognormal/skewness studies remain separate. |
| [sim-028](../observed/native020-families-arm64-v1/sim-028-r0.json) | 4 / 4 | Complete-group correlated Gaussian fits and existing/unseen-group forecasts, with known/estimated covariance. No generic covariance-formula claim follows. |

A method record can contain several independent group fits. The table therefore
counts method records, while the grouped receipt also reports the individual
fits. In that initial smoke stage these scenarios have replication zero only,
so their conditional scalar MCSE values are null. The failed beta-binomial
method/scenario has no successful estimate or held-out metric to average; its
conditional count is zero. The expanded stage below adds separately retained
datasets and its own failure denominators without rewriting this first stage.

### Pooling changes the target, not just the execution layout

Under equal generating group means, the pooled and independent procedures had
future MSE 1.137802294 and 1.234874838. Under heterogeneous means, those values
were 4.568573648 and 1.356767232. Separate group vectors can describe this second
mean structure, whereas one pooled vector cannot. Both are row-model fits; the
independent route does not introduce random-effect integration or shrinkage.
All four group models per scenario stayed on Spark. The small requested future
outputs and aggregate group diagnostics were the only results collected.

These realized comparisons do not establish repeated-sampling dominance.
Each group has sixteen training rows in this smoke, so the broader sim-009
question about small samples and boundary variance estimates is still open.

### Structural zeros and overdispersion need their own densities

For ordinary Poisson truth, the mean held-out NLL was 1.507226371 for Poisson,
1.507229699 for ZIP and 1.594566174 for the hurdle model. Under structural-zero
truth, it was 1.196595033, 1.126995988 and 1.190710909, respectively. Each score
uses its fitted normalized probability mass, including the hurdle's positive-count
normalizer. The ZIP zero predictor and its exposure/count predictor play different
roles. A hurdle with a zero predictor using z alone need not reproduce the ZIP
zero probability, which also depends on x and exposure.

On beta-binomial truth, binomial and beta-binomial mean held-out NLLs were
3.547296613 and 2.403307362, while their MSEs were 9.789324578 and 9.881705902.
The distributional score and mean-prediction error answer different questions.
A model can describe dispersion better without winning the realized mean MSE.
Neither calculation uses a Gaussian surrogate density.

The other beta-binomial fit is a concrete failure case. On binomial truth it
returned `line_search_failed`, with log_precision at its upper bound 6 and
projected score (1.759224406983062\times10^{-6}), above the unchanged
(10^{-6}) criterion. It remains failed, despite a finite objective and despite
separate numerical/API qualification of the family. No fitted prediction, future
MSE or success label was generated for it. The binomial is a limiting case as
beta-binomial precision tends to infinity; that fact does not prove the specific
cause of the recorded line-search failure or authorize relaxing its gate.

### Robustness and conditional covariance have visible limits

For Gaussian truth, Gaussian and fixed-df Student-t future MSEs were 1.178288086
and 1.196296638. Under symmetric contamination they were 1.214218356 and
1.183492073; corresponding mean NLLs were 1.651899063 and 1.506801701. The
contamination DGP is a Gaussian scale mixture, not exactly Student-t. Degrees
of freedom were fixed to five, scale was estimated, and Student-t scale was not
misreported as its standard deviation. Gaussian bands are labeled only for the
Gaussian fit; no Gaussian coverage label is attached to the Student-t result.

For positive latent correlation, known- and estimated-covariance fits gave
existing-group future MSEs 0.312005435 and 0.258540927. For negative correlation,
the values were 0.375547728 and 0.363048237. These forecasts condition on each
observed group's complete available history. Separate unseen-group forecasts
integrate the latent prior and were checked for both methods and both scenarios.
Their rows do not borrow unseen training responses.

The positive-correlation estimated-covariance fit reached the upper bound
atanh_correlation=4. It passed the constrained optimizer criterion, but eight
training groups do not establish accurate covariance estimation. Its existing-
group pointwise coverage was 0.75 across sixteen requested future rows; that
small conditional observation is not a Monte Carlo coverage guarantee. Public
outputs remain marginal moments. They do not provide the reference's full joint
covariance, forecast covariates or include population-parameter uncertainty.

To select another already prepared study, use its ID in the same command:

```sh
spark-submit --master 'local[2]' --jars /opt/spark-tmbad/spark-tmbad.jar \
  studies/run_native_extended.py --manifest /opt/spark-tmbad/artifact.json \
  --fixtures studies/fixtures/native020-smoke.json \
  --study sim-022 --replicate 0 --partitions 2 --output /out/sim-022-r0-new.json
```

That command may complete with a failed fit retained. Completion and universal
convergence are different fields. Use the exact receipt and declared criteria;
do not tune a failed attempt into a retroactive pass.

The optional R project has its own [qualified scope](../../reference/QUALIFICATION.md).
It does not establish native/Torch parity or turn these studies into
posterior-sampling experiments.

## Expanded family studies: eight datasets and four retained failures

Thirty-five new shards add replications 1..7 to the five preserved initial shards.
The [public summary](../observed/native020-families-arm64-expanded-v1/aggregate-derived.json)
is an independent derivation from those forty unchanged actual runtime receipts,
using the frozen aggregate_extended.py and study_support.py implementations.
It is not another fit or a rerun. The
[identity verification](../observed/native020-families-arm64-expanded-v1/identity.json)
binds every raw receipt and dataset hash; all training and future hashes are
unique across the eight replication indices within each study/scenario. Recomputing
this derived summary reproduces it exactly.

The full aggregate SHA256 is
`8b703f6bde9a4e708069b31afa78c88e0d47a2e6f19a829a0144a45b3f3ab9fa`.
The [source inventory](../observed/native020-families-arm64-expanded-v1/source-inventory.json)
and artifact metadata retain JVM SHA256
`4bc78a3be973d8e3e62eea12df2bf1e2410299b7bf39144b2f75257958814b8c`.
These are observations of that earlier JAR. They do not qualify a later proximal
implementation, migrate saved models to another artifact or reclassify any failed
attempt. The environment was the retained Linux ARM64 Spark 4.0.1 local[2] setup;
no distributed-scale, hosted or cloud acceptance is inferred.

| Study | Accepted method records / attempted | Additional accounting |
| --- | --- | --- |
| sim-009 | 32 / 32 | All 64 individual normal-group fits accepted, 32 per mean scenario |
| sim-020 | 47 / 48 | One ZIP fit on ordinary Poisson data failed |
| sim-022 | 30 / 32 | Two beta-binomial fits on binomial data failed |
| sim-024 | 31 / 32 | One Gaussian fit on contaminated data failed |
| sim-028 | 32 / 32 | Known/estimated covariance and existing/unseen-group forecasts retained |
| Total | 172 / 176 | 22 target/scenario/method groups, eight attempted datasets per group |

Method records containing independent fits are complete procedures, not individual
group models. The grouped records retain successful/attempted group counts on
Spark. Dataset-level MCSE uses eight generated datasets per scenario; it does not
use 64 fitted groups or all 176 method records as interchangeable replications.
The original small-group/boundary-variance, broader family and covariance
contrasts remain unfinished even though these chosen contrasts now have repeated
local execution.

### Failures are part of the result

The [derived failed-method ledger](../observed/native020-families-arm64-expanded-v1/failed-methods.json)
records the exact unchanged outcomes:

| Study and scenario | Method | Replication | Optimizer status | Projected score |
| --- | --- | --- | --- | --- |
| sim-020, poisson_truth | zero_inflated | 2 | function_stalled_without_stationarity | 2.230311471e-6 |
| sim-022, binomial_truth | beta_binomial | 0 | line_search_failed | 1.759224407e-6 |
| sim-022, binomial_truth | beta_binomial | 3 | line_search_failed | 1.858423142e-6 |
| sim-024, symmetric_contamination | gaussian | 7 | function_stalled_without_stationarity | 1.235516544e-6 |

Each score remains above the unchanged 1e-6 requirement. A small residual above a
threshold is still a failed criterion. Each failed record retains its parameters,
objective, identity and diagnostics, but has no fitted prediction or held-out
metric. No seed was replaced, no tolerance was relaxed and no historical result
was overwritten to make this stage all-pass. A later implementation needs its
own separately identified observations.

### Conditional scores need their actual successful denominator

The following normalized log scores and MCSEs are conditional on the method
returning an accepted fit. Different successful counts are scientifically relevant:

| Generating scenario | Method | Successful / attempted | Mean held-out NLL | Dataset-level MCSE |
| --- | --- | --- | --- | --- |
| Poisson | Poisson | 8 / 8 | 1.501146 | 0.037611 |
| Poisson | ZIP | 7 / 8 | 1.503183 | 0.042993 |
| Binomial | Binomial | 8 / 8 | 1.834724 | 0.045288 |
| Binomial | Beta-binomial | 6 / 8 | 1.833182 | 0.049411 |
| Beta-binomial | Binomial | 8 / 8 | 2.937885 | 0.147158 |
| Beta-binomial | Beta-binomial | 8 / 8 | 2.312559 | 0.021155 |
| Symmetric contamination | Gaussian | 7 / 8 | 2.074600 | 0.170646 |
| Symmetric contamination | Student-t, df=5 | 8 / 8 | 1.759428 | 0.149930 |

These are each model's proper density scores, not Gaussian substitutes for count
or Student-t distributions. Subtracting two conditional means with different
successful datasets is not a paired comparison. A paired analysis would use their
matched successful intersection and still report the complete failure ledger.
No failed log score is silently replaced by zero.

Under beta-binomial truth, the two models have similar mean squared prediction
errors, 7.539655 for binomial and 7.510378 for beta-binomial, with MCSEs 0.677242
and 0.672133. Their log scores differ more because they describe dispersion
differently. That bounded observation concerns this generating mechanism, not
universal model superiority or calibrated uncertainty.

### Procedure failure changes reported coverage

For the Gaussian fit under contamination, successful-fit pointwise coverage is
0.958333 across seven datasets, with MCSE 0.024056. Procedural coverage over all
eight attempted datasets is 0.838542 with MCSE 0.121590, because the failed fit
returns no interval and contributes zero procedural coverage. Dropping that
attempt would conceal the difference between a conditional interval calculation
and a usable complete procedure. Student-t results still have no falsely labeled
Gaussian-band coverage field.

For equal-mean normal groups, pooled and independent procedures have observed
future MSEs 1.064102 and 1.064476, with MCSEs 0.076359 and 0.069682. Under
heterogeneous means, the respective values are 3.626730 and 0.968553, with MCSEs
0.247464 and 0.125936. This changes the mean structure being fitted; it is not
merely a partitioning optimization. Coverage alone cannot rank these predictions:
a misspecified pooled normal can absorb mean heterogeneity into its fitted scale.

All individual group fits in this stage succeeded. That means zero observed
group failures, not proof that failure is impossible. Per-procedure zero failures
among eight datasets still have a Wilson 95% upper bound of approximately 0.3244.
Do not pool correlated method/group outcomes to manufacture a much smaller
uncertainty claim.

### Conditional panel forecasts remain different from unseen-group forecasts

For negative latent correlation, the known-covariance method has existing-group
future MSE 0.243318 with MCSE 0.028852; estimating covariance gives 0.275155 with
MCSE 0.026692. For positive correlation those values are 0.242003 and 0.245369,
with MCSEs 0.023283 and 0.024531. The initial dataset's ordering need not persist
across the additional draws.

Unseen groups are scored separately, integrating a newly drawn latent effect
rather than reusing an observed group's history. Under positive correlation,
the unseen-group MSE is about 1.420350 with MCSE 0.662373 for this balanced design.
That large uncertainty is visible rather than hidden by the successful optimizer
statuses. Eight datasets do not establish nominal coverage, accurate covariance
recovery or a universal preference for estimating versus fixing covariance.
Returned pointwise moments still omit population-parameter uncertainty and do
not constitute a full joint predictive distribution.

The public folder keeps bounded aggregate and identity/failure summaries; it does
not duplicate every raw fit trace. The preserved initial receipts and all later
raw shards remain distinct evidence. Use the existing explicit study/replication
commands for any new work, with a fresh artifact/input identity and output path.

## Diagnose the common mistakes

- A lower named-Gaussian training objective may reflect its normalizing constant.
  Compare common held-out scores and inspect the data/prior components.
- A large raw score on a fixed nuisance coordinate is not evidence that the free
  coefficients failed to converge. Inspect the constrained target residual.
- A nonzero smooth score can be exactly correct at an L1 optimum. Check its
  subgradient cancellation and summed-target KKT units.
- Reusing the same rows with a new seed label does not add estimator replications.
  Preserve the dataset hashes and report the actual simulation unit.
- A pointwise variance is not a joint predictive covariance or a posterior
  distribution over the population parameters.

The next bounded step is a predeclared extension of a remaining study contrast,
using separately retained source, inputs and criteria. The named-target sixteen-
dataset expansion and the family eight-dataset stage do not complete broader
study contrasts or establish general calibration. Broader
collinearity/tuning, small-group failures, posterior inference, large Monte Carlo
calibration and classroom admission remain explicit later work.
