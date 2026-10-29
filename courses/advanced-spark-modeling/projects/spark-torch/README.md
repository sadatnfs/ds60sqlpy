# Custom likelihoods with Spark and PyTorch

This optional project runs Spark 4.0.1, PyTorch 2.9.1 CPU and Lightning 2.6.1
together. The ordinary Spark and Torch coding pads remain separate environments.
The project is a complete local Docker workflow, with prepared dependencies and
offline execution. It uses the same source package as the worked chapters.

## Prepare and run

Start Docker, open a terminal in the repository and prepare the two ordinary
base images if they are not already present:

```bash
./classroom build --profile spark-local-python --profile llm-torch-cpu
cd courses/advanced-spark-modeling/projects/spark-torch
./workshop build
./workshop run additive-logistic
./workshop check
```

Linux, macOS and Windows with WSL 2 use these same Linux containers. Native
Linux AMD64 and ARM64 wheels are pinned; each architecture still requires its
own execution qualification. This project needs approximately 4 GiB of available
container memory, two CPU cores and room for its separate image. No GPU is
required. A successful CPU run does not demonstrate GPU or remote-cluster
support.

The build downloads pinned additional dependencies and packages the checked-in
examples. It never executes an uploaded C++ file or changes classroom volumes.
Run and check use the existing image with no network. They do not rebuild it,
pull another image, install packages or mount the Docker engine socket.
After editing source, run build explicitly to package the revision.

When using already-prepared compatible bases with other local image names,
set `DS60_SPARK_BASE` and `DS60_TORCH_BASE` for build.
These must retain Spark 4.0.1, JDK 17, Python 3.12 and Torch 2.9.1 CPU.
`DS60_SPARK_TORCH_IMAGE` selects the project image name for build
and run. It is not a claim that an arbitrary image is compatible.

Every execution saves a new log beneath `.workshop/spark-torch/`
at the repository root. Container removal preserves these host logs. A log is
an observation of the executed image; rebuilding a newer image does not update
an older result.

## Choose a case

| Case                 | What actually runs                                                       | What the result establishes                                                                  |
| -------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `additive-logistic`  | Spark partition tasks, local Torch derivatives, a driver SciPy optimizer | Weighted global Bernoulli MLE against exact log odds                                         |
| `nonlinear-gaussian` | A custom exponential-decay likelihood with four parameters               | Distributed derivatives and fitted parameters compared with a separate NumPy/SciPy objective |
| `independent-groups` | Arrow/Pandas complete groups and one local fit per group                 | Separate means and variances, with no shared population parameter                            |
| `arrow-batches`      | Actual `mapInPandas` batches containing Torch tensor computation         | Preserved row identities and bounded batch sizes                                             |
| `torch-distributor`  | Spark's TorchDistributor launches two CPU ranks                          | One correct DDP update with unequal shard sizes and exact record coverage                    |
| `lightning-ddp`      | The same launcher runs a two-rank Lightning trainer                      | Correct update and complete nonduplicated sampling for a divisible dataset                   |
| `standalone-package` | An independently built wheel, two real executor import probes, numerical and DataFrame/ML tests | Exact installed/source identity and all 33 ML checks, including complete units and Pipeline persistence |
| `sharding-audit`     | Actual PyTorch sampler construction                                      | How padding duplicates rows and `drop_last` omits them                                       |

The two-process training cases use `local_mode=True`. Spark invokes
Torch's launcher on the driver machine. This is real process coordination and
gradient synchronization, but it is not a multi-node Spark executor deployment.
The launcher maps its fixed container hostname to loopback because rendezvous
must work with the container network disabled.

## Understand the additive objective

For observations \(z_i\), nonnegative weights \(w_i\), parameters
\(\theta\), and normalized negative log-likelihood \(\ell(\theta;z_i)\),
the sum objective is

\[
L(\theta)=\sum_{p=1}^{P}\sum_{i\in I_p}w_i\ell(\theta;z_i)
+\frac{\lambda}{2}\|\theta\|_2^2.
\]

Each Spark partition returns its row count, total weight, objective sum and
gradient sum. The driver checks all partition IDs and exact parameter digests,
then adds the penalty once. With `weighted_mean`, it divides the
data term and data gradient by the global weight sum before applying the
penalty. Averaging partition means would overweight small partitions.
Changing the reduction changes the meaning of the same numerical penalty.

