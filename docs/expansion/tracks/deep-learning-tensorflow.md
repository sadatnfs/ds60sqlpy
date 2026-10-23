# Design: deep learning with TensorFlow and Keras

Status: **planned**, checked against active catalog baseline `75ec445` on
**2026-10-22**. This document and its [structured plan](../plans/deep-learning-tensorflow.json)
are a review proposal. They add no active lesson, runtime adapter, dependency,
model download, image build or completion record. The active catalog remains
168 lessons. The [pilot](../samples/deep-learning-tensorflow-pilot.md) is a full
teaching sample, not a registered course artifact.

## North star and the gap being closed

A learner should be able to explain a network computation, inspect the update
that changes its parameters, and defend the evidence behind a small model
release. A high-level training call must not hide a malformed target, a missing
gradient or a reused test set.

The existing Python course contains an overview (`python-46`), a PyTorch loop
(`python-47`), CNN transfer learning (`python-48`) and broad model evaluation.
It does not provide a progressive TensorFlow/Keras path through tape semantics,
Keras 3 state/export behavior, training-only preprocessing, mask propagation,
checkpoint continuation and a release decision. These are the reasons for the
36 units below. There is no target of sixty for its own sake.

## Entry, placement and reuse

The hard entry prerequisite is active `python-16`: its prerequisite chain
already supplies Python syntax, functions, files, tests and NumPy arrays. The
new track teaches its required derivative and tensor reasoning explicitly;
prior calculus, GPU experience and PyTorch are not assumed.

Use a short placement interview: trace a `(3,)` versus `(3,1)` subtraction,
explain a mean's denominator and run a small NumPy assertion from a fresh
process. A learner missing these skills returns to `python-16` or the applicable
beginner on-ramp. A learner who already knows them still predicts the shape
failure before continuing.

Reuse active material as targeted retrieval rather than copying whole lessons:
`python-31` for probability, `python-32` and `python-stats-01` for inference and
resampling, `python-33` for matrix vocabulary, `python-35` and `python-ml-02`
for evaluation/leakage, and `python-ml-01` for reproducible delivery. These are
explicit review links, not hidden hard prerequisites or claims of completion.
The legacy catalog has a broad transitive chain, including a geospatial unit;
forcing that whole chain before the first gradient experiment would obscure
the entry goal. Promotion to an active track must review that prerequisite
policy with the planner, not silently waive any active ID.

## Framework, platform and resource decisions

