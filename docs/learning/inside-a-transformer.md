# Inside a Transformer: from text to a trained prediction

This companion connects the pieces taught across the LLM journey. Read it once
for the overall picture, then revisit each mechanism alongside its dedicated
lesson. It assumes basic Python arrays and multiplication. A **parameter** is
a number adjusted during training; an **activation** is a number computed for
the current input. Keeping those two kinds of numbers separate makes almost
every later explanation easier.

The complete [NumPy walkthrough program](examples/transformer_forward.py)
runs without network access or pretrained weights. It is deliberately small
enough to inspect. Open an authored `python-core` lesson, save any existing pad,
and paste the complete program into that pad to run it in Docker. The filename
does not matter for the Python pad. Alternatively, run the downloaded file in
a prepared Python environment with NumPy. The program includes its own checks
and prints the observations discussed below.

## 1. What the model is trying to compute

A causal language model predicts a probability distribution for the next token
given the tokens already visible. For a sequence of token IDs `x0,x1,x2`, the
probability assigned to the sequence factors into conditional probabilities.
With an explicit start context, the factorization is:

```text
P(x0,x1,x2 | start)
  = P(x0 | start) × P(x1 | start,x0) × P(x2 | start,x0,x1)
```

That identity does not specify a neural network. A table of counts can estimate
the conditionals too. The Transformer is a flexible way to calculate them from
a long, changing context while sharing learned parameters across positions.
A good next-token model can support completion, translation, classification,
code generation and dialogue when those tasks are represented as sequences.
The objective alone does not guarantee factual accuracy, reliable reasoning,
privacy, good calibration or compliance with an instruction.

Suppose a model assigns the next observed tokens probabilities `0.5,0.25,0.1`.
The sequence probability is `0.0125`. Multiplying many small probabilities
underflows, so training sums negative logarithms instead. The three losses
are approximately `0.693,1.386,2.303` nats. Their mean is `1.461`, and the
corresponding perplexity is `exp(1.461)`, approximately `4.31`. Perplexity is a
transformation of mean token loss. Comparisons require compatible tokenization,
target masks, datasets and aggregation rules. It is not a direct percentage of
correct facts.

Continue with [conditional likelihood](../../courses/llm-theory/guides/llm-003.md)
and [cross entropy and denominators](../../courses/llm-theory/guides/llm-005.md).

## 2. Text becomes IDs before it becomes vectors

A tokenizer maps text into a sequence of integer IDs. Tokens might correspond
to bytes, fragments of words, whole words or special markers. The vocabulary
is the finite set of available IDs. The number `42` is a label, not a statement
that its token is numerically halfway between tokens `41` and `43`.

Tokenization choices affect sequence length and which patterns the model must
learn. The string `unhappiness` might be one token or several. A rare identifier
or language can require more tokens than a common English word. Context and
billing limits usually count tokens rather than words. Whitespace, Unicode
normalization and special-token handling also matter. A tokenizer must not
silently turn a literal user string into a privileged instruction delimiter.

For the walkthrough, use a deliberately artificial four-token vocabulary:

| Token | ID | Initial embedding |
| --- | ---: | --- |
| red | 0 | `[1,0,-1,0]` |
| fox | 1 | `[0,1,0,-1]` |
| runs | 2 | `[1,1,0,-1]` |
| `<end>` | 3 | `[-1,0,1,1]` |

An embedding table with vocabulary size `V` and feature width `D` has shape
`[V,D]`. Looking up IDs `[0,1,2]` selects three rows, producing `[T,D]` with
`T=3`. A batch adds a leading dimension, giving `[B,T,D]`. The table is usually
learned. A repeated token initially selects the same row, but later layers
produce different contextual representations when its surroundings differ.

Do not interpret each feature coordinate as a named linguistic concept.
The coordinates jointly support a learned computation, and rotating a
representation together with compatible downstream weights can preserve
behavior. A visualization of nearby embeddings is useful evidence about that
representation, not proof of a human-like semantic taxonomy.

