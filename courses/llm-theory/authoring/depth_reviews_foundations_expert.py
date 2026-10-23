"""Prose-only reviews for directly maintained foundations and expert guides.

Python worked blocks and executable references are deliberately unchanged.
"""

from __future__ import annotations

# Long lines retain authored Markdown paragraphs.
# ruff: noqa: E501
import re

REVIEWS: dict[int, dict[str, object]] = {}


def review(number: int, findings: list[str], body: str, diagnosis: str = "") -> None:
    REVIEWS[number] = {"findings": findings, "body": body.strip(), "diagnosis": diagnosis.strip()}


review(
    1,
    [
        "Connected the evaluation unit to the intended deployment population",
        "Added paired change, abstention and contamination counterexamples",
    ],
    r"""
## From a fluent answer to a defensible measurement

A useful model claim identifies a task, an input distribution, an observable outcome and a decision. Consider a document assistant asked to extract the renewal date from a contract. The task is not simply "write good text." The input is a particular version of a document, the desired output is a date or an explicit abstention, and the correctness rule must specify which clause governs. A fluent date with no supporting clause can fail the task even when every sentence is grammatical. Conversely, a terse structured answer can succeed. Fix that contract before choosing a score.

Let c_i be 1 when question i passes the declared rule and 0 otherwise. Record accuracy is sum_i c_i / N for N questions. If questions belong to G source families, equal-family accuracy is (1/G) sum_g [(1/n_g) sum_(i in g) c_i]. Here n_g is the number of questions in family g. These formulas differ only in weighting, but that difference changes the population represented by the summary. Equal-family weighting can suit a target where each source family matters equally. Record weighting can suit a workload whose actual question frequencies resemble the sample. Neither formula automatically chooses the right deployment distribution.

In the worked table, adding eight more correct paraphrases to family A changes record accuracy from 2/3 to 10/11, while the equal-family value remains 1/2. The apparent record improvement did not add a new source family or fix the failure in B. This is an exact arithmetic counterexample to treating every added row as independent evidence. Group-aware splitting keeps related source material together; family-weighted reporting answers a weighting question. These are complementary controls. Weighting alone cannot repair a train/test overlap.

When comparing two versions, retain paired outcomes on the same questions. Suppose version A is right on q1 and q2, and version B is right on q1 and q3. Both score 2/3, but one previously successful case regressed while one failure improved. A single aggregate hides that exchange. Record the changed cases, their source families and failure categories. A paired comparison controls which cases were asked; it does not remove uncertainty about unobserved families or guarantee that the reference answers are valid.

Abstention changes the decision contract too. If an assistant answers two of three questions correctly and abstains on the third, answer-only accuracy is 2/2, coverage is 2/3, and answered-correct fraction over all requests is 2/3. The 100 percent figure alone conceals a third of requests receiving no answer. When unsupported answers are costly, that may be a useful tradeoff, but it must be a deliberate policy with coverage and error costs reported together. A system that abstains on every request has no defined answer-only accuracy; assigning it a perfect score would be a denominator mistake.

Mechanism tests and empirical tests catch different faults. A causal-mask test can show that later token values do not affect an earlier output under the supplied computation. It cannot show that a training corpus excluded the evaluation answer. A held-out answer check can expose a factual error without identifying the exact internal mechanism that caused it. Start diagnosis at the narrowest supported statement: what changed, which condition was violated, and which alternative explanations remain. Avoid translating a passed component test into a broader claim about knowledge or reasoning.

For data-science work, keep the numerical analysis independently executable. An LLM can suggest a query, summarize a result or propose an interpretation, but a generated explanation does not establish that the query ran against the intended dataset, that an estimator's assumptions hold, or that a correlation is causal. Preserve dataset/version identity, executable code and computed outputs separately from narrative. The applied assistant route develops that distinction through [grounded claims](../../llm-applied/guides/llm-applied-011.md) and [retrieval and answer evaluation](../../llm-applied/guides/llm-applied-012.md).

**Interview reasoning:** "Would more evaluation questions settle the reliability question?" More independent, representative observations can improve an estimate. More copies of an easy family may mainly change its weight. First inspect provenance, relatedness, coverage and the correctness rule, then decide what new cases would challenge the current conclusion. The three-row lesson table is enough to demonstrate the weighting mechanism; it is not enough to establish a stable population estimate.
""",
)

review(
    2,
    [
        "Derived softmax shift invariance, log odds and gradient coupling",
        "Explained masking order and temperature without equating probabilities with factual confidence",
    ],
    r"""
## Derive the normalizer before trusting the numbers

For K candidates with finite scores z_1 through z_K, define Z=sum_j exp(z_j) and p_i=exp(z_i)/Z. The denominator is shared by every candidate in one decision. Increasing one score can therefore lower other candidates' probabilities even when their own scores do not change. A row of a matrix is one decision in this lesson. Summing over the entire matrix instead mixes decisions and changes the question being answered.

Subtracting the same constant c from every score preserves the distribution because exp(z_i-c)=exp(z_i)exp(-c); that common factor cancels from numerator and denominator. Choosing c=max_j z_j ensures that every exponential is at most one and that at least one is exactly one. This avoids unnecessary overflow in exponentiation and keeps the denominator positive. Very small relative masses can still underflow to zero. Numerical stability means avoiding avoidable representation failure, not representing every arbitrarily small probability exactly.

The two-candidate case exposes the meaning of a score difference. Algebra gives p_1=1/[1+exp(z_2-z_1)] and p_1/p_2=exp(z_1-z_2). Scores [log(3),0] therefore yield [3/4,1/4]. Adding 1000 changes neither ratio. Dividing by temperature T changes the ratio to exp[(z_1-z_2)/T]. At T=2 the same pair becomes [sqrt(3)/(sqrt(3)+1),1/(sqrt(3)+1)], approximately [.634,.366]. The ranking is unchanged for positive T, while the separation shrinks. As T approaches zero from above, mass concentrates on maximal scores; a tie can retain multiple maxima. T=0 is not a valid divisor in this formula.

A forbidden candidate must be excluded before the maximum and denominator are formed. With allowed scores [0,0] and a forbidden score 1000, the intended weights are [.5,.5,0]. Computing softmax over all three and setting the third result to zero afterward leaves the first two near zero, so the row no longer sums to one. Multiplying a forbidden score by zero before softmax is also wrong: a score of zero contributes exp(0)=1. The reference's negative-infinity mask removes forbidden mass, and its all-masked-row check prevents normalizing an empty choice set.

The Jacobian explains gradient coupling. Differentiate p_i with respect to z_j to obtain p_i(delta_ij-p_j), where delta_ij is 1 for i=j and 0 otherwise. The diagonal p_i(1-p_i) is nonnegative; off-diagonal terms -p_i p_j are nonpositive. For p=[.75,.25], the matrix is [[.1875,-.1875],[-.1875,.1875]]. Each row sums to zero because a common shift must have no effect. This identity is a useful independent check of a later backward implementation.

For one observed target y, loss L=-log p_y has derivative dL/dz_j=p_j-1[j=y]. If candidate2 is the target in the [.75,.25] example, the gradient is [.75,-.75]. A small gradient-descent step lowers score1 and raises score2. A temperature inside the training softmax adds the factor 1/T to this derivative. That statement concerns this defined objective; changing a serving temperature after training does not run this gradient update or make the resulting probabilities calibrated.

Diagnose failures by inspecting the first broken invariant: finite scores, a nonempty allowed set, the intended key/candidate axis, finite shifted allowed scores, nonnegative mass, positive denominator and unit row sum. A unit sum alone cannot reveal a wrong axis or a swapped candidate identity. Retain a nonuniform example such as [log(3),0], since equal scores cannot expose every scaling error. The probabilities describe choices under a scoring rule. Their numerical normalization is not evidence that the favored answer is true.

**Interview reasoning:** "Why not subtract the mean instead of the maximum?" Any common offset preserves the exact mathematical distribution. The maximum specifically prevents positive exponent arguments. A mean can leave an enormous positive score difference and therefore fail to prevent overflow. The choice of maximum is a numerical implementation decision supported by the cancellation identity.
""",
)

review(
    3,
    [
        "Distinguished joint sequence probability from a probability conditioned on a fixed prefix",
        "Added EOS, teacher-forcing and ordering counterexamples",
    ],
    r"""
## A sequence score is a chain of declared events

For a token sequence x_1 through x_T, the chain rule is P(x_1,...,x_T)=product_t P(x_t | x_1,...,x_(t-1)). This is an identity of probability, not an independence assumption. A model may approximate each conditional using a restricted context, such as only the preceding token, but that restriction is an additional modeling choice. The three numbers in Example A are the probabilities of the three observed targets at their respective contexts. They are not three probabilities from one categorical row and need not sum to one.

Distinguish scoring a full sequence from scoring a suffix. If a prompt u is supplied and held fixed, an answer score is P(y|u), the product of conditionals for answer targets only. Including prompt tokens changes the scored event and denominator. Suppose a prompt contributes a large, easy block of targets while the answer remains difficult. Averaging over prompt and answer can make a model appear better at answering without improving any answer prediction. The scoring policy should say which tokens are context only and which are observations being scored.

A complete finite-string model also needs a termination convention. With an explicit end-of-sequence token EOS, the probability of the exact string includes the conditional probability of stopping after its last content token. Without that factor, the product can describe a prefix that is compatible with many longer strings. Imagine P(A|BOS)=.5 and P(EOS|A)=.2. The prefix A has probability .5 under this start policy, while the exact one-token terminated string has probability .1. A system that omits EOS cannot use that prefix score as though it were the exact terminated-string probability. The existing fixture supplies three targets directly and does not silently add an EOS event.

Taking a negative logarithm turns multiplication into addition. For [.5,.25,.8], the contributions are log2, log4 and log1.25, summing to log10. Dividing by three gives a mean in nats per target. A change of logarithm base changes the unit: divide a natural-log score by log2 to express bits. Probability products are unchanged by that bookkeeping, but comparing numeric loss values across different log bases without conversion is invalid.

Numerical underflow and a genuine zero conditional require different diagnoses. A thousand factors of .01 have a positive exact product 10^-2000, but float64 cannot represent that product. Summing their logs still gives about4605.17 nats. In contrast, a factor exactly zero assigns no probability to the observed event and gives infinite loss under that model. Replacing zero with epsilon changes the model or metric and caps its penalty. Such clipping can be a deliberate engineering policy, but its threshold and resulting interpretation must be disclosed.

Teacher forcing evaluates the conditional at the observed preceding tokens. During generation the model instead conditions on its own sampled or selected previous outputs. These contexts can diverge after the first generated error. Therefore a favorable teacher-forced score is useful evidence about observed-prefix prediction, not a demonstration of every free-generation trajectory. For a masked-attention Transformer, many observed-prefix conditional scores can be computed in one forward pass. That computational parallelism does not make the probability factors independent, nor does it remove the sequential hidden-state dependency of a recurrent model.

Greedy token choice also differs from maximizing a whole sequence. If the first token has probabilities A=.6 and B=.4, and the best second-step continuation has conditional probability .5 after A but .9 after B, the strongest two-token paths have probabilities .30 and .36. Choosing A greedily misses the better complete path. The example fixes a two-step length and ignores stopping solely to isolate this difference; real decoding must also specify length and EOS policies.

**Interview reasoning:** "Does adding log probabilities discard dependencies?" No. The conditional arguments still contain the declared prefixes. The logarithm changes the arithmetic representation of the product. Dependencies are lost only if the conditional model is replaced with marginals or a shorter context, not because multiplication becomes addition. Check the context supplied to every target before debugging the final sum.
""",
)

