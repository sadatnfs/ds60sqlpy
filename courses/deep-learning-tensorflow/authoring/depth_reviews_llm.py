"""Topic-specific prose additions; executable fixtures are deliberately unchanged."""

DEPTH_NOTES = {
'llm-012': '''## Derive the actual selection probabilities

For logits [2, 1, 0], stable softmax can subtract 2 and normalize [1, exp(-1), exp(-2)]. The probabilities are approximately [0.665241, 0.244728, 0.090031]. Temperature 0.5 first divides the logits by 0.5, giving probabilities [0.866813, 0.117310, 0.015876]. Temperature 2 gives approximately [0.506480, 0.307196, 0.186324]. The order remains unchanged for every positive temperature, so greedy selection still chooses token zero. Sampling frequencies change because the mass assigned to each interval changes.

Temperature modifies the selection distribution, not the learned weights or the factual evidence available to the model. A sharper distribution can confidently select an incorrect token. It should not be described as improving calibration merely because its highest probability increases. Zero temperature is implemented as a separate greedy policy here; dividing scores by zero is not a numerical implementation of that policy. When several logits tie for the maximum, a positive-temperature limit distributes mass among them, while this lesson's greedy rule selects the smallest index.

## Filtering and drawing are separate operations

Keeping only the first two logits produces probabilities [exp(2)/(exp(2)+exp(1)), exp(1)/(exp(2)+exp(1)), 0], approximately [0.731059, 0.268941, 0]. Removing the third probability after the original normalization would leave a total near 0.909969, which is not a complete categorical distribution. Filtering must be followed by normalization over the retained support.

For probabilities [0.5, 0.3, 0.2], cumulative boundaries are [0.5, 0.8, 1]. Draws in [0, 0.5) select token zero, [0.5, 0.8) select token one, and [0.8, 1) select token two. The right-sided search puts a draw exactly equal to 0.5 in the second interval. A draw of one belongs to none of these half-open intervals and must be rejected. Zero-probability tokens have empty intervals and should not be selected.

The fixture supplies explicit draws so the decision can be reconstructed without a hidden RNG state. Real generation must preserve both the random-source state and the decoding policy if it is to be replayed. Changing top-k, temperature, tie ordering or the number of earlier draws can change output despite reusing a seed. The later nucleus-sampling chapter adds a probability-mass cutoff, termination rules and output caps; these are policy choices with their own failure cases.
''',
'llm-013': '''## Two different information boundaries

A causal mask constrains which input positions can influence a representation. The training objective separately specifies which target that representation must predict. For [2, 5, 7, 3], inputs [2, 5, 7] pair with targets [5, 7, 3], giving three next-token events. Copying inputs into labels creates targets [2, 5, 7] instead. The current token is visible under an ordinary causal mask, so an identity objective can appear easy while answering a different question. Mask correctness does not establish objective correctness.

Document boundaries are another part of the objective. Documents of lengths four and two contribute three plus one adjacent transitions. Concatenating them without an explicit boundary policy adds a fifth transition from the final token of the first document to the first token of the second. Whether that transition is meaningful depends on how the corpus is defined. A separator or end-of-document token is a deliberate modeling choice, not a repair that can be silently added after observing a score.

## Trace where evaluation information can enter

Exact text hashes catch byte-identical duplicates across files. They do not identify every paraphrase, translated copy, templated document or later revision. Family IDs can keep related records together when those relationships are known. The family grouping rule should reflect the deployment question: predicting another paragraph from the same document is different from generalizing to a new document source or organization.

Representation fitting also belongs to training. If a vocabulary is fitted on training words alpha and beta, the validation-only word gamma should follow the declared unknown-token policy. Adding gamma while evaluating changes the fitted representation. The same reasoning applies to learned normalization, prompt selection, deduplication thresholds and retrieval-index choices when their tuning uses held-out outcomes.

Keep a manifest of document identities, families, split assignments, normalization rules and fitted-artifact versions. Freezing that manifest before evaluation makes later changes visible. It does not prove the source data has no unknown relationship, so report the detection limits of exact hashes and available family metadata. An honest leakage audit combines known relationships and reproducible checks rather than treating one empty hash intersection as universal independence.
''',
'llm-014': '''## Work through the fitted table

The training documents ABAB and AC create four transitions: A to B twice, B to A once and A to C once. With vocabulary [A, B, C], the unsmoothed A row is [0, 2, 1], the B row [1, 0, 0], and the C row [0, 0, 0]. Add-one smoothing changes these to [1, 3, 2], [2, 1, 1] and [1, 1, 1], with denominators six, four and three. The resulting rows are [1/6, 1/2, 1/3], [1/2, 1/4, 1/4] and [1/3, 1/3, 1/3].

The held-out sequence A, C, B contains two scored transitions. A to C has probability 1/3 and C to B has probability 1/3, so total negative log likelihood is 2 log(3), mean loss is log(3), and perplexity is 3. The unseen C context is handled by the predeclared uniform smoothed row. It must not be fitted from its held-out successor merely to avoid an unknown event.

Smoothing is a modeling assumption that trades some probability mass from observed transitions to unobserved ones. Adding one to each numerator requires adding vocabulary size to the denominator. Changing vocabulary size or pseudocount strength changes the model and the score, even when observed counts stay fixed. Choose that policy before using the held-out result to judge the baseline.

## What the evidence notebook should preserve

Store the count matrix, vocabulary order, document-boundary policy, active target count and evaluation sequence identity. A probability matrix without its vocabulary ordering is ambiguous: row two and column one have meaning only through the token mapping. Preserve counts before evaluation and compare afterward to demonstrate that assessment did not update the fitted state.

The baseline's transparency makes it useful for diagnosing later neural-model experiments. If a complex decoder cannot beat a simple count model under the same tokenization, split and scoring rule, investigate the task and training loop before attributing the result to model capacity. Conversely, beating this tiny baseline on two held-out transitions does not establish broad language capability. The denominator is too small to support a stable deployment conclusion, and one document cannot represent every relevant family.

A successful capstone therefore includes a bounded claim and reproducible intermediate values, not only a final perplexity. The same structure will be reused when the model has learned weights: identify fitted state, freeze assessment conditions, count the actual prediction events, and show at least one controlled failure that would invalidate the conclusion.
''',
'llm-015': '''## The gradient is a local calculation, not an update

For L(w)=(w-2)^2, the derivative is 2(w-2). At w=0 the loss is 4 and the gradient is -4. backward computes and accumulates that derivative into the leaf tensor's grad field; it does not change w. An optimizer or an explicit update rule would still need to apply w_new=w-learning_rate*gradient. With learning rate 0.1, that rule would move w to 0.4, but the current derivative fixture deliberately keeps the parameter fixed while inspecting gradient state.

A central finite difference compares L(h) and L(-h), divided by 2h. For this quadratic the real-arithmetic expression equals -4 for any nonzero h, while floating-point subtraction can still introduce error. More general nonlinear functions have truncation error as well, so a useful check balances a sufficiently small step against cancellation. Float64 makes this small diagnostic easier to inspect than an unnecessarily low-precision calculation.

## Accumulation, detachment and snapshots

Two separate backward calls at the same unchanged w add two copies of -4, producing grad=-8. Setting grad=None clears accumulated state so the next backward produces -4 again. This is intentional accumulation behavior, not evidence that the derivative formula changed. A training loop must choose whether several microbatches contribute to one update or whether each update begins with cleared gradients.

A detached tensor keeps the value but removes the autograd connection. Detach is not a deep copy: storage may still be shared. Use detach().clone() when an independent snapshot is required. Converting a tensor to a Python scalar with item also leaves the differentiable tensor path. Such operations are useful for reports, but putting them into the computation that should produce a training loss can disconnect parameters.

Embedding lookup is differentiable with respect to table entries, not the integer token IDs. Looking up IDs [2, 0, 2] returns rows two, zero and two. If an objective sums all six returned coordinates, the table-row derivative would count those uses: row two receives [2, 2], row zero [1, 1], and untouched rows receive zero under the dense-gradient default. Repeated token identity therefore accumulates evidence into one shared learned row. This connects the simple scalar accumulation example to language-model parameter sharing.
''',
'llm-017': '''## Derive the active-token denominator

The four IDs [2, 5, 7, 3] produce three input/target pairs. Uniform logits over eight classes give each target probability 1/8, so every active token contributes log(8), approximately 2.079442, to negative log likelihood. Total loss over the three targets is 3 log(8). Dividing by three gives the correct token mean. Appending two ignored positions should change neither that numerator nor its active-token denominator.

Dividing the same numerator by padded length five instead gives 3 log(8)/5, approximately 1.247665. That lower number is not a better prediction. It is an accounting change caused by padding. If used for backpropagation, the wrong denominator also rescales the gradient, making the effective update depend on padding density. Comparing losses from batches with different valid-token counts requires consistent weighting rather than an unweighted average of batch means.

## Shape and derivative checks

The model supplies logits [batch, time, vocabulary]. Cross entropy expects the class axis in the position required by its API. Flattening batch and time to [batch*time, vocabulary], with targets flattened in the same row order, preserves the intended event pairing. Treating time as the class dimension can produce a legal tensor call that scores a different problem.

For one active event with softmax probabilities p and target y, the logit derivative of summed cross entropy is p minus the one-hot target vector. Under a mean over three active events, divide that by three. With eight uniform classes, the true-class derivative is -7/24 and each other-class derivative is 1/24. Ignored positions contribute zero gradient under the stated loss masking. An all-ignored batch has no active mean and should be rejected or explicitly skipped under a declared training policy, not reported as successful learning.

The ignore_index value -100 is a label sentinel, not a valid embedding ID. Targets may contain it because the loss handles it; input token IDs must still follow the vocabulary contract. Loss masking also does not automatically create an attention key mask. Right padding may lie beyond valid causal prefixes, while left padding and position IDs require additional care. This fixture proves target accounting and gradient masking, not every padding strategy in a complete decoder.
''',
'llm-018': '''## Follow one update through all mutable state

The two four-token sequences create inputs of shape [2, 3] and six next-token targets. The decoder returns [2, 3, 16] logits, which are reshaped into six rows of sixteen class scores. The objective is a mean over those six target events. The loop clears parameter gradients, computes a fresh forward pass, constructs the loss, backpropagates, records gradient information and applies one Adam update. Moving zero_grad to the wrong side of backward could erase the gradients before the optimizer uses them.

The global gradient norm in this fixture is the square root of the sum of squared entries across every accumulated parameter gradient. It is not an average of per-parameter norms. A finite positive norm shows that some derivative path exists for this batch, but does not prove every expected parameter participates. Unused embedding rows can legitimately have zero gradients; a missing registered module or a detached branch is a different problem requiring a parameter-by-parameter inspection.

Adam owns state in addition to model weights, including moment estimates and an update count. Reconstructing an optimizer after every step would repeatedly reset that history and define a different algorithm. A model snapshot and optimizer state therefore answer different questions when comparing trajectories or resuming a run.

## Interpret the recorded curve correctly

Each loss is recorded before its corresponding optimizer step. The last stored training loss is the objective seen before update twelve, not necessarily the loss of the final post-update weights. To report that final state's loss, perform a separate forward evaluation afterward under a declared mode and reduction. The reference's field name last_training_loss describes its observed pre-update point and does not claim convergence.

The checks establish a twelve-update budget, finite losses and norms, and an actual change in the vocabulary projection. They intentionally do not assert that every step decreases loss or that twelve steps reach an optimum. Optimization can fluctuate, especially under minibatching, stateful optimizers or stochastic layers. A repeated tiny batch is useful for debugging the data and gradient path; held-out task performance remains a separate experiment.

When a curve fails, first verify shifted targets, class axis, active-token denominator, optimizer membership and gradient clearing. Preserve the smallest failed batch before changing learning rate, model width or training budget. Increasing the budget can hide a diagnostic error without explaining it.
''',
'llm-019': '''## Why overfitting one batch is a diagnostic

The fixture uses one sequence of three input positions with targets [2, 3, 4]. A sufficiently flexible model can memorize that tiny mapping. Failing to reduce its loss is a reason to inspect target alignment, gradients, optimizer membership and the forward computation before spending resources on a large corpus. Succeeding does not demonstrate that the model learned a transferable language rule, since a position table or token lookup can help memorize three cases.

The trained model and no-update control begin with identical parameter values. Copying state into a separately constructed model preserves isolation; keeping two references to one model would not. The control snapshot clones every state tensor, so later mutation cannot silently alter the recorded before-state. The trained model takes thirty updates while the control takes none.

The current TinyDecoder has no dropout or running batch statistics, making repeated control passes deterministic under its fixed input. In a model with stochastic or stateful components, unchanged weights alone would not imply identical outputs. Set the intended evaluation mode, control randomness and inspect non-parameter state before interpreting a changing control curve. no_grad disables gradient recording but does not itself switch dropout or BatchNorm into evaluation behavior.

## What a lower training loss establishes

A finite decreasing curve and changed parameters support the claim that this optimization path can fit the repeated batch. Uniform logits over sixteen vocabulary items would give loss log(16), but the actual random model is not constrained to uniform logits, so its initial loss must be measured rather than replaced with that theoretical baseline. The loss axis must remain vocabulary, with logits [1, 3, 16] and three aligned targets.

The experiment has zero held-out examples. It cannot estimate generalization error, calibration, robustness to a new document family or useful generation behavior. A training curve and a held-out evaluation are different evidence sources. Keep the memorization experiment as a debugging fixture, then restore a clean initialization and a frozen split for the actual model comparison. Reusing a model already tuned on a supposed evaluation fixture would compromise that next experiment.
''',
'llm-020': '''## Calculate scale effects before a large model

For x=[1, -1, 2, -2], the Euclidean norm is sqrt(10). A diagonal weight aI produces ax, so output norm is abs(a)*sqrt(10). Moving a from 0.01 to 100 multiplies the output norm by 10, 000. This is an exact property of the fixture, not an empirical recommendation for an initialization scale.

With loss equal to the mean of four squared outputs, L=(1/4)||xW||^2. At W=aI, the loss is 2.5a^2 and the weight gradient is (a/2)x^T x. The Frobenius norm of x^T x is ||x||^2=10, so the gradient norm is 5*abs(a). The small and large gradient norms are therefore about 0.05 and 500, again a factor of 10, 000, while the loss changes by a factor of 100, 000, 000. Forward magnitudes, gradient magnitudes and objective magnitudes scale differently.

## Locate the first nonfinite operation

At scale 1e38 in float32, the largest output magnitude in this fixture is about 2e38, still within the finite representation range. Squaring that output exceeds the range, so the objective can overflow even though the preceding matrix product is finite. Inspecting only the final loss cannot identify this first failing operation. Track intermediate tensors and their dtypes before widening tolerances or blaming the optimizer.

The repair uses the same input with a smaller scale, making the comparison controlled. It demonstrates numeric sensitivity; it does not prove that this diagonal initialization is suitable for a trained Transformer. Real initialization methods account for fan-in, fan-out, activation behavior and layer depth. Under simplified independent zero-mean assumptions, a sum of Din products has variance proportional to Din times input variance times weight variance, motivating inverse-fan-in scaling. Those assumptions should be named rather than treated as a universal distribution law.

Residual addition also needs a matching representation shape. A [1, 4] input can add a [1, 4] branch, while a [1, 3] branch violates the feature contract. Shape compatibility alone does not ensure good numerical conditioning: repeated residual branches can still amplify or cancel directions. The normalized decoder and later pre/post-norm chapter connect this scale diagnostic to actual model structure.
''',
}

