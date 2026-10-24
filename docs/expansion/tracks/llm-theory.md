# Design: language models, mechanisms and evidence

Status: **planned**, checked against active catalog baseline `75ec445` on
**2026-10-22**. The [structured plan](../plans/llm-theory.json) and
[full pilot](../samples/llm-theory-pilot.md) are design-review artifacts. They
register no new lesson or runner and leave the 168 active lessons unchanged.

## North star and the gap being closed

A learner should explain a language-model component, test what information it
can use, and evaluate a bounded system without treating fluency as evidence of
truth or safety. The track connects mathematical mechanisms to training and
inference failures, then to an honest system decision.

The existing Python material introduces PyTorch and NLP/Hugging Face workflows;
`bridge-ai-01` teaches bounded application behavior. Missing is a staged account
of tokenizer fitting, likelihood units, causal masks, shifted targets, decoder
training, KV-cache equivalence, adaptation objectives and the separation of
retrieval coverage from answer support. Forty-two units close these gaps.
They are not forty-two promises to build a frontier model.

## Entry, placement and reuse

The hard entry ID is active `python-16`. A learner can already write/test Python
and inspect NumPy arrays; previous NLP, calculus, TensorFlow, model downloads or
service accounts are not required. Begin with a distribution summing to one,
a token/byte round trip and a declaration of what a held-out unit means.
Probability, loss and attention math are explained before they are used.

Reuse `python-31`, `python-32`, `python-33`, `python-stats-01`, `python-35` and
`python-ml-02` as targeted review for probability, matrices, uncertainty and
leakage. `python-47` is optional PyTorch review and `bridge-ai-01` is optional
application review. Neither becomes a hidden hard gate: the legacy `python-47`
chain would require unrelated geospatial, deployment and NLP-adjacent work
before the first tiny transformer. The intermediate stage teaches the needed
PyTorch operations in its own context. No TensorFlow lesson is a prerequisite.

## One canonical path and an explicit comparison elective

The beginner stage uses **NumPy float64** and authored local text. The
intermediate/advanced implementation uses **one small PyTorch 2 decoder on
CPU**, reusing the repository's existing `deep-learning` package-profile
policy. The proposed `llm-torch-cpu` logical runtime does not request a second
PyTorch installation or a dependency bump. Retain the repository's
platform-specific lock constraints and prove the required operations on each
target; modern stable documentation is not an installation receipt.

The official PyTorch stable API links resolved to version **2.14** during this
2026-10-22 documentation review. That is the documentation snapshot, not a
proposal to override the repository's existing wheel pins. The teaching model
uses basic tensor operations, Linear/Embedding layers, explicit attention,
cross entropy and AdamW. Fast attention kernels, GQA, accelerators and newer
API conveniences are optional, version-gated studies. Code that uses
`scaled_dot_product_attention` must pass an explicit inference dropout of zero
and respect its include-True mask semantics. Do not transfer a boolean mask
from another API by its name alone.

`llm-041` is an optional reading/comparison unit. It maps NumPy/PyTorch contracts
to documented Keras APIs and can include a TensorFlow experiment only when that
separate runtime is already prepared. The required final capstone depends on
`llm-040`, not `llm-041`. Completing this course never requires both frameworks.

## Resource, offline and data boundaries

The first attention pilot uses three tokens and two features. The canonical
trained model has width 32, two heads, one decoder block, vocabulary at most
128, context at most 32, batch at most 8 and fewer than 50,000 parameters. A
training run has at most 200 optimizer steps and a proposed 120-second wall
cap, including imports; implementation must measure actual targets and report
stops honestly. Larger experiments require a separately declared budget.

Use at most 64 KiB of authored local text, stored with source/permission and
split-family metadata. No pretrained weights, model hub, tokenizer download,
service credential or external embedding endpoint is needed by default.
NumPy and PyTorch are installed only during a deliberate connected setup;
subsequent required labs work offline. A mock retrieval corpus or fake answer
provider is labeled as such and never passed off as a measured LLM service.

Every artifact records tokenizer configuration/hash, corpus version, document
families, split IDs, model configuration, seed/profile, objective reduction and
step count. A changed tokenizer creates a new experiment: token perplexities
from incompatible tokenizations cannot be directly ranked. A frozen test set
is not reused for prompt, retrieval or model selection.