review(
    4,
    [
        "Derived smoothing as a count/prior mixture with a concrete unseen-context limit",
        "Separated boundary policy, train-only fitting and baseline comparison",
    ],
    r"""
## What the count table assumes, and what smoothing changes

Let C_uv count how often context token u is followed by candidate v within the training documents, and let C_u=sum_v C_uv. The unsmoothed estimate is C_uv/C_u when C_u is positive. A bigram model uses one preceding token, so two long prefixes ending in the same u receive the same next-token distribution. This deliberately discards information before u. A transparent weak baseline is valuable precisely because its limitations are visible and its likelihood can be independently reconstructed.

With vocabulary size V and a positive smoothing coefficient alpha, the additive estimate is (C_uv+alpha)/(C_u+alpha V). The lesson uses alpha=1. The denominator must include alpha once per candidate, not merely once for the whole row. For context A, counts [1,1,0] and V=3 yield [2,2,1]/5. Dividing by C_u+1=3 would make the row sum5/3, which is not a probability distribution. For B, [1,0,0] becomes [2,1,1]/4. For C, the zero row becomes uniform [1,1,1]/3.

When C_u>0, rewrite the estimate as a mixture: [C_u/(C_u+alpha V)] times the empirical row plus [alpha V/(C_u+alpha V)] times the uniform row. For A this is2/5 times [.5,.5,0] plus3/5 times [1/3,1/3,1/3]. The result is [.4,.4,.2]. This makes the tradeoff concrete: with only two observed transitions, three pseudo-counts have substantial influence. A huge vocabulary with alpha=1 can dominate sparse observations. More smoothing avoids zero assigned probability but can flatten real preferences; tune the policy using designated validation data, then freeze it before final evaluation.

The zero-count context and an unknown context string are distinct situations. C is inside the declared vocabulary but has no observed outgoing transition. A token outside [A,B,C] has no allocated row. The reference explicitly chooses a uniform known-candidate fallback for an unseen scoring context. That is an application policy, not an inference that all continuations of an arbitrary new symbol are equally plausible. Unknown training tokens are rejected so fitting cannot silently change the candidate domain. A richer system could reserve an UNK ID, but it would need an explicit mapping and a corresponding count row/column.

Document boundaries determine which observations exist. The sequences [A,B,A] and [A,A] contain two and one transitions, for three total. Concatenating them would introduce an extra A→A transition across the boundary, incorrectly changing A's row to [2,1,0]. Its smoothed distribution would become [3,2,1]/6 instead of [2,2,1]/5. The arithmetic would still normalize, so a row-sum test would miss the semantic defect. Counting the expected number of transitions, sum_d max(length_d-1,0), supplies an independent boundary oracle.

This baseline does not model a start distribution or stopping probability unless BOS/EOS are explicitly added. It scores transitions conditioned on each document's supplied first token. Scoring the transition path A→B→A gives .4*.5=.2, with total loss log5 over two targets. Calling that the unconditional probability of the complete string A,B,A would omit the start and termination contracts. State exactly what is conditioned on when comparing it with a neural next-token model.

Fit-on-train-only covers more than the count values. It includes vocabulary selection, normalization, document segmentation, smoothing selection and any fallback policy learned from data. Merely freezing the final count matrix after examining validation failures does not undo that information use. Compare systems using the same held-out target events and compatible representations. If the neural model beats this baseline, that establishes improvement on the measured score and split; it does not independently prove grounded answering or reasoning.

**Interview reasoning:** "Why keep a model we know ignores long context?" It provides a cheap reproducible floor, exposes dataset and scoring mistakes, and shows whether a more expensive model captures useful structure beyond local frequencies. If a complex model fails to beat it, inspect training, leakage and evaluation alignment before adding architectural complexity.
""",
)

review(
    5,
    [
        "Derived perplexity as inverse geometric mean rather than average reciprocal probability",
        "Added exact unequal-document weighting and masking counterexamples",
    ],
    '\n## Read cross entropy as a weighted expectation\n\nFor active target probabilities p_1 through p_N, the empirical mean cross entropy is H=-(1/N) sum_i log p_i. Perplexity is exp(H), so algebra gives PPL=(product_i 1/p_i)^(1/N). It is the inverse geometric mean of the observed target probabilities. It is not the arithmetic mean of their reciprocals. For [.5,.25], the inverse probabilities are2 and 4, whose geometric mean is sqrt8≈2.828; their arithmetic mean is3. The latter is a different statistic.\n\nA helpful special case is a uniform predictor over K candidates. Every observed target has probability1/K, giving H=log K and PPL=K. This motivates the rough interpretation of perplexity as an effective number of equally plausible choices. Real distributions are not uniform and their candidate sets may be constrained differently at each position, so this interpretation must not be turned into a literal count of alternatives considered by the model.\n\nCross entropy includes the uncertainty present in the data as well as mismatch between predictor and target distribution. For a fixed discrete true distribution q and model p on compatible support, H(q,p)=H(q)+KL(q||p). The entropy H(q) is not something a model can reduce by guessing better; the nonnegative KL term describes mismatch. In the lesson we observe a finite set of target events rather than know q exactly, so the empirical loss is an estimate under its stated sampling/weighting policy. This distinction matters when one dataset is intrinsically less predictable than another.\n\nWrite masking into both numerator and denominator: H=-sum_i m_i log p_i / sum_i m_i, with m_i in{0,1}. An ignored event contributes neither a term nor a count. In implementation, selecting active targets before evaluating problematic logs avoids expressions such as0*infinity producing NaN. An all-ignored batch has no empirical mean. The correct response is a defined no-target policy or explicit refusal, not a fabricated zero loss that looks like perfect prediction.\n\nUnequal document lengths expose a second denominator choice. Document A has one target of probability.5; document B has three targets of probability.25. The combined sum is7log2 over four targets, so token-weighted mean is7log2/4 and perplexity is2^(7/4), about3.364. Equal-document averaging first forms means log2 and2log2, then averages to1.5log2 and perplexity sqrt8. Averaging document perplexities directly gives(2+4)/2=3, which agrees with neither policy. Aggregate losses and counts under the intended unit before exponentiating.\n\nA low mean can hide a catastrophic rare failure. Compare target probabilities [.99,.99,.01] with [.5,.5,.5]. The first predictor is very confident and correct on two observations but assigns only.01 to the third. Its loss contributions are about.01005,.01005,4.60517, so the mean is about1.54176 and perplexity about4.673. The uniform two-choice predictor has mean log2 and perplexity2. The log score strongly penalizes assigning very little mass to an event that actually occurs. An accuracy metric using only top choices would tell a different part of the story.\n\nTokenization and inclusion rules must remain compatible. If one model uses a single token for a string while another uses three, equal string probability can coexist with different per-token loss: probability1/8 gives NLL3log2, yielding PPL8 for one target or PPL2 for three targets. A byte-normalized score can provide a common unit only after defining which bytes, boundaries and conditional events correspond to the exact same evaluated strings. It is not enough to divide arbitrary losses by a convenient byte count while changing prompt or EOS treatment.\n\n**Interview reasoning:** "Can a new model have lower perplexity but worse answers?" Yes. Perplexity measures assigned target-token probabilities under a specific representation and dataset. Answer correctness, citation support, refusal behavior and task utility have different acceptance rules. Use perplexity to assess the defined prediction objective, then evaluate the behaviors required by the application separately.\n',
)

review(
    6,
    [
        "Separated reversible encoding from lossy normalization and token segmentation",
        "Explained byte fragments, grapheme boundaries and raw versus canonical identity",
    ],
    r"""
## Trace the representation boundary before tokenization

A displayed mark, a Unicode code point, an encoded byte and a model token are different units. The precomposed letter é is U+00E9 and occupies two UTF-8 bytes, C3 A9 in hexadecimal. The decomposed spelling e followed by U+0301 occupies two code points and three UTF-8 bytes, 65 CC81. Both can render as one visible accented letter. A code-point count of one versus two therefore says nothing by itself about what a reader sees. Emoji sequences, combining marks and joiners produce further cases where one displayed grapheme spans multiple code points.

UTF-8 assigns a variable-length byte sequence to each Unicode scalar value. ASCII letters use one byte; many accented letters use two; the smile in Example A uses four. A strict encode/decode round trip preserves the represented Unicode string when the input is valid. It does not automatically preserve an original external file's line endings, byte-order mark, encoding choice or normalization history if earlier processing changed them. Define the boundary being tested: raw bytes→decoded string→re-encoded UTF-8 is a stronger byte claim than string→UTF-8→same string.

A byte-level tokenizer can split a multibyte code point across tokens. For é, one token might contain C3 and the next A9. Decoding either byte alone under strict UTF-8 fails, while concatenating the token bytes first reconstructs the valid sequence. The same issue appears when streaming generated tokens to a display: use an incremental decoder or buffer incomplete byte sequences instead of replacing each incomplete fragment independently. Replacement decoding can turn one valid cross-token character into several replacement marks, changing the eventual text.

Normalization changes the equality relation. NFC maps canonically equivalent strings to a composed representation where possible. The composed/decomposed é pair then agrees, but retaining only the normalized result cannot reveal which raw spelling arrived. NFC does not generally perform case folding, remove accents or equate unrelated look-alike characters. Compatibility normalization forms have a different contract and can erase distinctions that canonical normalization preserves. Do not add such transformations merely because they reduce the number of unique strings. The [Unicode normalization specification](https://www.unicode.org/reports/tr15/) defines these distinctions; the lesson uses only a small fixed canonical-equivalence example.

Consider duplicate detection. A raw-byte hash keeps the two accented spellings distinct, while a hash of their NFC UTF-8 encoding can identify them as the same canonical content. Both choices can be correct for different purposes. A source archive may need byte identity; an evaluation split may need canonicalized near-duplicate grouping to avoid putting equivalent text in both train and test. Retain the raw source identifier and transformation policy so the grouping is auditable. A content hash is not encryption and does not authorize access to the underlying text.

Token offsets must declare their coordinate system. If a span begins after café, its boundary can be four code points but five UTF-8 bytes from the start of that word. Applying a code-point offset directly to a byte buffer can cut inside a multibyte sequence. Applying offsets from normalized text to raw source text can select the wrong range even when the display looks similar. Extraction and citation systems should carry an explicit mapping or validate the quoted span against the exact source representation used to compute offsets.

The empty string illustrates why validation belongs to the current operation. It has a perfectly valid empty UTF-8 representation and a successful round trip. A later average over token losses may reject zero active targets. Rejecting empty text everywhere would conflate encoding validity with a downstream statistical requirement; accepting it into a mean without a defined denominator would make the opposite mistake.

**Interview reasoning:** "If the decoded text looks right, is the pipeline lossless?" Appearance alone cannot distinguish canonical spellings, dropped invalid bytes, line-ending changes or replacement decoding. Establish losslessness by comparing the promised representation under a strict policy. When normalization is intentional, state the equivalence being preserved and retain enough provenance to explain which original distinctions were discarded.
""",
)

