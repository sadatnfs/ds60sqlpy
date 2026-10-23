# 33. Deep Learning, Language, and Generative Modeling

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-033`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Deep learning learns compositions of numerical transformations from data. Language modeling is one application of that idea, not a replacement for statistical problem formulation. A data scientist should connect the training objective, available information, representation and decision before choosing an architecture. A model that predicts plausible text can support extraction, classification, coding and synthesis, but fluency alone does not establish factual accuracy, calibrated uncertainty or valid causal inference.

### Start with tensors and the chain rule

A tensor is a multidimensional numerical array. For one dense layer, input x is multiplied by weights W and shifted by bias b, producing z=Wx+b. A nonlinear activation a=g(z) allows compositions to represent more than one overall linear transformation. A loss L compares the output with a target or training signal. Backpropagation applies the chain rule through the recorded computation, producing derivatives such as dL/dW. An optimizer then changes weights. Forward computation, gradient calculation and parameter update are three separate operations.

The derivative is local: it describes how an infinitesimal parameter change affects the current objective on the current batch. It does not guarantee that a finite update improves validation performance or that the objective matches the real task. Check gradients on a tiny deterministic calculation, use numerically stable losses, and monitor training and held-out behavior separately. A decreasing training loss can accompany memorization, label leakage or an unsuitable target.

### Turn language into a prediction problem

Text is converted into token IDs by a tokenizer. Tokens may be words, subwords, bytes or other units; one visible word can span several tokens. An embedding lookup maps IDs to learned vectors. Positional information tells a sequence model how order should matter. For an autoregressive language model, the sequence probability factorizes as p(x_1,...,x_T)=product_t p(x_t|x_<t). Training usually minimizes the negative log probability of observed next tokens. The target is shifted relative to the input, and a causal mask prevents a position from reading future target tokens.

This objective rewards statistical prediction of text in the training distribution. It can produce useful internal representations and broad capabilities, but it is not a direct truth-verification objective. At generation time, the model emits a distribution over the next token. Greedy decoding selects the largest probability; temperature and sampling change the distribution of outputs. A low-temperature answer may be repeatable and still wrong. Confidence in one token is also not automatically confidence in a multi-claim answer.

### Understand attention without treating it as a metaphor

For a sequence with n positions and representation dimension d, linear projections produce query, key and value matrices Q, K and V. Scaled dot-product attention computes softmax(Q*K_transpose/sqrt(d_k)+M)*V, where M encodes forbidden positions with negative infinity before softmax. Each query position obtains weights over allowed key positions and forms a weighted sum of their values. Multihead attention repeats this with different projections. Residual connections, normalization and feed-forward blocks surround attention in a transformer.

The matrix expression makes several failure modes concrete. A mask with the wrong triangle can leak future tokens. Softmax without subtracting the maximum can overflow numerically. Confusing batch, position and feature axes can produce valid-looking arrays with the wrong semantics. Attention weights describe one internal computation; they are not automatically faithful explanations of why a final answer was produced. Long context also creates memory and computation costs, and adding more documents can dilute useful evidence.

### Distinguish the adaptation choices

Pretraining learns broad parameters from a large self-supervised corpus. Continued pretraining or domain-adaptive pretraining continues a similar objective on domain text, helping with vocabulary and distribution but risking forgetting or contamination. Supervised fine-tuning, or SFT, uses curated input-output examples to teach a desired task or response behavior. For conversational SFT, the loss may be restricted to assistant response tokens while prompt and padding tokens are masked. The dataset must encode the behavior you want, including boundaries and appropriate abstention, rather than merely contain documents about the topic.

Full fine-tuning updates many or all base parameters. Parameter-efficient approaches update a smaller representation, such as LoRA matrices whose product adds a low-rank weight change. They reduce trainable-state cost but still require a valid dataset, a compatible base model, carefully chosen optimization settings and an independent evaluation. Quantization changes numerical representation and memory use; it is not the same operation as fine-tuning. A smaller adapter does not make an experiment automatically cheap, safe from overfitting or transferable between incompatible base versions.

Retrieval-augmented generation, or RAG, supplies selected external evidence at inference time. It changes the context available for an answer without necessarily changing model weights. This is often appropriate for frequently changing facts, auditable sources and permission-sensitive enterprise documents. Fine-tuning is often better suited to stable response patterns, extraction formats or domain-specific task behavior. The methods can be combined: an adapted model may still need retrieval, and a retrieval system may benefit from trained query or ranking components. Decide from measured failure cases rather than treating either as a universal upgrade.

### Build a subject-matter assistant as an evidence system

Start with a bounded task, such as extracting outage attributes from reports or answering questions about a versioned procedure collection. Preserve document IDs, versions, timestamps, section boundaries and permissions during ingestion. Chunking should retain enough local context to interpret a passage, with metadata connecting a chunk to its source. Retrieve candidates, optionally rerank them, and construct a prompt that distinguishes the user request from quoted evidence. Retrieved text is data to evaluate, including potentially misleading instructions, not an authority to redefine the assistant's task.

The answer contract should require claims tied to specific supporting passages and an explicit unsupported/unknown outcome when evidence is insufficient. Citations must be checked for entailment and source identity, not merely for presence. A policy document may support what a process says, while a runtime log supports what actually happened. The assistant must preserve that evidence distinction. Conflicting sources need recency, scope and authority reasoning; silently merging them can create a rule no source ever stated.

For data science, let tested code compute statistics, model metrics, SQL aggregations and confidence intervals. The language model can propose code, explain an estimator, identify documentation or draft a narrative, but the final numerical claim should link to the executed artifact and assumptions. A generated sentence saying that a treatment caused an outcome is not a substitute for identification. Structured extraction also needs schema validation and representative error measurement before its fields become analytical data.

### A measured path from baseline to adaptation

Create a held-out collection of realistic tasks before changing prompts or weights. Partition related documents, customers and time periods so near-duplicate material does not cross the development/evaluation boundary. Establish a simple prompt and retrieval baseline, then classify failures: missing evidence, poor ranking, misunderstood instructions, wrong output format, unsupported reasoning or stale source. Change the component implicated by the evidence. Compare task success, abstention, subgroup failures, cost and latency, and inspect regressions in previously working cases.

The following NumPy demonstrations expose backpropagation, causal masking, low-rank updates and response-only training loss. A fifth example creates a source-identified retrieval packet. They use no downloaded model and do not claim to fine-tune or evaluate a real language model. Their purpose is to make the mathematical and information boundaries inspectable before moving to the dedicated applied LLM route.

## Methods, mechanisms, and limits

### stat-33-01

**Backpropagation**

Backpropagation computes derivatives by traversing a computation graph in reverse and applying local chain-rule factors. Shared parameters accumulate gradient contributions from every use. The gradient is of the implemented loss, so a wrong mask or mislabeled target can yield perfectly correct gradients for the wrong objective. Use finite differences on a tiny smooth example to check implementation, while recognizing that nondifferentiable points, floating precision and stochastic layers complicate that diagnostic.

### stat-33-02

**Convolutional neural networks**

Convolutional networks apply shared local filters across positions, exploiting locality and translation structure. Kernel width, stride, dilation and padding determine the receptive field and output shape. Pooling or striding can discard spatial detail, useful for invariance but harmful for precise localization. In text, a one-dimensional filter can recognize local token patterns; it does not inherently model arbitrarily distant dependencies. Verify tensor axes and boundary padding before interpreting a learned feature.

### stat-33-03

**Recurrent neural networks**

Recurrent networks maintain hidden state h_t=f(x_t,h_(t-1)), sharing parameters across sequence positions. This provides a compact sequential memory but makes training depend on gradients propagated through many transitions. Repeated multiplication by Jacobians can shrink or amplify gradients. Truncated backpropagation limits training history and memory cost. Reset state at true sequence boundaries, and distinguish a model's hidden state from a guaranteed record of every earlier fact.

### stat-33-04

**LSTMs and gated recurrent units**

LSTMs and GRUs add gates that control retention, writing and reading of recurrent information. An LSTM cell state provides an additive pathway that can improve gradient flow compared with a simple recurrence. Gate values are learned from the task, not hand-coded guarantees of long-term memory. Sequence padding, masking and hidden-state initialization remain important. Compare their value against simpler temporal models rather than assuming gated recurrence always captures the relevant history.

### stat-33-05

**Attention mechanisms**

Attention computes data-dependent weighted combinations of value vectors using compatibility between queries and keys. The softmax normalizes weights over allowed positions, and masking defines which positions may contribute. It is useful for retrieving context within a sequence or between sequences. Attention weights can be diffuse, saturated or sensitive to representation scale, and their magnitude is not automatically a faithful feature-importance explanation of the final model output.

### stat-33-06

**Transformers**

Transformers combine attention, position information, feed-forward layers, normalization and residual pathways. Encoder-style attention can use both directions for representation tasks, while autoregressive decoding needs a causal mask. Encoder-decoder models add cross-attention to a separate input representation. Tokenizer, context limits and positional scheme are part of the model contract. Architecture capacity does not remove the need for representative training data, stable optimization and task-specific evaluation.

### stat-33-07

**Residual connections**

A residual connection adds a block's input to its transformed output, such as y=x+F(x). This preserves a direct path for information and gradients while the block learns a correction. Shapes must match or use an explicit projection. Residual paths help optimization but do not ensure every layer learns a useful distinct function. Large activation scales or poorly placed normalization can still destabilize deep networks.

### stat-33-08

**Normalization methods**

Normalization methods rescale activations using selected axes and statistics. Batch normalization uses batch-dependent training statistics and different inference behavior; layer normalization operates within a representation and is common in transformers. These methods are not interchangeable. Record which dimensions are normalized, how epsilon prevents division by zero and whether learned scale/shift parameters are used. Training-serving mismatches in statistics can cause failures despite unchanged weights.

### stat-33-09

**Dropout**

Dropout randomly removes selected activations during training and commonly rescales survivors so their expectation is preserved. At ordinary inference the stochastic removal is disabled. Its regularization effect depends on placement, rate and architecture; too much dropout can destroy useful signal. A reproducibility check must control the random state or compare distributional behavior. Leaving training-mode dropout active accidentally can make otherwise identical evaluations inconsistent.

### stat-33-10

**Self-supervised learning**

Self-supervised learning derives targets from the data itself, such as the next token, a masked segment or another view of the same observation. It reduces the need for manually labeled targets but still inherits corpus selection, contamination and shortcut risks. The pretext objective should encourage representations useful for the downstream task. A lower pretraining loss does not guarantee better extraction accuracy, safer abstention or more faithful domain explanations.

### stat-33-11

**Masked modeling**

Masked modeling hides selected input portions and trains the model to reconstruct them from the remaining context. The masking distribution controls which dependencies are learned. A bidirectional masked-language model solves a different conditional problem from left-to-right generation. If preprocessing leaves trivial clues to the hidden value, the objective can be solved without learning the desired structure. Evaluate transfer to actual tasks, not only reconstruction of the training mask pattern.

### stat-33-12

**Autoregressive modeling**

Autoregressive modeling factorizes a joint distribution into conditionals ordered by a chosen sequence. Training must shift inputs and targets and forbid access to later target positions. At generation, earlier sampled outputs become later inputs, creating error propagation and a distribution difference from teacher-forced training. The factorization is mathematically general, but practical quality depends on context length, ordering, optimization and decoding decisions.

### stat-33-13

**Sequence-to-sequence modeling**

Sequence-to-sequence modeling maps a variable-length input sequence to an output sequence, as in translation, summarization or structured extraction. Encoder-decoder and prompted decoder-only architectures implement different conditioning paths. Evaluation should distinguish content preservation, unsupported additions and format validity. A fluent summary can omit a critical qualification, so a generic language score may miss the task's most costly failure.

### stat-33-14

**Language modeling**

Language modeling estimates probabilities over token sequences, usually through a next-token or masked objective. Cross-entropy measures predictive fit to the evaluation token distribution, and perplexity exponentiates average negative log likelihood under a defined tokenization. Scores are not directly comparable across different tokenizers without care. Better predictive fit does not by itself establish truthfulness, reasoning correctness or useful calibration of multi-sentence answers.

### stat-33-15

**Topic modeling**

Topic modeling discovers latent co-occurrence structure in document collections, often representing documents by mixtures or low-dimensional factors. The learned topic is a statistical pattern, not necessarily a stable human concept. Tokenization, stopword handling, corpus composition and topic count shape results. Inspect representative documents and stability, and avoid treating topic proportions as error-free measurements when they become predictors in a later statistical analysis.

### stat-33-16

**Latent Dirichlet allocation**

Latent Dirichlet allocation assumes documents draw topic mixtures and words arise through topic-specific categorical distributions, with Dirichlet priors controlling mixtures. Its bag-of-words structure ignores word order and many linguistic relationships. Inference approximates latent assignments, and topic labels are assigned by analysts after inspection. Coherence and predictive metrics help comparison, but neither guarantees that a topic corresponds to the substantive construct a study wants to measure.

### stat-33-17

**Variational autoencoders**

A variational autoencoder combines a generative latent-variable model with an approximate encoder posterior. Training maximizes an evidence lower bound comprising expected reconstruction log likelihood minus a KL divergence to the prior. Reparameterization permits gradient estimates for suitable continuous latent variables. Reconstruction quality, posterior collapse and latent regularization must be considered together. A low-dimensional latent coordinate is not automatically an identifiable causal or semantic factor.

### stat-33-18

**Generative adversarial networks**

A generative adversarial network trains a generator against a discriminator or critic that distinguishes generated and observed samples. The generator learns through the critic's feedback rather than an explicit normalized likelihood in the basic formulation. Training can oscillate or collapse to a limited set of outputs. Evaluate diversity, fidelity and task utility separately; convincing individual samples can hide missing regions of the data distribution.

### stat-33-19

**Normalizing flows**

Normalizing flows transform a simple base distribution through invertible mappings and use the change-of-variables Jacobian determinant to evaluate density. The architecture trades expressiveness against tractable inverse and determinant calculations. Exact likelihood under the model does not ensure perceptual quality or meaningful outlier ranking. Support restrictions and numerical stability matter when applying a continuous density model to discrete or constrained data.

### stat-33-20

**Diffusion models**

Diffusion models learn to reverse a specified progressive noise process, commonly through noise or score prediction at different noise levels. Sampling applies a sequence of denoising steps, with a speed-quality tradeoff determined by the sampler and model. Conditioning can guide generation, but outputs still require task evaluation. The noise schedule, objective and sampling procedure are distinct components, and one denoising calculation is not a complete trained generative system.

### stat-33-21

**Energy-based models**

Energy-based models assign a compatibility score E(x) and often define probability proportional to exp(-E(x)), with a normalization constant that may be intractable. Learning and sampling must address that normalization or use alternative objectives. An energy difference can rank examples without providing calibrated probabilities. Mixing behavior, negative-sample construction and numerical scale are central to whether the learned score represents the intended distribution.

### stat-33-22

**Multimodal models**

Multimodal models combine signals such as text, images, audio and structured records through shared or interacting representations. Alignment requires paired data or a justified correspondence objective, and missing modalities need an explicit policy. One modality can provide shortcuts that fail when collection conditions change. Evaluate cross-modal consistency and provenance: a generated description of an image should be checked against the image, not only against plausible accompanying text.

### stat-33-23

**Fine-tuning**

Fine-tuning updates a pretrained model using a narrower dataset or objective. SFT teaches demonstrated input-output behavior; continued pretraining adapts language distribution; task-specific heads learn a particular prediction. These are different experiments. Split by source/entity/time before curating examples, preserve a frozen test set and compare with a prompt/retrieval baseline. Monitor overfitting, forgetting, subgroup regressions and output behavior rather than using training-loss reduction as acceptance.

### stat-33-24

**Parameter-efficient adaptation**

Parameter-efficient adaptation changes a restricted parameter set or low-dimensional update. In LoRA, W_effective=W0+(alpha/r)*B*A with A of shape r by input_dimension and B of shape output_dimension by r. The base W0 is frozen, while A and B learn a rank-at-most-r correction. Savings depend on r and targeted layers. Adapter compatibility, initialization and optimizer state still matter, and reduced trainable count does not guarantee adequate capacity or generalization.

### stat-33-25

**Knowledge distillation**

Knowledge distillation trains a student to reproduce a teacher's predictions, distributions or intermediate representations, often combining teacher and labeled losses. Soft distributions can convey relative alternatives beyond a hard target. The teacher can also transfer errors, biases and unsupported behavior. Evaluate the student independently on the real task and account for distribution shift; matching a teacher is a training objective, not proof of task correctness.

### stat-33-26

**Retrieval-augmented generation**

Retrieval-augmented generation supplies selected external passages to a generator so answers can use evidence outside model weights. The pipeline includes ingestion, chunking, indexing, permission filtering, retrieval, reranking, context construction, generation and verification. Failures can arise at each stage. Cite versioned source passages and support abstention when evidence is absent. Retrieval improves access to facts but does not force correct interpretation, and retrieved instructions must not override the task authority.

### stat-33-27

**Preference optimization**

Preference optimization adjusts behavior using comparisons between outputs rather than only a single demonstrated answer. Reward-model approaches and direct methods such as DPO use different optimization constructions. A preference dataset encodes a rubric and population of raters, including their biases and disagreements. Improving preference fit can reward verbosity or style instead of factuality unless the comparisons are designed carefully. Keep independent factual, utility and regression evaluations after optimization.

## Worked Python demonstrations

Complete offline program: [chapter_33.py](../examples/chapter_33.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_33.py
```

