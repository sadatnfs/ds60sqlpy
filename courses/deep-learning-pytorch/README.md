# Deep Learning with PyTorch

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Deep Learning with PyTorch** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


This complete 36-lesson authored route gives PyTorch the same broad subject coverage as the [36-lesson TensorFlow course](../deep-learning-tensorflow/README.md). It progresses from tensor storage and gradients through data loading,training,classifiers,convolutions,recurrent sequences,attention,custom autograd,transfer,checkpointing,numerics,profiling,export and a model-release capstone. Each topic is paired with its TensorFlow counterpart so you can compare the mathematical contract and the framework-specific implementation separately.

The [authored manifest](lessons.json) lists real guide,learner and separate solution artifacts. The [track plan](track.json) preserves prerequisites and paired IDs. Every guide has three worked examples,six concrete exercises,progressive hints,answered interview reasoning and a copy-ready Codex prompt. Read the [comparison guide](COMPARISON.md) for layout,reduction,state and mode differences. Source completion does not imply runtime acceptance;the [execution checkpoint](../../docs/implementation/pytorch-content-status.md) records actual receipts.

## Run the same prepared CPU environment

Use the Docker classroom's `llm-torch-cpu` profile. Its historical name does not restrict it to language models:the prepared PyTorch2.9.1 CPU/NumPy2.2.6 worker runs this whole deep-learning route. No host PyTorch,GPU,torchvision,external dataset or pretrained-model download is needed. DataLoader usesnum_workers=0 in the default examples. See [classroom setup](../../docs/docker-classroom.md) for image preparation,logs and persistent learner pads.

The first lesson is a reading worksheet;the other35 have executable Python references. Work in your saved pad or an ignored `.learning/` copy. Keep official solutions closed until you attempt the exercises or explicitly request comparison. A successful reference run verifies its assertions,not your independent understanding or a production model's reliability.

## Study both frameworks by contract

Match data identities,shapes,dtypes,initial state,loss reduction and optimizer policy before comparing numbers. PyTorchLinear and Keras Dense store weight axes differently. BatchNorm momentum conventions differ. PyTorchbackward accumulates leaf gradients unless cleared,andtrain/eval is separate from gradient mode. Checkpoint and inference artifacts have different state and lifetime contracts. The paired lessons expose these differences with controlled failures rather than treating similarly named APIs as interchangeable.