review(
    7,
    [
        "Explained overlapping pair counts versus nonoverlapping replacement",
        "Connected merge order, byte fallback and model/table compatibility",
    ],
    r"""
## BPE learns a sequence of rewrites, not a meaning dictionary

The starting symbols in this lesson are byte tuples. A one-byte token a is(97,), and a merged token ab is(97,98). The tuple records the payload, while a production vocabulary normally assigns a separate integer token ID to that payload. Payload and ID should not be confused: changing an ID can change the selected embedding row even if the human-readable token text looks identical. The special end-of-word symbol256 is deliberately outside the byte range0..255 and is handled separately by the decoder.

A training iteration counts adjacent token pairs in the current segmentation, chooses one pair and rewrites its nonoverlapping occurrences. Counts must be recomputed after rewriting because the neighbors have changed. With words ab and ac, the observed pairs are(a,b),(b,end),(a,c),(c,end), each once. The declared lexicographic rule on integer tuples chooses(a,b), independently of input order. A different tie rule can produce a different first merge and later vocabulary, so the rule is part of reproducibility rather than an unimportant implementation detail.

An overlap counterexample is the word aaa, represented as a,a,a,end. The pair(a,a) occurs twice as an adjacent pattern: positions0-1 and1-2. A single left-to-right nonoverlapping replacement can merge only the first pair, producing aa,a,end. It must not use the middle a twice and produce aa,aa,end, which would decode to four a bytes instead of three. Pair frequency is the selection statistic; realized replacement count can be smaller when occurrences overlap. Byte conservation is an independent invariant that catches this mistake.

The saved merge order determines encoding. Suppose the learned rules include(a,b)→ab and(ab,c)→abc. Starting from a,b,c, applying them in that order yields abc. Applying the second rule first finds no ab token yet and leaves ab,c after the later rule. An unordered set of possible merged payloads does not reproduce the trained tokenizer. The lesson's sequential application is a deliberately transparent rewrite policy; compatibility with an external tokenizer also depends on its pre-tokenization, merge-ranking convention, boundary handling and special tokens.

Byte fallback addresses representation coverage, not semantic competence. The unseen d in validation word ad still has base byte100, so the sequence can be encoded without fitting an a+d merge. This does not mean the model learned how to use d in that context. Encoding coverage and predictive quality are separate questions. Likewise, a byte vocabulary does not imply that each token can be decoded as a complete Unicode character independently; concatenate payload bytes and apply the declared decoding policy.

Training text composition affects which merges become common. If one domain's repeated boilerplate dominates counts, the tokenizer may compress it well while representing another domain with longer sequences. Under a fixed token budget, different segmentations expose different amounts of source text to the model. Longer segmentation can also increase attention work and alter per-token loss denominators. These are reasons to measure token lengths and task coverage on a held-out corpus, not reasons to refit on that corpus after seeing inconvenient lengths.

A tokenizer/model artifact should bind at least normalization, pre-tokenization, byte/special-token definitions, ordered merges, ID assignment and the associated embedding/output vocabulary. Two tokenizers with the same vocabulary size can disagree completely about row identity. A hash of only an unordered token list misses merge-order changes. The immutable rule list in the example is a small proxy for that larger artifact contract, not proof that arbitrary pretrained tokenizers are interchangeable.

**Interview reasoning:** "Why not learn a new merge for every unknown validation word?" That would change the representation after observing evaluation data and could introduce IDs without trained embedding/output rows. The proper action is to apply the frozen policy and report its behavior. If domain adaptation justifies a new tokenizer, treat it as a new model/pipeline experiment with a fresh fitting split and compatibility plan. The original subword motivation is described in [Sennrich, Haddow and Birch](https://aclanthology.org/P16-1162/); this byte-tuple implementation uses its own explicit teaching conventions.
""",
)

review(
    8,
    [
        "Derived lookup gradients with repeated IDs",
        "Explained padding, tied output weights and vocabulary permutation failures",
    ],
    '\n## A lookup selects parameters and accumulates their gradients\n\nLet E have shape(V,D), where V is vocabulary size and D is feature width. For token IDs t_1 through t_T, the output row i is X_i=E_(t_i). A one-hot selection matrix S with shape(T,V) gives the same operation as X=SE. Each row of S contains one1. This algebra explains why lookup preserves token order and why repeated IDs select the same parameter row. An implementation need not materialize S; direct indexing avoids allocating T*V mostly-zero entries.\n\nFor the fixture IDs[2,0,2], S selects vocabulary row2 twice and row0 once. The output is a three-position sequence with feature width2. There are still only four vocabulary parameters rows in the table. Token ID2 is an address into that table; it is not a magnitude that should be interpreted as "twice token 1." Interpolating between integer IDs or averaging them before lookup therefore has no justified semantic meaning under this representation.\n\nThe backward relation follows directly: if G=dL/dX has shape(T,D), then dL/dE=S^T G. In coordinates, the gradient of row r is the sum of G_i over positions whose ID equals r. Take upstream rows G=[[1,2],[3,4],[5,6]] for the three fixture positions. Row0 receives[3,4]; row2 receives[6,8]; rows1 and3 receive[0,0]. The two appearances of token 2 accumulate into the same parameter. Assigning rather than adding the second occurrence\'s gradient would lose one contribution. The current NumPy lookup example does not execute this backward update; this is an independent derivation of what a differentiable embedding layer must do.\n\nThat gradient statement assumes the loss depends on E through the input lookup alone. If the table is also tied to the output classifier, logits for hidden state h may be E h, and the softmax loss supplies additional gradients through output-vocabulary rows. With weight tying, a row absent from the input sequence can still receive an output-side gradient. This is why "unused input IDs never change" is too broad unless all paths and optimizer behavior have been specified.\n\nPadding has similarly separate contracts. An embedding layer may suppress gradient accumulation for a designated padding row, but that does not automatically prevent padding positions from participating in attention, pooling or loss. Nor does it prove that optimizer weight decay or another shared use cannot alter that row. A model needs an input padding convention, an attention mask where appropriate, and a supervised-target inclusion rule. These controls operate on different axes and should be checked independently.\n\nA vocabulary permutation can produce a silent failure while all shapes remain valid. Suppose a new tokenizer swaps IDs0 and2, but the old table is kept unchanged. The new ID0 now means the token formerly represented by row2, yet lookup returns[1,0] instead of[2,2]. No index error occurs because both IDs are legal. Correct migration would remap every affected input ID and the corresponding input/output vocabulary parameters consistently. Keeping vocabulary size and file format unchanged is not a compatibility proof.\n\nThe NumPy storage behavior in this lesson is also deliberate. Advanced integer indexing creates a separate result array. Editing output[0] does not update E or output[2], despite both having originally selected row2. Parameter sharing describes which source parameter a computation reads and which gradients accumulate; it does not require all returned activation rows to alias the same memory. In an automatic-differentiation framework, mutation rules and gradient tracking add further constraints, so inspect that framework\'s documented semantics before translating a NumPy mutation experiment.\n\n**Interview reasoning:** "Where is meaning stored in an embedding?" The lookup mechanism itself only associates IDs with vectors. Useful structure can emerge from the training objective, data and downstream transformations. The supplied table has no such training history. A similarity between two hand-authored rows demonstrates a geometric relation in this fixture, not a validated semantic relation between words. Also distinguish this context-independent token table from a contextual representation produced after attention layers process the whole allowed prefix.\n',
)