## The teacher and learner journey

The welcome page offers a short NumPy/probability diagnostic and an explicit
reading path when execution is unavailable. The first teaching question is
what a token prediction can establish, not which model endpoint to call.
At the causal-mask pilot, the learner predicts which positions are allowed
before seeing the matrix result. The teacher then changes a future token while
keeping the prefix fixed and asks for an invariant, not a persuasive story.

Each lesson follows explain, saved prediction, own attempt, one progressive
hint, explicit solution comparison, then closed-reference retrieval and a new
transfer case. Save the code, smallest failing input, observed output and the
learner's explanation separately. A successful run does not mark mastery.

At beginner review, ask why a perfect mask does not stop tokenizer/test-set
leakage. At intermediate review, ask the learner to break a cache or loss
mask deliberately and identify the first failed invariant. At advanced review,
separate retriever recall, support for claims, final correctness, abstention,
resource cost and trust boundaries. The reviewer may recommend a no-go.

Use a new fixture for stage assessment. The worked examples and published
solutions are learning material, so reproducing them is an open-book rehearsal,
not independent certification. A paired evaluation keeps the same question IDs;
paraphrases stay grouped by family. Small red-team sets measure those cases,
not universal safety or freedom from bias.

## Coverage and pacing

The structured JSON owns IDs, direct prerequisites, runtime, objective,
concrete lab, independent check and concepts. Units 1-14 are beginner within
this subject, 15-28 intermediate and 29-42 advanced. Unit 41 is elective, so the
required path to the final capstone contains 41 units. Estimates include
reasoning and investigation rather than only execution time.

### Compute the mechanism and challenge the claim

Trace token probabilities, tokenization, attention and a count baseline with NumPy.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `llm-001` | Language-model claims and evaluation units | 75 | Separate predicting tokens from evidence of knowledge, reasoning or reliability. |
| `llm-002` | Scores, stable softmax and probability mass | 90 | Convert finite scores into a stable categorical distribution with an explicit axis. |
| `llm-003` | Conditional probability and a sequence likelihood | 90 | Expand a sequence probability without treating tokens as independent. |
| `llm-004` | A count-based next-token baseline | 105 | Fit and inspect a tiny bigram model before adding neural machinery. |
| `llm-005` | Cross entropy, perplexity and denominator traps | 105 | Compute token loss and compare models only under compatible tokenization and scoring units. |
| `llm-006` | Unicode, bytes and tokenizer round trips | 105 | Trace text through a reversible representation without confusing characters and bytes. |
| `llm-007` | A tiny train-only subword vocabulary | 120 | Learn deterministic merge rules without leaking evaluation text into a tokenizer. |
| `llm-008` | Embedding lookup is a learned table | 90 | Map token IDs to rows and track the feature axis independently of vocabulary size. |
| `llm-009` | Causal attention and prefix invariance | 120 | Prove that a query cannot use later token positions and diagnose a mask that only looks plausible. |
| `llm-010` | Position, order and tokenwise normalization | 105 | Explain why content attention alone does not identify position and preserve causal normalization. |
| `llm-011` | Multiple heads, residuals and a decoder block | 120 | Trace every dimension through a small decoder block and keep residual paths valid. |
| `llm-012` | Greedy decoding, temperature and sampling | 105 | Separate a distribution from the algorithm that selects a token. |
| `llm-013` | A leakage audit before a model score | 105 | Identify target leakage, duplicate documents and test-set reuse independently of mask correctness. |
| `llm-014` | Capstone: a small language-model evidence notebook | 180 | Present a count-based model and an independently tested attention mechanism with bounded claims. |

### Train and inspect a tiny transformer

