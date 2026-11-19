"""Authored learning objectives for every PyTorch lesson.

Each entry states an observable outcome, the central investigation and the
finish condition with its concrete values. The renderer publishes these fields
to track.json and the guides instead of splicing sentences from other prose.
"""

# Long lines preserve authored prose and exercise programs.
# ruff: noqa: E501

OBJECTIVES = {
    "torch-001": (
        "Write an experiment card that names the prediction unit, the training and holdout rows, a training-only baseline and the claims a tiny CPU fixture cannot support.",
        "Split seven points of y = 2x into three training and four untouched rows, score a constant training-mean baseline and audit a holdout that was reused for selection.",
        "The card records 3 training and 4 holdout rows, a baseline mean of 4 with holdout MSE 54, the hand rule labeled as an analytic oracle rather than a trained model, and the reused holdout reclassified as validation.",
    ),
    "torch-002": (
        "Predict a tensor's shape, stride, dtype, device and storage sharing before running code, and tell a view, a clone and a broadcast pairing apart.",
        "Create a 2-by-3 float64 CPU tensor, mutate a row view and a clone, transpose it, and subtract a vector from its column form.",
        "The tensor reports shape (2, 3) and stride (3, 1); the view write changes x[0, 0] to 99 while the clone stays independent; the transpose has stride (1, 3); the column subtraction broadcasts to (3, 3); and adding shapes (2, 3) and (4,) raises RuntimeError.",
    ),
    "torch-003": (
        "Compute an nn.Linear output by hand from its stored (out, in) weight, count its registered parameters and diagnose a feature-width mismatch.",
        "Load known weights into a 3-to-1 Linear layer, compare the module with X @ W.T + b, remove the bias and register state correctly.",
        "The layer returns [[0], [2]] with shape (2, 1) and 4 registered scalars, the manual product matches it within 1e-12, the bias-free layer gives -2 and 0, and a 2-feature row raises RuntimeError.",
    ),
    "torch-004": (
        "Choose a loss reduction deliberately and predict how sum, mean and masked means change the loss value and the gradient scale.",
        "Reduce the residuals [1, -1, 2] with sum and mean, duplicate the batch, differentiate both objectives and mask a padded loss.",
        "Sum is 6 and mean is 2, duplication doubles only the sum, the sum gradient is 3 times the mean gradient, and the masked mean of [1, 4, 100] with the last entry invalid is 2.5 rather than 5/3.",
    ),
    "torch-005": (
        "Obtain a derivative with autograd.grad, confirm it with central finite differences and keep the gradient separate from the optimizer update it informs.",
        "Differentiate (w-2)**2 at w = 0 with autograd, compare three central-difference steps and apply one learning-rate 0.1 update by hand.",
        "Autograd returns -4 at loss 4, every finite-difference slope agrees within 1e-10, the update gives w = 0.4, the stationary point w = 2 has gradient 0, and invalid probes raise ValueError.",
    ),
    "torch-006": (
        "Trace a chain-rule derivative through an autograd graph and recognize the two in-place mutations that autograd refuses.",
        "Backpropagate loss = (a-1)**2 with a = z*z and z = 2w at w = 1, check it numerically and mutate a leaf and a saved tensor.",
        "The trace gives z = 2, a = 4, loss 9 and gradient 48, a central difference agrees within 1e-5, and both the leaf mutation and the saved-tensor mutation raise RuntimeError.",
    ),
    "torch-007": (
        "Explain when PyTorch stores, accumulates, detaches or skips gradients, and clear accumulated gradients before an independent step.",
        "Backpropagate twice into the same leaf at w = 0, detach a shared view, and compare no_grad with eval mode.",
        "The leaf gradient becomes -4 then -8 without clearing and returns to -4 after reset, the detached view shares storage while a detached clone does not, no_grad output has requires_grad False, and eval output still requires grad.",
    ),
    "torch-008": (
        "Audit one optimizer step by checking the loss, the gradient and the updated weight as three separate states.",
        "Fit w in y = 2x on x = 1, 2, 3 from w = 0 with one SGD step at learning rate 0.1, then repeat with mismatched target shapes.",
        "The initial loss is 56/3, the gradient is -56/3 before the step, the step gives w = 28/15 and loss 56/675, and the (3, 1) target broadcast keeps loss 56/3 but changes the gradient to -16.",
    ),
    "torch-009": (
        "Relate epochs, batches and optimizer steps, and combine unequal batch means with record-count weights.",
        "Partition record IDs into batches, train three cleared updates on x = 1..6 and repeat the loop without zero_grad.",
        "Six IDs give three batches, five give sizes 2, 2, 1, the cleared run produces three distinct finite weights, omitting zero_grad changes the endpoint, and batch means 2 and 8 over 2 and 1 records combine to 4, not 5.",
    ),
    "torch-010": (
        "Build a Dataset and group-aware Subsets so that preprocessing statistics are fitted only on training groups.",
        "Load eight account records, hold out whole groups C and D, fit a centering mean on A and B, then contrast a row-level split.",
        "Group sets are disjoint, the training mean stays 4 even after a held-out value changes to 3200, the frozen transform maps held-out values to 16, 18, 26 and 28, and the alternating row split lets all four groups cross.",
    ),
    "torch-011": (
        "Register parameters and buffers in an nn.Module, run an explicit training step and detect an optimizer that still holds a replaced Parameter.",
        "Build a scalar module with weight 0 and buffer offset 0, take one SGD step, convert its dtype and replace its Parameter after creating an optimizer.",
        "The module exposes one parameter and one buffer in state_dict, one SGD step moves the weight to 28/15 while the buffer stays 0, both tensors convert to float32, and the stale optimizer still references the old Parameter.",
    ),
    "torch-012": (
        "Deliver an auditable regression run: fixed data identities, a training-only baseline, a bounded training loop and a separately opened holdout.",
        "Fit a bias-free 3-to-1 Linear model on four training rows of target 2a-b+c for 100 SGD steps and score two holdout rows afterward.",
        "The baseline mean is 0.5 with holdout MSE 7.25, the weight equals (1-0.95^100) times [2, -1, 1], the trained holdout error is below 7.25, and the report keeps the two-row limitation explicit.",
    ),
    "torch-013": (
        "Train binary classifiers on logits with BCEWithLogitsLoss and choose a decision threshold as a separate, explicit policy.",
        "Convert the logits -2, 0 and 2 to probabilities, evaluate the zero-logit loss, compare thresholds 0.5 and 0.8 and feed a probability into a logits loss by mistake.",
        "The middle probability is 0.5, the zero-logit loss is log 2, threshold 0.5 gives 0 errors and 0.8 gives 1 on truth 0, 1, 1, the double-sigmoid loss differs by more than 0.1, and logits of magnitude 1000 stay finite.",
    ),
    "torch-014": (
        "Select CrossEntropyLoss or BCEWithLogitsLoss from the label structure and give each its correct target shape, dtype and denominator.",
        "Score three zero logits as a multiclass row and as three independent labels, build both target forms and use an invalid class index.",
        "The multiclass loss is log 3, the independent probabilities 0.5 sum to 1.5, class indices have shape (2,) with dtype long while multilabel targets are floating (2, 3), and class index 3 is rejected.",
    ),
    "torch-015": (
        "Configure a DataLoader whose batching, dropping, shuffling and collation are reproducible and keep each input paired with its target.",
        "Load five ID/value records with batch size 2, then drop the tail, shuffle with seeded generators and pad two token sequences.",
        "Batches have sizes 2, 2, 1 with IDs 0..4 once, drop_last omits ID 4, two generators seeded 7 give the same permutation, padding yields [[2, 3], [4, 0]] with lengths 2 and 1, and invalid sequences raise ValueError.",
    ),
    "torch-016": (
        "Explain why a nonlinearity is required for XOR and test weight layout and initialization symmetry with deliberately chosen fixtures.",
        "Build XOR from two rectified differences, remove the ReLU, map the weights into nn.Linear and probe the layout with an asymmetric matrix.",
        "The ReLU construction outputs 0, 1, 1, 0, the linear version outputs four zeros, the asymmetric probe separates W from W.T, identical rows stay identical, and the continuous inputs (0.2, 0.8) and (0.8, 0.2) both give 0.6.",
    ),
    "torch-017": (
        "Separate explicit regularization penalties from Dropout's train and eval behavior and check each with exact values.",
        "Compute L1 and squared L2 penalties for weights [1, -2], run Dropout(0.5) in eval and train mode and differentiate the penalty.",
        "L1 is 3 and squared L2 is 5, eval-mode Dropout returns its input exactly, train mode outputs only 0 or 2, a 0.1 coefficient adds a penalty of 0.5 for a total of 2.5, and the penalty gradient is [0.2, -0.4].",
    ),
    "torch-018": (
        "Predict how BatchNorm running statistics and LayerNorm row statistics respond to train mode, eval mode and momentum conventions.",
        "Update a BatchNorm layer with momentum 0.5 on rows [1, 3] and [3, 5], evaluate it on an outlier row and compare LayerNorm rows alone and together.",
        "The running mean becomes [1, 2] and the running variance 1.5 after one step, eval leaves the running mean and batch counter unchanged, the LayerNorm row matches within 1e-6 alone or beside [100, 200], and PyTorch momentum 0.1 gives 1 where Keras momentum 0.1 gives 9.",
    ),
    "torch-019": (
        "Compute a Conv2d output by hand in NCHW layout, predict its output shape and count its shared parameters.",
        "Apply the 2-by-2 kernel [[1, 0], [0, -1]] to a 3-by-3 ramp image, flip the kernel, change the stride and perturb one pixel.",
        "The output has shape (1, 1, 2, 2) with every value -4, the flipped kernel gives +4, stride 2 gives shape (1, 1, 1, 1), a +10 top-left pixel changes only the top-left output, and the 1-to-2-channel 2-by-2 bias-free layer has 8 parameters.",
    ),
    "torch-020": (
        "Compare max and average pooling and apply augmentations whose labels transform consistently with the image.",
        "Pool the patch [[1, 3], [2, 4]], flip it horizontally, change its non-maximum pixel and map a directional label under reflection.",
        "Max pooling gives 4 and average 2.5, the flip gives rows [3, 1] and [4, 2] and round-trips exactly, lowering pixel 1 to 0 keeps max 4 but average becomes 2.25, and the label maps left to right and back.",
    ),
    "torch-021": (
        "Represent padded token sequences with embeddings, masks and packing so that padding never changes a gradient, a recurrent state or a loss.",
        "Embed IDs 2, 3, 0 with a padding row, run a packed GRU of length 2 and average token losses with a validity mask.",
        "The embedding has shape (1, 3, 2) with mask True, True, False, the padding row receives zero gradient, the packed final state matches the two-step state within 1e-6, the unmasked run differs, and the masked mean loss stays log 2.",
    ),
    "torch-022": (
        "Compute scaled dot-product attention with an explicit allowed mask and prove that future positions cannot change earlier outputs.",
        "Run causal attention on a three-token fixture, change only the third value vector and compare every prefix cut.",
        "Uniform causal outputs are [2, 0], [1, 1] and [8/3, 8/3], changing the third value to [100, 200] alters only the last row to [34, 202/3], all prefixes match within 1e-12, and an all-masked row raises ValueError.",
    ),
    "torch-023": (
        "Debug a custom training loop by checking graph connectivity, gradient clearing and norm clipping one state transition at a time.",
        "Detach a loss by mistake, repair two exact SGD updates and clip the gradient [3, 4] to norm 1 before stepping.",
        "The detached loss cannot backpropagate, the repaired weights are 28/15 then 448/225, clipping returns the original norm 5 and the gradient [0.6, 0.8], the clipped step gives approximately [-0.06, -0.08], and an infinite gradient raises RuntimeError.",
    ),
    "torch-024": (
        "Train and evaluate a small logistic classifier with training-only normalization, a confusion table, a baseline and group-level error counts.",
        "Normalize four training points, train 40 SGD steps on binary logits and threshold two test points at logit 0.",
        "Normalization uses mean 0 and scale sqrt(2.5), the trained weight is positive and finite, the test confusion counts are TP 1, TN 1, FP 0 and FN 0, the constant baseline makes 1 error, and the group report shows 0 of 1 and 1 of 1 wrong after the flip.",
    ),
    "torch-025": (
        "Train and audit an embedding objective by separating dot products, cosine similarity, temperature and candidate identities.",
        "Score an anchor against one positive and one negative vector, rescale the positive, compute the two-candidate loss and vary the temperature.",
        "Dot scores are 1 and 0 with cosines 1/sqrt(2) and 0, scaling the positive by 10 changes only the dot score, the loss is log(1+exp(-1)), temperature 0.5 raises the positive probability without changing the argmax, and a shared document ID is detected.",
    ),
    "torch-026": (
        "Write a custom module and a custom autograd Function whose state, shape checks and backward rule are verified explicitly.",
        "Build a width-2 residual module with a scale buffer, apply known kernels and validate a custom cube derivative with gradcheck.",
        "The zero-kernel residual returns its input with one parameter and one buffer, the identity kernel with scale 0.5 returns 1.5x, a width-3 input raises ValueError, gradcheck passes for Cube, and the incoming factor 2 gives gradient 24 at x = 2.",
    ),
    "torch-027": (
        "Freeze a pretrained base, train a new head and manage optimizer membership and normalization buffers during later unfreezing.",
        "Freeze an identity Linear base, train a zero-initialized head one step, then test BatchNorm buffers and an explicit unfreeze phase.",
        "The frozen base stays the identity with no gradients while the head changes, BatchNorm running means still change in train mode until eval is set, and the unfreeze optimizer changes the base weight.",
    ),
    "torch-028": (
        "Save and restore every state that determines the next training update, and show that weights alone do not resume training.",
        "Take two Adam updates, checkpoint model, optimizer, RNG and data position, then continue in place and in a fresh interpreter.",
        "The checkpoint holds Adam step 2 and data position 2, the fresh-process continuation reproduces the random probe and the next weight within 1e-6, a weights-only restart diverges, and the owned directory is removed.",
    ),
    "torch-029": (
        "Compute softmax losses stably and compare floating-point formats by their range and precision before choosing mixed precision.",
        "Exponentiate float32 logits 1000 and 999 directly, then compute the same loss, probabilities and gradients with stable operations.",
        "Direct exponentials overflow to infinity, the stable loss equals log(1+exp(-1)) within 1e-6, shifted logits give probabilities that match within 1e-6, gradients are finite and sum to about 0, bfloat16 has a larger range than float16, and a NaN logit raises ValueError.",
    ),
    "torch-030": (
        "Combine gradients across shards and microbatches so that they represent the declared global mean objective.",
        "Weight shard means by their counts, accumulate summed squared-loss gradients over shards of sizes 1 and 3, and contrast separate microbatch steps.",
        "Shard means 2 and 6 with counts 1 and 3 give 5 rather than 4, the accumulated gradient is -30 like the full batch, one SGD step gives w = 0.3, separate steps end elsewhere, and an empty shard contributes 0.",
    ),
    "torch-031": (
        "Measure performance honestly by separating an eager oracle, graph capture, warmed timing and profiler evidence.",
        "Compile f(x)=x*x+1 with a counting backend, reuse and change its input signature, time warmed calls and profile one eager call.",
        "The eager oracle returns [2, 5], the captured graph matches it, a float64 call adds a second graph, 20 warmed calls are correct with nonnegative elapsed time, aten::mul and aten::add appear, and the receipt makes no speedup claim.",
    ),
    "torch-032": (
        "Release a model as a state_dict and as an exported program, and verify inference parity and batch constraints in a fresh process.",
        "Save a 2-to-1 Linear model with weight [2, -1] both ways, reload each in a new interpreter and test a three-row batch.",
        "Both artifacts predict 0 and 2 for the two fixture rows, the static export rejects three rows while the module accepts them, the dynamic export with batch range 1..4 matches the module, and the temporary directory is removed.",
    ),
    "torch-033": (
        "Implement an inference function with an explicit input contract that rejects ambiguous inputs and never mutates caller data.",
        "Predict float32 rows [1, 2] and [3, 4], compare per-record and batched calls, then pass empty, oversized, wrongly typed and nonfinite inputs.",
        "The batch predicts 0 and 2 with shape (2,), single-row calls agree, invalid shapes raise ValueError, an int64 matrix raises TypeError, a NaN raises ValueError, and the caller's input is unchanged.",
    ),
    "torch-034": (
        "Report model reliability with group denominators, repeated identities, controlled perturbations and severe failures kept visible.",
        "Count group errors on three records, repeat one record, shift a threshold input and summarize nine minor passes with one severe failure.",
        "Group A has 1 error of 2 and group B 0 of 1, 8 rows contain only 3 unique IDs, the shifts give labels 1, 1, 0, the 0.9 pass rate still reports 1 severe failure, and an untested group is None rather than 0.",
    ),
    "torch-035": (
        "Compare two models on the same held-out identities with paired differences and a reproducible bootstrap.",
        "Align three predictions by ID, average the paired squared-loss differences and draw 1000 seeded bootstrap means.",
        "The paired differences are -1, 0, -1 with mean -2/3 favoring model A, all 1000 bootstrap means lie in [-1, 0], reseeding with 7 replays the same indices, and a missing ID is rejected before comparison.",
    ),
    "torch-036": (
        "Release a small model with hashed artifacts, a schema, a split manifest, fresh-process parity checks and a bounded decision record.",
        "Train a float64 Linear model for 30 steps, save weights, schema and manifest, reload them in a child process and corrupt the hash.",
        "Holdout error beats the training-mean baseline error of 26, the child reproduces holdout predictions within 1e-12, a zeroed hash makes the child exit nonzero with a mismatch diagnostic, and the record states a production no-go.",
    ),
}