review(
    9,
    [
        "Derived a nonuniform attention row and its scaling counterexample",
        "Explained all-head/layer causality, Jacobian paths and rectangular cached masks",
    ],
    '\n## Trace one attention row beyond the equal-score control\n\nFor query i, score s_ij=q_i^T k_j/sqrt(d_k) compares it with key j. The allowed mask removes unavailable keys, softmax normalizes the remaining row, and o_i=sum_j a_ij v_j mixes values. Query/key width d_k controls the dot product and scaling. Value width d_v controls the output width and need not equal d_k. The score matrix carries query and key positions, while the output carries query positions and value features. A dimension match alone cannot establish that these semantic axes were arranged correctly.\n\nThe equal-score fixture is an excellent mask control because every legal key receives equal weight. It cannot test whether Q and K are actually used or whether division by sqrt(d_k) is present: zero dot products stay zero under either correct or incorrect scaling. Consider instead a second query q_1=[1,0], allowed keys k_0=[1,0], k_1=[0,1], and d_k=2. Its two scores are[1/sqrt2,0], giving weights approximately[.66976155,.33023845]. With values[2,0] and[0,2], the output is approximately[1.33952310,.66047690]. Omitting the scaling gives weights about[.73105858,.26894142], so the output changes despite preserving the causal triangle and unit row sum.\n\nScaling has a statistical motivation, not a universal exact variance guarantee. If independent query/key components have zero mean and unit variance, a width-d dot product has variance d because it sums d product terms. Dividing by sqrt(d) keeps that variance near one under those assumptions. Learned features can violate independence or unit variance, and a model can use other architectural conventions. For this worksheet, the explicit formula is the contract to test, regardless of whether a particular literal vector resembles the motivating assumptions.\n\nMasking after softmax breaks normalization. With three equal scores, unconstrained weights are[1/3,1/3,1/3]. Zeroing future entries in the first row leaves[1/3,0,0], so its output is one third of the first value instead of that value. Renormalizing allowed mass afterward can recover the algebra in benign finite cases, but forming the distribution over forbidden extreme scores first can lose allowed mass numerically. Removing forbidden scores before maximum subtraction gives a clearer and safer computation. A fully masked query has no categorical distribution under this contract and is refused.\n\nA backward trace helps distinguish the roles of Q,K,V. For one query, let g=dL/do be the upstream value-width vector. Then dL/dv_j=a_j g, and dL/ds_j=a_j g^T(v_j-o). The latter term compares each value with the current mixture. Gradients then flow to the query through sum_j(dL/ds_j) k_j/sqrt(d_k), and to each key through(dL/ds_j) q/sqrt(d_k). A hard forbidden key has no contribution through this row. These equations describe the fixed attention operation; the reference does not train the projected Q/K/V matrices or a complete model.\n\nPrefix invariance is a whole-path property. A residual addition and a positionwise feed-forward transformation preserve it if their own inputs are causal. A normalization that mixes statistics across all token positions could violate it even when the attention mask is correct. So could a preprocessing step that inspects future targets or a batch construction that appends the answer unshifted. For teacher-forced next-token prediction, a diagonal attention entry is legal because input position i contains the previous target under the shifted convention. If it contains the current label instead, the same triangular mask leaks the answer.\n\nCached decoding changes mask coordinates. With three cached keys and one newly appended key, a single new query at absolute position3 may attend to all four keys. A naive lower triangle constructed with shape(1,4) allows only column0, because its query row index is 0 rather than absolute position3. The worksheet intentionally handles square self-attention; later cached/cross-attention implementations need an explicit absolute-position or cache-offset rule. Shape compatibility should never silently decide causal meaning.\n\n**Interview reasoning:** "Does prefix invariance prove correct attention?" It proves a useful information boundary for the checked inputs, but a function that always returns zeros could also satisfy it. Combine independent properties: exact nonuniform outputs, allowed-row sums, forbidden zeros, shape/type/domain guards, prefix recomputation and future perturbations. Even all of those checks establish a computation, not factuality or data-split independence. The [original Transformer paper](https://arxiv.org/abs/1706.03762) provides the architectural context; the numerical cases here isolate individual mechanisms.\n',
)

review(
    43,
    [
        "Separated source/target availability from objective supervision",
        "Derived cross-attention backward axes and teacher-forcing leakage counterexamples",
        "Added guard for finite inputs whose computed dot products overflow",
    ],
    '\n## Architecture is a graph of permitted information\n\nStart with the data available at the moment of prediction. In document classification, the complete document may already exist. A representation of its first word can legitimately use later words. In next-token generation, the next answer token has not been observed and cannot be used as context. In translation with a complete source sentence, the decoder may use all source words while remaining causal over target words. The word "future" must therefore identify both a sequence and an availability policy. A later source position is not automatically forbidden merely because a later target position is.\n\nThe three attention sublayers expose different axes. Encoder self-attention compares source queries with source keys. Decoder self-attention compares target-prefix queries with target-prefix keys. Decoder cross-attention compares target queries with encoded source keys. If the source has length S and the target has length T, their score shapes are(S,S),(T,T) and(T,S), respectively. The value feature width determines each output width; it does not determine either position axis. For a batch and multiple heads, additional batch/head axes precede these dimensions, but the query/key distinction remains the same.\n\nThe zero-score fixture makes permitted information visible. With source values[2,0],[0,2],[6,6], an all-allowed query returns their mean[8/3,8/3]. A causal first target row sees only[2,0], and the second sees the mean[1,1]. A rectangular cross-attention operation with two target queries and three source keys has two output rows, each[8/3,8/3] under zero scores. Marking source position2 as padding changes both cross outputs to[1,1]. Padding excludes an unavailable source value for every target query; it is not a rule forbidding target position1 from seeing source position2 merely because2>1.\n\nTeacher forcing is a target construction rule. For desired target[5,7,3] and BOS 1, decoder inputs[1,5,7] are paired with labels[5,7,3]. At index1 the input token5 is already observed context for predicting7. The diagonal is therefore legal. If inputs were[5,7,3] without the shift, the first position would contain the very label 5 it must predict. A triangular mask would not remove that same-position answer leak. A low training loss would then support neither useful prediction nor correct causality.\n\nLoss masking answers another question: which predictions contribute to the objective? A padded target row may have attention edges but zero loss weight. A corrupted-source objective may supervise one selected source position while allowing bidirectional source attention. With original source[2,5,7], corruption[2,0,7] and an active loss only at the middle position, the target remains5 even though input0 is the mask token. Reusing the source-corruption mask as an attention mask would prohibit useful surrounding context or create the wrong matrix shape. Keep the arrays named by their roles rather than calling all of them "the mask."\n\nThe conditional sequence objective is L=-sum_t log P(y_t|x,y_<t). An encoder-decoder explicitly computes source representations from x and lets each target state read them. A causal decoder can also condition on a source/prompt by concatenating an appropriate representation and using a deliberate attention/loss policy. Architecture family alone therefore does not uniquely identify the task or training objective. A masked-source objective generally scores selected corruptions and is not simply the same autoregressive factorization with a different drawing.\n\nCross-attention has a useful backward interpretation. If O=AV and G=dL/dO, then dL/dV=A^T G has source rows, while dL/dA=G V^T has target-by-source shape. After differentiating row softmax into H=dL/dS, query gradients are H K/sqrt(d), and key gradients are H^T Q/sqrt(d). Target-side errors can thus train source-side keys/values through the cross-attention path. The transpose is not an arbitrary coding trick: it sums contributions from every target query that used a source position.\n\nFor an assistant that turns a complete report into structured findings, a source encoder can use the whole report. If the product later promises live partial results before the report is complete, the earlier availability assumption changes. A valid test inserts or changes source text that arrives only later and checks whether already published outputs depend on it. A successful mask arithmetic test does not settle whether a cited claim is entailed by the source. That requires an evidence and task-evaluation contract in addition to the architecture.\n\n**Interview reasoning:** "Is an encoder allowed to see the answer?" It may see the complete source when the task permits it, but labels must not be smuggled into that source through data construction. Source availability, target shifting, label provenance and train/test separation are independent checks. The distinction follows the architecture in [the Transformer paper](https://arxiv.org/abs/1706.03762) and the bidirectional objective in [BERT](https://arxiv.org/abs/1810.04805); the numerical examples here do not reproduce those trained systems.\n',
    r"""
Start with a table naming every axis and which real-world information it represents. A square output may hide a swapped source/target axis when lengths happen to match, so retain the rectangular2-by-3 case. If loss is suspiciously small, inspect the target shift before changing the optimizer. If padding changes a result, inspect whether it was excluded before the normalizer.

Finite input elements do not guarantee a finite matrix product. Very large finite Q/K entries can overflow during their dot product. The helper controls NumPy's arithmetic warning behavior around that operation and explicitly rejects nonfinite computed allowed scores with ValueError. It does not silently propagate NaN weights. The reference remains a bounded pedagogical operation, not a trained encoder-decoder or a production backend.
""",
)

review(
    44,
    [
        "Expanded the relative-position identity into coordinate and cache-layout cases",
        "Separated norm preservation, phase resolution and empirical long-context quality",
    ],
    r"""
## Relative geometry depends on consistent coordinates

A rotary pair is a two-dimensional subspace. With q=(q_0,q_1), rotation by angle theta gives(q_0 cos theta-q_1 sin theta, q_0 sin theta+q_1 cos theta). Squaring and adding cancels the cross terms, leaving q_0²+q_1². Norm preservation is therefore an exact algebraic property before floating-point rounding. It does not mean that the query-key similarity is unchanged, because the query and key can rotate by different angles.

For q=k=[1,0], their rotated dot product is cos(n-m), where m and n are their respective angles. Equal positions give1; a relative angle pi/2 gives0; a relative angle pi gives-1. This example makes the distinction clear: each vector keeps unit length while their relative orientation changes. If both positions receive the same offset c and use the same frequency rule, R(m+c)^T R(n+c)=R(n-m), so the pairwise score is unchanged. Resetting only the new query's position is not a common shift and breaks that relation.

A width-d head applies this construction in multiple paired subspaces. The fixture uses adjacent pairs(0,1),(2,3),... and omega_i=base^(-2i/d). For d=4 and base10000, the frequencies1 and.01 give a rapidly changing first pair and a slower second pair. Another implementation may pair the first half of coordinates with the second half. Both conventions can be mathematically valid, but their projection weights and rotary layout must be converted together. Identical tensor shapes do not establish layout compatibility.

The usual rotary application transforms Q and K before their dot product. It does not automatically transform V or add a new vector to the residual stream. Consequently, a cached key needs to retain the position at which it was rotated. If positions0,1,2 were processed together, incremental processing of the third key must rotate it at2. Rotating that new key at0, or rotating an already rotated cached key again, changes the scores. Compare full-prefix and incremental outputs while holding weights, masks and token IDs fixed to isolate this state error.

ALiBi changes a score by an additive distance penalty. For positive slope a and causal key j<=i, the bias is-a(i-j). With a=log2, moving a key one position further into the past halves its exponential weight before normalization when content scores are equal. At query2 the three masses are1/4,1/2,1, so weights are1/7,2/7,4/7. If a future key3 were accidentally admitted, the same expression would give a positive log2 bias and mass2, favoring precisely the unavailable position. A distance bias is therefore not a substitute for a causal access mask.

A recency bias changes relative preference rather than imposing a fixed window. A sufficiently favorable content score can overcome a finite distance penalty. Conversely, a hard sliding window sets older positions to forbidden regardless of their content score. These mechanisms answer different design questions. If a task requires exact retrieval from a distant passage, test distance and distractor effects explicitly instead of assuming that a method's ability to evaluate a long index proves useful access to that passage.

There are at least three different long-context checks. Algebraic validity asks whether rotations and masks obey their formulas. Numerical validity asks whether positions, angles and trigonometric calculations retain enough precision at the intended scale. Behavioral validity asks whether a trained model uses information correctly across the required distances. Float32 cannot represent every consecutive integer once the magnitude grows beyond its precision, so assigning very large positions in a narrow dtype can collapse distinct coordinates even before sine/cosine evaluation. The fixture uses float64, but successful evaluation at one million still establishes no trained-model quality result.

Frequency or position scaling changes the computation seen by a trained model. A conversion can preserve output shape while altering phase relationships. Treat such a change as a model configuration requiring controlled evaluation, with distance-stratified retrieval, reasoning and failure cases. Record training context length, tested lengths, tokenizer policy, cache offsets and precision. A prompt that grows by adding irrelevant padding can be long without requiring long-distance reasoning.

**Interview reasoning:** "Why does relative-position algebra not guarantee extrapolation?" The identity determines how the chosen vectors' scores depend on coordinates. It says nothing about which vectors training learned, whether unseen phase combinations are useful, or whether a downstream task needs the relevant information. [RoPE](https://arxiv.org/abs/2104.09864) and [ALiBi](https://arxiv.org/abs/2108.12409) describe different mechanisms with empirical studies; this lesson separately checks their small geometric contracts.
""",
    r"""
If incremental and full-prefix outputs disagree, compare token IDs, position offsets and pairing layout before changing weights. Check whether cached keys are already rotated, whether only Q/K receive the intended transformation, and whether the mask still excludes future positions after adding a bias. Norm preservation alone will not detect a wrong angle: every wrong rotation can still preserve length.

Inspect long-context behavior by distance and task, not only by array shape or successful sine/cosine evaluation. Record the dtype used to form positions and angles. This fixture validates local algebra and cache bookkeeping; it does not implement a published context-extension training recipe or measure production long-context reliability.
""",
)