DIAGNOSIS_NOTES = {
'llm-012': 'If sampling selects an impossible or out-of-range token, inspect normalization after filtering and the half-open draw boundary before changing the RNG. If temperature changes the greedy answer for unequal finite logits, inspect sign, zero handling and numerical overflow. If a replay differs despite the same seed, compare policy, draw order and vocabulary indexing as well as generator state.',
'llm-013': 'Check the objective shift before inspecting the attention mask. Then audit document boundaries, exact duplicate hashes, known family overlap and fitted preprocessing artifacts separately. A passing causal test cannot detect a target copied from its current input or a tokenizer fitted using evaluation records. Preserve the manifest that made the assessment interpretable.',
'llm-014': 'Inspect the count numerator, vocabulary order and smoothing denominator before interpreting perplexity. An unseen context should follow the frozen smoothing policy. Confirm the number of held-out transitions and compare the count matrix before and after scoring. A lower score under changed tokenization or a changed target denominator is not automatically a model improvement.',
'llm-015': 'Separate parameter value, requires_grad, accumulated grad and graph connectivity. A second backward on a new loss can accumulate another derivative without moving the parameter. Zero and None gradients have different meanings. Detach removes a gradient path but may retain shared storage; a snapshot intended for comparison needs an independent copy.',
'llm-017': 'Inspect input and target arrays side by side, then count active targets explicitly. The -100 sentinel belongs to the loss labels rather than embedding inputs. Verify the vocabulary axis before flattening, and distinguish target-loss masking from attention visibility. Reject the all-ignored mean instead of interpreting a NaN or fabricated zero as progress.',
'llm-018': 'Check the first incorrect intermediate state: shifted labels, logits layout, loss denominator, parameter gradients, then optimizer update. Confirm that zero_grad happens before the intended backward and that the optimizer owns the expected parameters. Label recorded losses by whether they were measured before or after an update; finite steps and a positive gradient norm do not establish convergence.',
'llm-019': 'Verify that control and trained models have equal initial values but independent storage. If the no-update control changes output, inspect stochastic mode and non-parameter state. If the trained path cannot memorize the tiny batch, reduce the pipeline before scaling it. If it can, retain the narrow conclusion: repeated-batch fitting without held-out evidence.',
'llm-020': 'Find the first nonfinite tensor rather than only the final failing scalar. Compare output, squared-output and gradient scales on the same input and dtype. A finite matrix product can still overflow in a later square or reduction. Validate residual feature shapes, then examine conditioning; a skip connection does not eliminate numeric scale problems.',
}

