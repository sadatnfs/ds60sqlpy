# Deep learning with TensorFlow and Keras

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Deep learning with TensorFlow and Keras** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


This 36-lesson journey connects arrays, derivatives and exact scalar updates to
Keras models, convolution, sequence masks, attention, custom loops, checkpoint
recovery, inference export and evidence-based model release. Start with
[tf-001](guides/tf-001.md) and work through the prerequisite sequence. Each guide
explains the mechanism, gives concrete examples and six practice contracts,
and helps diagnose plausible wrong answers.

Use the browser's **Journeys** page with the `python-core` worker for NumPy
foundations and `tensorflow-cpu` for framework lessons. The
[Docker classroom guide](../../docs/docker-classroom.md) explains how to build
and start each profile. The host needs no Python or TensorFlow installation.
The first preparation uses the network; the ordinary examples then run on tiny
local CPU fixtures without downloading datasets or models.

Save predictions, code and explanations in the classroom. Some worked blocks
are standalone; the first eight lessons explicitly identify their sequential
A/B scratch-file contract. Follow the instruction beside the examples and run
a fresh process. Solutions are available for comparison after your attempt or
an explicit reveal. No checkbox or successful reference execution certifies
expertise.

The [PyTorch journey](../deep-learning-pytorch/README.md) covers the companion
framework in comparable depth. Pay particular attention to layout, reduction,
normalization-state and checkpoint differences rather than translating API
names mechanically. The [Transformer companion](../../docs/learning/inside-a-transformer.md)
connects the attention lessons to a complete small language-model forward pass.

## Lesson sequence

| Lesson | Level | Runtime |
| --- | --- | --- |
| [tf-001: A bounded deep-learning investigation](guides/tf-001.md) | Beginner | `reading` |
| [tf-002: Tensors, axes, dtypes and units](guides/tf-002.md) | Beginner | `python-core` |
| [tf-003: Linear neurons and matrix contracts](guides/tf-003.md) | Beginner | `python-core` |
| [tf-004: Loss, reduction and what a number measures](guides/tf-004.md) | Beginner | `python-core` |
| [tf-005: Derivatives as local sensitivity](guides/tf-005.md) | Beginner | `python-core` |
| [tf-006: The chain rule and activation boundaries](guides/tf-006.md) | Beginner | `python-core` |
| [tf-007: Eager tensors, variables and a tape](guides/tf-007.md) | Beginner | `tensorflow-cpu` |
| [tf-008: One gradient step you can audit](guides/tf-008.md) | Beginner | `tensorflow-cpu` |
| [tf-009: Batches and repeated updates](guides/tf-009.md) | Beginner | `tensorflow-cpu` |
| [tf-010: A split is part of the experiment](guides/tf-010.md) | Beginner | `python-core` |
| [tf-011: Keras models and explicit training contracts](guides/tf-011.md) | Beginner | `tensorflow-cpu` |
| [tf-012: Capstone: an auditable tiny regressor](guides/tf-012.md) | Beginner | `tensorflow-cpu` |
| [tf-013: Binary logits, probabilities and thresholds](guides/tf-013.md) | Intermediate | `tensorflow-cpu` |
| [tf-014: Multiclass and multilabel are different tasks](guides/tf-014.md) | Intermediate | `tensorflow-cpu` |
| [tf-015: A reproducible tf.data pipeline](guides/tf-015.md) | Intermediate | `tensorflow-cpu` |
| [tf-016: Nonlinearity and initialization](guides/tf-016.md) | Intermediate | `tensorflow-cpu` |
| [tf-017: Regularization and training/evaluation behavior](guides/tf-017.md) | Intermediate | `tensorflow-cpu` |
| [tf-018: Normalization state and batch dependence](guides/tf-018.md) | Intermediate | `tensorflow-cpu` |
| [tf-019: Convolution as a local, shared computation](guides/tf-019.md) | Intermediate | `tensorflow-cpu` |
| [tf-020: Pooling and augmentation without label leakage](guides/tf-020.md) | Intermediate | `tensorflow-cpu` |
| [tf-021: Sequences, embeddings and padding](guides/tf-021.md) | Intermediate | `tensorflow-cpu` |
| [tf-022: Attention with an explicit information boundary](guides/tf-022.md) | Intermediate | `tensorflow-cpu` |
| [tf-023: Debugging a custom training loop](guides/tf-023.md) | Intermediate | `tensorflow-cpu` |
| [tf-024: Capstone: a small classifier with honest evaluation](guides/tf-024.md) | Intermediate | `tensorflow-cpu` |
| [tf-025: Embedding objectives and negative examples](guides/tf-025.md) | Advanced | `tensorflow-cpu` |
| [tf-026: Custom layers, residuals and trainable state](guides/tf-026.md) | Advanced | `tensorflow-cpu` |
| [tf-027: Transfer learning without a model download](guides/tf-027.md) | Advanced | `tensorflow-cpu` |
| [tf-028: Restartable training and checkpoint evidence](guides/tf-028.md) | Advanced | `tensorflow-cpu` |
| [tf-029: Precision, overflow and stable objectives](guides/tf-029.md) | Advanced | `tensorflow-cpu` |
| [tf-030: Distributed gradient semantics on one CPU](guides/tf-030.md) | Advanced | `tensorflow-cpu` |
| [tf-031: Graphs, retracing and measurement](guides/tf-031.md) | Advanced | `tensorflow-cpu` |
| [tf-032: Saving, export and inference parity](guides/tf-032.md) | Advanced | `tensorflow-cpu` |
| [tf-033: Inference contracts and bounded batching](guides/tf-033.md) | Advanced | `tensorflow-cpu` |
| [tf-034: Robustness, privacy and model evidence](guides/tf-034.md) | Advanced | `python-core` |
| [tf-035: Comparing models with uncertainty](guides/tf-035.md) | Advanced | `python-core` |
| [tf-036: Capstone: release a small, reproducible model](guides/tf-036.md) | Advanced | `tensorflow-cpu` |

## Validation and limits

All runnable reference programs have successful local Linux arm64 Docker
receipts for their current source bytes. The
[implementation checkpoint](../../docs/implementation/CHECKPOINT.md) records
runtime, test and platform acceptance separately. Reading lessons use reasoning
and written evidence. Windows/WSL2 and amd64 configuration support does not by
itself establish an observed run on those systems.

All 36 guides received a substantive mechanism review; see the
[TensorFlow review ledger](../../docs/implementation/tensorflow-depth-review.md).
The small fixtures demonstrate arithmetic, API behavior and process boundaries.
They do not establish generalization, accelerator speed or distributed-training
performance. A failed capstone gate is a useful result to explain and repair.