The walkthrough adds a small fixed position table to the embedding rows.
This makes position visible without adding much arithmetic. Real models use
several position schemes. RoPE rotates query and key coordinates as a function
of position; it does not simply append a position ID to the text. Longer
position ranges require separate evaluation, even when the formula can be
evaluated there. See [tokenization](../../courses/llm-theory/guides/llm-007.md),
[embedding lookup](../../courses/llm-theory/guides/llm-008.md) and
[position methods](../../courses/llm-theory/guides/llm-044.md).

## 3. Attention: a learned way to mix information across positions

Each position needs information from other permitted positions. Self-attention
builds three projections from the current token representations:

```text
Q = X Wq          queries: what this position uses to select information
K = X Wk          keys: what other positions expose for that comparison
V = X Wv          values: the information mixed after selection
```

The words query, key and value are an intuition for matrix operations. They
are not stored natural-language questions, database keys or dictionary values.
In one head, `Q` and `K` have shape `[T,dh]`. Their product `Q K^T` has shape
`[T,T]`: row `i`, column `j` is the compatibility of query position `i` with
key position `j`. Divide scores by `sqrt(dh)`, apply the allowed-position mask,
then normalize each query row with softmax. Multiplying the resulting weights
by `V` produces a weighted combination of value vectors for every query.
This is the scaled dot-product mechanism introduced in the
[Transformer paper](https://arxiv.org/abs/1706.03762).

The normalization axis is crucial. With score row `[0,log(3)]`, exponentiating
gives `[1,3]` and dividing by the row sum gives `[0.25,0.75]`. If the two value
vectors are `[2,0]` and `[0,4]`, the mixture is `[0.5,3]`. Normalizing columns
instead would answer a different question: it would distribute each key's
mass among queries. Every allowed query row must have probability mass one.

For numerical stability, subtract the largest allowed score before
exponentiating. This changes neither the probabilities nor their sum because
the common exponential factor cancels. It prevents overflow for large positive
scores. If every position is masked, there is no probability distribution to
normalize. Reject that row or handle it using an explicitly defined padding
contract; do not silently divide zero by zero.

### Why the causal mask matters

During next-token training, the full training sequence is already in memory.
Without a mask, the representation used to predict `fox` could inspect `fox`
itself or later words. The model could reduce its training loss by using
information unavailable during generation.

For a three-position decoder input, the permitted-key matrix is:

```text
             key0  key1  key2
query0         1     0     0
query1         1     1     0
query2         1     1     1
```

The diagonal is permitted: the representation at input position 0 can use the
input token at position 0 to predict the target at position 1. Shifted targets
are what make this valid. The walkthrough obtains this first-head matrix:

```text
[[1.000000, 0.000000, 0.000000],
 [0.218664, 0.781336, 0.000000],
 [0.280402, 0.339558, 0.380041]]
```

The zeros above the diagonal are structural, not merely very small learned
preferences. The first position can attend only to itself. The second mixes
the first two positions. Changing the third input token must leave the first
two output rows unchanged. That **prefix-invariance** test is stronger than
checking that a matrix happens to contain zeros: it can catch future leakage
through another operation, such as normalization across the sequence.

Continue with [causal attention](../../courses/llm-theory/guides/llm-009.md).
When using a framework API, check its documented mask convention. Boolean
`True` can mean allowed in one API and blocked in another. The
[PyTorch scaled-dot-product API](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html)
also applies the requested dropout probability during the call; callers must
pass zero explicitly for evaluation when that API requires it.

## 4. Multiple heads, residual paths and nonlinear transformations

The walkthrough has feature width `D=4` and two heads of width `dh=2`. It
reshapes `[T,4]` into `[H,T,2]`, computes attention independently per head,
then joins the outputs back into `[T,4]`. For a general batch:

| Quantity | Shape | Meaning of the last dimensions |
| --- | --- | --- |
| token representations | `[B,T,D]` | positions, features |
| query/key/value heads | `[B,H,T,dh]` | heads, positions, head features |
| attention scores | `[B,H,T,T]` | query positions, key positions |
| per-head mixtures | `[B,H,T,dh]` | positions, mixed value features |
| joined output | `[B,T,H×dh]` | concatenated head features |
| vocabulary logits | `[B,T,V]` | a score for every next-token candidate |

Different learned projections allow heads to calculate different mixtures.
Head count is not a count of human-interpretable skills, and a head with an
interesting visualization need not be solely responsible for that behavior.
The walkthrough deliberately sets query, key, value and output projections to
identities so the numbers stay inspectable. Trained models generally learn
different matrices. These identity weights are a teaching simplification.

A residual connection adds the sublayer's result to its input. This preserves
a direct route for information and gradients while the sublayer learns a
change to the representation. It does not mean that early tokens bypass the
attention mask. Both branches still need to respect the causal information
boundary.

The block also needs a positionwise nonlinear transformation, usually called
the feed-forward network or MLP. Attention mixes across positions; the MLP
transforms feature combinations within each position using shared weights.
An ordinary MLP expands feature width, applies a nonlinear activation and
projects back. Without a nonlinearity, consecutive affine transformations
could collapse into a single affine map. Modern gated alternatives such as
SwiGLU use a learned multiplicative gate. The walkthrough uses a much smaller
fixed ReLU map to expose the role of nonlinearity without a large weight table.

Layer normalization computes a mean and variance across one token's feature
coordinates. It rescales that token's values using an epsilon to avoid division
by zero. Normalizing over all token positions instead can leak future
information. Pre-normalized and post-normalized block arrangements place this
operation differently and have different optimization behavior. The example
uses pre-normalized attention and MLP branches, then a final normalization.
Real implementations can have learned scale/bias parameters; the walkthrough
omits them explicitly. Read [decoder blocks](../../courses/llm-theory/guides/llm-011.md)
and [normalization and gates](../../courses/llm-theory/guides/llm-045.md).

## 5. From the final representation to a loss

The output projection maps each final feature vector to `V` logits. A logit
is an unnormalized score; a negative logit is allowed. Softmax converts the
scores into a probability distribution. The walkthrough starts its output
projection from the transpose of the embedding table, then copies it so a
later update does not mutate the embeddings. Production models sometimes tie
these weights, in which case gradients update their shared parameter.

The input and target arrays are deliberately shifted:

| Input prefix represented by a row | Target for that row |
| --- | --- |
| red | fox |
| red fox | runs |
| red fox runs | `<end>` |

For the last row, the untrained walkthrough assigns probabilities approximately
`[0.081183,0.271301,0.645946,0.001570]`. Its most likely next token is `runs`,
which is the wrong training target. That is expected: hand-chosen parameters
have not learned an English language model. Correct attention arithmetic does
not imply a useful predictor.

The mean target loss is approximately `3.388133`. The target mask and
denominator determine what this mean means. When examples have padding, exclude
padded target positions from both the loss sum and the active-token count.
For instruction tuning, it is common to train on assistant response tokens
while still making prompt tokens visible in attention. **Visible context** and
**scored targets** are different masks. See [shifted training batches](../../courses/llm-theory/guides/llm-017.md)
and [instruction-target masks](../../courses/llm-theory/guides/llm-031.md).

### One update you can derive

For one target token, softmax cross entropy has logit gradient `p - one_hot(y)`.
If the correct class has probability `0.1`, its component is `-0.9`; moving
against the gradient increases its logit. Incorrect classes have positive
components, so their logits decrease. The components sum to zero, reflecting
the fact that adding one constant to every logit changes no probabilities.

With frozen final features `F` and output weights `W`, the average gradient is
`F^T (P-Y) / N`. The program checks one element using a central finite
difference: perturb that weight by `+epsilon` and `-epsilon`, recompute both
losses, and divide their difference by `2×epsilon`. This independently checks
the analytic derivative without relying on an automatic differentiation engine.
An excessively small epsilon introduces subtraction error; an excessively
large one estimates a broad secant instead of a local derivative.

Taking a step of size `0.05` reduces this fixture's mean loss to approximately
`3.326634`. This is **one output-head update with frozen features**. It is not
full Transformer training, and a lower training loss on three targets says
nothing about held-out language quality. In a fully trained network, automatic
differentiation carries gradients through the MLP, attention, projections and
embedding lookups. The optimizer updates the selected parameters, and repeated
batches provide the training signal. The actual tiny-Transformer course builds
that whole loop in [llm-016](../../courses/llm-theory/guides/llm-016.md),
[llm-018](../../courses/llm-theory/guides/llm-018.md) and
[the training capstone](../../courses/llm-theory/guides/llm-028.md).

## 6. Why training can be parallel while generation is sequential

In ordinary teacher-forced training, the true prefix tokens are available.
All positions in a batch can compute predictions concurrently while the mask
prevents future access. During generation, the next input token is the token
just selected by the decoding procedure. It is unavailable until the previous
step finishes. The model appends it, calculates the next distribution, and
continues until a stop condition or budget is reached.

Greedy decoding chooses the largest logit. Sampling draws from a distribution.
Temperature divides logits before softmax: a smaller positive temperature
concentrates the distribution; a larger one flattens it. Top-p sampling retains
a probability-mass prefix under a specified sorting and cutoff rule. These
choices change generated output distributions without retraining the model.
They do not constitute a factuality guarantee. A model can confidently repeat
a wrong completion, and random sampling can produce different wrong answers.

The generated prefix is now partly the model's own output. An early error can
change later context. Record decoding settings when comparing two systems,
along with the prompt, tokenizer, weights, stop rules and maximum output
length. Otherwise a changed answer may be attributed to the wrong component.

### What a KV cache saves

During causal generation, earlier positions do not change when a token is
appended. Their previously computed keys and values can be reused at each
layer. The new token still needs its own query/key/value and a comparison with
the available cached keys. A cache saves repeated computation over earlier
tokens; it does not make long-context attention constant-cost.

For batch size `B`, layers `L`, cached positions `T`, key/value heads `Hkv`,
head width `dh`, and `s` bytes per stored scalar, the idealized K/V storage is
`2×B×L×T×Hkv×dh×s` bytes. The leading 2 accounts for keys and values. It excludes
allocator overhead, attention workspace, logits and model weights. Grouped
query attention uses fewer key/value heads than query heads, reducing this
term. It changes the model architecture and requires compatible weights.
Never estimate memory from parameter count alone.

Cache reuse must preserve positions, masks, request identity and the exact
model state. A cache accidentally shared across users can mix private context.
After a speculative branch is rejected, stale K/V entries must be removed
before continuing. The course tests numerical equivalence and rollback in
[llm-024](../../courses/llm-theory/guides/llm-024.md),
[llm-046](../../courses/llm-theory/guides/llm-046.md) and
[llm-048](../../courses/llm-theory/guides/llm-048.md).

## 7. Where pretraining, fine-tuning and RAG fit

**Pretraining** learns broad statistical patterns from a chosen corpus and
objective. Corpus composition, duplication, licenses, filtering and evaluation
contamination affect what its results mean. A training run on a tiny fixture
teaches mechanics but cannot establish scaling behavior for a large model.

**Supervised fine-tuning** continues optimization on examples of desired
behavior, often prompts paired with responses. It can teach output structure,
task conventions and domain-specific patterns. Training answers need quality
control and evaluation isolation. If all examples contain an answer, the model
may learn to answer confidently even when evidence is missing. Include the
actual abstention and uncertainty behaviors the application needs, then test
them on held-out families of cases.

Full fine-tuning updates the selected base weights. LoRA freezes a base matrix
and trains a low-rank update. For `W` of shape `[out,in]`, write
`W_effective = W + scale × B A`, with `A:[r,in]` and `B:[out,r]`. The additional
parameter count is `r×(in+out)`, rather than `in×out`. This reduces trainable
state, but activations and the frozen base still consume memory. Rank is a
capacity choice, not a guaranteed quality setting. The original
[LoRA work](https://arxiv.org/abs/2106.09685) motivates this construction;
the course demonstrates an actual adapter update in
[llm-applied-016](../../courses/llm-applied/guides/llm-applied-016.md).

**Retrieval-augmented generation**, or RAG, retrieves external evidence and
places selected material in the generator's context. A simple RAG application
can use frozen generator weights. The original
[RAG research](https://arxiv.org/abs/2005.11401) also studied joint learned
retrieval/generation formulations. Keep the architecture of the particular
system explicit instead of assuming every product called RAG is identical.

For a changing company handbook, retrieval gives you a practical way to use
the current approved document and cite its version. Fine-tuning can teach the
assistant to format answers and abstain appropriately. The two mechanisms can
be combined, but neither repairs an unauthorized or irrelevant source. The
retrieved text is evidence to inspect, not a privileged instruction channel.

Evaluate the pipeline in parts: did retrieval find the required passage; did
the selected context retain it; does each answer claim follow from that
context; are citations accurate; does the system decline unsupported requests?
An oracle-context experiment, where the correct passage is supplied directly,
helps distinguish retrieval failures from generator failures. Conversely, a
correct answer from memory can hide a broken retrieval stage. Start with
[the adaptation decision](../../courses/llm-applied/guides/llm-applied-001.md)
and [retrieval/answer evaluation](../../courses/llm-applied/guides/llm-applied-012.md).

## 8. A concrete data-science assistant design

Consider an assistant that explains a team's experiment metrics. A useful
answer needs the current metric definition, eligibility rules, allocation unit,
window, data quality checks and uncertainty method. Store those definitions in
versioned documents. Retrieve the relevant approved passages for a question,
including the definition's effective date. Ask the model for a structured
interpretation with evidence IDs and unresolved assumptions.

Use reviewed Python or SQL tools to calculate aggregates. Do not treat
model-generated arithmetic as the measurement. Validate tool arguments against
an explicit schema, select only permitted data sources, and bind values in SQL.
A read-only tool should remain read-only regardless of the text in a retrieved
document. Record the query, data version and result so the answer can be
reconstructed later.

Build a held-out evaluation set by independent business question or document
family. Rephrasing the same question ten times does not provide ten independent
cases. Include missing definitions, ambiguous time windows, outdated policies,
conflicting documents, empty groups and requests outside the assistant's data
access. Score evidence correctness and numerical correctness separately from
fluency. A polished unsupported answer is still a failed result.

If you then fine-tune, keep the evaluation families out of training and
retrieval-development decisions. Compare the same tasks against a prompt-only
baseline, a retrieval baseline and the proposed adapted system. Report cost,
latency, unsupported-answer rate and meaningful task quality together. A tiny
average improvement does not excuse a large regression on a critical slice.
Use [the applied assistant capstone](../../courses/llm-applied/guides/llm-applied-024.md)
to assemble those pieces and [statistical evaluation](../../courses/llm-theory/guides/llm-040.md)
to reason about the strength of the evidence.

## 9. Diagnose a model by the first broken contract

| Observation | Inspect first | Why this distinguishes causes |
| --- | --- | --- |
| Earlier predictions change when a future token changes | mask, normalization axes, positional state | causal leakage can occur outside attention too |
| Loss looks unusually good immediately | target shift, split boundaries, accidental target visibility | a shortcut can mimic learning |
| Loss is NaN | legal-key count, logits, finite values, reduction denominator | all-masked rows and empty targets have no valid normalization |
| Training falls while validation worsens | family split, duplication, capacity, regularization | optimization success and generalization are different |
| Full and cached decoding disagree | positions, cache length, mask offsets, evaluation/dropout mode | compare the first mismatching token before later errors accumulate |
| An adapter has zero useful effect | trainable flags, gradient flow, initialization, saved adapter loading | a completed loop does not prove intended weights changed |
| A RAG answer is unsupported | retrieval, context selection, claim-level evidence | fluent generation cannot restore missing evidence |

The walkthrough establishes a small set of exact computational properties.
The broader journey adds learned projections, automatic differentiation,
training loops, caches, adapter updates, retrieval and reliability studies.
Keep each claim matched to its evidence: source code shows an intended
algorithm, a passing execution shows one run, and held-out experiments support
only the population and conditions they actually examined.