DEPTH_NOTES.update({
'llm-021': '''## Different identities catch different problems

A filename is not content identity. Two files named a and a2 can contain the same bytes, and an exact hash can expose that duplication. A paraphrase such as red square versus square colored red has a different hash despite related meaning. A family label adds another relationship: revisions, fragments or templated records can stay together even when their text differs. Neither exact hashing nor known-family metadata proves that every unknown semantic relationship has been detected.

The fixture assigns family F, containing a and a2, wholly to training. Families G and H go to validation and test. Moving only a2 into validation creates a family intersection F even though the document IDs remain distinct. Checking only train-versus-test would miss a train-versus-validation leak, so every partition pair matters. Validation information can influence model or prompt selection long before the final test is read.

## Freeze the transformation policy too

Raw text hashes distinguish red square from red square followed by a space. Hashing stripped text makes those two values equal under a declared normalization policy. That policy may be appropriate for one corpus and destructive for another where whitespace or formatting matters. Record both the normalization version and what the digest actually identifies. Do not quietly change normalization after finding inconvenient duplicates.

The example's manifest hash covers document-to-partition assignments. It does not, by itself, bind every document ID to immutable content bytes. A complete run record should include content hashes, family metadata, preprocessing configuration and split assignments together. A stable split hash with changed source documents would not establish that the experiment used the same corpus.

Repeated documents also change effective weighting. Ten near-copies from one source are not necessarily ten independent observations about deployment performance. When evaluating transfer to new sources, preserve source-family units in both splitting and uncertainty analysis. The correct grouping rule follows the intended deployment question rather than a universal instruction that every task must use the same split granularity.
''',
'llm-022': '''## Why weights alone do not specify the next Adam step

Adam's update depends on a first-moment estimate, a second-moment estimate and a step count as well as the current parameter. At the first gradient g=-4, default beta values 0.9 and 0.999 give moments -0.4 and 0.016. Bias correction divides them by 0.1 and 0.001, recovering -4 and 16 for that first step. With learning rate 0.1 and the small epsilon term, the parameter moves from zero to approximately 0.1.

After more steps, the stored moments summarize earlier gradients. Starting a fresh optimizer at the same current weight instead initializes those moments to zero and starts the bias-correction counter again. The next update can therefore differ even with the same loss function, batch, learning rate and weight value. The reference compares that weights-only continuation against a restored optimizer rather than treating successful weight loading as a restart proof.

## What the fresh-process test actually preserves

The parent saves one scalar weight and the optimizer state after two updates, then computes the uninterrupted third update. A child interpreter constructs new objects, restores both components and computes the same next update. Matching those values within the stated tolerance tests reconstruction rather than another reference to the parent's live objects. Optimizer parameter-group structure and parameter ordering must match the state being restored.

This scalar task has a fixed objective and no stochastic data order, so the checkpoint does not need an RNG or sampler position to reproduce its declared next step. A realistic training continuation may also need Python/NumPy/framework RNG state, data position, scheduler state, mixed-precision scaler state and relevant preprocessing versions. The small success does not prove those unimplemented surfaces. Similarly, seeding after random model or adapter construction cannot reproduce the initialization that already happened.

The saved artifact is an owned local checkpoint, and loading uses the explicit CPU and weights-only options shown in the code. These choices do not authorize arbitrary untrusted files or prove general cross-version portability. Evaluation mode is another independent setting: Dropout.eval disables its random masking, while no_grad controls graph recording. A reproducibility claim should name all relevant state, mode, version and input contracts.
''',
'llm-023': '''## Why nucleus sampling keeps the crossing token

Sort the probability vector [0.5, 0.3, 0.2] in descending order. With a top-p threshold of 0.6, the first candidate supplies only 0.5 mass, so stopping there would miss the threshold. Including the second candidate reaches 0.8, which crosses it. The minimum retained prefix is therefore tokens zero and one, not just token zero. The implementation tests mass before the candidate, equivalent to keeping the crossing candidate under the stated positive-threshold policy.

The retained probabilities must be normalized: [0.5, 0.3]/0.8 gives [0.625, 0.375]. Top-p is not top-k with a different name. It chooses a support size according to the distribution: a highly concentrated distribution may retain one candidate, while a nearly uniform distribution can require many. The threshold domain must be declared; zero would produce an empty support under the literal previous-mass rule, so a general sampler needs an explicit validation or special-case policy.

Stable sorting makes the tie behavior reproducible for this fixture. When the cutoff falls among equal probabilities, index order can affect which tied candidate is retained. That is an implementation policy, not evidence that one tied token is more correct. Also distinguish a sampled index into the retained vector from the original vocabulary ID. If retained vocabulary IDs were [5, 2], retained index one would mean vocabulary token two. The current [0, 1] fixture makes those numbers coincide, so a general implementation must preserve the mapping explicitly.

## Sampling and termination have different contracts

Two local generators initialized identically produce matching draws for the same ordered support in the same prepared runtime. This does not imply that changing earlier calls, filtering or runtime versions preserves the entire generated sequence. Reproducibility needs the policy and RNG state, not merely a seed written somewhere in a report.

The termination fixture appends EOS before stopping, so its stored token list includes the EOS ID. A text presentation may choose not to display that token; the storage and display policies should not be confused. The maximum-new-token cap counts generated tokens, not prompt tokens. Total model context must still respect its positional and cache limits. Hitting a cap without EOS is a truncation outcome, not proof of a complete answer or valid structured output. A downstream parser should verify its own contract rather than assume a stopped generator finished the requested task.
''',
'llm-024': '''## Follow one incremental token through the cache

A full four-token pass computes logits [1, 4, 16]. Incremental inference instead supplies one token at a time. The first call stores K/V for position zero. The second call projects the new token at position one, appends its K/V to the stored tensors and forms a query that can read positions zero and one. After four calls, concatenating the four [1, 1, 16] outputs along time should match the full pass.

The positional offset is the existing cached length. Resetting the new token to position zero changes its representation even if key/value concatenation has the expected shape. A correct cache can therefore fail parity through a position mistake rather than a storage-size mistake. Likewise, a correct output shape does not prove that key order matches token order.

Past keys and values are reusable because the causal computation for an earlier token did not depend on later tokens. In a multilayer decoder, each layer stores its own projections of the corresponding hidden representations. If the model weights, adapter, prompt prefix or position policy changes, those stored values may no longer represent the requested computation. Editing an earlier token can invalidate later cached states that depended on it; it is not generally sufficient to replace one isolated cache row.

## Cache ownership is part of correctness

The local ownership record binds the cache to request A and model label v1. acquire rejects a different request or model label. This demonstrates the check, but the caller is responsible for binding that label to the actual model artifact. A string comparison does not automatically notice changed weights if the version label was left unchanged. A serving system also needs a clear tokenizer, prefix and position-policy identity, plus the relevant request/access boundary.

The returned K/V are detached for inference. Reusing them while expecting full-prefix training gradients would change the differentiable computation. The helper checks its declared batch/context conditions, while a complete general cache interface should additionally validate all head, width, dtype, device and mask contracts. The lesson does not claim that its small metadata wrapper is a sandbox for untrusted cache objects.

Caching removes repeated work on past projections and hidden states, but a new query still compares with stored keys and mixes stored values. It does not eliminate all context-length cost or expand the model's declared position range. Changing sampling temperature alone does not change K/V for an identical token prefix and model, but it can change which future tokens are selected, and therefore change the prefix that later cache entries must represent.
''',
'llm-025': '''## Derive score and cache storage separately

Materialized attention scores for one layer have B*H*T*T entries. With B=1, H=2, increasing T from 16 to 32 changes the count from 512 to 2, 048, a factor of four. At four bytes per element, those individual score arrays occupy 2 KiB and 8 KiB. This is a tensor-size calculation; an implementation may also materialize probabilities, masks or backward intermediates, or use an algorithm that avoids storing the full score matrix.

K/V cache data for L layers has 2*L*B*Hkv*T*Dh elements. The leading two counts keys and values. For one layer, batch one, two KV heads, head width sixteen and float32, T=16 gives 4, 096 bytes and T=32 gives 8, 192 bytes. Doubling context doubles this cache data rather than quadrupling it. The score and cache sizes happen to coincide at one chosen small shape; that coincidence is not a general identity.

Changing element size from four bytes to two halves the raw cache-byte arithmetic. It does not prove that the runtime supports a desired low-precision kernel or that numerical behavior remains acceptable. Increasing batch from one to three triples cache data. Redistributing a fixed model width between ordinary MHA head count and head width preserves H*Dh, so that particular cache count stays the same. MQA/GQA instead change the number of distinct KV heads, which the expert head-sharing chapter treats separately.

## Raw tensor bytes are not measured peak memory

Parameters, temporary buffers, framework state, Python objects, allocator caching and retained activations can all contribute to process memory. During training, storing intermediates for backward differs from inference with detached caches. A peak measurement also depends on the lifetime overlap of tensors, not only the sum of every tensor that ever exists. An allocator may retain released memory for reuse rather than returning it immediately to the operating system.

Vocabulary logits are another potential allocation: a full [B, T, V] output can be substantial for a large V, while an inference interface that requests only the last position has a different output contract. Do not infer the dominant cost from the tiny sixteen-token fixture. Likewise, CPU tensor arithmetic does not establish GPU kernel throughput or memory-traffic savings. The honest result here is an exact layout-based estimate with explicit exclusions, ready to be compared with a separate measured runtime experiment.
''',
'llm-026': '''## Decodable information is not necessarily used information

The synthetic representations are [-2, 0], [-1, 1], [1, 0], [2, 1], with labels determined by the sign of the first coordinate. A fixed threshold on that coordinate decodes every training label and the two supplied held-out labels. Consider a downstream model that instead reads only the second coordinate. The label remains decodable from the full representation even though that downstream computation ignores the informative coordinate. This is a concrete counterexample to equating decodability with causal use.

The fixture's threshold predictor is hand specified, and its separate trainable linear weight demonstrates a gradient path without updating the frozen representation tensor. It is not a full pretrained-model probe experiment. The shuffled-label comparison checks this fixed predictor against a permuted label vector; it is not the same as retraining a probe on shuffled labels under an equal optimization budget. Those distinctions keep the demonstration's conclusion aligned with the work actually performed.

## Design a real probe comparison

A probe study would identify a representation layer and token aggregation rule, freeze the base model, fit a declared-capacity predictor using training records and evaluate on held-out families. Probe capacity matters: a powerful predictor may memorize labels or solve a task from incidental structure rather than reveal a simple, accessible feature. Compare with meaningful baselines and controls under the same split and budget, not only with chance accuracy on the training set.

Known family overlap can make a held-out score optimistic even when the representations themselves are frozen. Two rows from one source family are not automatically independent examples of transfer. The two-point holdout here is a teaching fixture, not a precise estimate of deployment reliability. Report its count, label construction and limitations rather than attaching a broad semantic claim to perfect accuracy.

A causal-use claim needs an intervention or other design connecting the represented information to the model's behavior. Removing or changing a feature, activation or component can be informative, but such an intervention must be interpreted carefully because it may shift the representation outside its ordinary distribution. A probe result, an intervention result and an explanation of model behavior are related evidence, not interchangeable labels.
''',
'llm-027': '''## Metric weighting changes the question

Document mean losses 1 and 3 with token counts 1 and 3 produce a token-weighted mean (1*1+3*3)/4=2.5. An equal-document mean is 2. Both are valid summaries of different units, but reporting one as the other changes the interpretation. Comparing language-model scores requires the same tokenizer and event definition; a token under vocabulary v1 need not represent the same amount or kind of text as a token under v2.

For confidences [0.6, 0.8, 0.8, 1.0] and correctness [1, 1, 0, 1], one combined bin has mean confidence 0.8 and accuracy 0.75. Its absolute gap is 0.05. If the bins are [0.5, 0.8) and [0.8, 1], the first contains one correct event at confidence 0.6, while the second has average confidence about 0.8667 and accuracy 2/3. Under the common count-weighted absolute-bin-gap definition, these bins give 0.25 rather than 0.05. The underlying predictions did not change; the binning changed the summary.

This small example shows why calibration bin boundaries and event definitions should be fixed and reported. Empty bins have no observed accuracy and should remain explicitly empty, not be assigned a fabricated zero or one. A model token probability is also not automatically the probability that an entire cited answer is correct. Define the event being calibrated before assigning meaning to a confidence number.

## Pairing preserves information hidden by equal averages

Model A's errors are q1=0, q2=1, while B's are q1=1, q2=0. Correct ID alignment gives paired differences [-1, 1], with mean zero. Iterating their dictionaries in different orders can incorrectly pair [0, 1] with [0, 1], producing [0, 0]. The mean still happens to be zero, so an aggregate-only check misses the error, while the variability and per-question tradeoffs are destroyed.

Keep stable IDs and relevant family/group membership when comparing systems. Confidence intervals or paired resampling depend on the actual observation unit, not merely the number of tokens printed by an evaluator. A similar average can conceal different failure types, so preserve the question-level outcomes as well as the overall metric.
''',
'llm-028': '''## Compare models under one frozen prediction task

The two training sequences create six within-document next-token events. Their count baseline observes 1 to 2 twice, and 2 to 3, 3 to 4, 2 to 4, 4 to 3 once each. Add-one smoothing uses the same sixteen-token vocabulary as the neural model, so every row denominator includes sixteen pseudocounts. Changing that vocabulary would change the baseline and the comparison.

The held-out sequence [1, 3, 2, 4] has three events. The smoothed probabilities are 1/18 for 1 to 3, 1/17 for 3 to 2, and 1/9 for 2 to 4. Its baseline mean loss is (log(18)+log(17)+log(9))/3, approximately 2.640270. The neural score is measured from the trained model after its twenty updates. The reference intentionally does not require the neural model to beat the baseline; a fair comparison can reveal that a simpler method is adequate or that more investigation is needed.

The training curve stores pre-update objectives, while the held-out score is computed afterward in evaluation mode without gradient recording. These values describe different states and data. A lower training loss is not itself a better held-out result. Rechecking causal prefixes after training confirms that updating weights did not invalidate the declared information boundary, but does not substitute for contamination checks.

## Bind the report to its actual artifacts

The split digest identifies the recorded assignment dictionary. The parameter digest hashes the ordered parameter bytes under this known architecture. A robust reusable artifact manifest would additionally bind parameter names, shapes, dtypes, model configuration, corpus contents, tokenizer and software versions. A hash does not establish that an unlabeled sequence of bytes can reconstruct a model without those contracts.

The holdout contains one authored document and three correlated token predictions. Three targets are the loss denominator, not necessarily three independent experimental units for uncertainty estimation. The capstone therefore produces a reproducible small-model decision record rather than a production-quality claim. Preserve both model scores, the active count, the trained state identity, the split policy and a clear statement of what remains untested. A no-go conclusion is informative when it follows from those observations rather than from a preferred model narrative.
''',
})