review(
    45,
    [
        "Derived radial/tangential RMSNorm sensitivities and epsilon limits",
        "Expanded gated FFN matrix gradients and parameter-matched comparison",
    ],
    '\n## Normalization changes which directions a layer can preserve\n\nFor x in R^d, define r=sqrt[(1/d)sum_j x_j²+epsilon]. RMSNorm with unit gain returns y=x/r. For x=[3,4], the mean square is12.5 and r is approximately3.53553, so y is approximately[.848528,1.131371]. The feature mean is not zero. LayerNorm first subtracts the mean3.5, producing[-.5,.5], and divides by sqrt(.25+epsilon), giving values close to[-1,1]. Confusing the two normalizers would predict the wrong output even before training begins.\n\nThe normalizer uses a feature-axis average for each token independently in the ordinary transformer construction. It does not estimate statistics across the sequence or batch. Mixing token positions into the normalizing reduction can introduce dependencies across positions, including future positions in a causal model. A module named "normalization" is not enough to establish the intended axis. Record normalized dimensions, gain/bias shapes and epsilon placement when reproducing a checkpoint.\n\nThe RMSNorm Jacobian is J=I/r-xx^T/(d r³). A direction u perpendicular to x satisfies x^T u=0 and therefore Ju=u/r. Along the radial direction x, Jx=epsilon*x/r³. With epsilon exactly zero and nonzero x, changing only the positive scale of x has no first-order effect: normalization removes that radial magnitude. With positive epsilon, the radial sensitivity is small but generally not zero. This is why exact scale invariance must be qualified when an epsilon is present.\n\nAt x=0, r=sqrt(epsilon) and J=I/sqrt(epsilon). Epsilon prevents division by zero, but a very small epsilon can still produce large local sensitivity near zero. It is not a universal gradient bound. A learned gain multiplies output coordinates and corresponding Jacobian rows, further changing sensitivities. A learned bias, if present, changes outputs while leaving this derivative with respect to x unaffected. The fixture uses an explicit unit-gain contract to keep the formulas inspectable.\n\nLayerNorm removes a common feature shift because subtracting the mean cancels x+c*1 for any scalar c. Its Jacobian annihilates the all-ones direction under the stated feature reduction. RMSNorm generally does not: adding the same constant changes both the numerator and root mean square without centering it away. A test that shifts every feature by5 distinguishes them even when both return finite normalized vectors. Do not infer zero mean from a name containing "Norm."\n\nResidual placement changes the route followed by gradients. Pre-norm y=x+F(N(x)) has Jacobian I+J_F J_N. Post-norm y=N(x+F(x)) has J_N(I+J_F). In the zero-branch control F=0, pre-norm leaves both the forward value and derivative equal to the identity, while post-norm still applies N. The direct identity path is a useful local explanation for optimization differences, but a stack also includes initialization, residual scaling, final normalization, optimizer state and depth. The two-line Jacobian comparison is not a theorem that every pre-norm model trains better.\n\nFor a gated feed-forward layer, let G=XW_g, U=XW_u, A=SiLU(G), H=A elementwise_mul U and Y=HW_d. If the upstream matrix is R=dL/dY, then dL/dH=R W_d^T. The up-branch derivative is(dL/dH) elementwise_mul A; the gate derivative is(dL/dH) elementwise_mul U elementwise_mul SiLU\'(G). Multiplying by X^T accumulates gradients for W_u and W_g. These shapes explain why both projections matter and why a zero local gradient need not indicate a disconnected graph.\n\nThe scalar example sets g=0 and u=2. SiLU(0)=0 but SiLU\'(0)=1/2, so the output is 0, the derivative with respect to g is1, and the derivative with respect to u is 0. Changing u to0 would make both branch derivatives zero at this point. This is a property of the multiplicative gate, not evidence that autograd failed. A large negative gate can also make sigmoid-based activation and derivatives small; inspect actual intermediate values before assuming the optimizer ignored a parameter.\n\nA bias-free plain FFN has matrices d-by-h and h-by-d, totaling2dh weights. A bias-free gated FFN has three such projections totaling3dh. Holding h fixed adds50 percent more FFN weights. Equal weight count requires h_gated=(2/3)h_plain when integer/layout constraints permit: d=4,h_plain=6 and h_gated=4 both yield48 entries. This equalizes one resource count, not necessarily activation memory, kernel efficiency or task quality.\n\n**Interview reasoning:** "Can RMSNorm replace LayerNorm without retraining?" The formulas have different invariances and can produce different states under the same weights. Whether a particular conversion works is an empirical model-specific question. First reproduce the existing architecture\'s axes, epsilon, gains, biases and placement; then evaluate a deliberate change. The [RMSNorm paper](https://arxiv.org/abs/1910.07467) motivates the alternative, while this chapter\'s autograd checks test precise local derivatives.\n',
    r"""
For a normalization mismatch, inspect the feature axis, centering, variance convention, epsilon inside or outside the square root, and affine gain/bias before widening tolerances. Use both a nonconstant vector and a zero vector. A zero-branch residual control distinguishes placement independently of a complicated learned branch.

For a gated FFN, inspect gate and up activations and their separate gradients. A connected zero gradient at one point is different from a missing gradient tensor or a parameter absent from the optimizer. This CPU lesson validates explicit float64 formulas and autograd behavior; it does not demonstrate a large-model training run or establish a universally best normalization architecture.
""",
)

review(
    46,
    [
        "Derived grouped-head storage and an online-softmax merge with changing maxima",
        "Separated exact attention arithmetic from quadratic work and hardware performance",
        "Added positive head-width and computed-score overflow guards",
    ],
    '\n## Separate model sharing from execution efficiency\n\nQuery heads decide how many distinct query projections are available. KV heads decide how many distinct key/value projections are stored and shared. In the fixture Hq=4 and Hkv=2, query heads0 and 1 read KV head0, while query heads2 and3 read KV head1. The mapping h//(Hq/Hkv) assumes contiguous equal groups and divisibility. A different head layout requires a corresponding mapping; repeating or reshaping tensors until shapes match is not enough to establish equivalence.\n\nThe repeated-head oracle deliberately constructs equivalent inputs. It duplicates each of the two existing KV heads twice and then executes four ordinary head computations. Agreement establishes that the grouping code applies the intended sharing. It does not prove that four independently trained KV heads can be replaced by two without changing outputs. Averaging arbitrary trained head weights would define a new model, even if it reduced cache storage. The [GQA work](https://arxiv.org/abs/2305.13245) treats conversion and training as part of the model study, rather than a lossless file-format rewrite.\n\nFor one layer with batch B, cached length L, Hkv KV heads, key/value width d and s bytes per entry, raw cache bytes are2BLHkvds. The2 counts K and V. With B=1,L=5,d=2,s=4, using4,2,1 KV heads gives320,160,80 bytes. A stack with N layers multiplies this raw count by N if each layer has the same dimensions. Real allocation also includes paging, alignment, metadata and any unequal K/V widths. Query-head count does not multiply cached K/V storage again after Hkv has already been counted.\n\nThe projection-weight count tells a related but different story. For model width D and query output width Hq*d, W_Q contains D*Hq*d entries, W_K and W_V together contain2D*Hkv*d, and the output projection contains Hq*d*D. With D=8,Hq=4,d=2, the total is256,192,160 for Hkv=4,2,1. This excludes biases and other blocks. Reducing KV heads by four changes raw cache bytes by four, but does not reduce Q/output projections or the rest of the model by that factor.\n\nOnline softmax solves a numerical aggregation problem. For a processed set of keys, store a maximum m, mass ell=sum exp(s_j-m), and weighted numerator n=sum exp(s_j-m)v_j. The final output is n/ell. The absolute scale exp(m) is never needed because it cancels. To combine summaries from two blocks with maxima m_a,m_b, choose m=max(m_a,m_b), scale each block by exp(m_block-m), and add both its denominator and numerator. In exact arithmetic this merging is associative; floating-point operation order can still create small differences.\n\nTrace a changing maximum with scores[0,log2] and scalar values[2,5], processed one key at a time. The first state is m=0,ell=1,n=2. The second score raises the reference maximum to log2, so the old state is scaled by exp(-log2)=1/2. The new state is ell=.5+1=1.5 and n=1+5=6, giving output4. A dense calculation uses weights[1/3,2/3] and also gives4. If only the denominator were rescaled, the numerator would be2+5=7 and the output14/3, which is wrong. If only the numerator were rescaled, the denominator would2 and the output3, also wrong.\n\nA fully masked block contributes no legal key and can be skipped. A query whose entire allowed set is empty cannot be normalized. Keeping an initial m=-infinity and ell=0 is useful state bookkeeping, but it does not make0/0 a valid output. The helper validates the row-level allowed set before accumulation. It also requires positive head width and rejects nonfinite computed dot products, since finite elements alone do not prevent multiplication/summation overflow.\n\nExact blockwise attention avoids retaining the full score matrix in that routine, but still evaluates the relevant query-key pairs. For dense self-attention, the pair count remains quadratic in sequence length. The local `peak` counter reports the largest score block in this implementation; it is not a process peak-memory measurement. The independent dense oracle intentionally allocates a dense score matrix, so the whole verification process cannot be advertised as having the online routine\'s memory footprint.\n\n[FlashAttention](https://arxiv.org/abs/2205.14135) combines exact attention algebra with hardware-aware tiling and memory traffic reduction. The NumPy loops here teach one mathematical ingredient, not a GPU implementation or speedup. Performance evaluation must separate prompt prefill, incremental decode, batch size, cache lengths, precision, warmup and synchronization. A faster small CPU loop would not establish the bandwidth or scheduling behavior of a device kernel.\n\n**Interview reasoning:** "Does GQA make FlashAttention unnecessary?" They address different dimensions. GQA changes which heads share learned keys and values, while an IO-aware kernel changes how the selected attention operation is executed. A model can use both. Validate the model\'s output contract separately from measuring the implementation\'s memory and latency under representative workloads.\n',
    r"""
When grouped outputs disagree with the oracle, inspect group membership and the head axis before changing tolerances. When an online result diverges after a larger score arrives, print the old/new maxima and both rescaled accumulators; rescaling only one is a characteristic error. Use multiple block sizes and a case where the maximum arrives in a later block.

The positive head-width check prevents division by zero, and controlled score calculation rejects overflowed or NaN scores with ValueError. Finite original arrays are not sufficient evidence of finite products. Distinguish raw cache entries, the local largest score block, process peak memory and end-to-end latency. This NumPy program establishes algebraic parity and local storage counts, not a FlashAttention kernel benchmark.
""",
)