The independent-group case optimizes a different parameter vector for each
group. Averaging those vectors generally does not produce the global MLE.
A covariance structure linking groups, a global latent state or a pairwise
loss across partitions also breaks the simple additive contract.

## Customize a model deliberately

The independent distribution `ds60-spark-likelihood` lives in [packages/spark-likelihood](../../../../packages/spark-likelihood/). Its import namespace is `ds60_spark_likelihood`; historical classroom imports are compatibility aliases. The project builds its pure wheel offline from the checked-in source, installs it before preparing Spark, and never imports a checkout copy.

For whole-group likelihoods and real ML fit/transform, read the package's [DataFrame/ML guide](../../../../packages/spark-likelihood/docs/DATAFRAME-ML.md) and [custom model guide](../../../../packages/spark-likelihood/docs/custom-models.md). They include exact Gaussian group marginals and an original Gamma-Poisson custom model without R.
Importing its contract module does not import Spark, Torch, NumPy or SciPy.

1. Define a deterministic callable `loss(theta, features, targets)`
   that returns one CPU float64 loss per row and retains its autograd graph.
2. Wrap it in `TorchLoss(model_id, parameter_count, feature_count, loss)`.
   Include normalizing terms when estimating scale or comparing likelihoods.
3. Supply an immutable input snapshot. The RDD row contract is features,
   target, then weight. The DataFrame helper selects named numeric columns.
4. Use `SparkObjective` as a context manager. It owns a derived
   cache and releases only that cache. A cache is not a durable snapshot.
5. Compare loss, gradients and fitted results with independent oracles before
   increasing data size. Vary partition counts and batch sizes as well.

The adapter allows at most 64 parameters and 4,096 partition summaries, and
each local batch has at most 8,192 rows. It is designed to teach low-dimensional
additive likelihood optimization. It does not move arbitrary neural-network
gradients to the driver or claim to implement native Catalyst autodiff.

The optimizer reports raw and bound-projected gradients, active bounds,
iteration counts, evaluation counts and convergence status. A successful
status does not prove identifiability, a global optimum, valid confidence
intervals or useful forecasting. Inspect conditioning and parameter boundaries,
use multiple starts when appropriate, and evaluate predictions on genuinely
held-out data.

## Pinned launcher correction

Spark 4.0.1's bundled Torch process wrapper waits for torchrun but does not
propagate its return code. A rank can serialize its result and then fail during
shutdown, leaving an apparently successful outer launch. This project applies
one preparation-time correction in `patch_spark.py`: it verifies the exact
upstream file SHA256, retains the original Apache license header, and propagates
the child exit code. A different upstream source is refused for review.

The check deliberately returns a result and then exits a worker with code 7.
The launch must still fail. Successful numerical outputs alone do not satisfy
this acceptance gate. Lightning's example also explicitly synchronizes and
destroys its process group before the workers exit.

See the [pinned upstream wrapper](https://github.com/apache/spark/blob/v4.0.1/python/pyspark/ml/torch/torch_run_process_wrapper.py).
The correction is local to this prepared workshop image; it does not silently
modify another Spark installation.

## Validation boundaries

The checks compare weighted logistic and normal MLEs with closed forms;
nonlinear gradients with finite differences; nonlinear fitted parameters with
a separate serial objective; and two-rank updates with a hand-derived gradient.
They reject malformed inputs and stale partition results, require empty
partitions to be represented, and check that caller-owned caches survive.

Complete-group Pandas functions require a whole group in memory. A row-count
assertion inside the function cannot prevent an oversized group from exhausting
memory before that assertion. The included fixture has three known small
groups. Production work needs upstream group-size measurement and a policy for
large groups.

Prepared images, passing local checks, native CI results, remote-cluster
acceptance and GPU qualification are separate evidence. Consult the track's
validation ledger for the platforms actually exercised. No performance or
multi-node claim follows from these small numerical examples.

## Primary references

- [Spark 4.0.1 Arrow and Pandas integration](https://spark.apache.org/docs/4.0.1/api/python/tutorial/sql/arrow_pandas.html)
- [Spark 4.0.1 TorchDistributor source](https://github.com/apache/spark/blob/v4.0.1/python/pyspark/ml/torch/distributor.py)
- [PyTorch 2.9 autograd gradients](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad.html)
- [PyTorch distributed data parallel](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html)
- [Lightning 2.6.1 release](https://pypi.org/project/lightning/2.6.1/)

All lesson examples here are original. Installed dependencies retain their own
licenses. The project does not copy implementation code from those references.