DIAGNOSIS_NOTES.update({
'llm-021': 'Distinguish document ID, raw content hash, normalized content hash and family membership. Each checks a different relationship. Audit all partition pairs and freeze normalization rules before scoring. A stable assignment-only hash does not prove that the corpus bytes were unchanged, and an empty exact-hash intersection does not rule out paraphrases or shared provenance.',
'llm-022': 'Compare the uninterrupted and reconstructed next update, not only loaded weights. Check optimizer state, step count and parameter-group mapping. State explicitly whether RNG, data position and scheduler state matter to the declared experiment. A seed applied after random initialization cannot reproduce an earlier draw, and evaluation mode is separate from gradient recording.',
'llm-023': 'If top-p retains too little mass, check whether the crossing candidate was discarded. Validate a nonempty support and renormalize it, then map sampled retained indices back to vocabulary IDs. Keep EOS inclusion, generated-token cap and total context budget separate. A truncated sequence should not be silently reported as a completed structured answer.',
'llm-024': 'Check cache shape and token order, then positional offset and actual model identity. Recompute from an empty cache when the prefix or model changes. A request/version string check only enforces the metadata supplied to it. Detached inference caches do not preserve full-prefix training gradients, and matching tensor sizes alone does not establish semantic cache validity.',
'llm-025': 'Write every factor and unit in the byte formula: keys/values, layers, batch, KV heads, time, head width and element size. Separate score materialization from cache storage and raw data bytes from measured process peak. A fixed-width MHA head repartition is not the same change as reducing KV heads with GQA or MQA.',
'llm-026': 'Ask whether the result shows information present in a representation, a predictor trained to recover it, or the original model using it. These are distinct claims. Inspect probe capacity, split families and the exact shuffled-label control that ran. Perfect accuracy on two synthetic holdout rows is not broad semantic or causal evidence.',
'llm-027': 'Name the averaging unit and tokenizer before comparing losses. Preserve empty calibration bins and fixed boundary conventions. Align paired outcomes by stable ID even when overall means happen to match; a mistaken pairing can leave the average unchanged while destroying the variance and failure interpretation.',
'llm-028': 'Verify document boundaries and the common vocabulary before comparing baseline and neural scores. Keep pre-update training points separate from post-training held-out evaluation. Bind hashes to their actual scope, and report the one-document holdout limitation rather than treating three token targets as three independent studies.',
})