review(
    47,
    [
        "Derived top-k renormalized gradients and the top1 zero router-gradient consequence",
        "Expanded capacity/order tradeoffs and auxiliary-loss gradient interpretation",
    ],
    r"""
## Routing has a smooth interior and a discrete boundary

A mixture-of-experts block first computes router scores z_ti for token t and expert i. A top-k operation selects a set S_t, and a gate rule combines selected expert outputs. Within one fixed selected set, this lesson renormalizes the selected probabilities. Since the full-softmax denominator cancels, selected gate g_i equals exp(z_i)/sum_(j in S) exp(z_j). Scores of unselected experts have no effect on that normalized mixture until they cross the selection boundary. This local statement is essential when interpreting a finite-difference router gradient.

For selected scalar expert outputs e_1=1,e_2=2 and gates[3/4,1/4], the mixture y is5/4. Differentiating with the selected set held fixed gives dy/dz_j=g_j(e_j-y). Thus the first derivative is(3/4)(1-5/4)=-3/16 and the second is+3/16. Raising the score of the smaller-output expert lowers this scalar output. The derivatives sum to zero because a common shift of selected scores leaves their softmax unchanged. The fixture's finite difference verifies this smooth local behavior, not a derivative through every top-k identity change.

At a routing tie, a small perturbation can change which expert is selected. The reference makes ties deterministic by stable descending sorting, so a lower index wins an equal score. Deterministic does not mean differentiable. Finite-difference checks should stay away from membership boundaries when testing the smooth formula, then test the boundary behavior separately as a discrete policy. If a gradient estimate changes dramatically with step size near a tie, the first question is whether the selected expert set changed.

For top1 with renormalization among selected experts, the only selected gate is exactly1. Within a fixed assignment, the main expert-mixture output has zero derivative with respect to the router score through that gate. Training the router then requires another mechanism, such as a different gating convention or an auxiliary signal. Retaining the selected probability from the full softmax would produce a different gradient and output scale. The capacity example deliberately uses a unit-weight top1 expert delta in a residual path, so it must not be presented as every sparse-transformer implementation's training rule.

Capacity adds an admission policy after assignment. The example assigns counts[3,1] to two experts, each with capacity2. Only two of expert0's three tokens are admitted, leaving accepted counts[2,1] and one overflow. The dropped token is not removed from the sequence or loss denominator; its output keeps the residual input while omitting the expert delta. With input[2,1], that fallback remains[2,1]. Silently dropping its entire output row would change sequence alignment and the evaluation unit.

The implementation admits tokens in input order. Reordering a batch with the same assigned counts can therefore change which token overflows and which task predictions are affected. Load counts alone cannot reveal that fairness or quality effect. A production policy could select by gate confidence, reserve capacity or use another dispatch scheme, but each choice defines different behavior and needs an explicit acceptance test. Increasing capacity reduces some drops while increasing activation buffers and potentially changing worst-case work.

For T tokens and N experts, let f_i be the fraction of hard assignments and P_i the mean router probability. The auxiliary term is alpha*N*sum_i f_i P_i. In a local derivative that treats the hard f as fixed, one token's score derivative is alpha*N/T times p_tj[f_j-sum_i f_i p_ti]. This reveals what can receive a gradient: the probability path, not the discrete counts. For f=[.75,.25],p_t=[.7,.3],N=2,T=4,alpha=.01, the derivatives are+.000525 and-.000525. Gradient descent pushes this token's probabilities away from the more heavily assigned expert under the fixed-count local approximation.

Balanced f=P=[.5,.5] gives the stated .01 fixture value, while f=[.75,.25],P=[.7,.3] gives.012. These two calculations do not prove that .01 is a universal lower bound over every feasible collection of routing distributions, nor that reducing the auxiliary term necessarily improves task loss. Monitor assigned counts, accepted counts, dropped tokens, per-family errors and the main objective together. The auxiliary coefficient trades off objectives and must not be interpreted as a stand-alone quality metric.

Sparse activation also differs from storage. With E experts each containing two bias-free matrices D-by-H and H-by-D, stored expert weights total2EDH even if only k experts execute per token. Distributed dispatch requires transporting activations to selected experts and combining their outputs. Uneven loads, synchronization, communication and padding can dominate wall-clock cost. The local linear experts do not measure these effects or reproduce the [Switch Transformer](https://arxiv.org/abs/2101.03961) training system.

**Interview reasoning:** "Does activating only two experts make an enormous model as cheap as a small dense one?" It reduces one category of active expert computation under the stated shapes. Total weight storage, routing, dispatch, memory traffic and latency remain. State the counted operations first, then measure the actual system rather than converting an active-parameter count directly into a speed claim.
""",
    r"""
When router gradients disagree, check the selected expert identities before comparing numbers. Verify whether the implementation renormalizes selected mass, retains full-softmax gates or uses a unit residual delta. For capacity failures, retain token identities as well as assigned/accepted counts; the same histogram can hide a different dropped token after reordering.

A lower auxiliary loss does not prove fewer drops or better task quality. The reference fixes tiny linear experts and uses a local router derivative away from selection boundaries. It neither trains a large sparse model nor executes distributed expert dispatch. Report those boundaries alongside any exact parameter or gate calculation.
""",
)

review(
    48,
    [
        "Connected rejection mass to total variation and corrected-output distribution",
        "Derived expected emitted length under explicit acceptance assumptions",
        "Expanded cache rollback, token budget and EOS state contracts",
    ],
    r"""
## Preserve the target law while changing the execution schedule

At one fixed prefix, let p be the target distribution and q the draft distribution over the same token identities. A draft token i is proposed with probability q_i and accepted with probability min(1,p_i/q_i). The resulting accepted mass is min(p_i,q_i). A token with q_i=0 cannot be proposed by a valid draw from q, so the acceptance ratio need not be evaluated there. If p_i>0 while q_i=0, that target mass can still be produced by the correction distribution after rejecting another draft proposal.

Let R=sum_i max(p_i-q_i,0). Because both distributions have unit mass, the total positive difference equals the total negative difference in magnitude, so R=(1/2)sum_i|p_i-q_i|, their total variation distance. Accepted probability is1-R. When p=q, R=0 and every valid draft proposal is accepted. The residual distribution is undefined in that case because its total mass is zero; it is never needed on a valid rejection branch. Creating an arbitrary residual for equal distributions would conceal a control-flow mistake.

For p=[.5,.3,.2] and q=[.2,.5,.3], accepted mass is[.2,.3,.2]. Rejection mass is.3 and the residual places all its mass on token0. Combining accepted mass with.3 times that residual recovers p exactly. If rejection instead sampled directly from p, the result would be[.2,.3,.2]+.3*[.5,.3,.2]=[.35,.39,.26], which differs from the target. An acceptance check followed by an intuitive "fallback to target" is therefore not the exact algorithm.

The random-draw contract matters at boundaries. Sampling from cumulative probabilities uses half-open intervals, so a draw exactly on one cumulative boundary belongs to the next interval. A zero-probability token must never be chosen merely because two adjacent cumulative values coincide. Likewise, acceptance uses a uniform draw in[0,1) and the strict comparison u<a_i. Floating-point normalization and cumulative rounding need deliberate treatment, but a tolerance must not silently admit a negative probability or change token identity.

A block round proposes several tokens under successive draft prefixes. Verification accepts a contiguous prefix. Before the first rejection, the accepted prefix matches the proposal prefix used to compute each stored q distribution, so the one-step correction applies at that position. At the first rejection, later draft proposals were conditioned on an uncommitted token and are discarded. Continuing to accept that suffix would compare probabilities under the wrong context. If the whole proposal block is accepted and budget remains, a bonus token comes from the target's next conditional distribution.

A simple latency calculation illustrates why acceptance alone is insufficient. Assume, only for this calculation, that each proposal has the same independent acceptance probability a and that at most gamma proposals are made. Ignoring EOS and a binding token cap, expected emitted tokens per round are1+a+a²+...+a^gamma: the mandatory correction/bonus contribution and the successive accepted-prefix opportunities. With a=.8 and gamma=3 this is2.952. If target verification cost is C_v, each draft step costs C_d and coordination/cache work costs C_o, a rough per-token time is(C_v+gamma*C_d+C_o)/2.952. Compare that with measured ordinary target decode cost, not with an assumed cost of zero for the draft. Real acceptance is prefix-dependent, and batch/device effects can violate this simplified cost model.

Cache state must match committed tokens exactly. Suppose an old prefix has length5, three draft tokens were appended speculatively, and only the first was accepted before a correction. Keep the first6 positions, discard the unaccepted two, then append the correction at position6. The resulting committed length is7. Keeping rejected K/V entries, retaining their position offsets or appending the correction after the discarded suffix changes the next attention context. A correct probability formula cannot repair that state error.

Target and draft caches belong to different models. Even when their token vocabularies match, their layer counts, projected keys, values, positional layouts and dtypes may differ. They should each be restored or rebuilt from the same committed token prefix using their own model computation. Copying raw target K/V tensors into the draft cache is not justified by shared token IDs. The tiny cache in this lesson makes token/position-dependent values observable, but it does not implement a production multilayer decoder cache.

Termination is part of the distribution contract. An accepted EOS ends the sequence and prevents a bonus token. A hard output cap can stop a round even without EOS and defines truncation of the generation process. Both target and draft probabilities must already include the intended temperature and filtering policy at the same prefix. Using raw logits for one and a top-p filtered distribution for the other while claiming to preserve a different target sampling policy is a mismatch of laws.

**Interview reasoning:** "Does exact speculative sampling return exactly the same text as ordinary sampling with the same seed?" It preserves the target distribution under its assumptions, not necessarily a draw-for-draw sequence from a different random-number schedule. Compare exact probability decomposition and state transitions first. Frequency experiments can supplement those checks, while a speed claim requires measured serving behavior. The [speculative decoding](https://arxiv.org/abs/2211.17192) and [speculative sampling](https://arxiv.org/abs/2302.01318) papers establish the algorithmic context; this fixture verifies the small numerical and cache contracts.
""",
    r"""
For a distribution mismatch, compare accepted mass and corrected rejection mass per token before examining long generated strings. Check vocabulary identity, effective temperature/filtering, q-support and the prefix attached to every saved proposal distribution. A same-seed string mismatch is not by itself evidence of a changed law.

For divergence after rejection, compare committed token IDs, cache length, positions, keys, values and the next attention output against a fresh reconstruction. Check EOS and the remaining token budget before producing a bonus. The fixture demonstrates exact small-distribution arithmetic and a concrete cache rollback; it does not run an optimized target/draft serving stack or establish hardware speedup.
""",
)


