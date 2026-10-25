# Language-model mechanisms and evidence

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Language-model mechanisms and evidence** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work.


All **48 chapters** are authored, from probability and tokenization through actual tiny-model training, inference, evaluation and modern Transformer mechanisms. The route has 27 Core/NumPy lessons, 16 PyTorch CPU lessons and 5 reading lessons. The index below is generated from the reviewed plan and complete authored manifest.

## Start in the Docker classroom

Use the [Docker classroom setup](../../docs/docker-classroom.md), open **All learning paths**, and choose the LLM theory journey. Select a chapter, read its guide, save your own learner pad and use **Run** for an executable lesson. The selected worker supplies the declared Python packages. Host Python, PyTorch and TensorFlow installations are not prerequisites for this route.

Reading chapters use written calculations and reasoning cases. Their read marker is a study record, not an executed test or proof of mastery. For code chapters, record predictions, attempt the six tasks, use progressive hints, then compare the separate executable and explained solutions after an attempt. Preserve learner work under the classroom's saved pad or ignored `.learning/expansion/` directories.

The default lessons use tiny literal offline fixtures and bounded CPU computations. No default chapter downloads model weights or calls a paid model API. The [implementation checkpoint](../../docs/implementation/CHECKPOINT.md) explains the current architecture and evidence boundaries. Runtime evidence is separate from a claim that a small model is a reliable subject expert.

## Follow a complete Transformer calculation

[Inside a Transformer](../../docs/learning/inside-a-transformer.md) walks through an inspectable NumPy decoder forward pass, tensor shapes, causal-prefix checks, a finite-difference derivative and an explicitly head-only update. Use it alongside chapters 009-011 and 016, then continue to 043-048 for architecture families, positional methods, RMSNorm/SwiGLU, head sharing and exact blockwise attention, sparse experts and speculative decoding.

For a subject assistant, retrieval or fine-tuning project, continue into [Applied LLM systems](../llm-applied/README.md). That route develops corpus provenance, chunking, lexical/hybrid retrieval, access boundaries, grounded citations, abstention, evaluation, actual tiny-model adaptation and an explicitly optional pretrained recipe. [NLP foundations](../nlp/README.md) supplies additional text and classical retrieval methods. The dedicated [PyTorch](../deep-learning-pytorch/README.md) and [TensorFlow](../deep-learning-tensorflow/README.md) journeys cover their frameworks broadly.

## Complete chapter index

### Probability, tokens and attention

| Chapter | Topic | Runtime |
| --- | --- | --- |
| [llm-001](guides/llm-001.md) | Language-model claims and evaluation units | Reading |
| [llm-002](guides/llm-002.md) | Scores, stable softmax and probability mass | Core / NumPy |
| [llm-003](guides/llm-003.md) | Conditional probability and a sequence likelihood | Core / NumPy |
| [llm-004](guides/llm-004.md) | A count-based next-token baseline | Core / NumPy |
| [llm-005](guides/llm-005.md) | Cross entropy, perplexity and denominator traps | Core / NumPy |
| [llm-006](guides/llm-006.md) | Unicode, bytes and tokenizer round trips | Core / NumPy |
| [llm-007](guides/llm-007.md) | A tiny train-only subword vocabulary | Core / NumPy |
| [llm-008](guides/llm-008.md) | Embedding lookup is a learned table | Core / NumPy |
| [llm-009](guides/llm-009.md) | Causal attention and prefix invariance | Core / NumPy |
| [llm-010](guides/llm-010.md) | Position, order and tokenwise normalization | Core / NumPy |
| [llm-011](guides/llm-011.md) | Multiple heads, residuals and a decoder block | Core / NumPy |
| [llm-012](guides/llm-012.md) | Greedy decoding, temperature and sampling | Core / NumPy |
| [llm-013](guides/llm-013.md) | A leakage audit before a model score | Core / NumPy |
| [llm-014](guides/llm-014.md) | Capstone: a small language-model evidence notebook | Core / NumPy |

### A tiny causal model: training, inference and evidence