DEPTH_NOTES.update({
'llm-029': '''## Separate corpus size, tokens processed and training work

In this table, interpret D=10, 000 as the size of the unique available corpus, not as the total number of token presentations made to the optimizer. Both runs can use the same corpus while run B takes twice as many steps. If each step consumes a fixed batch of b nonpadding target tokens, the processed-token count is b*S. Repeatedly visiting a document increases that count without increasing the unique corpus size. These quantities answer different questions about optimization work and information available for generalization.

P is the trainable parameter count, S is the optimizer step count and C is the supplied relative compute budget. The table does not specify enough implementation details to derive C exactly from P, D and S. Multiplying all three can double-count repeated data. A real compute report should state the measured or estimated operation convention, batch size, sequence lengths, forward/backward work and exclusions. Equal wall time is yet another comparison because hardware and implementation affect elapsed time.

## Derive a slope without inventing a law

The two hypothetical observations are (C, L)=(1, 2) and (2, 1.8). The log-log secant slope is log(1.8/2)/log(2/1), approximately -0.152003. Under the additional assumption L=A*C^(-alpha) with no irreducible floor, those two points give alpha about 0.152003 and A=2. Continuing that fitted expression to C=4 predicts L=1.62. This is an extrapolation from an assumed functional form, not a third observation or a demonstrated universal exponent.

A model with an unknown floor, L=L_floor+A*C^(-alpha), can agree at these two points while predicting a different continuation. In particular, log(L) is not generally linear in log(C) when the floor is material. Data quality, architecture, optimizer, evaluation distribution and the range of budgets also matter to interpreting a fit. A tiny fixture cannot establish the range over which a power law holds or identify the best allocation between model size and training tokens.

The original [scaling-law study](https://arxiv.org/abs/2001.08361) and the later [compute-optimal training study](https://arxiv.org/abs/2203.15556) used broad empirical experiments to study budget allocation. Their conclusions motivate controlled measurements; they do not turn this two-row worksheet into a replication. When a larger model appears better, first ask what was held constant and what prediction unit the reported loss averages. A defensible next experiment varies a specified factor across several budgets, repeats relevant measurements and reserves independent evaluation data.
''',
'llm-030': '''## A corpus is a lineage graph, not just a folder

Imagine a source document d2 and an answer key d3 derived from its benchmark question. Even if their byte hashes differ, training on d3 can expose the information that evaluation on d2 was supposed to withhold. The relevant relationship is derivation or shared family, not only exact file equality. A source ID, a content hash, a family ID and a split label record different parts of this relationship. Keep the raw source identity and the transformation history when normalized or chunked derivatives are created.

The short hash labels in this worksheet are illustrative identifiers. They are not actual digest receipts for external datasets. A real manifest would name the digest algorithm and bind the exact raw bytes or the precise normalized representation. Normalization itself needs a versioned rule: case folding, whitespace changes or boilerplate removal may expose duplicates but can also discard information needed by the task. Preserve enough lineage to explain why two items were considered related.

## Information can leak before the optimizer runs

Training examples are one route for contamination. Prompt selection, retrieval-index construction, threshold tuning and repeated manual inspection of held-out answers can also adapt a system to its supposed test set. Keeping benchmark-derived d3 out of gradient updates is insufficient if its answers choose the final prompt or retrieval configuration. Assign families before those choices and keep an evaluation partition reserved for the final declared comparison.

Permission and scientific independence are separate checks. A permission record describes the documented basis and conditions for using material; a split record describes its role in an experiment. Neither is implied by the other. Unknown permission or unknown ancestry should remain explicit rather than being converted into an assumed approval or an assumed clean split. This lesson audits recorded provenance; it does not determine legal rights from a file name.

For a subject assistant, retrieval documents additionally need revision, validity period and access metadata. A document may be permitted for one audience but excluded for another, or remain a valid historical source while becoming unsuitable for a current-policy answer. An exact hash can detect changed bytes, but it cannot decide which policy revision governs a question. The applied course develops those operational checks in [corpus provenance and chunking](../../llm-applied/README.md). The useful output here is a traceable inclusion decision with a reason, not a larger corpus at any cost.
''',
'llm-031': '''## Align the loss mask with the shifted target

The literal sequence is [1, 2, 5, 6, 3]. Feeding [1, 2, 5, 6] into a causal decoder predicts targets [2, 5, 6, 3]. The answer mask [false, true, true, true] therefore excludes prediction of target 2 and includes targets 5, 6, 3. It is a mask over prediction events after shifting. Applying a mask made for the unshifted sequence without checking this alignment can train on a prompt token or omit the first answer token.

Uniform logits over eight vocabulary entries give each target probability 1/8 and each active negative log probability log(8). The answer-only mean is (3*log(8))/3=log(8), while the sum is 3*log(8). A mean over all four positions would also happen to equal log(8) in this uniform fixture, so the mean alone cannot reveal the masking error. Inspect the active count and per-position gradients as well. For the excluded prediction, the logit gradient is zero; for an included prediction, it is (p-one_hot(target))/3 under this mean reduction.

## Ignoring a target does not hide the prompt

The prompt remains an input to the causal computation. Answer tokens can attend to its allowed positions and gradients from answer losses can flow through their use of prompt representations. Loss masking chooses which predictions contribute directly to the objective. An attention mask chooses which input relationships exist. A padding mask and an instruction/answer loss mask therefore have related but distinct jobs.

The EOS decision is part of the task contract. This fixture includes the final3 as an answer target, teaching the modeled sequence to terminate there. A different template might encode turns or end markers differently. For a real tokenizer, verify the rendered chat template and the actual token boundaries, especially around prompt/answer joins. Independently tokenizing two strings and concatenating their IDs need not reproduce tokenizing the combined text under every tokenizer.

An all-false answer mask has denominator zero and must be rejected or handled by an explicit policy before reduction. Returning a plausible zero loss would hide the absence of supervision. Likewise, template variants from one source family should not cross the train/evaluation boundary merely because their strings differ. The code verifies loss and gradient mechanics on literal IDs; it does not demonstrate instruction-following quality. The [applied adaptation route](../../llm-applied/README.md) adds data construction, real tiny updates and an explicitly optional pretrained workflow with template and masking checks.
''',
'llm-032': '''## Derive the first low-rank update exactly

This lesson uses row vectors and the convention y=x*(W+A*B), with W[8, 8], A[8, 2] and B[2, 8]. There is no additional alpha/r multiplier here, so the effective scale is one. The frozen W is the identity, every element of A is 1/8, B starts at zero and x is an all-ones row. Thus x*A=[1, 1], the adapter output is zero, y is all ones and mean(y squared)=1.

For this loss, the gradient G=dL/dy has eight entries equal to 2/8=0.25. Matrix differentiation gives dL/dB=(x*A).T*G, so every B gradient is 0.25. It also gives dL/dA=x.T*G*B.T, which is zero at this first step because B is zero. Zero initial dA is therefore expected, not evidence that autograd is broken. If both A and B started at zero, both adapter gradients would vanish for this bilinear path.

SGD at learning rate 0.1 changes every B entry to-0.025. Each entry of A*B is then2*(1/8)*(-0.025)=-0.00625. Multiplying by the eight ones in x changes each output by-0.05, giving y=0.95 and loss 0.9025. The update has rank at most two, but these identical columns and rows make its actual rank one. A rank bound is not a promise that optimization uses every available direction.

## Frozen weights still participate in the computation

Freezing W prevents optimizer updates to that parameter; it does not remove its contribution to the output or necessarily stop gradients to earlier layers. For a trainable input, dL/dx=G*(W+A*B).T still includes W. Distinguish a frozen parameter from detaching an entire activation path. Confirm which tensors the optimizer receives and inspect both parameter changes and gradients.

The [LoRA paper](https://arxiv.org/abs/2106.09685) motivates learning a low-rank change to a frozen base. The arithmetic above is an original small illustration, not a replication of large-model quality or memory measurements. Trainable parameter count here is 8*2+2*8=32 rather than 64 for a full W update. The frozen base still occupies memory; activations and optimizer states also matter. Merging W+A*B can remove the extra adapter operations for this linear layer, but changing dtype or quantization can change numerical parity. Compare with [applied LoRA](../../llm-applied/guides/llm-applied-016.md), whose explicitly stated scale is two and whose first-step numbers therefore differ.
''',
'llm-033': '''## What the preference margin measures

For a common prompt x and chosen/rejected answers, let delta_policy=log p_policy(chosen|x)-log p_policy(rejected|x), with an analogous delta_reference. The objective used here is L=log(1+exp(-m)), where m=beta*(delta_policy-delta_reference). A positive margin means the policy favors the chosen answer more than the reference does under this sequence-scoring convention. It does not mean the chosen answer has high absolute probability or that its factual claims are true.

In the first case, policy scores-2 and-3 give delta_policy=1, while reference scores-4 and-5 also give delta_reference=1. Their difference is zero, so the loss is log(2), about 0.693147, even though both systems prefer the chosen answer. In the second case the supplied differences are2 and0 with beta0.5, yielding margin 1 and loss about 0.313262. Reversing the preference gives margin-1 and loss about 1.313262. The objective rewards a change in relative preference against the reference.

The derivative with respect to the margin is -sigmoid(-m). For a large positive margin it approaches zero; for a very negative margin it approaches-1. Computing logaddexp(0, -m) avoids directly exponentiating a huge positive number. At margins1000 and-1000 the stable losses are approximately 0 and1000, rather than an overflow in the latter case.

## Objective, optimization and preference quality are separate

The [DPO formulation](https://arxiv.org/abs/2305.18290) connects a preference objective to a reference policy. This chapter evaluates the scalar objective and its counterexamples. It does not train a policy, fit a reward model, collect online rollouts or implement an RLHF pipeline. The [applied preference lesson](../../llm-applied/README.md) supplies actual small gradient updates and discusses the distinct workflows.

A practical comparison needs paired answers for the same prompt, a declared label collection procedure and consistent sequence likelihood accounting. A sum of token log probabilities and a length-normalized score are different quantities; changing the reduction changes the objective. Preference labels can reflect style, brevity or annotation error. They require separate factual, task-specific and held-out evaluation. Reusing the final evaluation answers to choose beta or prompts would also contaminate the reported result. A decreasing preference loss is evidence about the fitted comparison objective, not a universal reliability certificate.
''',
'llm-034': '''## Quantization changes values before the matrix product

The full-precision fixture has W=[[0.1, -0.9], [1.7, -0.2]] and x=[1, -2], giving W*x=[1.9, 2.1]. A symmetric shared scale s=1.7/127 maps the weights to integer codes round(W/s)=[[7, -67], [127, -15]]. Dequantization multiplies these codes by s. The resulting output is approximately[1.887401575, 2.101574803], so the maximum absolute output error is about 0.012598425.

The largest magnitude1.7 sets the shared scale. With a separate scale per row, the first row can use0.9/127, yielding codes[14, -127] and output1.899212598. The second row is unchanged. The maximum error then becomes approximately 0.001574803. This improvement is specific to the supplied weights and input, and costs an additional scale. More granular scales can reduce some representation errors while increasing metadata and implementation complexity.

For nearest rounding without clipping, each weight error has magnitude at most s/2. Writing E=W_restored-W, the output error in row i obeys |(E*x)_i| <= sum_j |E_ij|*|x_j| <= (s/2)*||x||_1. Here the bound is approximately 0.02007874 because ||x||_1=3. It is a worst-case bound for these assumptions, not the observed error. Clipping an out-of-range value can exceed the half-step bound. A zero-valued block also needs an explicit scale convention to avoid division by zero in a general implementation.

## Count the intended storage and the actual operations

Four int8 codes and one float32 scale would use8 raw data bytes; two float32 scales would use12. Those are layout calculations for the proposed representation. This NumPy program uses float64 for its analysis scales and dequantized arithmetic, plus array metadata and intermediates. It does not demonstrate an eight-byte process allocation or an integer matrix-multiplication kernel.

The code restores floating values before multiplying. Therefore it measures numerical error from a specified quantizer, not inference speed, GPU memory savings or a full low-bit model. It also declares NumPy's ties-to-even rounding:0.5 goes to 0, 1.5 to 2 and2.5 to 2. Quantization comparisons should state code range, scale shape, rounding, clipping, accumulation dtype and the calibration data used to set ranges. Evaluate downstream outputs under a representative task; a small weight error alone need not imply a small decision change near a classification boundary.
''',
'llm-035': '''## Trace two requests without sharing their state

Request A has tokens[2, 5, 7], while B has[1, 3]. The scheduler alternates A0, B0, A1, B1, A2, always retrieving the cache belonging to that request. After A1, A has two positions while B still has one. At completion their cache lengths are three and two. Combining each request's incremental logits must match its own full-prefix pass, regardless of this interleaving.

The key includes request, model-version and tokenizer-version identities. A different model or tokenizer label misses the existing entry in the fixture. That demonstrates the lookup policy, but the surrounding system must bind those labels to actual artifacts. Reusing label v1 after changing weights would fool a string-key check. Prompt prefix, position policy, adapter identity and access boundary can also matter to whether reuse is valid.

## Scheduling is more than alternating a loop

This demonstration performs serial CPU calls. It does not build one batched GPU operation from active requests or establish continuous-batching throughput. Interleaving and batching are distinct: the former chooses an execution order, while the latter combines compatible work into an operation. A serving implementation also has to handle different lengths, finished requests, cancellation, capacity and output ownership without mixing state.

Prefill processes an available prompt, whereas decode adds one new position using existing state. Their compute and memory behavior differ. The active cache budget sums the storage for all live requests, not just the maximum length of one. Even when a request is temporarily waiting, retaining its cache consumes capacity. A token cap bounds this fixture's work but does not by itself establish a deadline, fairness guarantee or acceptable latency for other requests.

A useful failure diagnosis first checks ownership and version, then position offsets, cache lengths and logits. Matching final text can hide a mismatch in probability distributions, so the oracle compares logits directly with a declared tolerance. Resource measurements require a separate experiment that names the workload, hardware, concurrent load and measurement window. The current success establishes per-request numerical equivalence under the stated interleaving, not production serving performance.
''',
})