| PyTorch lesson | Topic | TensorFlow pair |
| --- | --- | --- |
| [torch-001](guides/torch-001.md) | A bounded PyTorch investigation and framework comparison | [tf-001](../deep-learning-tensorflow/guides/tf-001.md) |
| [torch-002](guides/torch-002.md) | Tensors, devices, dtypes, strides and views | [tf-002](../deep-learning-tensorflow/guides/tf-002.md) |
| [torch-003](guides/torch-003.md) | Linear modules, parameters and matrix contracts | [tf-003](../deep-learning-tensorflow/guides/tf-003.md) |
| [torch-004](guides/torch-004.md) | Loss functions, reductions and gradient scale | [tf-004](../deep-learning-tensorflow/guides/tf-004.md) |
| [torch-005](guides/torch-005.md) | Derivatives, requires_grad and finite-difference checks | [tf-005](../deep-learning-tensorflow/guides/tf-005.md) |
| [torch-006](guides/torch-006.md) | Autograd graphs, the chain rule and in-place hazards | [tf-006](../deep-learning-tensorflow/guides/tf-006.md) |
| [torch-007](guides/torch-007.md) | Leaf tensors, detach, no_grad and gradient accumulation | [tf-007](../deep-learning-tensorflow/guides/tf-007.md) |
| [torch-008](guides/torch-008.md) | One optimizer step you can audit | [tf-008](../deep-learning-tensorflow/guides/tf-008.md) |
| [torch-009](guides/torch-009.md) | Batches, zero_grad and repeated updates | [tf-009](../deep-learning-tensorflow/guides/tf-009.md) |
| [torch-010](guides/torch-010.md) | Datasets, held-out families and leakage controls | [tf-010](../deep-learning-tensorflow/guides/tf-010.md) |
| [torch-011](guides/torch-011.md) | nn.Module, registered parameters and explicit training loops | [tf-011](../deep-learning-tensorflow/guides/tf-011.md) |
| [torch-012](guides/torch-012.md) | Capstone: an auditable tiny PyTorch regressor | [tf-012](../deep-learning-tensorflow/guides/tf-012.md) |
| [torch-013](guides/torch-013.md) | Binary logits, BCEWithLogitsLoss and thresholds | [tf-013](../deep-learning-tensorflow/guides/tf-013.md) |
| [torch-014](guides/torch-014.md) | CrossEntropyLoss, multiclass and multilabel contracts | [tf-014](../deep-learning-tensorflow/guides/tf-014.md) |
| [torch-015](guides/torch-015.md) | Dataset, DataLoader, collation and reproducible sampling | [tf-015](../deep-learning-tensorflow/guides/tf-015.md) |
| [torch-016](guides/torch-016.md) | Initialization, nonlinearities and gradient diagnostics | [tf-016](../deep-learning-tensorflow/guides/tf-016.md) |
| [torch-017](guides/torch-017.md) | Dropout, regularization, train and eval modes | [tf-017](../deep-learning-tensorflow/guides/tf-017.md) |
| [torch-018](guides/torch-018.md) | BatchNorm, LayerNorm and stateful normalization | [tf-018](../deep-learning-tensorflow/guides/tf-018.md) |
| [torch-019](guides/torch-019.md) | Convolutions, channel layouts and shared computation | [tf-019](../deep-learning-tensorflow/guides/tf-019.md) |
| [torch-020](guides/torch-020.md) | Pooling, local augmentation and label invariants | [tf-020](../deep-learning-tensorflow/guides/tf-020.md) |
| [torch-021](guides/torch-021.md) | Embeddings, padded sequences and recurrent models | [tf-021](../deep-learning-tensorflow/guides/tf-021.md) |
| [torch-022](guides/torch-022.md) | Attention, transformer masks and information boundaries | [tf-022](../deep-learning-tensorflow/guides/tf-022.md) |
| [torch-023](guides/torch-023.md) | Debugging custom loops, accumulation and clipping | [tf-023](../deep-learning-tensorflow/guides/tf-023.md) |
| [torch-024](guides/torch-024.md) | Capstone: a small classifier with honest evaluation | [tf-024](../deep-learning-tensorflow/guides/tf-024.md) |
| [torch-025](guides/torch-025.md) | Contrastive embeddings and negative sampling | [tf-025](../deep-learning-tensorflow/guides/tf-025.md) |
| [torch-026](guides/torch-026.md) | Custom modules, residual paths, buffers and autograd checks | [tf-026](../deep-learning-tensorflow/guides/tf-026.md) |
| [torch-027](guides/torch-027.md) | Transfer learning, frozen layers and optimizer membership | [tf-027](../deep-learning-tensorflow/guides/tf-027.md) |
| [torch-028](guides/torch-028.md) | Restartable training, optimizer state and RNG evidence | [tf-028](../deep-learning-tensorflow/guides/tf-028.md) |
| [torch-029](guides/torch-029.md) | Stable objectives, precision and mixed-precision boundaries | [tf-029](../deep-learning-tensorflow/guides/tf-029.md) |
| [torch-030](guides/torch-030.md) | Distributed gradients and accumulation semantics on CPU | [tf-030](../deep-learning-tensorflow/guides/tf-030.md) |
| [torch-031](guides/torch-031.md) | Profiling, torch.compile and honest performance measurement | [tf-031](../deep-learning-tensorflow/guides/tf-031.md) |
| [torch-032](guides/torch-032.md) | state_dict, torch.export and inference parity | [tf-032](../deep-learning-tensorflow/guides/tf-032.md) |
| [torch-033](guides/torch-033.md) | Inference mode, model contracts and bounded batching | [tf-033](../deep-learning-tensorflow/guides/tf-033.md) |
| [torch-034](guides/torch-034.md) | Robustness, privacy and evidence beyond a score | [tf-034](../deep-learning-tensorflow/guides/tf-034.md) |
| [torch-035](guides/torch-035.md) | Paired model comparisons and uncertainty | [tf-035](../deep-learning-tensorflow/guides/tf-035.md) |
| [torch-036](guides/torch-036.md) | Capstone: release a small reproducible PyTorch model | [tf-036](../deep-learning-tensorflow/guides/tf-036.md) |

## Evidence and limits

Tiny CPU fixtures establish local arithmetic,gradient,state and artifact contracts. They do not establish GPU throughput,distributed scaling,privacy,fairness or representative population quality. The compilation lesson uses a transparent eager graph backend and makes no native-kernel speedup claim. Persistence lessons use fresh subprocesses,owned temporary directories and explicit failure diagnostics. The release capstone deliberately rejects a corrupted artifact and permits a no-go decision.

For domain assistants and actual tiny-model adaptation,continue with [applied LLMs](../llm-applied/README.md). For inference and study-design reasoning,see the [statistics and machine-learning book](../statistics-ml/README.md). Those topics complement the framework mechanics and do not replace them.