| Chapter | Topic | Runtime |
| --- | --- | --- |
| [llm-015](guides/llm-015.md) | PyTorch tensors and automatic gradients | PyTorch CPU |
| [llm-016](guides/llm-016.md) | A tiny causal transformer from explicit parts | PyTorch CPU |
| [llm-017](guides/llm-017.md) | Shifted batches, padding and token loss | PyTorch CPU |
| [llm-018](guides/llm-018.md) | A bounded training loop with visible state | PyTorch CPU |
| [llm-019](guides/llm-019.md) | Overfit one batch to diagnose the loop | PyTorch CPU |
| [llm-020](guides/llm-020.md) | Initialization and residual scale | PyTorch CPU |
| [llm-021](guides/llm-021.md) | Document splits and contamination controls | Core / NumPy |
| [llm-022](guides/llm-022.md) | Reproducibility, evaluation mode and restart | PyTorch CPU |
| [llm-023](guides/llm-023.md) | Top-p, termination and decoding failure cases | PyTorch CPU |
| [llm-024](guides/llm-024.md) | KV caches and incremental equivalence | PyTorch CPU |
| [llm-025](guides/llm-025.md) | Memory and compute without a GPU | Core / NumPy |
| [llm-026](guides/llm-026.md) | What a representation probe establishes | PyTorch CPU |
| [llm-027](guides/llm-027.md) | Calibration and comparable evaluation | Core / NumPy |
| [llm-028](guides/llm-028.md) | Capstone: train and audit a tiny transformer | PyTorch CPU |

### Adaptation, evaluation and system decisions

| Chapter | Topic | Runtime |
| --- | --- | --- |
| [llm-029](guides/llm-029.md) | Scaling laws and the limits of a toy experiment | Reading |
| [llm-030](guides/llm-030.md) | Pretraining data provenance and evaluation contamination | Reading |
| [llm-031](guides/llm-031.md) | Instruction tuning and loss masks | PyTorch CPU |
| [llm-032](guides/llm-032.md) | Low-rank adaptation without a package download | PyTorch CPU |
| [llm-033](guides/llm-033.md) | Preference objectives and what they do not prove | Core / NumPy |
| [llm-034](guides/llm-034.md) | Precision and quantization error budgets | Core / NumPy |
| [llm-035](guides/llm-035.md) | Inference scheduling and cache isolation | PyTorch CPU |
| [llm-036](guides/llm-036.md) | Retrieval: what RAG changes and what it cannot supply | Core / NumPy |
| [llm-037](guides/llm-037.md) | Evaluate retrieval and answers separately | Core / NumPy |
| [llm-038](guides/llm-038.md) | Tools, structured output and trust boundaries | Core / NumPy |
| [llm-039](guides/llm-039.md) | Robustness, fairness and finite safety evidence | Reading |
| [llm-040](guides/llm-040.md) | A statistical evaluation and reliability argument | Core / NumPy |
| [llm-041](guides/llm-041.md) | Optional framework comparison without a second prerequisite | Reading |
| [llm-042](guides/llm-042.md) | Capstone: a defensible language-system decision | PyTorch CPU |

### Expert Transformer mechanisms

| Chapter | Topic | Runtime |
| --- | --- | --- |
| [llm-043](guides/llm-043.md) | Encoder, decoder and encoder-decoder architectures and objectives | Core / NumPy |
| [llm-044](guides/llm-044.md) | RoPE, relative positions, ALiBi and long-context limits | Core / NumPy |
| [llm-045](guides/llm-045.md) | Pre/post normalization, RMSNorm and gated feed-forward networks | PyTorch CPU |
| [llm-046](guides/llm-046.md) | MHA, MQA, GQA and blockwise exact attention | Core / NumPy |
| [llm-047](guides/llm-047.md) | Sparse experts, routing capacity and load balancing | Core / NumPy |
| [llm-048](guides/llm-048.md) | Exact speculative decoding and cache rollback | Core / NumPy |

## Maintainer sources

[The authored manifest](lessons.json) records complete bundles. [The reviewed plan](../../docs/expansion/plans/llm-theory.json) supplies stable IDs, ordering and prerequisites. The earlier completion specifications live under `courses/deep-learning-tensorflow/authoring/`; the six expert chapters have their own [authoring sources](authoring/README.md). Regenerate this index with `python courses/llm-theory/authoring/readme.py` rather than hand-maintaining a second lesson list.