DIAGNOSIS_NOTES.update({
'llm-029': 'Define unique corpus tokens separately from processed target tokens and optimizer steps. Treat relative compute as the supplied quantity unless an operation model is specified. A two-point log slope fits an assumed expression but cannot validate its range, floor or extrapolation. Keep hypothetical table values visibly separate from measured training runs.',
'llm-030': 'Trace raw and derived records through source, family and split boundaries. A different content hash does not eliminate benchmark ancestry, and a permission label does not prove evaluation independence. Keep unknown lineage explicit. Exclude held-out answers from prompt, retrieval and threshold selection as well as from optimizer updates.',
'llm-031': 'Write shifted inputs and targets side by side before applying the answer mask. Inspect active counts and per-position gradients because uniform logits can hide a denominator mistake in the mean. Separate attention visibility from direct loss contribution, and reject an empty answer mask before dividing.',
'llm-032': 'Confirm the matrix orientation and adapter scale before copying numerical results from another implementation. Zero initial A gradient is expected when B starts at zero; zeroing both factors stalls the bilinear path. Check actual parameter changes, rank and merge parity separately from parameter-count or memory estimates.',
'llm-033': 'Compute the policy and reference log-ratios separately, then subtract and scale. Use a stable logistic loss for extreme margins. Inspect prompt pairing, token reduction and label quality before treating a lower preference loss as a better task outcome. This program calculates the objective rather than training an RLHF system.',
'llm-034': 'Inspect integer codes, scale shape and clipping before measuring the final output error. The half-step bound assumes unclipped nearest rounding. Raw proposed layout bytes are not the actual NumPy allocation, and dequantize-then-multiply is not an integer kernel benchmark. Report the input and task whose error was measured.',
'llm-035': 'A correct cache shape can belong to the wrong request. Check ownership and artifact identity before positional offsets and logit parity. Distinguish serial interleaving from a batched kernel, and per-request caps from aggregate capacity or fairness guarantees. Preserve both full-prefix and incremental outputs when diagnosing a mismatch.',
})

