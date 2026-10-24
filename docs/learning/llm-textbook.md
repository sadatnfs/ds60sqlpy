# Language models: a textbook reading route

This route joins **48 chapters on how language models work** with **24 chapters
on building and evaluating subject-matter assistants**. Read it as a connected
book, then use the coding pad to inspect the small experiments. The browser
opens these two journeys in a wide reading view; **Show code and notes** brings
back the experiment panel. Your layout preference is remembered for each journey.

Start the whole classroom with `./classroom`. The
[one-command guide](../one-command-classroom.md) covers macOS, Linux and Windows
through WSL 2. The lessons below use the prepared Core or PyTorch CPU worker.
Default examples use small local fixtures without API keys, model downloads or
GPU requirements. The optional pretrained recipe is identified explicitly.

## What you will be able to explain

A language model assigns probabilities to possible next tokens given a prefix.
A useful assistant is a larger system: it chooses context, controls access to
information, may retrieve documents or call defined tools, produces a proposal,
and checks that proposal against the intended task. Learning both levels matters.
A correct attention implementation is not evidence that a generated business
answer is supported, and a fluent answer does not establish that a calculation
used the correct denominator.

The mechanism chapters build from concrete sequences and counts into embeddings,
attention, Transformer blocks, objectives and optimization. The later chapters
connect the same mathematical objects to caching, inference budgets, adaptation,
quantization, routing and evaluation. The applied route carries a running
**Methods Desk** case: an assistant helping analysts answer questions from
versioned subject-matter material and structured data. It makes the transitions
between data preparation, retrieval, generation, tools and measurement visible.

Each chapter starts with an explanation of the problem the mechanism solves.
Notation and assumptions appear before they are used in derivations. Numerical
traces connect equations to the existing code and show which intermediate value
should change. Counterexamples explain where an attractive shortcut fails.
Chapter bridges identify the new idea needed next, so the route does not reduce
to a list of library calls.

## A small notation map

| Symbol or word | Meaning to establish before using it |
| --- | --- |
| Token | A vocabulary item produced by a particular tokenizer; its boundaries need not match words |
| Vocabulary size V | The number of token IDs the output distribution can assign probability to |
| Sequence length T | The number of token positions participating in the particular computation |
| Batch size B | The number of sequences processed together, not their total active-token count |
| Feature width D | The number of representation coordinates at a token position |
| Embedding | A vector looked up or computed for a token; it is not a stored dictionary definition |
| Logit | An unnormalized score, distinct from the probability obtained after normalization |
| Q, K and V in attention | Query, key and value matrices; this V means values, not vocabulary size |
| Mask | A declaration of permitted information or participating loss positions; the exact meaning depends on the API and operation |
| Parameter | Learned persistent state, such as a projection matrix |
| Activation | An intermediate value computed for particular inputs and parameters |
| Gradient | A local derivative of the declared objective with respect to a chosen quantity |
| Cache | Retained computation state whose correctness depends on model, sequence and position identity |
| Evaluation unit | The observation, customer, document family or other unit to which a reported metric applies |

For a decoder, one common representation layout is `(B, T, D)`. Attention heads
introduce another axis, so an implementation might reshape to `(B, H, T, d)` with
`D = H*d`. That equality belongs to a particular architecture. Grouped-query
attention, cross-attention and different framework APIs need their own dimension
contracts. Keep the axis names beside an equation rather than guessing from a
square example that happens to multiply successfully.

Similarly, distinguish the causal attention mask from the loss mask. The first
limits which positions can influence a prediction. The second determines which
target positions contribute to an objective. Excluding a prompt token from loss
does not necessarily make it invisible as context. Several chapters derive this
separation using exact logits and gradients.

## How to read equations and experiments together

First identify the inputs and their units. Write the operation in words, then
name the axes it preserves or reduces. Follow one small numerical case from
input to output before relying on a final scalar. Only then run the code and
compare the intermediate quantities with your calculation.

A program's boundary is as important as its happy path. Ask what happens for an
empty candidate set, an all-masked row, a different feature width, an unseen
identity or a nonfinite intermediate. A check that rejects an undefined quantity
can be more informative than a program that always prints a number. Preserve a
counterexample that distinguishes the intended mechanism from a plausible wrong
implementation.

