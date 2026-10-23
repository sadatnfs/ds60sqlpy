# PyTorch content and depth-review checkpoint

Updated 23 October 2026. All **36 chapters are authored and substantively reviewed**. The route preserves the paired TensorFlow IDs and established prerequisites. Lesson001 is reading; the other35 use the existing prepared `llm-torch-cpu` profile. The review did not add shared runtime definitions, download data or models, or change learner state.

## What the review changed

The original course had executable fixtures and practice contracts, but35 decision sections were empty and many diagnosis sections repeated generic advice. The review replaced those gaps with topic-specific model selection, symbolic and numerical derivations, tensor and gradient ledgers, state-transition reasoning, counterexamples, interpretation and explicit limits. Foundation chapters001-018 and advanced019-036 were reviewed in parallel, with each paired TensorFlow guide checked before adding the corresponding explanation.

The checked-in [review matrix](../../courses/deep-learning-pytorch/authoring/review_matrix.json) records concrete findings for every chapter, paired-guide review, executable-change flags and the new runtime receipts. Guide word counts currently range from 2219 to 2795 whitespace words. These counts describe artifact size; the review findings and derivations are the substantive evidence.

The durable authoring source is in [authoring/](../../courses/deep-learning-pytorch/authoring/README.md). Regeneration uses only standard-library Python. A test regenerates every published artifact in an isolated temporary root and compares exact bytes. Another test compares the worked program's syntax tree with reference setup and the first three exercises. The three worked blocks have an explicit sequential A-C contract in one fresh process.

## Completed chapter review matrix

| Chapter | Main review outcome | Reference behavior changed |
| --- | --- | --- |
| [torch-001](../../courses/deep-learning-pytorch/guides/torch-001.md) | Assessment timeline, baseline MSE54 and visible extrapolation limits | No |
| [torch-002](../../courses/deep-learning-pytorch/guides/torch-002.md) | Storage offsets, ownership, strides and pairwise-broadcast counterexample | No |
| [torch-003](../../courses/deep-learning-pytorch/guides/torch-003.md) | Linear layout, parameter count and explicit input/weight/bias gradients | No |
| [torch-004](../../courses/deep-learning-pytorch/guides/torch-004.md) | Loss denominators, mask participation and incompatible ranking criteria | No |
| [torch-005](../../courses/deep-learning-pytorch/guides/torch-005.md) | Finite-difference error, domain checks, kinks and optimizer overshoot | Yes, requalified |
| [torch-006](../../courses/deep-learning-pytorch/guides/torch-006.md) | Chain-rule factors, symbolic derivative and saved-value invalidation | No |
| [torch-007](../../courses/deep-learning-pytorch/guides/torch-007.md) | Graph, storage, buffers, None gradients and optimizer state | No |
| [torch-008](../../courses/deep-learning-pytorch/guides/torch-008.md) | Exact SGD recurrence, stability interval and wrong-broadcast optimum | No |
| [torch-009](../../courses/deep-learning-pytorch/guides/torch-009.md) | Minibatch trajectory, stale-gradient counterexample and weighted aggregation | No |
| [torch-010](../../courses/deep-learning-pytorch/guides/torch-010.md) | Train-only preprocessing, grouped identity and held-out perturbation | No |
| [torch-011](../../courses/deep-learning-pytorch/guides/torch-011.md) | Parameters, buffers, mutable state snapshots and optimizer membership | No |
| [torch-012](../../courses/deep-learning-pytorch/guides/torch-012.md) | Independent 100-step coefficient and train/test-loss recurrence | Yes, requalified |
| [torch-013](../../courses/deep-learning-pytorch/guides/torch-013.md) | Stable binary-logit loss, gradient, threshold costs and weighting limits | No |
| [torch-014](../../courses/deep-learning-pytorch/guides/torch-014.md) | Cross-entropy axes, index/soft labels, reduction and double-softmax limits | No |
| [torch-015](../../courses/deep-learning-pytorch/guides/torch-015.md) | Sampling, collation, token identity validation and valid-position counts | Yes, requalified |
| [torch-016](../../courses/deep-learning-pytorch/guides/torch-016.md) | XOR capacity proof, asymmetric layout oracle and initialization assumptions | Yes, requalified |
| [torch-017](../../courses/deep-learning-pytorch/guides/torch-017.md) | Penalty coefficients, Dropout moments, gradient mode and optimizer decay | No |
| [torch-018](../../courses/deep-learning-pytorch/guides/torch-018.md) | Normalization axes, estimators, momentum recurrence and state-freeze distinctions | No |
| [torch-019](../../courses/deep-learning-pytorch/guides/torch-019.md) | Convolution shape and receptive-field derivation plus shared backward accumulation | No |
| [torch-020](../../courses/deep-learning-pytorch/guides/torch-020.md) | Pooling derivatives, information loss, padding and augmentation target semantics | No |
| [torch-021](../../courses/deep-learning-pytorch/guides/torch-021.md) | Packed recurrent state trace, true lengths and padding-gradient boundaries | No |
| [torch-022](../../courses/deep-learning-pytorch/guides/torch-022.md) | Mask shapes/polarity, nonuniform scaled attention and backward dependencies | No |
| [torch-023](../../courses/deep-learning-pytorch/guides/torch-023.md) | Two-step optimization, detached loss, accumulation weights and clipping order | No |
| [torch-024](../../courses/deep-learning-pytorch/guides/torch-024.md) | Train-only classifier normalization, first gradient, threshold and held-out limits | No |
| [torch-025](../../courses/deep-learning-pytorch/guides/torch-025.md) | Contrastive objective, temperature and exact projection-gradient interpretation | No |
| [torch-026](../../courses/deep-learning-pytorch/guides/torch-026.md) | Residual paths, custom backward composition and independent gradcheck limits | No |
| [torch-027](../../courses/deep-learning-pytorch/guides/torch-027.md) | Frozen features, optimizer membership, gradient routes and mutable buffers | No |
| [torch-028](../../courses/deep-learning-pytorch/guides/torch-028.md) | RNG draw ordering, fresh-process restart and checkpoint scope | No |
| [torch-029](../../courses/deep-learning-pytorch/guides/torch-029.md) | Cancellation, stable logit objectives, precision and AMP scope | No |
| [torch-030](../../courses/deep-learning-pytorch/guides/torch-030.md) | Unequal shards, global normalization and distributed-gradient scaling | No |
| [torch-031](../../courses/deep-learning-pytorch/guides/torch-031.md) | Capture boundaries, graph inspection and measured profiling scope | No |
| [torch-032](../../courses/deep-learning-pytorch/guides/torch-032.md) | State/export schemas, tested dynamic shapes and guard limitations | No |
| [torch-033](../../courses/deep-learning-pytorch/guides/torch-033.md) | Inference schema, ownership, empty/finite boundaries and extreme-value limits | No |
| [torch-034](../../courses/deep-learning-pytorch/guides/torch-034.md) | Assessment identity, perturbation labels and privacy-mechanism boundaries | No |
| [torch-035](../../courses/deep-learning-pytorch/guides/torch-035.md) | Paired loss units, exact small bootstrap distribution and pairing counterexample | No |
| [torch-036](../../courses/deep-learning-pytorch/guides/torch-036.md) | Thirty-step recurrence, fresh-process release gates and rollback evidence | No |