DEPTH_NOTES.update({
'llm-036': '''## Retrieval changes available evidence, not model weights

The retriever lowercases and splits text on whitespace, then scores a document by the number of distinct query terms in its token set. Query red square gives two matches for both d1 and d2, with document ID breaking the tie. Those two relevant documents give recall@1=1/2 and recall@2=2/2. Repeating a term does not increase this set-overlap score because duplicates disappear in a set. Punctuation and alternate word forms remain a limitation of the deliberately simple tokenizer.

Retrieval selects context for an answer operation. It does not update the language model's parameters, and it cannot supply evidence absent from the corpus. The demonstration uses literal text and explicit answer records rather than an online pretrained generator. This is a lexical retrieval and evidence-boundary baseline, not a deployed RAG assistant. The [original RAG study](https://arxiv.org/abs/2005.11401) integrates retrieval with generation; the applied course builds the components and their evaluation in greater depth.

## Zero overlap exposes an important failure mode

An absent query can give every document score zero. The current ranking function still returns documents, using ID order to break ties. Thus receiving a nonempty top-k list does not imply that any item contains positive evidence for the query. The missing-evidence exercise declares an empty relevant set for analysis; it does not implement a learned answerability detector or automatic abstention threshold.

A practical pipeline needs a separately evaluated policy for unsupported queries, possibly including a minimum retrieval score, a reranker and evidence sufficiency checks. A threshold chosen on training or validation data must be tested on held-out questions, including near misses. A high lexical score can come from shared words without a supporting fact. In the fixture, a retrieved statement about a red square does not entail that the square weighs 10 kg. Relevance and support for a particular claim are different relationships.

The instruction-like text in d6 remains document data. The recorded action is None; the program does not execute its imperative. This simple boundary illustrates why retrieved content should not acquire tool authority merely by appearing in context. A production design also needs source access checks before retrieval and citation, freshness rules and an explicit tool policy. Those controls require actual implementation and tests; retrieving a malicious-looking sentence while taking no action is only the narrow check performed here.
''',
'llm-037': '''## Locate a failure before assigning one overall score

The four authored evaluation rows represent a retrieval miss, an unsupported answer despite available evidence, a correct abstention and a correct supported answer. They contain one example of each outcome. This table lets us reason about where to intervene: changing the retriever addresses a different mechanism from changing how an answer uses already retrieved evidence. An overall accuracy alone would conceal that distinction.

An oracle-context experiment asks the answer system to process the same question with known sufficient evidence supplied directly. If the ordinary system fails and the oracle-context system succeeds, retrieval is a plausible limiting component for that case. If both fail, the answer mechanism or task formulation still needs investigation. The lesson's oracle record is a literal teaching record, not an actual rerun of a pretrained generator. A real experiment must preserve the exact question, context, model, prompt, decoding policy and scoring procedure for both conditions.

## A citation has several independent obligations

A document ID must resolve, the cited source must be available to the user, the quoted span must occur in that source revision, and the span must support the associated claim. These checks are progressively stronger. A substring check proves that particular text appears; it does not automatically prove entailment of an expanded answer. In the fixture, a valid document about a square cannot substantiate an invented 10 kg weight claim.

Store a mapping from each factual claim to its evidence span and source version. This makes an unsupported clause visible even if the answer contains another correct, well-cited clause. For numerical or statistical results, the evidence should include the validated calculation and its input assumptions rather than only a plausible prose explanation. Quoting an LLM-generated summary does not independently verify the underlying computation.

Stable question IDs prevent silent duplication and support paired comparisons. Relevant-source labels and answerability labels also need a declared construction process. An empty relevance set can mean genuinely unavailable evidence or incomplete annotation; decide which interpretation the evaluation permits. Correct abstention should be assessed against answerability, while unsupported answering is assessed against the evidence actually provided. The four-row fixture checks the bookkeeping and diagnosis, not the prevalence of those failure classes in a wider population.
''',
'llm-038': '''## A structured proposal is still only a proposal

The accepted object has exactly the fields tool and document_id, with tool equal to read_fixture and document_id equal to an allowed fixture identifier. Checking exact fields rejects hidden extra instructions as well as missing arguments. Checking types before values avoids treating a list, number or Boolean as a string identifier by accident. Validating a syntax shape and deciding whether an operation is authorized remain separate responsibilities.

The executor performs a lookup in a fixed in-memory dictionary. It does not interpret a document ID as a path, construct shell text, import a named function or evaluate retrieved content. A traversal-shaped ID therefore has no special power: it is rejected because it is not an allowed dictionary key. The small interface is useful because its implemented capability is easy to state precisely.

## Follow the authority boundary through every step

A future model may emit a candidate JSON object. Parse it as data, validate the declared schema, check the requested operation against policy, and only then call a preselected implementation with typed arguments. The model's confidence or wording does not grant the operation additional permissions. A retrieved passage asking for a different action should remain evidence text, not become a second instruction source for the dispatcher.

In this lesson there is no shell tool and no write capability. Describing confirmation or approval requirements in an architecture does not implement them. If a later application adds an operation with side effects, it needs a concrete authorization check, idempotency or duplicate-handling policy where relevant, bounded inputs and observable outcomes. A schema-valid command can still be disallowed for a particular user or resource.

The negative cases serve different purposes: unknown tool tests the operation allowlist, extra keys test schema strictness, a wrong type tests parsing assumptions, and a traversal-shaped identifier tests the data-versus-path boundary. Keep those observations separate rather than accepting any exception as proof that the intended validation ran. The safe outcome here is a rejected proposal or a known read-only fixture value. It is not evidence that arbitrary model-supplied programs can be safely executed in the same process.
''',
'llm-039': '''## Zero observed failures is a finite observation

Group A has zero failures in ten trials; group B has zero failures in one trial. Both observed rates are zero, but the amount of evidence is very different. Under an explicit independent, identically distributed Bernoulli model with failure probability p, the probability of seeing zero failures in n trials is (1-p)^n. Setting this probability to 0.05 gives the one-sided 95% zero-failure upper confidence bound p_upper=1-0.05^(1/n).

For n=10 the bound is about 0.2589; for n=1 it is 0.95. These large values show how little zero failures can establish with very small samples. The formula depends on the sampling model. Ten paraphrases from one prompt family may not behave like ten independent trials, and a hand-selected challenge set does not automatically estimate deployment prevalence. State the unit and collection process before attaching a population interpretation to an interval.

An untested group has no observed rate. Filling it with zero would confuse absence of evidence with observed success. Group definitions also need a task-relevant rationale and enough coverage to support the intended comparison. A pooled result can hide a concentrated failure in one slice, while many tiny slices can produce unstable estimates. Preserve counts and concrete failure examples alongside any aggregate.

## Robustness tests need a justified invariance

A counterfactual pair changes a feature while holding the task-relevant information constant. If the changed attribute should not affect the answer under the task specification, a different answer is a useful diagnostic. Not every attribute change should preserve output: changing an actual causal input to the requested calculation may correctly change the result. Specify why invariance is expected before grading the pair.

A severe-failure gate can remain unsatisfied despite 90% overall success. If the predeclared policy disallows a particular severe failure, averaging it with many easy passes does not remove it. Conversely, a passing finite challenge set cannot establish that all future cases are safe. The worksheet supplies fictional cases and a reasoning framework, not personal-data analysis or a deployment approval. A defensible report states the tested scenarios, counts, collection method, observed failures and unresolved coverage.
''',
'llm-040': '''## The sampling unit determines the comparison

The supplied question families are A, A, B, with paired score differences[-1, -1, +1]. An equal-row mean is-1/3. First averaging within family gives A=-1 and B=+1, whose equal-family mean is zero. These answer different questions: performance on the observed row mix versus performance when each sampled family receives equal weight. A report must say which target weighting it intends.

Now duplicate a negative A-type row ten more times. The equal-row mean becomes-11/13, but the two family means remain-1 and+1, so the equal-family mean remains zero. Duplicating related prompts increases the number of rows without necessarily increasing the number of independent units. This is why resampling arbitrary rows can understate uncertainty when the data have family structure.

With only these two empirical family means, drawing two families with replacement gives mean-1, 0 or+1 with probabilities1/4, 1/2 and1/4. Running a thousand bootstrap draws samples that small empirical distribution more densely; it does not create a thousand new independent families or establish transfer to unrepresented families. The interval is conditional on the observed sample and chosen resampling scheme. More independent evaluation families would provide different evidence from more repetitions of the same bootstrap.

## Accuracy and coverage describe different decisions

If a system answers two of four questions and both answers are correct, coverage is 2/4=0.5 and selective accuracy is 2/2=1. A system answering none has zero coverage but undefined selective accuracy under this definition, not perfect accuracy. Correct abstention additionally needs answerability labels; a system could avoid errors simply by refusing questions it could have answered.

Keep prompt and threshold selection in the development process and reserve independent assessment data for the final declared system. Paired IDs make per-question changes visible, but do not by themselves remove selection bias. Required gates with unknown evidence should remain unknown and block release when the policy requires a pass. The confidence or average score in one column cannot silently substitute for missing provenance, severe-failure checks or coverage. This lesson checks the arithmetic and gate logic; it does not estimate real population reliability from three synthetic rows.
''',
'llm-041': '''## Match a mathematical map before matching framework names

For row input x=[1, 2] and W=[[1, 2, 3], [4, 5, 6]], x*W=[9, 12, 15]. A Keras Dense kernel for this map has shape[2, 3]. PyTorch Linear stores its weight as[out_features, in_features], so the same map uses W transposed with shape[3, 2], because its forward operation multiplies by the stored weight's transpose. Comparing equal-shaped square matrices can conceal this orientation error, which is why the worksheet uses a rectangular example.

A meaningful parity experiment explicitly assigns weights and biases, fixes dtype, uses the same epsilon and reduction rules, and selects equivalent training/evaluation modes. Matching a seed across two frameworks does not assign identical parameter arrays, since initialization algorithms and random streams can differ. Equal layer names are also insufficient when defaults, layouts or state updates differ.

## Boolean masks do not share one universal polarity

In [PyTorch functional scaled-dot-product attention](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html), a Boolean true entry permits attention. In [MultiheadAttention](https://docs.pytorch.org/docs/stable/generated/torch.nn.MultiheadAttention.html), true in its Boolean attention mask means disallowed, and true in its key-padding mask marks an ignored key. A key-padding mask has a different shape and purpose from a causal attention matrix: a batch-by-key array cannot encode a distinct triangular restriction for every query position. Translate semantic intent, shape and polarity together.

[Keras MultiHeadAttention](https://keras.io/api/layers/attention_layers/multi_head_attention/) uses a Boolean attention mask that uses true for an allowed query/key relationship. This makes it similar to functional SDPA's polarity, but it does not make every broadcasting or call contract interchangeable. Draw a small allowed-relation table, then translate it into each API and verify which output changes when a future token changes. A passing output shape alone cannot detect reversed mask meaning.

Functional SDPA applies the dropout probability passed to the function. A surrounding module's eval mode does not automatically rewrite that numeric argument to zero. A wrapper should pass zero when evaluation requires deterministic attention and the configured probability only during training. This is a call-site policy, distinct from disabling autograd. The worksheet explains these contracts without claiming a new cross-framework runtime comparison; the dedicated framework routes provide their actual qualified examples.
''',
'llm-042': '''## Read the capstone's evidence ledger literally

The three questions cover shape, color and an astronomy question with missing evidence. The candidate correctness records give the tiny candidate 1/3, count candidate 0/3 and retrieval candidate 3/3, with the last retrieval success meaning correct abstention. These are hand-authored saved decision records used to demonstrate comparison logic. They are not answers newly generated by the model in this program and must not be reported as measured benchmark quality for a trained system.

The program separately initializes a small decoder and runs a full forward pass and three incremental cached passes on tokens[2, 5, 7]. Their logits must agree within the stated tolerance. This is an actual numerical mechanism check with an untrained random model. It establishes neither subject knowledge nor the correctness of the hand-authored answer ledger. The elapsed time includes those particular calls and Python orchestration; it is not a general generation-throughput benchmark.

| Artifact in this exercise | What it supports | What it does not establish |
| --- | --- | --- |
| Fixed question/answerability records | Stable IDs and the declared task cases | Population coverage or independent annotation quality |
| Saved candidate correctness table | Arithmetic and paired bookkeeping | That the instantiated decoder produced those answers |
| Full-versus-cached logits | Incremental numerical parity for this model and prefix | Correct facts or useful assistant behavior |
| Parameter and fixture hashes | Identity of the bytes included by the hashing procedure | A causal link between a hash and an unrelated answer table |
| Required-gate dictionary | The implemented go/no-go decision rule | That an external evaluator actually verified every input gate |

## A complete decision can honestly be no-go

The declared generated-token cap is metadata in this record; there is no generation loop here enforcing that cap against a live assistant. A full system would bind the policy to actual inference and preserve the resulting answers, citations, token counts and failure observations. Similarly, hashing raw parameter bytes under a known architecture is useful, but a reusable artifact identity should include names, shapes, dtypes, configuration, tokenizer and version information.

The gate dictionary contains mechanism=True, trust_boundary=True, population_evidence=None and severe_failures_absent=False. The rule accepts only if every required value is exactly True, so the observed result is no-go. The latter three values are supplied review inputs in this teaching exercise, not findings inferred by the decoder test. An unknown required result and a declared failed condition both block the decision.

To turn the template into a real study, freeze the evaluation families and scoring rubric, run each candidate on the same permitted evidence, preserve actual answers, independently score supported claims and abstention, then apply the predeclared gates. The [applied assistant capstone](../../llm-applied/README.md) develops a more connected local pipeline. Keep the distinction between mechanism execution and answer-quality evidence throughout: a useful review record can explain exactly what failed and what observation is needed next without claiming readiness.
''',
})