### Derive and check one gradient

The two-feature input is [1,2], weights are [0.2,-0.1], and the tanh activation initially receives zero. With target 0.8, squared-error differentiation gives gradient [-0.8,-1.6]. Central finite differences agree within tolerance, and a small step in the negative-gradient direction lowers this same example's loss. This checks calculus and implementation, not generalization.

### Prove that future input is masked

Three two-dimensional positions form queries, keys and values. Scores above the causal diagonal become negative infinity before a stable row-wise softmax, yielding exactly zero weight on future positions. Replacing the last position with a dramatically different vector leaves the first two outputs unchanged. This is a meaningful negative-control test for information leakage, not merely a shape check.

### Count a low-rank adaptation honestly

The base matrix has shape 8 by 6 and 48 entries. A rank-two adapter uses A with 12 and B with 16 entries, 28 trainable values in total. Their product has the correct 8 by 6 shape and rank at most two. The example demonstrates the algebra and count only; actual memory includes base weights, activations, optimizer state and framework overhead.

### Separate prompt tokens from response supervision

Four target-token probabilities are [0.01,0.02,0.8,0.5], but only the final two are assistant-response targets. The masked loss is -log(0.8*0.5)/2, about 0.458. Changing the prompt-token probabilities leaves it unchanged. Real SFT also needs shifted labels, padding/attention masks, consistent chat formatting and careful sequence packing.