As of **2026-10-22**, the proposed modern reference is **Python 3.12,
TensorFlow 2.21.0 and Keras 3 APIs with the TensorFlow backend**. The official
[tested-build table](https://www.tensorflow.org/install/source) lists Python
3.10-3.13 for TensorFlow 2.21.0. That source-build table is evidence of an API
and interpreter target; it is not evidence that we installed every platform
wheel. Keras documents that TensorFlow 2.16 onward uses Keras 3 by default.
Use `tf.keras` consistently in this track. Legacy `tf_keras`, JAX and a second
backend are outside its required path. Exact compatible Keras/NumPy patches
must be locked with TensorFlow during implementation.

The [official installation guide](https://www.tensorflow.org/install/pip)
documents these important differences:

| Platform | Proposed default | Implementation gate |
| --- | --- | --- |
| Windows x86-64 | Native CPU is sufficient; WSL 2 Linux is an alternative | Verify the exact CPU wheel/profile and a clean first run. TensorFlow 2.10 was the last native-Windows GPU release; this course does not send beginners to that old GPU stack. |
| macOS arm64 | CPU on a supported macOS version | Verify the exact Python 3.12 wheel and small gradients; no Metal/GPU plugin is required. |
| macOS Intel | Separate legacy CPU compatibility lane, or an explicitly prepared supported Linux CPU environment | The official guide identifies TensorFlow 2.16 as the last macOS x86 line and lists a 2.16.2 Python 3.12 wheel. Do not claim the modern 2.21 profile runs natively here. The legacy lane needs its own lock and API/parity checks. |
| Linux x86-64 | CPU-only environment | Verify wheel/glibc/architecture compatibility and the declared small workload; CUDA is optional. |
| Linux arm64 | CPU only, subject to vendor-wheel verification | The guide identifies AWS-maintained ARM CPU distribution paths. Record the actual wheel/provider; a green x86 test does not prove arm64 readiness. |

`tensorflow-cpu` in the proposal is a **logical runtime ID**, not a promise that
one pip distribution name or one wheel works on all these platforms. No runtime
profile is activated by these files. `python-core` reuses the normal selected
Python and NumPy/data setup; it does not mean that NumPy is in the standard
library. Keep the TensorFlow environment separate from unrelated backend/GPU
experiments. Installation is a deliberate future bootstrap, never a notebook
cell or an automatic response to an import failure.

The required experiments use literal arrays or authored local fixtures. The
pilot has three scalar observations and one update. Later default labs use at
most 512 examples, two hidden layers of at most 64 units, and 200 optimizer
steps. A proposed run has a 120-second wall cap, a bounded output/artifact size
and explicit stopped-budget reporting. These are design budgets to implement
and measure, not benchmark results. Cold framework import is included in
runtime acceptance. A slow machine may continue an authored checkpointed
exercise across runs; it must not relabel a timeout as convergence.

GPU/TPU work, real multi-host training, pretrained application weights, large
image corpora and external serving infrastructure are optional follow-ons.
Transfer learning defaults to the locally trained tiny base. No service key,
private dataset or first-use network download is needed after bootstrap.

## The teacher and learner journey

The first screen states the stage outcome, prerequisites, runtime readiness,
expected budget and where saved work lives. The teacher starts with a concrete
prediction, not a package installation tour. For `tf-008`, the learner commits
to a gradient sign and shape explanation before executing the three-point
example. The teacher then asks what the same scalar loss failed to reveal in
the broadcasting counterexample.

For every unit, use this sequence:

1. **Explain:** introduce its mental model and the units/axes of one example.
2. **Predict:** save a result, shape or failure prediction before execution.
3. **Attempt:** modify the learner's own working copy and retain the actual
   output, parameter state and smallest failing input.
4. **One hint:** ask for a single next investigation, such as checking the
   watched forward path or the target shape. Do not open the solution first.
5. **Compare:** reveal the separate reasoning only after an attempt or an
   explicit request; preserve both the learner version and reference.
6. **Retrieve and transfer:** explain the mechanism without the reference and
   apply it to new numbers, a new reduction or a new target shape.

Every third unit includes a five-minute closed-reference retrieval of an
earlier mechanism. After each capstone, use a fresh transfer fixture and an
oral explanation before recommending the next stage. Worked-example numbers
are public teaching material; reproducing them is not a blind assessment.
Evidence remains a learner/teacher record, never an automatic mastery claim.

## Coverage and pacing

The structured plan is the source of IDs, direct prerequisites, runtime,
objective, concrete lab, verification and concepts. The overview below is
derived from it. Estimates include prediction, diagnosis and explanation;
capstones span multiple sessions. Units 1-12 are beginner within this subject,
13-24 intermediate and 25-36 advanced.

### From arrays to an auditable update

Derive and inspect a tiny learning step before relying on a training API.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `tf-001` | A bounded deep-learning investigation | 75 | Distinguish fitting a function from evidence that it generalizes. |
| `tf-002` | Tensors, axes, dtypes and units | 90 | Trace each axis and unit through vector arithmetic without accidental broadcasting. |
| `tf-003` | Linear neurons and matrix contracts | 90 | Relate a scalar slope to a batched affine layer and verify dimensions. |
| `tf-004` | Loss, reduction and what a number measures | 90 | Compute loss with an explicit example denominator and distinguish it from a metric. |
| `tf-005` | Derivatives as local sensitivity | 105 | Check a scalar derivative against a finite difference away from a kink. |
| `tf-006` | The chain rule and activation boundaries | 105 | Explain how local derivatives compose and where a derivative convention matters. |
| `tf-007` | Eager tensors, variables and a tape | 105 | Identify which forward operations and variables are recorded for differentiation. |
| `tf-008` | One gradient step you can audit | 120 | Derive, execute and independently check one SGD update before using a training API. |
| `tf-009` | Batches and repeated updates | 105 | Distinguish examples, batches, epochs and optimizer steps. |
| `tf-010` | A split is part of the experiment | 105 | Detect duplicate/group leakage before reporting held-out performance. |
| `tf-011` | Keras models and explicit training contracts | 120 | Map compile/fit/evaluate to the explicit forward-loss-gradient-update sequence. |
| `tf-012` | Capstone: an auditable tiny regressor | 180 | Present a reproducible training experiment with arithmetic and held-out evidence. |

### Build, debug and evaluate small networks

Choose objectives, data pipelines and architectures with explicit information and shape contracts.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `tf-013` | Binary logits, probabilities and thresholds | 105 | Use a binary loss with the correct logit/probability convention. |
| `tf-014` | Multiclass and multilabel are different tasks | 105 | Choose target shape and loss from the task rather than the final layer name. |
| `tf-015` | A reproducible tf.data pipeline | 120 | Keep preprocessing, cardinality and order visible in a bounded dataset pipeline. |
| `tf-016` | Nonlinearity and initialization | 120 | Explain why an affine-only network cannot express XOR and inspect a nonlinear construction. |
| `tf-017` | Regularization and training/evaluation behavior | 105 | Separate regularization penalties from data loss and switch stochastic layers correctly. |
| `tf-018` | Normalization state and batch dependence | 120 | Distinguish BatchNorm moving statistics from per-example LayerNorm. |
| `tf-019` | Convolution as a local, shared computation | 120 | Trace a convolution kernel, channels and receptive field on a tiny array. |
| `tf-020` | Pooling and augmentation without label leakage | 105 | Apply only label-preserving training transforms and keep evaluation deterministic. |
| `tf-021` | Sequences, embeddings and padding | 120 | Carry a padding mask through a small sequence model and loss denominator. |
| `tf-022` | Attention with an explicit information boundary | 120 | Verify causal masking independently of apparent model accuracy. |
| `tf-023` | Debugging a custom training loop | 120 | Diagnose a silent missing update and distinguish graph tracing from tensor execution. |
| `tf-024` | Capstone: a small classifier with honest evaluation | 210 | Deliver a bounded classifier with a baseline, leakage checks and error analysis. |

### Reproduce, export and defend a model release

Prove restart/inference behavior and bound reliability claims with controlled evidence.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `tf-025` | Embedding objectives and negative examples | 120 | Connect embedding similarity to the objective and negative sampling policy. |
| `tf-026` | Custom layers, residuals and trainable state | 120 | Create weights once and keep build/call responsibilities separate. |
| `tf-027` | Transfer learning without a model download | 120 | Freeze and adapt a locally trained feature extractor with an explicit gradient boundary. |
| `tf-028` | Restartable training and checkpoint evidence | 135 | Prove a checkpoint restores the next update rather than only the current predictions. |
| `tf-029` | Precision, overflow and stable objectives | 120 | Locate overflow before it becomes a misleading training conclusion. |
| `tf-030` | Distributed gradient semantics on one CPU | 120 | Distinguish a mean over examples from an unweighted mean over unequal shards. |
| `tf-031` | Graphs, retracing and measurement | 120 | Separate trace/setup cost from steady-state execution and preserve equivalent results. |
| `tf-032` | Saving, export and inference parity | 135 | Choose the correct Keras 3 save/export API and verify a restored prediction contract. |
| `tf-033` | Inference contracts and bounded batching | 120 | Validate an inference request independently of training success. |
| `tf-034` | Robustness, privacy and model evidence | 120 | Bound a reliability or privacy claim to the observations actually collected. |
| `tf-035` | Comparing models with uncertainty | 135 | Use paired evidence and keep model selection separate from final assessment. |
| `tf-036` | Capstone: release a small, reproducible model | 240 | Defend a local model release with reproducibility, inference and rollback evidence. |


## Capstone review gates

### tf-012: An auditable tiny regressor

Build a tiny regression experiment with an independent arithmetic oracle.

**Deliverables**

- learner code and clean-run transcript
- training/holdout IDs and preprocessing statistics
- baseline comparison and an error explanation

**Acceptance**

- The tf-008 oracle matches within its stated tolerance.
- Training statistics use training IDs only.
- Held-out results are reported separately and never used for another tuning decision.

### tf-024: A small classifier with honest evaluation

Compare a small local classifier with a transparent baseline.

**Deliverables**

- bounded model/data configuration
- frozen split and confusion/group-error tables
- failure case and a revision justified on validation only

**Acceptance**

- Model has at most two hidden layers and uses only local fixtures.
- Confusion counts sum to test cardinality and groups remain disjoint.
- A weak model is reported honestly; no arbitrary accuracy target conceals errors.

### tf-036: A reproducible local model release

Assemble a release decision from training, inference, provenance and rollback evidence.

**Deliverables**

- model and preprocessing/split manifest hashes
- next-step checkpoint proof
- fresh-process .keras/export parity transcript
- model card, release decision and rollback artifact

**Acceptance**

- Schema/hash failures block recommendation.
- Fresh predictions agree within declared tolerance.
- Optimizer-state restoration reproduces the next step.
- The model card separates tested behavior, untested conditions and intended use.

## Failure cases the author must preserve


The sequence deliberately includes wrong target broadcasting, None versus zero
gradients, stale/reused gradients, too-large steps, from_logits mismatches,
validation preprocessing leakage, short-batch denominators, stochastic layers
left in training mode, padding loss contamination, weights-only restarts,
retracing mistaken for execution, and broken export/input contracts. These
failures must remain observable in authored fixtures. Do not hide them behind
a generic training metric or a random accuracy target.

## From plan to an implemented course

Before promotion, author real guides, learner artifacts, separate executable
and explanatory solutions, and fixed local fixtures under the proposed course
folder. Meet two worked examples and six distinct exercise contracts per unit.
Register only completed artifacts through an additive manifest, extend the
practice ledger and regenerate the catalog/library/readers. The planned IDs in
this design are not valid active MCP/course CLI lesson requests yet.

Prove actual runtime readiness, fresh-process execution, persistence, failure
cleanup, output/time budgets and the three OS/architecture lanes. If a profile
is missing, keep reading/notes available and report execution unavailable.
Run reproducibility and leakage checks before calling a capstone ready. These
design files deliberately do not install packages or build images.

## Design-phase verification record

Checked **2026-10-22** in the original repository:

- The structured plan has 36 unique lessons, 12 per stage, and three capstones.
  The shared design validator accepts its references and prerequisite graph.
  All sample links resolve and the active catalog remains byte-identical to
  baseline `75ec445`, with 168 lessons.
- Python syntax parsing succeeds for the JSON pilot, both guide examples and
  all seven solution code blocks. This establishes Python syntax only.
- An independent standard-library `fractions.Fraction` calculation verifies the
  loss and gradient at zero, rate-0.1 update, rate-0.25 overshoot, fresh two-step
  recurrence, broadcast objective's gradient, and every bias/held-out oracle.
  These checks do not import TensorFlow or substitute for framework execution.
- **TensorFlow was not installed or run.** No wheel/platform acceptance,
  checkpoint/export behavior, memory use or elapsed-time claim is established.
  There was no package/model/data download or image build for this track.

The full pilot has two worked examples, six distinct Expected/Verify contracts,
three progressive hints, a retrieval transfer and a separate six-section
solution reference. These are reviewed teaching samples; implementation of the
other 35 lessons and runtime qualification are still future work.

## Primary sources and compatibility review

Every source below was opened during the design review on **2026-10-22**.
Version/platform guidance is time-sensitive and must be checked again when
creating a runtime lock. A primary document supports a design choice; it is
not proof that a particular machine executed the course.

- [TensorFlow pip installation](https://www.tensorflow.org/install/pip), checked 2026-10-22. CPU routes, native Windows GPU boundary, macOS architecture support and disclosed platform differences.
- [TensorFlow tested build configurations](https://www.tensorflow.org/install/source), checked 2026-10-22. The checked table lists TensorFlow 2.21.0 with Python 3.10-3.13; Python 3.12 is the proposed course baseline, not a performed wheel-install test.
- [Keras getting started](https://keras.io/getting_started/), checked 2026-10-22. TensorFlow 2.16+ uses Keras 3 by default; choose TensorFlow backend explicitly and avoid accidental legacy tf_keras.
- [TensorFlow automatic differentiation](https://www.tensorflow.org/guide/autodiff), checked 2026-10-22. GradientTape records operations, variables are watched, disconnected gradients differ from zero and integer tensors are not ordinary differentiable weights.
- [Keras 3 migration guide](https://keras.io/guides/migrating_to_keras_3/), checked 2026-10-22. Keras 3 save/export differences and backend-specific migration boundaries.
- [TensorFlow data guide](https://www.tensorflow.org/guide/data), checked 2026-10-22. Finite Dataset pipelines, batching and data transformations.
- [TensorFlow checkpoint guide](https://www.tensorflow.org/guide/checkpoint), checked 2026-10-22. Model/optimizer checkpoint objects and restoring training state.
- [Keras reproducibility recipes](https://keras.io/examples/keras_recipes/reproducibility_recipes/), checked 2026-10-22. Seed/deterministic-operation controls do not by themselves prove cross-platform bitwise equality.