START = "<!-- reviewed-mechanism-start -->"
END = "<!-- reviewed-mechanism-end -->"


def enrich_guide(identity: str, document: str) -> str:
    """Insert reviewed prose without modifying any fenced program."""
    number = int(identity.rsplit("-", 1)[1])
    if number not in REVIEWS:
        return document
    record = REVIEWS[number]
    document = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n*", "", document, flags=re.S)
    body = str(record["body"])
    block = START + "\n\n" + body + "\n\n" + END + "\n\n"
    anchor = "## Vocabulary and concepts"
    if anchor not in document:
        raise ValueError("Expected vocabulary insertion point")
    document = document.replace(anchor, block + anchor, 1)
    diagnosis = str(record["diagnosis"])
    if diagnosis:
        document, count = re.subn(
            r"## Common pitfalls and diagnosis\n.*?(?=\n## )",
            "## Common pitfalls and diagnosis\n\n" + diagnosis + "\n",
            document,
            count=1,
            flags=re.S,
        )
        if count != 1:
            raise ValueError("Expected expert diagnosis section")
    if "\u2014" in document:
        raise ValueError("Em dash in reviewed guide")
    return document


# Exact prose-only repairs. Fenced code is never passed through this function.
_JOINED = {
    "and": """and1 and2KVheads andLayerNorm andPythonloops andSwiGLU andV andacceptance andactive andan andbatching andbias andbiases andbonus andboth andbranch andcache andcache-position andcache-state andcapacity0 andcheck andcoefficient andcommunication andcompare andcompareKVheads4 andcompareblock andcomparepre-normx andcomparethefirstthree andcorrected andcorrection anddenominator anddoesnotverify anddraftprobabilitiesq anddropped-token andeffective andemit andempty andend-to-end andepsilon1e-8 andevaluation andeven andexpertmatrices andfailure andfinite-difference andgate andgating andinspectable andinvalid anditsrouting andkeeps andkey andload andmasking andmean andmoving andneednot andnormalizes andnormalizezero andoptimizer andoutput andoutputSiLU andoverflowpolicy andparameter andperformance andpositions0 andprojection andq andreal andreject andresidual andresourceuse andserving andslope andsmallfeature andstops andstructured andtail andtarget andthe andtheir andthree andties andtop2activation andtraffic andtraining andunit andupbranch andusebonusdraw andusing andvalue andvalues andvalues1 andvaluevectors andverifies andweighted-value andzero-vector""",
    "the": """theacceptance theactual theall-ones thearchitecture theartifact theblockwise thebudget thecapacity thecompute thecorrection thedeclared thedraft thedrop theexact theexpert thefirstlogit thefirstrejection thefullscore thefullsoftmax thefunction thegate thehard theintended theother theprepared thesameprefix thetarget thetransformedbranch thetwo theunaccepted theupbranch thezero""",
    "with": """withHq withJ withSwiGLUhidden4 withWd withacceptancedraw withcapacity2 withdense withmanytotalparameters withpost-normLayerNorm withprobabilitymin withrespecttou0 withthetarget withtheup withunitgain withunitmass withwidth64""",
    "or": """orALiBi orGPUthroughput orGQA oracceptedEOS oracknowledge orapplying orbonus orclaim orcommunication orcoordination ordistributed orfiltering orhardware orkey orloss orprobabilities orproductionquality orrequesting orretraining orsample-from-target orthroughput""",
    "for": """fordiscarded forquality forqueryposition2 forrouter fortheother""",
    "from": """fromp-q fromthenormalized fromtheproduct fromthetarget""",
    "to": """tocheck toexperts0 tofloating-point toinput topexactly toreduce tothesame tozero""",
    "an": """anall-false anassumption anattention anexpert anexplicit anoptimizedkernel""",
    "of": """ofdraftproposals offirstoutputcoordinate ofnumerical ofp-q ofthefirsttop2mixture""",
    "by": """by50percent byChen byHkv bypi byup2 byxWu""",
    "at": """atposition0 atposition1000000 atposition2 atx1""",
}
_REPAIRS = {
    "theirproposal": "their proposal",
    "doesnotverify": "does not verify",
    "doesnotmean": "does not mean",
    "doesnotprove": "does not prove",
    "doesnot": "does not",
    "neednot": "need not",
    "notreplace": "not replace",
    "asdropping": "as dropping",
    "aspeedup": "a speedup",
    "thesame": "the same",
    "thefirsttop2mixture": "the first top-2 mixture",
    "thefirstthree": "the first three",
    "theother": "the other",
    "thenormalized": "the normalized",
    "theproduct": "the product",
    "thetarget": "the target",
    "theup": "the up",
    "butstill": "but still",
    "whilepost-norm": "while post-norm",
    "Apre-norm": "A pre-norm",
    "Apost-norm": "A post-norm",
    "thanLayerNorm": "than LayerNorm",
    "thanidentity": "than identity",
    "inonebatch": "in one batch",
    "pertoken": "per token",
    "under a": "under a",
    "undera": "under a",
    "incrementalcache": "incremental cache",
    "firstlogit": "first logit",
    "firstrejection": "first rejection",
    "fullscore": "full score",
    "fullsoftmax": "full softmax",
    "sameprefix": "same prefix",
    "transformedbranch": "transformed branch",
    "upbranch": "up branch",
    "unitgain": "unit gain",
    "unitmass": "unit mass",
    "expertmatrices": "expert matrices",
    "overflowpolicy": "overflow policy",
    "resourceuse": "resource use",
    "smallfeature": "small feature",
    "valuevectors": "value vectors",
    "draftproposals": "draft proposals",
    "draftprobabilitiesq": "draft probabilities q",
    "manytotalparameters": "many total parameters",
    "optimizedkernel": "optimized kernel",
    "GPUthroughput": "GPU throughput",
    "productionquality": "production quality",
    "expertweights": "expert weights",
    "queryposition2": "query position 2",
    "rawKVbytes320": "raw KV bytes 320",
    "assignedcounts3": "assigned counts 3",
    "assignedcounts": "assigned counts",
    "acceptedcounts": "accepted counts",
    "tokenload": "token load",
    "top2tieindices0": "top-2 tie indices 0",
    "top2activation": "top-2 activation",
    "total131072expertweights": "total 131072 expert weights",
    "both48weightentries": "both 48 weight entries",
    "bothzerocasesfinite": "both zero cases finite",
    "LayerNormshiftinvariant": "LayerNorm shift invariant",
    "RMSNormchanges": "RMSNorm changes",
    "meanapproximately0": "mean approximately 0",
    "matricesagreewithin1e-10": "matrices agree within 1e-10",
    "gradientwithrespecttog1": "gradient with respect to g is 1",
    "withrespecttou0": "respect to u is 0",
    "outputSiLU": "output SiLU",
    "gategradient1": "gate gradient 1",
    "gatevalue": "gate value",
    "zero gradient": "zero gradient",
    "zero gatevalue": "zero gate value",
    "Atzero": "At zero",
    "hasderivativeone-half": "has derivative one-half",
    "Aconnectedzero": "A connected zero",
    "isnot": "is not",
    "abrokenautograd": "a broken autograd",
    "usesSiLU": "uses SiLU",
    "usesF": "uses F",
    "setofinvariances": "set of invariances",
    "trainingpolicy": "training policy",
    "model-specific": "model-specific",
    "initializationdepth": "initialization depth",
    "settingsstillmatter": "settings still matter",
    "stillmatter": "still matter",
    "ForSwiGLU": "For SwiGLU",
    "forSwiGLU": "for SwiGLU",
    "actualPyTorchautograd": "actual PyTorch autograd",
    "actualheld-out": "actual held-out",
    "aftermechanical": "after mechanical",
    "xWu": "xWu",
    "theupbranch": "the up branch",
    "gradient at": "gradient at",
    "particularinput": "particular input",
    "canfollow": "can follow",
    "directlyfrom": "directly from",
    "UseMQA": "Use MQA",
    "fewerKVheads": "fewer KV heads",
    "thisreference": "this reference",
    "andPythonloops": "and Python loops",
    "Pythonloops": "Python loops",
    "cachework": "cache work",
    "highacceptance": "high acceptance",
    "targetverification": "target verification",
    "draftcost": "draft cost",
    "draft or": "draft or",
    "both models": "both models",
    "acheaperdraft": "a cheaper draft",
    "cheaperdraft": "cheaper draft",
    "samplingpolicy": "sampling policy",
    "RNGschedule": "RNG schedule",
    "Exactdistribution": "Exact distribution",
    "identicalrandomsamples": "identical random samples",
    "identical randomsamples": "identical random samples",
    "numericalprecision": "numerical precision",
    "exact correctionrule": "exact correction rule",
    "rulewithargmax": "rule with argmax",
    "agreementwiththetarget": "agreement with the target",
    "agreement withthetarget": "agreement with the target",
    "claiming distributionpreservation": "claiming distribution preservation",
    "whileclaiming": "while claiming",
    "large-model": "large-model",
    "tinyCPU": "tiny CPU",
    "small NumPyK": "small NumPy K",
    "NumPyK": "NumPy K",
    "doesnotrun": "does not run",
    "fastservingkernel": "fast serving kernel",
    "ameasuredspeedup": "a measured speedup",
    "thefullsoftmax": "the full softmax",
    "sparseexperts": "sparse experts",
    "all experts": "all experts",
    "all models": "all models",
}