DIAGNOSIS_NOTES.update({
'llm-036': 'Inspect the actual query terms and overlap scores before trusting a nonempty top-k list. Zero-score ties still return documents in this implementation. Relevance does not entail every answer claim, and a literal missing-evidence label is not an automatic abstention detector. Keep retrieved instructions as data and test access and evidence rules separately.',
'llm-037': 'Separate retrieval failure, unsupported answering and abstention quality using stable question IDs. A valid source ID and a matching substring are weaker than support for the associated claim. Mark oracle records as recorded or actually rerun, and preserve the model/context artifacts if drawing a causal diagnosis from a controlled comparison.',
'llm-038': 'Validate exact fields and types before dispatch, then check the operation and resource allowlists. Do not reinterpret a document identifier as a filesystem path or an instruction. Each negative case should fail for its intended reason. A typed proposal does not create authority, and a read-only fixture dispatcher is not an arbitrary-code execution system.',
'llm-039': 'Keep zero observed failures, unknown coverage and a guaranteed zero population rate separate. State the independence and sampling assumptions behind an interval. Explain why a counterfactual should preserve the task answer, and apply severe-failure gates without averaging them away in an overall pass rate.',
'llm-040': 'Choose the observational unit before averaging or bootstrapping. Duplicated family rows do not add independent families, and more bootstrap repetitions do not add new data. Report both answer coverage and conditional accuracy, preserve undefined denominators, and keep development selection separate from final assessment.',
'llm-041': 'Use rectangular literal weights to expose transposition errors. Check mask shape, meaning and polarity for the exact API, and do not use a padding mask as if it were a query-dependent causal mask. Match dtype, epsilon, modes and dropout arguments explicitly rather than assuming equal seeds or names imply parity.',
'llm-042': 'Trace every claim to the artifact that actually produced it. The saved answer ledger and the random decoder parity test are separate experiments. A hash does not join them automatically. Preserve unknown and failed gates, distinguish a declared budget from an enforced generation loop, and require actual candidate answers before reporting system quality.',
})


def apply_prose_review(specs):
    """Repair prose spelling without touching imports, helpers or exercise code."""
    import re
    replacements = {
        'parametersP, tokensD, stepsS, computeC': 'parameter count P, unique corpus tokens D, optimizer steps S, relative compute C',
        'lossL': 'loss L', 'andcontent_hash': 'and content_hash', 'with-100': 'with -100',
        'shaped8x8': 'shaped 8x8', 'A8x2': 'A 8x2', 'andB2x8': 'and B 2x8',
        'has 32': 'has 32', 'with 64': 'with 64', 'InitializingB': 'Initializing B',
        'ofA': 'of A', 'byB': 'by B', 'whileB': 'while B', 'throughA': 'through A',
        'andB': 'and B', 'withW': 'with W', 'as(out, in)': 'as (out, in)',
        'values-127': 'values -127', 'toint8': 'to int8', 'retaink': 'retain k',
        'from(request': 'from (request', 'anddocument_id': 'and document_id',
        'asX@W': 'as X@W', 'appliesX@W.T': 'applies X@W.T', 'uses1': 'uses 1',
        'orTrue': 'or True', 'supply0': 'supply 0', 'asTrue': 'as True',
        'OnlyTrue': 'Only True', 'orNone': 'or None', 'held-out': 'held-out',
        'whereq3correct': 'where q3 correct', 'scores1/3': 'scores 1/3',
        'on2, 5, 7': 'on 2, 5, 7', 'within1e-6': 'within 1e-6',
        'below50000': 'below 50000', 'two64-character': 'two 64-character',
        'cap4': 'cap 4', 'mechanismTrue': 'mechanism True',
        'trust-boundaryTrue': 'trust-boundary True', 'evidenceNone': 'evidence None',
        'gateFalse': 'gate False', 'decisionno-go': 'decision no-go',
        'theno-go': 'the no-go', 'namesq3': 'names q3', 'unsupportedanswer': 'unsupported answer',
    }
    def clean(value):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return re.sub(r', (?=[A-Za-z])', ', ', value)
    for number in range(29, 43):
        spec = specs[f'llm-{number:03}']
        for field in ['mental', 'anatomy']:
            spec[field] = clean(spec[field])
        spec['terms'] = [(clean(term), clean(definition)) for term, definition in spec['terms']]
        for exercise in spec['exercises']:
            for field in ['title', 'prompt', 'expected', 'why']:
                exercise[field] = clean(exercise[field])
    specs['llm-042']['mental'] = '''This capstone implements a decision-report template using hand-authored candidate correctness records and a separate actual tiny-decoder parity probe. It does not generate or train the candidate answers whose scores appear in the ledger. The purpose is to learn which artifacts support a claim, how paired comparisons and required gates work, and why unknown or failed evidence can justify a no-go. A real language-system study must replace the illustrative records with actual frozen-question runs, answer artifacts and independent scoring. Keep task quality, numerical mechanism checks and resource observations separate throughout the review.'''