The chapters label whether worked blocks are complete standalone programs or a
sequential A/B/C experiment. A sequential experiment shares explicitly introduced
state inside one fresh process. It does not rely on hidden variables in an old
notebook. Save your own pad before replacing it with an example. Ordinary practice
sections and separately revealed solutions remain available after the exposition.

Small examples make a mechanism inspectable. They do not replace the evidence
needed for a deployment decision. Track four different questions: whether the
algebra is right, whether this implementation executes, whether the measurement
matches its stated unit, and whether the resulting system is useful on new work.
The final question requires data and evaluation beyond a published toy fixture.

## Part I: mechanisms, training and inference

Begin with chapters 001-009 if token probability, vector shapes or gradients are
unfamiliar. Chapters 010-024 assemble the Transformer and examine training,
masking, decoding and state. Chapters 025-042 connect resource use, adaptation,
evaluation and a complete bounded system. Chapters 043-048 examine architecture families, positional rotations,
normalization and gated feed-forward networks, grouped and blockwise attention,
sparse experts, and exact speculative decoding. The exact prerequisites remain in each guide.

For an additional connected architectural walkthrough, read
[Inside a Transformer](inside-a-transformer.md). Its NumPy program traces a full
small decoder forward pass and independently checks an output-head gradient.
It explicitly distinguishes the untrained forward mechanism from full-model
learning. The primary [Transformer paper](https://arxiv.org/abs/1706.03762) is
background reading; the checked-in chapters supply the explanation locally.

| Chapter | Topic |
| --- | --- |
| llm-001 | [Language-model claims and evaluation units](../../courses/llm-theory/guides/llm-001.md) |
| llm-002 | [Scores, stable softmax and probability mass](../../courses/llm-theory/guides/llm-002.md) |
| llm-003 | [Conditional probability and a sequence likelihood](../../courses/llm-theory/guides/llm-003.md) |
| llm-004 | [A count-based next-token baseline](../../courses/llm-theory/guides/llm-004.md) |
| llm-005 | [Cross entropy, perplexity and denominator traps](../../courses/llm-theory/guides/llm-005.md) |
| llm-006 | [Unicode, bytes and tokenizer round trips](../../courses/llm-theory/guides/llm-006.md) |
| llm-007 | [A tiny train-only subword vocabulary](../../courses/llm-theory/guides/llm-007.md) |
| llm-008 | [Embedding lookup is a learned table](../../courses/llm-theory/guides/llm-008.md) |
| llm-009 | [Causal attention and prefix invariance](../../courses/llm-theory/guides/llm-009.md) |
| llm-010 | [Position, order and tokenwise normalization](../../courses/llm-theory/guides/llm-010.md) |
| llm-011 | [Multiple heads, residuals and a decoder block](../../courses/llm-theory/guides/llm-011.md) |
| llm-012 | [Greedy decoding, temperature and sampling](../../courses/llm-theory/guides/llm-012.md) |
| llm-013 | [A leakage audit before a model score](../../courses/llm-theory/guides/llm-013.md) |
| llm-014 | [Capstone: a small language-model evidence notebook](../../courses/llm-theory/guides/llm-014.md) |
| llm-015 | [PyTorch tensors and automatic gradients](../../courses/llm-theory/guides/llm-015.md) |
| llm-016 | [A tiny causal transformer from explicit parts](../../courses/llm-theory/guides/llm-016.md) |
| llm-017 | [Shifted batches, padding and token loss](../../courses/llm-theory/guides/llm-017.md) |
| llm-018 | [A bounded training loop with visible state](../../courses/llm-theory/guides/llm-018.md) |
| llm-019 | [Overfit one batch to diagnose the loop](../../courses/llm-theory/guides/llm-019.md) |
| llm-020 | [Initialization and residual scale](../../courses/llm-theory/guides/llm-020.md) |
| llm-021 | [Document splits and contamination controls](../../courses/llm-theory/guides/llm-021.md) |
| llm-022 | [Reproducibility, evaluation mode and restart](../../courses/llm-theory/guides/llm-022.md) |
| llm-023 | [Top-p, termination and decoding failure cases](../../courses/llm-theory/guides/llm-023.md) |
| llm-024 | [KV caches and incremental equivalence](../../courses/llm-theory/guides/llm-024.md) |
| llm-025 | [Memory and compute without a GPU](../../courses/llm-theory/guides/llm-025.md) |
| llm-026 | [What a representation probe establishes](../../courses/llm-theory/guides/llm-026.md) |
| llm-027 | [Calibration and comparable evaluation](../../courses/llm-theory/guides/llm-027.md) |
| llm-028 | [Capstone: train and audit a tiny transformer](../../courses/llm-theory/guides/llm-028.md) |
| llm-029 | [Scaling laws and the limits of a toy experiment](../../courses/llm-theory/guides/llm-029.md) |
| llm-030 | [Pretraining data provenance and evaluation contamination](../../courses/llm-theory/guides/llm-030.md) |
| llm-031 | [Instruction tuning and loss masks](../../courses/llm-theory/guides/llm-031.md) |
| llm-032 | [Low-rank adaptation without a package download](../../courses/llm-theory/guides/llm-032.md) |
| llm-033 | [Preference objectives and what they do not prove](../../courses/llm-theory/guides/llm-033.md) |
| llm-034 | [Precision and quantization error budgets](../../courses/llm-theory/guides/llm-034.md) |
| llm-035 | [Inference scheduling and cache isolation](../../courses/llm-theory/guides/llm-035.md) |
| llm-036 | [Retrieval: what RAG changes and what it cannot supply](../../courses/llm-theory/guides/llm-036.md) |
| llm-037 | [Evaluate retrieval and answers separately](../../courses/llm-theory/guides/llm-037.md) |
| llm-038 | [Tools, structured output and trust boundaries](../../courses/llm-theory/guides/llm-038.md) |
| llm-039 | [Robustness, fairness and finite safety evidence](../../courses/llm-theory/guides/llm-039.md) |
| llm-040 | [A statistical evaluation and reliability argument](../../courses/llm-theory/guides/llm-040.md) |
| llm-041 | [Optional framework comparison without a second prerequisite](../../courses/llm-theory/guides/llm-041.md) |
| llm-042 | [Capstone: a defensible language-system decision](../../courses/llm-theory/guides/llm-042.md) |
| llm-043 | [Encoder, decoder and encoder-decoder architectures and objectives](../../courses/llm-theory/guides/llm-043.md) |
| llm-044 | [RoPE, relative positions, ALiBi and long-context limits](../../courses/llm-theory/guides/llm-044.md) |
| llm-045 | [Pre/post normalization, RMSNorm and gated feed-forward networks](../../courses/llm-theory/guides/llm-045.md) |
| llm-046 | [MHA, MQA, GQA and blockwise exact attention](../../courses/llm-theory/guides/llm-046.md) |
| llm-047 | [Sparse experts, routing capacity and load balancing](../../courses/llm-theory/guides/llm-047.md) |
| llm-048 | [Exact speculative decoding and cache rollback](../../courses/llm-theory/guides/llm-048.md) |

## Part II: subject assistants and data-science work

The applied route starts by defining the decision, analytical unit and evidence
policy. It then follows documents through ingestion, chunking, indexing,
retrieval, ranking and answer construction. Evaluation separates missing
evidence, unsupported generation, inappropriate abstention and calculation
errors. Access control and provenance apply before a convenient answer is
assembled, not after it has already exposed information.

The adaptation chapters explain why changing model weights and supplying current
retrieved context solve different parts of the problem. Fine-tuning is not an
automatic substitute for a maintained source of facts. RAG does not guarantee
that the selected evidence is relevant or that a generated answer follows it.
The [original RAG paper](https://arxiv.org/abs/2005.11401) and
[LoRA paper](https://arxiv.org/abs/2106.09685) support the mechanism references;
the course derives concrete local examples and their limits.

For data-science use, keep structured computation separate from prose generation.
Define the population and time window, run the authorized calculation, retain
its units and denominator, then explain the result with the available evidence.
The Methods Desk chapters show why an assistant can quote the correct document
and still answer the wrong analytical question.

| Chapter | Topic |
| --- | --- |
| llm-applied-001 | [The subject assistant decision: prompts, retrieval or fine-tuning](../../courses/llm-applied/guides/llm-applied-001.md) |
| llm-applied-002 | [Data-science task contracts and structured extraction](../../courses/llm-applied/guides/llm-applied-002.md) |
| llm-applied-003 | [Prompt and context engineering with measurable boundaries](../../courses/llm-applied/guides/llm-applied-003.md) |
| llm-applied-004 | [Corpus provenance, versions and evaluation isolation](../../courses/llm-applied/guides/llm-applied-004.md) |
| llm-applied-005 | [Chunking, overlap, offsets and context budgets](../../courses/llm-applied/guides/llm-applied-005.md) |
| llm-applied-006 | [Lexical retrieval and BM25 from first principles](../../courses/llm-applied/guides/llm-applied-006.md) |
| llm-applied-007 | [Embedding retrieval, similarity and representation limits](../../courses/llm-applied/guides/llm-applied-007.md) |
| llm-applied-008 | [Hybrid retrieval, reciprocal-rank fusion and reranking](../../courses/llm-applied/guides/llm-applied-008.md) |
| llm-applied-009 | [Metadata filtering and access-controlled retrieval](../../courses/llm-applied/guides/llm-applied-009.md) |
| llm-applied-010 | [Query rewriting and bounded multi-hop retrieval](../../courses/llm-applied/guides/llm-applied-010.md) |
| llm-applied-011 | [Grounded claims, citations and evidence-based abstention](../../courses/llm-applied/guides/llm-applied-011.md) |
| llm-applied-012 | [Evaluating retrieval and answers with oracle controls](../../courses/llm-applied/guides/llm-applied-012.md) |
| llm-applied-013 | [Paired reliability studies and family-aware uncertainty](../../courses/llm-applied/guides/llm-applied-013.md) |
| llm-applied-014 | [Supervised fine-tuning data and answer-target masks](../../courses/llm-applied/guides/llm-applied-014.md) |
| llm-applied-015 | [Full supervised fine-tuning of a tiny causal decoder](../../courses/llm-applied/guides/llm-applied-015.md) |
| llm-applied-016 | [Low-rank adaptation: dimensions, gradients and a real update](../../courses/llm-applied/guides/llm-applied-016.md) |
| llm-applied-017 | [Quantized frozen bases, adapter gradients and QLoRA limits](../../courses/llm-applied/guides/llm-applied-017.md) |
| llm-applied-018 | [Compare full and adapter fine-tuning on frozen tasks](../../courses/llm-applied/guides/llm-applied-018.md) |
| llm-applied-019 | [Preference optimization, DPO and the RLHF distinction](../../courses/llm-applied/guides/llm-applied-019.md) |
| llm-applied-020 | [Fine-tuning embeddings and a small reranker](../../courses/llm-applied/guides/llm-applied-020.md) |
| llm-applied-021 | [Optional pretrained-model adaptation with pinned offline artifacts](../../courses/llm-applied/guides/llm-applied-021.md) |
| llm-applied-022 | [Structured tools for extraction, aggregation and data-science work](../../courses/llm-applied/guides/llm-applied-022.md) |
| llm-applied-023 | [Domain assistant boundaries: freshness, injection, budgets and traces](../../courses/llm-applied/guides/llm-applied-023.md) |
| llm-applied-024 | [Capstone: a grounded and evaluated data-science subject assistant](../../courses/llm-applied/guides/llm-applied-024.md) |

## Companion routes

Use [NLP](../../courses/nlp/README.md) for a broader treatment of text processing,
representation, classification, sequence tasks and language evaluation.
[PyTorch](../../courses/deep-learning-pytorch/README.md) and
[TensorFlow](../../courses/deep-learning-tensorflow/README.md) explain the tensor,
training, state and export machinery in comparable depth. The
[statistics book](../../courses/statistics-ml/README.md) develops the sampling,
modeling, experimentation and causal reasoning needed to judge a data-science
assistant's outputs.

These are connected learning resources, not a certification that reading alone
creates expertise. Reconstruct a mechanism, run the experiment, explain a failure
case, and then apply it to a new question with its assumptions made explicit.