### Construct evidence without pretending to generate an answer

A tiny lexical retriever selects source-identified passages from a policy, runtime log and glossary. The first retrieved source supports the approval rule. A log about one completed restart would support a runtime event, not a general permission rule. The program returns a packet, not an invented model response; a real generator would need separate grounding and citation evaluation.

### Complete executable example

```python
import numpy as np

def gradient_check():
    x=np.array([1.,2.]);w=np.array([.2,-.1]);target=.8
    def loss(weights):
        prediction=np.tanh(x@weights)
        return .5*(prediction-target)**2
    prediction=np.tanh(x@w)
    gradient=(prediction-target)*(1-prediction**2)*x
    eps=1e-6;numerical=np.empty_like(w)
    for i in range(len(w)):
        step=np.zeros_like(w);step[i]=eps
        numerical[i]=(loss(w+step)-loss(w-step))/(2*eps)
    assert np.allclose(gradient,numerical,atol=1e-8)
    assert loss(w-.1*gradient)<loss(w)
    print("Analytic and numerical gradient:",gradient,numerical)

def causal_attention():
    x=np.array([[1.,0.],[0.,1.],[1.,1.]])
    def attention(values):
        logits=values@values.T/np.sqrt(values.shape[1])
        mask=np.triu(np.ones(logits.shape,dtype=bool),k=1)
        logits=np.where(mask,-np.inf,logits)
        weights=np.exp(logits-np.max(logits,axis=1,keepdims=True))
        weights/=weights.sum(axis=1,keepdims=True)
        return weights@values,weights
    output,weights=attention(x)
    changed=x.copy();changed[2]=[100.,-100.]
    later,_=attention(changed)
    assert np.allclose(weights.sum(axis=1),1.)
    assert np.allclose(weights[np.triu_indices(3,k=1)],0.)
    assert np.allclose(output[:2],later[:2])
    print("Causal attention weights:",weights)

def low_rank_update():
    base=np.zeros((8,6));a=np.arange(12,dtype=float).reshape(2,6)/10
    b=np.arange(16,dtype=float).reshape(8,2)/20
    update=b@a;effective=base+update
    assert effective.shape==(8,6) and np.linalg.matrix_rank(update)<=2
    assert a.size+b.size==28 and base.size==48
    print("Full weights versus adapter parameters:",base.size,a.size+b.size)

def response_only_loss():
    target_probability=np.array([.01,.02,.8,.5])
    response_mask=np.array([False,False,True,True])
    loss=-np.log(target_probability[response_mask]).mean()
    changed=target_probability.copy();changed[:2]=[.9,.9]
    assert np.isclose(loss,-np.log(changed[response_mask]).mean())
    assert np.isclose(loss,-np.log(.4)/2)
    print("Response-only negative log likelihood:",loss)

def evidence_packet():
    docs=[("runbook-v2","restart requires an approved change"),
          ("runtime-17","restart completed at 14:00"),
          ("glossary-v1","a restart creates a new process")]
    query=set("restart approved change".split())
    scored=sorted(((len(query & set(text.split())),doc_id,text) for doc_id,text in docs),reverse=True)
    packet=[{"source_id":doc_id,"text":text} for score,doc_id,text in scored[:2]]
    assert packet[0]["source_id"]=="runbook-v2"
    assert all(item["source_id"] and item["text"] for item in packet)
    print("Retrieved evidence packet:",packet)

def main():
    gradient_check();causal_attention();low_rank_update();response_only_loss();evidence_packet()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: When would you choose RAG over fine-tuning?** Start with the observed failure. Missing, changing or permission-controlled facts suggest retrieval and source management. Repeated formatting, extraction or task-behavior errors may justify SFT with curated examples. Neither choice eliminates evaluation, and the two can be combined when evidence access and behavior both need improvement.

**Interview: What does LoRA actually learn?** It learns low-rank correction factors added to selected frozen weight matrices. It does not merely append documents to a search index, and it does not guarantee that every training fact can later be retrieved faithfully. Rank, target layers, base-version compatibility and the task dataset determine the experiment.

**Interview: Can lower language-model loss validate a subject-matter assistant?** It establishes better predictive fit under that token-level evaluation. The assistant may still cite the wrong source, confuse policy with runtime evidence, mishandle access restrictions or produce invalid structured fields. Validate representative end-to-end tasks and explicit failure boundaries.

**Interview: How should an LLM assist statistical analysis?** It can help formulate code, retrieve method documentation and explain a checked result. Execute the analysis in a controlled environment, verify data and assumptions, and link the narrative to the output. Generated confidence intervals or causal claims are proposals until the computation and identification argument are reviewed.

**Interview: Why keep an abstention case in the training and test data?** A domain assistant must recognize when available evidence does not support an answer. If every demonstration forces a confident answer, adaptation can reward guessing. Evaluate both unsupported-answer rate and unnecessary abstention so reliability is not achieved by refusing every useful task.

## Primary sources and official APIs

- [Vaswani and colleagues, Attention Is All You Need](https://proceedings.neurips.cc/paper/7181-attention-is-all-you-need)

- [Hu and colleagues, LoRA](https://arxiv.org/abs/2106.09685)

- [Lewis and colleagues, Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)

- [Ouyang and colleagues, instruction following with human feedback](https://arxiv.org/abs/2203.02155)

- [Rafailov and colleagues, Direct Preference Optimization](https://arxiv.org/abs/2305.18290)

- [Kingma and Welling, Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114)

- [Ho and colleagues, Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239)

## Continue into applied language-model work

The [SFT data and masking guide](../../llm-applied/guides/llm-applied-014.md) develops the response-only loss boundary into an applied workflow. The [grounded claims and citations guide](../../llm-applied/guides/llm-applied-011.md) turns the subject-assistant evidence contract into inspectable examples. Use those guides for implementation details while retaining this chapter's distinction between weight adaptation, retrieved evidence and statistically validated conclusions.

## Reading connections

[Previous chapter](32-recommendation-information-retrieval-and-ranking.md) | [Book contents](../README.md) | [Next chapter](34-generative-ai-and-language-model-evaluation.md)