Build one bounded PyTorch decoder and prove mask, loss, split, restart and cache contracts.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `llm-015` | PyTorch tensors and automatic gradients | 120 | Translate a NumPy calculation to tensors without requiring another deep-learning course. |
| `llm-016` | A tiny causal transformer from explicit parts | 135 | Assemble one decoder block and verify its shape and information boundary before training. |
| `llm-017` | Shifted batches, padding and token loss | 120 | Align inputs, targets and ignored padding without changing the evaluation denominator. |
| `llm-018` | A bounded training loop with visible state | 135 | Implement forward, loss, zero_grad, backward and optimizer.step in the correct order. |
| `llm-019` | Overfit one batch to diagnose the loop | 120 | Use a deliberately tiny overfit experiment to separate implementation failure from generalization. |
| `llm-020` | Initialization and residual scale | 120 | Locate unstable activations and gradients without blaming data first. |
| `llm-021` | Document splits and contamination controls | 120 | Design a corpus split around the source unit and freeze it before model selection. |
| `llm-022` | Reproducibility, evaluation mode and restart | 120 | Distinguish repeatable inference from repeatable training and preserve optimizer state. |
| `llm-023` | Top-p, termination and decoding failure cases | 120 | Implement a bounded decoder with explicit sampling and stop conditions. |
| `llm-024` | KV caches and incremental equivalence | 135 | Prove a cache optimization preserves the uncached causal computation. |
| `llm-025` | Memory and compute without a GPU | 120 | Estimate attention and cache costs before choosing a context size. |
| `llm-026` | What a representation probe establishes | 105 | Distinguish accessible information from a causal explanation of a model decision. |
| `llm-027` | Calibration and comparable evaluation | 120 | Report predictive confidence under an explicit scoring and grouping policy. |
| `llm-028` | Capstone: train and audit a tiny transformer | 240 | Defend a bounded local training run with a frozen corpus and diagnostic evidence. |

### Evaluate adaptation and complete language systems

Assess adaptation, retrieval, tools and reliability without conflating a small test with a safety guarantee.

| ID | Lesson | Minutes | Observable finish |
| --- | --- | ---: | --- |
| `llm-029` | Scaling laws and the limits of a toy experiment | 105 | Interpret a scaling claim without extrapolating a tiny classroom fit to frontier systems. |
| `llm-030` | Pretraining data provenance and evaluation contamination | 120 | Specify provenance and removal policies before training or evaluating on collected text. |
| `llm-031` | Instruction tuning and loss masks | 135 | Explain how a supervised objective changes when only answer tokens receive loss. |
| `llm-032` | Low-rank adaptation without a package download | 135 | Derive and test a low-rank update while keeping base weights frozen. |
| `llm-033` | Preference objectives and what they do not prove | 120 | Compute a preference loss and separate preference evidence from factual correctness. |
| `llm-034` | Precision and quantization error budgets | 120 | Measure a toy quantization tradeoff rather than claiming universal compression quality. |
| `llm-035` | Inference scheduling and cache isolation | 120 | Keep request ownership and stop conditions correct when batching inference. |
| `llm-036` | Retrieval: what RAG changes and what it cannot supply | 120 | Separate retrieval coverage from generation faithfulness and model knowledge. |
| `llm-037` | Evaluate retrieval and answers separately | 120 | Identify whether an observed failure came from retrieval, reasoning or unsupported citation. |
| `llm-038` | Tools, structured output and trust boundaries | 120 | Represent a tool request as untrusted data and require a separate authorization boundary. |
| `llm-039` | Robustness, fairness and finite safety evidence | 120 | Turn a broad safety claim into a scoped test plan with explicit missing coverage. |
| `llm-040` | A statistical evaluation and reliability argument | 135 | Choose paired units and uncertainty before comparing complete systems. |
| `llm-041` | Optional framework comparison without a second prerequisite | 105 | Translate attention contracts without requiring TensorFlow to complete the LLM route. |
| `llm-042` | Capstone: a defensible language-system decision | 270 | Recommend a bounded system only when its evidence and operating limits support the intended use. |


## Capstone review gates

### llm-014: A language-model evidence notebook

Use local counts and attention invariants to distinguish implementation evidence from a broad model claim.

**Deliverables**

- training-only tokenizer/count baseline
- fixed document split and NLL/perplexity worksheet
- causal-mask tests and a leakage counterexample

**Acceptance**

- Every conditional distribution sums to 1.
- Token and document denominators are declared.
- Prefix invariance and malformed-mask checks pass.
- No online model or pretrained asset is needed.

### llm-028: A tiny transformer under a hard budget

Train and inspect one CPU decoder on a small local corpus.

**Deliverables**

- model/tokenizer/split hashes and configuration
- <=200-step log and held-out baseline comparison
- mask/cache/restore tests and error analysis

**Acceptance**