def polish_prose(text: str) -> str:
    for _ in range(2):
        for prefix, words in _JOINED.items():
            for word in words.split():
                text = re.sub(
                    r"\b" + re.escape(word) + r"\b", prefix + " " + word[len(prefix) :], text
                )
        for source, target in _REPAIRS.items():
            text = text.replace(source, target)
    # Spacing only around ordinary prose counts, not identifiers or code fences.
    text = re.sub(
        r"\b(is|are|gives|gives us|about|approximately|contains|counts|equals|yield|yields|at|by|in|from|to|of|with|for|and|or|both|uses|total|mean|width|capacity|token|tokens|inputs|labels|norm|outputs|output|frequencies|positions|position|indices|experts|expert|alpha|coefficient|rejection|residual|accepted_count|accepted|count|budget|score|scores|values|value|base|log|slope|query|head|queryheads|headwidth|modelwidth|KVheads|hidden)(?=\d)",
        r"\1 ",
        text,
    )
    text = re.sub(r"(?<=\d)(?=percent\b|bytes\b|tokens\b|entries\b|weights\b|seconds\b)", " ", text)
    text = text.replace("within1e-", "within 1e-").replace("Truefor", "True for")
    return text


_unpolished_enrich_guide = enrich_guide


def enrich_guide(identity: str, document: str) -> str:
    before = re.findall(r"```python\n(.*?)```", document, re.S)
    document = _unpolished_enrich_guide(identity, document)
    parts = re.split(r"(```.*?```)", document, flags=re.S)
    document = "".join(part if part.startswith("```") else polish_prose(part) for part in parts)
    if before != re.findall(r"```python\n(.*?)```", document, re.S):
        raise ValueError("Prose review changed a Python worked block")
    return document


_REPAIRS.update(
    {
        "aRoPE": "a RoPE",
        "ForALiBi": "For ALiBi",
        "everypaper": "every paper",
        "indexi": "index i",
        "positionp": "position p",
        "a2Drotation": "a 2D rotation",
        "byp*frequency": "by p*frequency",
        "add-slope": "add -slope",
        "Normalizevector3": "Normalize vector [3",
        "4 with unit gain": "4] with unit gain",
        "epsilon1e-8": "epsilon 1e-8",
        "hiddenwidth": "hidden width",
        "Inspectbothgate": "Inspect both gate",
        "aunit": "a unit",
        "appearsinactive": "appears inactive",
        "taskquality": "task quality",
        "usefloat64": "use float64",
        "computesx": "computes x",
        "timesgain": "times gain",
        "Apre/post": "A pre/post",
        "linearbranch": "linear branch",
        "beforecounting": "before counting",
        "Usebatch1": "Use batch 1",
        "time5": "time 5",
        "compareKVheads4": "compare KV heads 4",
        "weights256": "weights 256",
        "withoutbiases": "without biases",
        "raiseValueError": "raise ValueError",
        "outputNaNs": "output NaNs",
        "aremeasured": "are measured",
        "peakmemory": "peak memory",
        "Queryheadh": "Query head h",
        "headh//": "head h//",
        "UseexpertsI": "Use experts I",
        "probabilities3/4": "probabilities 3/4",
        "policiesraiseValueError": "policies raise ValueError",
        "supportconditional": "support conditional",
        "itsrouting": "its routing",
        "justmeanexpert": "just mean expert",
        "cost ofa": "cost of a",
        "densemodel": "dense model",
        "ThisCPUreference": "This CPU reference",
        "realexpert-parallel": "real expert-parallel",
        "routerlogits": "router logits",
        "Thecapacity": "The capacity",
        "fractionsf": "fractions f",
        "probabilitiesP": "probabilities P",
        "heldfixed": "held fixed",
        "Usep[": "Use p[",
        "acceptedmass": "accepted mass",
        "rejectionmass": "rejection mass",
        "combinedmassp": "combined mass p",
        "isNone": "is None",
        "enoughagreement": "enough agreement",
        "servingstack": "serving stack",
        "exploitparallel": "exploit parallel",
        "ifdraft": "if draft",
        "differentRNG": "different RNG",
        "itdoes": "it does",
        "notmeasure": "not measure",
        "GPUkernels": "GPU kernels",
        "whereq": "where q",
        "ispositive": "is positive",
        "azero-qtoken": "a zero-q token",
        "cannotbe": "cannot be",
        "avaliddraftsample": "a valid draft sample",
        "acceptedEOS": "accepted EOS",
        "position-dependentkeyvectors": "position-dependent key vectors",
        "canbe": "can be",
        "targetprobabilitiesp": "target probabilities p",
        "adrafttokeni": "a draft token i",
        "isaccepted": "is accepted",
        "withprobabilitymin": "with probability min",
        "Ifrejected": "If rejected",
        "sample fromthenormalized": "sample from the normalized",
        "add back topexactly": "add back to p exactly",
        "mustalready": "must already",
        "theintended": "the intended",
        "mustrefer": "must refer",
        "At thefirstrejection": "At the first rejection",
        "Ifallproposals": "If all proposals",
        "areaccepted": "are accepted",
        "mustbe": "must be",
        "itscorrectposition": "its correct position",
        "Itdoesnotrun": "It does not run",
        "It doesnotrun": "It does not run",
        "real small": "real small",
        "notclaim": "not claim",
        "models mustrefer": "models must refer",
        "matchingvocabulary": "matching vocabulary",
        "same tokenidentities": "same token identities",
        "smallmatrices": "small matrices",
        "doesnotverify": "does not verify",
        "gate rule": "gate rule",
        "localgradient": "local gradient",
        "output scale": "output scale",
        "differentRNGschedule": "different RNG schedule",
        "targetsampling": "target sampling",
        "the declaredformula": "the declared formula",
        "lowerauxiliary": "lower auxiliary",
        "not itself": "not itself",
        "taskloss": "task loss",
        "capacitydrops": "capacity drops",
        "distributedutilization": "distributed utilization",
        "dropped token": "dropped token",
        "lasttoken": "last token",
        "auxiliaryloss": "auxiliary loss",
        "balancedfixture": "balanced fixture",
        "token1": "token 1",
        "token2": "token 2",
        "corrected to0": "corrected to 0",
        "rejection.3": "rejection .3",
        "long_context_quality_verifiedFalse": "long_context_quality_verified=False",
        "firstoutputcoordinate": "first output coordinate",
        "firsttop2mixture": "first top-2 mixture",
        "usesame": "use same",
        "thenrollbackandappend": "then roll back and append",
        "before branching": "before branching",
        "the exact target": "the exact target",
        "with respect to u is 0": "with respect to u is 0",
        "gradient with respect to g is 1": "gradient with respect to g is 1",
    }
)

_REPAIRS.update(
    {
        "mechanism:it": "mechanism: it",
        "differ:adding": "differ: adding",
        "problem:how": "problem: how",
        "free:all": "free: all",
        "explicitly:the": "explicitly: the",
        "computesNorm": "computes Norm",
        "everyfeature": "every feature",
        "aplain": "a plain",
        "largerbudget": "larger budget",
        "Useq[": "Use q[",
        "anglesm": "angles m",
        "keys0": "keys 0",
        "Usewidth4": "Use width 4",
        "comparepre-normx": "compare pre-norm x",
        "post-normLayerNorm": "post-norm LayerNorm",
        "g0, u2": "g=0, u=2",
        "respecttou0": "respect to u is 0",
        "Compareautograd": "Compare autograd",
        "at x1, 2, 3": "at x=[1, 2, 3]",
        "CompareplainFFNwidthd4": "Compare plain FFN model width d=4",
        "SwiGLUhidden4": "SwiGLU hidden width 4",
        "excludingbiases": "excluding biases",
        "executea4-to-4gatedblock": "execute a gated block with input and output width 4",
        "outputshape": "output shape",
        "Shiftx1, 2, 3": "Shift x=[1, 2, 3]",
        "comparethetwo": "compare the two",
        "normalizezero": "normalize zero",
        "Use4queryheads": "Use 4 query heads",
        "Try4queryheads": "Try 4 query heads",
        "2KVheads": "2 KV heads",
        "3KVheads": "3 KV heads",
        "eachKVhead": "each KV head",
        "compareblock": "compare block",
        "sizes1": "sizes 1",
        "rows3and4": "rows 3 and 4",
        "comparethe first": "compare the first",
        "firstthree": "first three",
        "overexperts": "over experts",
        "lessconcentrated": "less concentrated",
        "butit": "but it",
        "Routefourtokens": "Route four tokens",
        "Usehard": "Use hard",
        "routerprobabilities": "router probabilities",
        "expertcount2": "expert count 2",
        "coefficient.01": "coefficient .01",
        "loss.012": "loss .012",
        "fixture.01": "fixture .01",
        "selectedexperts": "selected experts",
        "is-3/16": "is -3/16",
        "Use8two-layerexperts": "Use 8 two-layer experts",
        "excludingrouter": "excluding router",
        "131072expert": "131072 expert",
        "32768selectedexpert": "32768 selected expert",
        "Rejecttopk0": "Reject top-k 0",
        "checkequal": "check equal",
        "lowerindices": "lower indices",
        "policiesraise": "policies raise",
        "probabilitymin": "probability min",
        "draftmass": "draft mass",
        "pexactly": "p exactly",
        "Cachedkeys": "Cached keys",
        "draftpositions": "draft positions",
        "correctposition": "correct position",
        "Varrays": "V arrays",
        "Itdoes": "It does",
        "notrun": "not run",
        "measuredspeedup": "measured speedup",
        "acceptancedraw.8": "acceptance draw .8",
        "withdraw.5": "with draw .5",
        "Setdraft": "Set draft",
        "equal top;": "equal to p;",
        "withdraws.1": "with draws .1",
        "usebonusdraw.7": "use bonus draw .7",
        "Useconstanttargetp": "Use constant target p",
        "draftq": "draft q",
        "draws.1": "draws .1",
        "draws.2": "draws .2",
        "acceptedprefix": "accepted prefix",
        "correction0": "correction 0",
        "Startcacheprefix": "Start cache prefix",
        "appendthetwo": "append the two",
        "comparewithafreshcache": "compare with a fresh cache",
        "equality,EOS,budgets": "equality, EOS, budgets",
        "Checkp=q": "Check p=q",
        "hasnoresidual": "has no residual",
        "stoponanaccepted": "stop on an accepted",
        "EOS2": "EOS 2",
        "capoutputat2": "cap output at 2",
        "draftproposal": "draft proposal",
        "label5": "label 5",
        "weight0": "weight 0",
        "BOS1": "BOS 1",
        "MASK0": "MASK 0",
        "queryheads": "query heads",
        "headwidth": "head width",
        "modelwidth": "model width",
    }
)


def polish_document_prose(document: str) -> str:
    """Repair prose while leaving every fenced block byte-identical."""
    parts = re.split(r"(```.*?```)", document, flags=re.S)
    return "".join(part if part.startswith("```") else polish_prose(part) for part in parts)