## Focused validation

The complete host suite `tests/test_pytorch_lessons.py` passes **10 tests**, with **38 explicit runtime skips** because the host development environment does not contain PyTorch. The skipped cases are35 numerical reference executions and three additional numerical negative controls. This is not reported as host numerical execution. The test file passes Ruff, formatting and strict MyPy.

The passing host tests cover36 complete bundles, links and prerequisites, six-task practice contracts, all displayed sequential programs, fresh-process child parsing, absence of download operations, complete depth records, exact authoring regeneration and current qualification hashes. Independent NumPy-only calculations also checked finite-difference point rejection, the100-step regression recurrence, asymmetric matrix orientation, Dropout moments, normalization momentum and a finite-difference check of the LayerNorm backward derivation.

The related statistics-book, Python/SQL-deepening and final Spark content suites separately passed **205 tests**. That combined content result does not substitute for the PyTorch worker evidence below.

## Observed prepared-worker qualification

The earlier35 runnable references passed the prepared Linux arm64 CPU worker, recorded in `work/pytorch-lessons-first-acceptance.jsonl`, `work/pytorch-lessons-advanced-acceptance.jsonl` and `work/pytorch-export-repaired-acceptance.jsonl`. Those baseline receipts precede this depth review.

The review made four executable improvements and then ran each final reference through the existing isolated production worker:

- **005:** reject nonfinite probe points, including a constant function that would otherwise hide the invalid input.
- **012:** assert the independently derived fitted coefficients and exact training/held-out loss recurrence, beyond merely requiring an improved loss.
- **015:** reject fractional, Boolean, negative and overflowing token IDs before integer collation can silently change their identity.
- **016:** add an asymmetric matrix because the symmetric XOR matrix cannot detect a missing transpose.

All four passed. Two additional references,014 and030, had only exercise-comment changes and were also rerun for current-byte provenance. The six successful results are in `work/pytorch-depth-repaired-acceptance.jsonl`, with source, worker and image hashes. The same four guides were extracted as sequential A-C programs and each ran successfully in a separate fresh worker process, recorded in `work/ml-worked-pytorch-depth-repaired-acceptance.jsonl`. Their standard manifest is `work/pytorch-depth-worked-manifest.json`.

A compact checked-in [evidence record](../../courses/deep-learning-pytorch/authoring/review_runtime_evidence.json) preserves the observed metadata. Tests recompute each reference/program hash and each qualified guide hash. All four behavior changes and both comment-only source changes therefore have matching final-source receipts. These runs used the existing `llm-torch-cpu` image, network disabled, read-only mounts, bounded scratch, two CPUs and the production worker. No image was built during this review.

## Remaining evidence limits

There are no pending chapter-authoring or reviewed-code requalification gaps in this pass. The following bounded claims remain deliberately visible in the teaching material:

- CPU fixtures do not establish GPU performance, multi-GPU collectives, multiprocess DataLoader portability, population generalization or production reliability.
- Chapter031 observes actual capture/profiling behavior and times a bounded loop; its existing assertion checks the final output, not every timed invocation or a speedup claim.
- Chapter032 declares a dynamic batch range1..4 but its executable acceptance exercises batch3 and a separate fixed-shape guard. It does not claim exhaustive tests of batches1,4,5 or arbitrary export portability.
- Chapter033's finite-input contract does not prove that every extreme finite float32 input yields a representable output; the guide identifies that domain limit explicitly.
- Chapter035 explains that the original B losses are constant, so that fixture alone cannot demonstrate every consequence of breaking pairing. A separate analytic counterexample supplies the missing distinction.
- Keras/PyTorch normalization parity is bounded by actual axes, momentum meanings, estimators, epsilon, affine state and mode rules. Matching a running mean does not establish full-state equivalence.

Shared catalog/readers, full-repository gates, browser delivery and any broader runtime qualification remain parent-owned. This checkpoint records the review and observed executions without treating source presence, static checks, reference execution or learner mastery as interchangeable.