- Parameter count<50000 and context<=32.
- Training, selection and test documents are disjoint.
- Fresh inference and cache equivalence match within 1e-6.
- A completed budget is not reported as proof of useful generalization.

### llm-042: A defensible language-system decision

Compare bounded alternatives and recommend a system or a justified no-go.

**Deliverables**

- frozen question-family evaluation set
- paired baseline/transformer/retrieval result table
- retrieval/support/abstention and trust-boundary evidence
- resource manifest, limitations and go/no-go rationale

**Acceptance**

- No test-set prompt tuning or document-family leakage occurs.
- Claims cite the evaluation unit and preserve paired samples.
- Unsupported answers, missing retrieval and unsafe tool proposals are counted separately.
- No TensorFlow installation or hosted service is required.

## Failure cases the author must preserve


Keep counterexamples for post-softmax masking, wrong boolean polarity, a fully
masked row, unshifted labels, tokenizer fitting on validation, duplicate document
families, padding in the denominator, dropout during evaluation, stale position
offsets, cross-request KV reuse, incomparable perplexities, unsupported RAG
citations, prompt injection treated as authority and preference scores treated
as factual correctness. A zero observed failure count is still a finite result.

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

- The plan has 42 unique lessons, 14 per stage, and three capstones. The shared
  design validator accepts its references and prerequisite graph. The final
  required capstone directly depends on `llm-040`; the optional TensorFlow
  comparison `llm-041` is outside that path. The 168-lesson active catalog is
  byte-identical to baseline `75ec445`.
- The JSON pilot, the guide's two Python blocks and the solution's seven Python
  blocks parse successfully. They execute in three separate fresh namespaces
  using an existing prepared interpreter with NumPy 2.4.6, without installation.
- All six solution exercises pass: exact mixtures and row sums, future-value
  mutation, independently recomputed nonuniform prefixes, the broken
  post-softmax mask, five invalid-input cases, and shifted-target/family-leakage
  checks. Comparisons use `rtol=0, atol=1e-12`.
- Additional NumPy checks verify unmasked permutation equivariance and its
  failure under an unchanged causal-order mask, the quantization fixture's
  full-precision output, and the threshold-crossing top-p example.
- No PyTorch transformer training, pretrained weight, hosted service, package
  installation or image build was performed. Later training/cache/adaptation
  labs and cross-platform resource budgets remain implementation gates.

The pilot contains two worked examples, six distinct Expected/Verify contracts,
three hints, retrieval and a separate six-section solution. Execution proves
only these fixed local checks, not language-model quality or complete-system
safety. The remaining 41 lesson bodies are still planned.

## Primary sources and compatibility review

Every source below was opened during the design review on **2026-10-22**.
Version/platform guidance is time-sensitive and must be checked again when
creating a runtime lock. A primary document supports a design choice; it is
not proof that a particular machine executed the course.

- [Attention Is All You Need](https://arxiv.org/abs/1706.03762), checked 2026-10-22. Scaled dot-product attention, positional information, multihead composition and decoder masking; the course adds independent causal invariants.
- [PyTorch scaled dot-product attention](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html), checked 2026-10-22. API-specific mask polarity, causal behavior and explicit dropout_p control. The stable alias resolved to 2.14 at review; this is not a dependency upgrade request.
- [PyTorch cross entropy](https://docs.pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html), checked 2026-10-22. Class-index targets, ignore_index and reduction semantics.
- [Subword units with byte pair encoding](https://arxiv.org/abs/1508.07909), checked 2026-10-22. Subword segmentation by learned merge operations; training-only vocabulary fitting is an explicit course evaluation rule.
- [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751), checked 2026-10-22. Nucleus sampling as a decoding method, not a correctness guarantee.
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), checked 2026-10-22. Retrieval plus generation as distinct mechanisms; retrieval does not establish answer support by itself.
- [LoRA](https://arxiv.org/abs/2106.09685), checked 2026-10-22. Low-rank adaptation with a frozen base; the course uses a tiny explicit matrix experiment.
- [Direct Preference Optimization](https://arxiv.org/abs/2305.18290), checked 2026-10-22. Preference loss relative to a reference policy; preference optimization is not proof of factual accuracy.
- [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556), checked 2026-10-22. Controlled parameter/data/compute tradeoffs and the limits of extrapolating classroom experiments.
