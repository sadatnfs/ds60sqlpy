# TensorFlow explanation-depth review

Updated 2026-10-23. This document records the root-authored 26-chapter review.
Root also completed the eight independently authored pilot chapters below.
The normalization/tracing chapters were reviewed by the ML author. It is a review ledger, not a claim of exhaustive
coverage of every possible deep-learning technique.

The additions explain each chapter's concrete mechanism, derive numerical
values where appropriate, state its assumptions, and diagnose a failure that
would otherwise remain hidden by a passing aggregate. The source of these
additions is `courses/deep-learning-tensorflow/authoring/depth_reviews_tf.py`.
The shared renderer now leads with the Docker classroom and the declared
worker profile, with native study linked as an optional alternative.

| Chapter | Reviewed mechanism and independent check |
| --- | --- |
| tf-009: Batches and repeated updates | Three exact SGD updates and example-weighted reporting. |
| tf-010: A split is part of the experiment | Train-only mean, group/time information boundaries and split-hash limits. |
| tf-011: Keras models and explicit training contracts | Exact scalar MSE gradient, first update and broadcasting counterexample. |
| tf-012: Capstone: an auditable tiny regressor | Train-fitted constant baseline, holdout MSE and small-sample limits. |
| tf-013: Binary logits, probabilities and thresholds | Logits versus probabilities, derivative, costs and threshold equality. |
| tf-014: Multiclass and multilabel are different tasks | Mutually exclusive classes versus independent labels and loss units. |
| tf-015: A reproducible tf.data pipeline | Paired record identity, cache placement, shuffling and remainders. |
| tf-016: Nonlinearity and initialization | Affine collapse, XOR nonlinearity and behavior away from truth-table corners. |
| tf-017: Regularization and training/evaluation behavior | Regularization derivatives, dropout scaling and optimizer decay differences. |
| tf-019: Convolution as a local, shared computation | Cross-correlation orientation, dimensions, kernel counts and padding limits. |
| tf-020: Pooling and augmentation without label leakage | Max versus average pooling, gradient routing and augmentation target semantics. |
| tf-021: Sequences, embeddings and padding | Padding masks, active denominators, right-padding assumptions and empty inputs. |
| tf-022: Attention with an explicit information boundary | Mask-before-softmax, axis contracts, prefix invariance and all-masked rows. |
| tf-023: Debugging a custom training loop | Missing versus zero gradients, exact recurrence and tape state. |
| tf-024: Capstone: a small classifier with honest evaluation | Train-only scale, classification versus cross entropy and two-row assessment. |
| tf-025: Embedding objectives and negative examples | Dot product versus cosine, temperature gradients and false-negative identities. |
| tf-026: Custom layers, residuals and trainable state | Residual identity, exact kernel gradient and persistent state ownership. |
| tf-027: Transfer learning without a model download | Head/base parameter boundaries, optimizer phase changes and forward mode. |
| tf-028: Restartable training and checkpoint evidence | Fresh-process next-update proof, optimizer history and stochastic-state limits. |
| tf-029: Precision, overflow and stable objectives | Stable log-sum-exp, representational loss and unscaled-gradient conventions. |
| tf-030: Distributed gradient semantics on one CPU | Global numerators, unequal/empty shards and regularization scaling. |
| tf-032: Saving, export and inference parity | Training objects versus inference endpoints, lifetime and shape/schema contracts. |
| tf-033: Inference contracts and bounded batching | Input validation, batching invariance assumptions and mutation checks. |
| tf-034: Robustness, privacy and model evidence | Independent units, subgroup denominators, perturbation semantics and severity. |
| tf-035: Comparing models with uncertainty | Paired error differences, resampling unit and selection boundaries. |
| tf-036: Capstone: release a small, reproducible model | Feature-order probe, lineage identity, three-state gates and recoverable rollback. |

## Executable evidence

The prose-only regeneration preserved all 108 TensorFlow learner and solution
files byte for byte and all 52 Python worked blocks in these 26 guides.
`work/tensorflow-prose-depth-parity.json` records before/after guide hashes and
unchanged code hashes. Existing exact-source Docker receipts therefore remain
applicable to those executable blocks; a changed guide hash alone does not
imply that the code changed.

Separately revised tf-018 and tf-031 references and their five worked programs
all passed actual offline TensorFlow Docker execution in
`work/ml-worked-tensorflow-depth-acceptance.jsonl`. Those seven cases supersede
the older code receipts for those two lessons. Host syntax or structural
checks are not substituted for these framework runs.

All observed Docker execution here is Linux arm64 on the local engine. This
review does not establish accelerator performance, distributed execution,
Windows/amd64 runtime acceptance, generalization from tiny fixtures or
production model quality. The chapters explicitly distinguish those claims.

## Pilot chapter review

All eight pilot guides were inspected against their concrete reference programs.
The additions explain training-fit ambiguity (001), reduction concealing an
axis error (002), parameter counts and units (003), objective and observation
weighting (004), finite-difference truncation versus rounding (005), summed
graph paths and nonsmooth conventions (006), object identity and tape intervals
(007), and the exact scalar learning-rate contraction interval (008).

All pilot Python worked blocks are unchanged; before/after hashes are recorded
in `work/tensorflow-pilot-depth-parity.json`. Their Docker-first run sections
replace stale native-first and unexecuted-runtime wording. These pilots remain
independently authored Markdown; the completion renderer intentionally preserves
them. Together with the 26 rows above and the reviewed 018/031 chapters, all
36 TensorFlow guides have now received this substantive explanation review.
