"""Topic-specific TensorFlow prose reviews; executable examples stay unchanged."""

REVIEWS = {
    "tf-009": (
        """## Trace the optimizer's clock

An epoch counts exposure to a chosen dataset; a step counts an optimizer
update. Those clocks need not advance together. Six observations in batches
of two produce three updates, while batches of one produce six. Keeping the
epoch count fixed while changing batch size therefore changes the number of
updates, the noise in each gradient and the weights at which later gradients
are evaluated. A fair comparison must say which budget it holds fixed.

For this lesson's y=2x model, a batch gradient is
2(w-2) times the batch mean of x squared. Starting at w=0 with learning
rate 0.01, the first batch x=[1,2] has mean square 2.5, gradient -10 and new
weight 0.1. The next batch x=[3,4] has mean square 12.5 and sees that new weight:
its gradient is -47.5 and the next weight is 0.575. The last batch sees 0.575,
not zero, and produces 1.44425. This is a state trajectory, not three
independent estimates whose final weights can simply be averaged.

The reporting clock is another choice. If two examples have losses 1 and 3
and a final short batch contains loss 8, their overall mean is 4. Averaging
the two batch means 2 and 8 gives 5, which weights batches equally instead of
examples. Accumulate loss sums and contributing counts when reporting an
example-weighted epoch mean. The same rule applies to validation loops.

Shuffling should permute complete example records, including IDs and targets.
The identity ledger is a useful check even when the loss falls: a training
curve cannot reveal that features and labels were shuffled independently.
Dropping the tail is a sampling decision that belongs in that ledger.""",
        """Check the number of optimizer updates before interpreting a changed
training curve. Then inspect the first two before/after weights against the
explicit recurrence. If per-batch metrics look plausible but the epoch metric
disagrees, compare its numerator and denominator with the retained record IDs.
Do not repair a dropped remainder by silently pretending it was observed.""",
    ),
    "tf-010": (
        """## A split determines what the experiment can claim

Training and validation are roles assigned to observations. Preprocessing
must respect those roles too. In the supplied fixture the training mean is 4,
so validation values 20,22,30 and 32 become 16,18,26 and 28. A future value 1000
becomes 996. Its extremeness does not authorize refitting the mean: doing so
would make the supposedly frozen transformation depend on evaluation data.

An account-level split answers a different question from a row-level split.
When several rows describe the same account, a row split may put near copies
or stable account characteristics on both sides. A high score then measures
performance partly on familiar accounts. An account-disjoint split measures
transfer to different accounts under the remaining sampling assumptions.
Neither automatically proves transfer to a later time period or a new region.

Write the intended prediction moment before choosing the split. A feature
computed after the outcome is unavailable at that moment even if its column
is present in both files. A split can be disjoint by ID and still leak through
future aggregates, duplicate documents or feature-selection decisions made
using held-out labels.

A split hash makes one particular assignment identifiable. It does not prove
independence, good sampling or absence of leakage. Retain the IDs, grouping
rule, time boundary and preprocessing-fit partition with the hash. If a
validation score drives model choice, it is no longer a fresh final test of
the selected model; keep that last assessment separate.""",
        """If an extreme validation record changes a fitted training statistic,
the preprocessing boundary is broken. If account IDs cross the split, first
decide whether the intended use involves new or already observed accounts.
Inspect feature timestamps and duplicate families even when the explicit ID
intersection is empty. A new split hash documents a change; it does not
explain or justify the change.""",
    ),
    "tf-011": (
        """## Connect the Keras abstraction to one scalar calculation

The no-bias Dense layer represents y_hat=wx. Its single kernel is trainable
state; the predictions and loss are activations computed from that state.
Building or compiling a model configures those relationships. Training is the
later operation that evaluates a gradient and changes the kernel.

For x=[1,2,3], targets 2x and mean squared error, the loss is
(14/3)(w-2) squared. Its derivative is (28/3)(w-2). At zero the gradient is
-56/3; an SGD step of size 0.1 therefore gives w=28/15. The residual coefficient
is then -2/15, making the post-update loss 56/675. Those fractions provide an
independent check on the layer, loss reduction and optimizer configuration.
A smooth training curve alone would not distinguish an unintended sum loss
from the intended mean loss.

Keep predictions and targets explicitly shaped as one output per row. A
prediction shaped (B,1) and a raw target shaped (B,) can broadcast to a
(B,B) matrix in a manually written subtraction. That would compare each
prediction with several targets instead of its paired target. Inspect shapes
before reducing; reduction can hide the accidental extra axis.

Adding a bias changes the model to wx+b and raises the parameter count from
one to two. The intercept is useful when the relationship need not pass
through the origin, but it changes the hand calculation and the optimization
problem. Evaluation should read the current parameters without performing a
training update; distinguish that property from any layer-specific moving
state introduced later.""",
        """A wrong first kernel value points to learning rate, reduction,
initialization or target shape before it points to an optimizer mystery.
Print the unreduced error shape and the parameter count. If evaluation changes
the kernel, inspect whether a training operation was called. If only moving
statistics change, investigate training mode rather than assuming all state
is an ordinary trainable weight.""",
    ),
    "tf-012": (
        """## Build a comparison that can fail usefully

The capstone's constant baseline is the training-target mean 0.5. On the two
held-out targets 2 and 4 it has squared errors 2.25 and 12.25, averaging 7.25.
That is the relevant comparison in this fixture: the trained model should
improve on a predictor that can be fitted without seeing the holdout.
Choosing the holdout mean instead would give the baseline information the
candidate was not allowed to use.

The known linear relationship makes this a plumbing and reasoning experiment.
It checks whether features remain aligned, weights actually change and the
evaluation uses the frozen partition. It is intentionally easier than a
real data problem with noise, selection bias, missingness and an uncertain
functional form. A successful tiny fit demonstrates implementation evidence;
it does not establish that a neural network is necessary for the task.

Keep three observations separate: initial training error, final training
error and final holdout error. The first pair checks optimization on the
selected training data. The third examines the chosen held-out records.
Neither a finite weight vector nor a falling training loss guarantees an
improvement on the holdout.

The two held-out records are also too few to support a precise population
claim. Report their count and exact errors. In a larger investigation,
compare against simple alternatives, use a split that matches the intended
prediction setting, and preserve the final evaluation boundary while choosing
architecture and training budget.""",
        """A candidate that loses to the constant baseline may have a coding
error or may simply be unsuitable. First reproduce the known scalar update,
then inspect feature order, target alignment and the frozen holdout IDs.
Do not repeatedly tune against the two holdout rows until the required
inequality happens to pass and then describe that result as untouched evidence.""",
    ),
    "tf-013": (
        """## Separate the probability model from the action rule

A logit z represents log odds. Its sigmoid p=1/(1+exp(-z)) lies between zero
and one. A zero logit therefore represents probability 0.5, not probability
zero. For a binary target y, the logits form of cross entropy is
log(1+exp(z))-yz; a stable implementation avoids directly exponentiating a
very large positive z. Its derivative with respect to z is p-y.

The from_logits setting is a contract about the supplied numbers. Feeding
probability 0.5 as if it were a logit applies another sigmoid, producing about
0.622 rather than 0.5. For target 1 the corresponding loss is about 0.474
instead of log(2), about 0.693. The calculation remains finite, so a NaN check
cannot detect this semantic mismatch.

A decision threshold adds a policy on top of probabilities. With false-positive
cost C_FP and false-negative cost C_FN, zero cost for correct decisions and
calibrated probabilities for the decision population, predicting positive has
expected cost C_FP(1-p), while predicting negative costs C_FN p. The resulting
threshold is C_FP/(C_FP+C_FN). Costs 1 and 4 give 0.2. Those assumptions matter:
class weighting during fitting can change how a score should be interpreted.

Specify the equality convention at the threshold. This lesson includes p=0.5,
so greater-than and greater-than-or-equal rules differ on an actual fixture
row. Moving a threshold changes decisions and error counts without changing
the fitted logits, ranking or probability-loss calculation.""",
        """Check whether the loss expects logits before adding sigmoid.
Compare the zero-logit case with log(2), then inspect large positive and
negative scores using the stable operation. If probability loss is correct
but classification counts differ, inspect the threshold and its equality
rule. A three-row success does not establish population calibration.""",
    ),
    "tf-014": (
        """## Let the target's meaning determine the output geometry

Multiclass classification assumes one selected class among C alternatives.
The model produces C competing logits and softmax normalizes their probability
mass to one. With three equal logits, each class has probability 1/3 and the
negative log probability of the selected class is log(3).

Multilabel classification permits several labels to be true at once. Three
zero logits passed through independent sigmoids produce three probabilities
of 0.5 whose sum is 1.5. That sum is valid because the labels are not mutually
exclusive outcomes of one categorical draw. Replacing those sigmoids with
softmax would force labels to compete and change the modeling assumptions.

Target shapes encode part of this distinction. Sparse categorical targets
use one class index per example, often shape (B,). A multilabel target uses
one indicator for each example-label pair, shape (B,C). A categorical one-hot
target also has shape (B,C), so shape alone cannot identify the task: its row
constraints and intended probability distribution must agree too.

Reduction defines the reported unit. For two examples and three independent
binary labels with zero logits, six binary losses each equal log(2). Their
sum is 6 log(2), and their mean is log(2). If some labels are unobserved, count
only the intended active targets; treating an unknown label as a negative
creates supervision that the data did not supply.""",
        """If softmax probabilities look plausible but several labels should
coexist, revisit the target definition before tuning the model. Reject class
indices outside 0 through C-1. Check whether unknown multilabel entries were
converted to zeros and whether the loss denominator counts examples, labels
or active example-label pairs.""",
    ),
    "tf-015": (
        """## Treat the input pipeline as part of the model's experiment

A pipeline describes a traversal, not just a collection of arrays. Mapping,
shuffling, batching, caching and repeating have different effects depending
on their order. Batching five records by two gives sizes 2,2,1. Adding an
explicit drop-remainder policy changes the observed sample to four records.
The absent record should remain visible in the ID ledger.

Shuffle whole records before separating their components. Shuffling feature
and target datasets independently is unsafe even if their lengths match.
An equal seed is not a robust pairing mechanism once one branch filters,
maps, repeats or consumes randomness differently. Keep the ID, feature and
target together through transformations, then unpack them at the model boundary.

Cache placement affects what is repeated. Caching after a random augmentation
can preserve the first materialized augmented values across later traversals.
Caching the deterministic source before augmentation allows later augmentation
calls to produce different values. Neither policy is universally required;
state which behavior the experiment intends and test it on a small fixture.

Prefetch overlaps production of later elements with consumption of current
ones. It is not a justification for changing labels or evaluation order.
Reproducibility also depends on deterministic transformation behavior, seeds,
parallel execution choices and the sequence of iterations. A repeatable five-row
traversal checks this local contract, not every possible production input.
Fit preprocessing statistics only on the training partition before placing
the frozen transform in validation or test pipelines.""",
        """When observations vanish, inspect filtering and remainder policy
before blaming training. When labels drift, compare IDs before and after
mapping. When augmentations unexpectedly repeat, inspect cache placement.
When timing changes, preserve output equality and the traversal contract
before interpreting a prefetch or parallel-map optimization.""",
    ),
    "tf-016": (
        """## Derive why a hidden nonlinearity matters

Two affine layers without an intervening nonlinearity remain affine:
(XW_1+b_1)W_2+b_2 equals X(W_1W_2)+(b_1W_2+b_2). More such layers do not by themselves
create the curved decision regions that motivate a nonlinear network.
They can still change parameterization and optimization, so equivalence of
the represented function class does not make every training trajectory equal.

The supplied XOR construction uses two ReLU branches. One keeps the positive
part of x_1-x_2; the other keeps the positive part of x_2-x_1. Their sum is the
absolute difference. At the four Boolean corners it equals the XOR labels,
but at (0.2, 0.8) it is 0.6. That extension is determined by the learned or
constructed function, not by the name XOR. Correct corner predictions do not
tell you how an arbitrary network behaves between or beyond those corners.

Initialization also controls whether hidden units can develop different
roles. Identically initialized units receiving identical gradients stay
symmetric under the same deterministic update. Appropriate random variation
breaks that symmetry; its scale matters because excessively large or small
activations can make optimization unstable or uninformative.

For a negative ReLU input the local derivative is zero; for a positive input
it is one. The boundary at exactly zero needs an implementation convention.
Do not confuse a local zero gradient in a closed region with proof that the
whole model has converged. Trace preactivations, active regions and upstream
gradient paths before changing learning rates.""",
        """If a deeper model behaves like one linear map, check whether its
nonlinearity was omitted. If hidden columns remain identical, inspect their
initial values and gradients. If a ReLU branch never updates, inspect its
preactivation distribution and connectivity. Do not infer a probability
interpretation merely because the XOR corner outputs are zeros and ones.""",
    ),
    "tf-017": (
        """## Keep objective penalties, optimizer rules and stochastic layers distinct

For weights [1, -2], the L1 norm is 3 and the sum of squares is 5. Multiplying
the weights by two doubles the first quantity and quadruples the second.
This scaling difference helps explain why the two penalties impose different
preferences. The penalty used here is lambda times the sum of squares, so
its derivative is 2 lambda w. A convention with an extra one-half factor
would produce a different coefficient.

The training objective can include data loss plus regularization, while a
reported prediction metric may intentionally include only data loss. In the
fixture, data loss 2 and penalty0.5 give total objective2.5. State which
quantity is being compared across experiments; a lower penalized objective
and a lower held-out prediction error are different observations.

In inverted dropout with keep probability q, a retained activation is divided
by q and a dropped activation becomes zero. Its expectation matches the input,
but one realization need not drop exactly the requested fraction. At q=0.5,
an input of one produces either zero or two. Evaluation disables that sampling
and should return the unchanged activation for this layer.

Weight decay is an optimizer operation that must also be defined precisely.
For adaptive optimizers, adding a squared-weight penalty to the gradient and
decaying parameters separately generally produce different updates because
the adaptive scaling acts on different terms. Avoid treating every library
argument called regularization or decay as the same mathematical operation.""",
        """If a penalty gradient is off by a factor of two, check its defining
formula rather than changing a test tolerance. If evaluation varies across
identical inputs, inspect training mode and other stochastic operations.
For dropout, test allowed values and shape, not an exact randomly retained
count. Keep data-loss metrics separate from regularized training objectives.""",
    ),
    "tf-019": (
        """## Trace spatial sharing without losing the indexing convention

TensorFlow's convolution operation uses the common neural-network
cross-correlation convention: the supplied kernel is applied without the
spatial flip used in the mathematical definition of convolution. Flipping
the difference kernel therefore changes the sign of this fixture's result.
Write one window and its coefficient products before reasoning from a picture.

For valid padding, a spatial dimension with input length H, kernel length K,
stride S and unit dilation has output length floor((H-K)/S)+1. Dilation changes
the effective kernel size to 1+(K-1)D. Padding changes which locations are
available. A shape calculation should specify those choices instead of
assuming the output matches the input dimensions.

A kernel tensor shaped (kh, kw, Cin, Cout) contains kh×kw×Cin×Cout weights.
The lesson's 2×2, one-input-channel, two-output-channel construction has eight.
An explicit bias would add one parameter per output channel. Increasing
image height adds output positions and computation, but it does not create
a separate set of weights for every location.

Locality limits influence. A corner input pixel belongs to fewer valid
windows than an interior pixel, so changing one pixel need not change every
output. A zero-sum kernel is invariant to adding the same constant to every
value of a fully covered window. That argument needs care at zero-padded
boundaries, where padding values may not receive the same constant shift.""",
        """A sign reversal suggests a kernel-orientation mismatch. A wrong
output shape suggests padding, stride, dilation or channel-order assumptions.
Count weights from kernel dimensions and biases from the layer definition.
For an unexpected global effect from one pixel, inspect the exact windows
containing that pixel before assuming weight sharing means global mixing.""",
    ),
    "tf-020": (
        """## Ask what information a transformation discards

For the patch with values 1,3,2 and 4, max pooling returns 4 while average pooling
returns 2.5. Changing the smallest value from 1 to 0 leaves the maximum unchanged
but changes the average to 2.25. This is a direct demonstration of two different
summaries. Neither retains the full spatial arrangement or every input value.

The gradient consequences differ too. Away from ties, a maximum routes local
sensitivity through its maximizing input; an average distributes sensitivity
across the averaged positions. Tie behavior belongs to the particular
operation's definition and implementation. Pooling is therefore a modeling
choice about retained information, not a universal improvement over an
unpooled representation.

Augmentation introduces another assumption: the transformed example must
retain a valid target or receive the corresponding target transformation.
A horizontal flip can preserve an object category while changing a left/right
label. A segmentation mask or bounding box must be transformed consistently
with the image. Applying the same-looking transform to only the pixels can
create mislabeled supervision.

Keep the default evaluation representation fixed so repeated measurements
refer to the same task. Test-time augmentation is a separate inference policy
that needs its own aggregation rule and evaluation. An involution check,
such as flipping twice and recovering the original image, proves the transform's
mechanics; it does not prove that one flip preserves the label's meaning.""",
        """When an augmented model degrades, inspect a transformed input and
its target together. Distinguish information discarded by pooling from
incorrect labels introduced by augmentation. If a transform passes a
round-trip pixel check, still ask whether its intermediate image has the
same semantic target. Keep evaluation randomness explicit.""",
    ),
    "tf-021": (
        """## Padding is storage, not an observed target

Padding allows examples of different lengths to share one rectangular tensor.
It creates positions for storage and computation, not new observations.
If two valid token losses equal log(2) and a padded position has arbitrary
loss 100, the masked mean is still log(2). The numerator excludes the padding
loss and the denominator counts two active positions.

An embedding lookup maps token IDs to feature vectors. Reserving zero as a
padding ID is a vocabulary convention. Keras's mask-zero behavior propagates
mask information; it does not mean that every custom downstream operation
automatically ignores those positions or that row zero must be a zero vector.
Inspect mask handling at each custom layer or loss boundary.

Selecting a sequence summary also needs a length contract. The element at
length-1 is the last valid position only when valid tokens form a contiguous
prefix followed by right padding. If the mask can contain holes, count-minus-one
can select a padded position. Use the actual valid indices or reject layouts
outside the declared contract.

An entirely padded example has no active-token mean. Returning zero would
quietly change the objective and could make an empty batch look perfect.
Reject it or define an explicit exclusion policy with its own contributing
count. The same principle applies when instruction tuning excludes prompt
tokens from the loss while retaining them as visible context.""",
        """If appending padding changes a metric, inspect both masking and
the denominator. If summaries select a padding state, verify the right-padding
assumption. If a custom layer ignores a Keras mask, pass or apply the mask
deliberately instead of assuming embedding metadata changes arbitrary tensor
operations. Empty participation requires an explicit decision.""",
    ),
    "tf-022": (
        """## Normalize only over information the prediction may use

An attention row describes one query's distribution over permitted keys.
With zero scores and three keys, an unmasked softmax gives each key one-third.
If future weights are then zeroed without renormalization, the first causal
row has mass one-third and the second has mass two-thirds. The output has been
shrunk as well as restricted. Masking scores before normalization instead
produces a proper distribution over the remaining legal positions.

The score matrix has query positions on one axis and key positions on the
other. Its multiplication by values contracts the key axis. Confusing that
axis with feature width can still produce plausible-looking numbers when
small dimensions happen to coincide. Keep dimensions distinct in at least
one diagnostic fixture and check every output shape.

Prefix invariance is an end-to-end causality property. Recomputing a prefix
alone should agree with the corresponding early outputs of the full sequence
when weights, positions and evaluation behavior are unchanged. Perturbing a
future value is a useful negative control, but attention is not the only
possible leakage path: an upstream reduction across time can also change
an earlier query or key.

A row with no permitted keys has no normalized attention distribution under
this contract. Reject it instead of converting undefined arithmetic into a
uniform distribution. Check the mask convention of the exact API you call;
some boolean masks identify permitted positions while others identify
positions to block.""",
        """Inspect row sums immediately after the mask operation. If early
outputs change with future data, test the attention layer and its upstream
normalization separately. Use nonuniform scores to expose ignored queries
or keys, and unequal axis lengths to expose transposition mistakes. Reject
all-masked rows before exponentiation can produce NaNs.""",
    ),
    "tf-023": (
        """## Differentiate a missing path from a stationary point

Automatic differentiation follows recorded tensor operations. Converting an
intermediate to a NumPy value or constructing a new constant can disconnect
that recorded path even when the intended mathematical expression depends
on the parameter. A None gradient means the tape did not return that
connection. A tensor containing zero is a different result: the recorded
derivative can be zero at the evaluated point.

For the scalar squared-loss fixture, the update with learning rate 0.1
contracts the residual w-2 by a factor of 1/15 on each full-batch step.
Starting from zero gives \\(w_1=\\frac{28}{15}\\) and \\(w_2=\\frac{448}{225}\\). The squared residual, and
therefore this fixed-batch loss, contracts by 1/225 per step. These exact
relationships provide a way to locate the first incorrect update without
guessing from a final training curve.

The tape normally watches accessed trainable Variables. Differentiating with
respect to an ordinary input tensor may require explicitly watching it.
A nonpersistent tape is intended for one gradient extraction; retaining a
tape for repeated derivatives has a different lifetime and memory cost.
Treat those choices as part of the loop's state contract.

Check loss and gradient finiteness before assignment. Updating a weight with
an invalid gradient can contaminate later predictions and optimizer state,
making the first failure harder to locate. Recompute the post-update loss
after the assignment; printing an earlier tensor does not measure the new
parameter state.""",
        """When a gradient is None, inspect tape scope, watched objects and
NumPy/constant conversions before replacing anything with zeros. When it is
zero, inspect the evaluated point and local derivative. For a wrong second
step, verify that the gradient used the updated weight and that the reported
loss was recomputed after assignment.""",
    ),
    "tf-024": (
        """## Read the classifier as an experiment

The training inputs [-2, -1, 1, 2] have mean zero and population standard
deviation sqrt(2.5). Those training statistics define the transformation used
for every later record. Keeping a held-out record's original ID alongside its
transformed value lets you check both the numerical operation and the
information boundary. The two checks answer different questions.

The supplied training loop has a fixed budget of 40 updates. Its purpose is
to demonstrate a complete small experiment with a baseline, a fitted model
and an assessment on two reserved rows. One true positive and one true
negative give accuracy 2/2 on those rows. A constant predictor makes one
mistake. This establishes the observed comparison, with a denominator of two;
it does not establish a narrow population error bound or calibrated scores.

Classification accuracy and cross entropy can tell different stories even
on the same records. Once two logits fall on the correct sides of zero,
their classifications may stop changing while their probabilities and losses
continue to change. On perfectly separable data, unregularized logistic
training can keep increasing coefficient magnitudes to reduce cross entropy
without improving already perfect training accuracy. A fixed update budget
is therefore part of the experiment, not just a convenience for the worker.

Inspect false positives and false negatives separately when the downstream
costs differ. Keep any subgroup denominator beside its metric, including
groups with no observations. Use validation data for threshold or architecture
selection; preserve a separate final assessment if those choices are tuned.
This tiny capstone makes the bookkeeping visible before a larger dataset
makes accidental leakage harder to see.""",
        """If training improves but held-out decisions do not, inspect the
train-only transform and the ID join before changing model capacity. If
accuracy stays fixed while loss moves, inspect logits rather than assuming
the optimizer stopped. Report the two-row assessment as two observed cases;
do not turn the exact fixture result into a population guarantee.""",
    ),
    "tf-025": (
        """## Similarity is a modeling decision

For anchor [1, 0] and positive [1, 1], the dot product is 1 and cosine is
1/sqrt(2). Multiplying the positive by ten raises the dot product to 10
while leaving its direction, and therefore its cosine, unchanged. A retrieval
system using dot products can prefer a large-norm candidate for a reason
that cosine deliberately removes. Neither score is automatically correct;
the choice should match the training objective and intended use.

With candidate scores [1, 0] and the first candidate designated positive,
the two-candidate cross entropy is log(1 + exp(-1)). Dividing scores by a
positive temperature changes the probability gap. Temperature 0.5 produces
scores [2, 0] and a smaller loss for this already correctly ranked pair.
The ordering is unchanged, but the derivative with respect to each original
score contains a factor of one over temperature. Temperature changes both
the probabilities and the gradient scale.

A negative is a sampling claim, not a fact inferred from a different row
position. If the negative is another copy of the positive, the model receives
contradictory supervision. Compare canonical identities before constructing
the candidate set. Identity checks catch known duplicates; two distinct
documents can still express the same meaning, so the broader false-negative
problem requires examining the sampling policy and data.

Cosine is undefined for a zero vector because its denominator vanishes.
Adding an epsilon silently chooses a different behavior near zero. This
lesson rejects zero norms explicitly. For a larger system, document how
empty, failed or near-zero representations are handled and count them in
evaluation instead of dropping them from the reported denominator.""",
        """If rankings change after positive rescaling, first check whether
the intended score was dot product or cosine. If contrastive loss looks
reasonable but duplicate candidates disagree, inspect the identity policy.
Check temperature before comparing losses across runs, and reject an undefined
cosine instead of treating a finite replacement value as ordinary evidence.""",
    ),
    "tf-026": (
        """## Separate persistent state from each forward calculation

The residual layer computes \\(Y=X+XW\\). For a feature width D, its square
kernel has D squared scalar parameters. At W = 0 it is exactly the identity;
at W = I it doubles every input. These two states are useful independent
oracles because neither requires trusting the layer's implementation.

If the loss is the sum of all output elements, the derivative of that loss
with respect to W is X transposed times an all-ones matrix of output shape.
For X with rows [1, 2] and [3, 4], the gradient is [[4, 4], [6, 6]]. The
skip connection contributes to the input gradient but introduces no extra
kernel parameter. A zero initial kernel can therefore still receive a
nonzero gradient and learn a residual correction.

Weights belong to the layer's persistent state. In this shape-dependent
example, build creates the kernel through add_weight after the feature width
is known; call reuses it for each batch. Calling the same layer twice should
leave both the number and identity of its variables unchanged. Two equal
output tensors are a weaker check: a broken implementation could recreate
the same zero kernel on every call and appear correct until training begins.

A residual addition also commits to compatible shapes. If a transformation
changes feature width, a deliberate projection is needed on the skip path
or the architecture must reject the mismatch. Accidental broadcasting is
not a substitute for that design decision. The
[Keras layer contract](https://www.tensorflow.org/api_docs/python/tf/keras/Layer)
describes tracked trainable and nontrainable state; the fixture checks the
particular square-kernel contract used here.""",
        """Count variables and compare their identities across repeated calls.
If they grow, inspect state creation in call. If the initial output is wrong,
check the zero-kernel identity before debugging training. If the gradient is
wrong, derive X transposed times ones independently and inspect the reduction
axes. Reject a new feature width with a clear contract error.""",
    ),
    "tf-027": (
        """## Freezing answers which state may change

This lesson's local base is an identity transformation chosen for inspection.
It has not learned reusable features from a large external dataset. Freezing
it demonstrates parameter selection and state boundaries, not the empirical
benefit of pretrained representations. A real transfer-learning claim would
need a documented source model, suitable target data and a comparison against
training from scratch or a simpler baseline.

During head-only training, the optimizer should receive the head's selected
variables. Check the base weights before and after an update, and separately
check that the head changed. A falling loss is insufficient: the model could
improve by changing a base that was supposed to remain fixed.

Unfreezing creates a new optimization phase. The optimizer must know about
the newly trainable variables and any state it maintains for them. With Keras
fit, changing trainable flags calls for recompilation so the training setup
reflects the new set. Decide whether to carry or restart optimizer state and
record the learning rate for the new phase. Those choices change the next
updates even when the initial weights are identical.

Trainability and forward-pass mode are separate concepts. Dropout changes
its behavior with training mode despite having no learned kernel. Batch
normalization has trainable affine parameters and moving statistics; its
Keras-specific frozen behavior also needs attention during fine-tuning.
Read the [Keras transfer-learning guide](https://keras.io/guides/transfer_learning/)
before adapting that layer. State which parameters and buffers may change
instead of using the word frozen as an ambiguous promise about all behavior.""",
        """Compare snapshots of the base and head separately. If an unfrozen
variable never changes, inspect the optimizer's variable set and compilation
boundary. If weights stay fixed but outputs vary, inspect dropout, batch
statistics and evaluation mode. Keep the identity-base demonstration separate
from claims about useful pretrained features.""",
    ),
    "tf-028": (
        """## A restart is a claim about the next operation

Equal model weights do not imply equal training state. Consider a momentum
rule \\(v_{\\mathrm{next}}=0.9v+g\\) and \\(w_{\\mathrm{next}}=w-0.1v_{\\mathrm{next}}\\). At the same w and gradient
g = 2, a saved velocity of 1 gives a step of 0.29; a reset velocity of zero
gives a step of 0.2. Adam uses different moment equations, but the same
principle applies: history affects the next update.

The fixture takes two updates before saving, so its Adam moments and update
counter contain nontrivial information. It then computes an uninterrupted
third step as a control. A fresh process constructs new objects, restores
the checkpoint and takes that same third step on the same batch. Comparing
the resulting weight and iteration counter tests continuation behavior.
Merely finding a checkpoint file, or restoring into still-live objects,
would provide weaker evidence.

The restore contract includes model variables and optimizer variables. Slots
must exist under the expected structure for a strict consumed-state check to
be meaningful. A weights-only negative control deliberately loses the Adam
history and should disagree with the uninterrupted control on this fixture.
That disagreement demonstrates why a model file and a training checkpoint
serve different purposes.

The exact continuation state depends on the training process. A shuffled
iterator, stochastic augmentation, random generator, learning-rate schedule
or gradient accumulator adds state beyond this fixed-batch example. The
lesson establishes one bounded CPU continuation with a declared tolerance;
it does not establish exact reproduction across devices or framework
versions. List the state required for the particular next operation you
intend to reproduce.""",
        """When restored predictions match but the next update differs, inspect
optimizer moments and the iteration counter before widening tolerance. If
the fixed-batch proof passes but a larger job diverges, inspect data order,
random generators, schedules and partially accumulated gradients. Keep the
fresh-process control and the weights-only failure case together.""",
    ),
    "tf-029": (
        """## Stable algebra and sufficient precision solve different problems

For logits z, log-sum-exp can be evaluated as m + log(sum(exp(z - m))),
where m is the largest logit. The exponentials then have nonpositive inputs,
avoiding overflow from unnecessarily large intermediate exponentials. For
logits [1000, 1001] with the second class correct, the loss is
log(1 + exp(-1)), about 0.3133. Computing exp(1001) first is unnecessary.

Softmax probabilities are mathematically unchanged by adding one common
constant to all logits. Floating-point computation has another boundary:
if a low-precision representation rounds two distinct logits to the same
stored number, subtracting the maximum cannot recover their lost difference.
Test shift invariance only where the chosen dtype still represents the
relevant differences. A stable operation is not a repair for already
corrupted inputs.

Float16 has a much narrower representable range than float32. Squaring a
representable input can overflow, and a small gradient can round to zero.
Mixed precision deliberately assigns different dtypes to suitable operations
and state. Loss scaling multiplies the loss before differentiation to help
represent small gradients, then removes that scale before an ordinary
optimizer update. If clipping is part of a custom implementation, it must
operate under the intended unscaled-gradient convention. Otherwise changing
the scale also changes the effective clipping threshold.

The [TensorFlow mixed-precision guide](https://www.tensorflow.org/guide/mixed_precision)
explains the framework mechanism. This CPU lesson demonstrates numerical
boundaries and stable formulas. It does not benchmark accelerator speedups
or claim that lower precision is beneficial for every operator or dataset.
Inspect forward values and gradients separately when diagnosing precision.""",
        """Locate the first nonfinite intermediate, then distinguish overflow
from a loss of small differences. Compare a stable float32 calculation with
the same input before any low-precision cast. If gradients are finite but
updates depend unexpectedly on loss scale, inspect unscaling and clipping.
Do not replace NaNs with zeros and call the training result repaired.""",
    ),
    "tf-030": (
        """## Derive the global objective before combining workers

For N examples, an example-weighted objective is the sum of individual losses
divided by N, plus any separately defined regularization term. A shard with
one example and mean gradient 2 contributes numerator 2. A shard with three
examples and mean gradient 6 contributes numerator 18. The combined gradient
is (2 + 18)/4 = 5. Averaging the two means gives 4 and silently assigns more
weight to each example in the smaller shard.

Microbatch accumulation follows the same arithmetic. Hold the parameters
fixed while computing gradient sums for all contributing microbatches, add
the sums and divide by the total count before one update. Applying an update
after the first microbatch changes the parameters at which the second
gradient is evaluated. That creates a different optimization trajectory,
even if the final reporting denominator is correct.

An empty shard contributes a zero numerator and count zero. Its local mean
is undefined, so forming that mean and multiplying a NaN by zero is not a
valid repair. If every shard is empty, there is no example mean at all.
Similarly, a token-weighted objective uses the number of participating tokens,
not automatically the number of sequences. Choose the unit before reduction.

Regularization needs its own scaling convention. If the intended global
objective adds lambda times R(w) once, adding that full term on every shard
and summing multiplies it by the number of shards. TensorFlow documents
[global loss and regularization scaling](https://www.tensorflow.org/tutorials/distribute/custom_training)
for distributed custom loops. This lesson verifies the arithmetic on one
CPU. Communication, device placement and distributed failure recovery need
separate runtime evidence.""",
        """Write each numerator and its contributing count before inspecting
an average. Unequal and empty shards expose assumptions that equal-sized
batches conceal. If accumulated and full-batch updates disagree, check whether
weights moved during accumulation, whether regularization was duplicated,
and whether the denominator counts examples or active tokens.""",
    ),
    "tf-032": (
        """## Save the object needed by the next consumer

A .keras archive is intended to reconstruct a Keras model with its saved
configuration and state. A SavedModel inference export exposes a callable
endpoint with an input/output contract. These are different consumers and
different restoration paths. Loading an inference endpoint does not by itself
reconstruct the optimizer and full training workflow.

In the fixture, retain the object returned by tf.saved_model.load while
using its serve endpoint. Treating the endpoint as an unrelated function
and discarding its owning module can lose the lifetime of captured variables.
The fresh-process comparison checks that the reconstructed owner and callable
actually produce the expected values without relying on the original model
remaining in memory.

A dynamic batch dimension means the endpoint can accept different numbers
of rows under its signature. It does not make the feature width arbitrary.
The one-feature model must still receive width one and the declared dtype.
For a larger model, feature order and units are semantic parts of the contract
too: swapping two columns of the same shape can change predictions without
producing a shape error. Keep that schema beside the model artifact.

Check parity on several deliberately different inputs, including more than
one batch size, and reject incompatible inputs explicitly. A content hash
identifies bytes; a parity check examines behavior on its probes. Neither
alone establishes generalization or compatibility with an untested runtime.
See the [Keras saving guide](https://keras.io/guides/serialization_and_saving/)
and [inference export contract](https://keras.io/api/models/model_saving_apis/export/)
for the separate APIs used by these consumers.""",
        """If reloading succeeds but calling the endpoint fails, retain the
loaded module and inspect its actual signature. If numerical parity fails,
check feature order, dtype, preprocessing and training mode. Do not infer
training-resume support from a successful inference export, or accept a
different feature width merely because batch length is dynamic.""",
    ),
    "tf-033": (
        """## Turn a tensor function into an explicit prediction contract

An inference boundary defines what callers may submit before the model
executes. The lesson checks rank, feature width, dtype, finite values and a
bounded batch size. Each condition prevents a different ambiguity: a flat
vector lacks an explicit batch axis, a different width changes the feature
schema, and NaNs can propagate through otherwise valid matrix operations.
Validate the whole request before publishing a partial result.

Shape alone does not encode meaning. Two columns representing age in years
and income in dollars cannot be swapped merely because both are float32.
Changing dollars to thousands of dollars also preserves shape while changing
the numerical problem. Store feature names, order, units and preprocessing
version with the model's input contract.

The fixture's fixed stateless model predicts each row independently. Its
result for a batch should match concatenated results for the same rows split
into smaller batches, within the declared tolerance. This is a useful
metamorphic check because it changes execution grouping without changing
the intended examples. It is not a universal property of every network:
training-mode batch normalization, stochastic layers or cross-example
operations can make a row depend on its neighbors.

The input array should remain unchanged after prediction. Mutating a caller's
buffer during normalization can make repeated requests behave differently
or contaminate another consumer. Compare a before/after copy in this bounded
fixture. Request validation and deterministic batching establish this local
function contract; a deployed service additionally needs measured capacity,
concurrency, lifecycle and operational behavior.""",
        """A batch-versus-singleton mismatch first calls for checking model
mode and cross-example operations. A repeated-call mismatch calls for checking
input mutation and hidden state. Reject invalid rank, width or nonfinite
values at the named boundary so the learner sees the violated contract,
not a later opaque matrix-multiplication exception.""",
    ),
    "tf-034": (
        """## Robustness needs a unit, a denominator and a failure policy

In the supplied group ledger, group A has one success among two records and
group B has zero among one. Those are observed fractions with denominators
2 and 1. They do not support precise comparisons of underlying population
rates. An absent group has no observed denominator; its result is unknown,
not zero percent or one hundred percent.

Duplicates can make the apparent sample size larger than the information
content. Eight rows representing three unique identities provide eight row
observations but only three identity units under an identity-level analysis.
Choose the unit that matches the decision. When repeated records from one
identity share errors, treating them as independent can understate uncertainty.
Report both row counts and unique-ID counts when both matter.

A perturbation test asks whether behavior changes under a specific input
change. The target must remain valid, or be transformed consistently. An
image flip may preserve an object category but reverse a left/right label;
a text rewrite can accidentally change a negation. Mechanical success of a
transformation does not establish semantic equivalence. Keep the assumption
beside each test case.

Average pass rate and severity are different summaries. Nine passing cases
out of ten give 90 percent, but one severe failure can still block a release
under the stated policy. Preserve the failure description and affected unit
instead of letting an aggregate erase it. Likewise, duplicate and exposure
checks are useful privacy controls, but passing a small checklist is not a
proof of privacy or a substitute for a defined threat model.""",
        """If a percentage looks surprisingly stable, inspect duplicate
identities and subgroup denominators. If an empty group displays a numeric
rate, inspect the missing-data policy. For perturbation failures, check that
the transformation preserved the intended target before calling the model
nonrobust. Keep severe individual failures visible beside aggregate scores.""",
    ),
    "tf-035": (
        """## Compare predictions on the same observational units

The fixture aligns both models to the same three IDs before comparing their
errors. Its paired error differences are [-1, 0, -1], with mean -2/3 under
the declared subtraction convention. A negative difference favors the
candidate in that convention. Write the sign rule beside the statistic so a
better score cannot be mistaken for a worse one.

Resampling this vector keeps the comparison paired: each selected unit brings
both models' outcomes together. Independently resampling the two error lists
would break their covariance and answer a different uncertainty question.
If units are clustered by customer or document family, resample at the
appropriate independent-unit level rather than automatically treating every
row as an independent draw.

The fixed random seed makes the resampling calculation repeatable. It does
not make three observations representative, create additional independent
data or remove uncertainty about deployment conditions. Repeated bootstrap
draws reuse the same three pieces of observed information. Report that small
sample size and the attainable distribution alongside any interval.

Require the full expected ID set before comparing scores. An inner join that
silently drops missing candidate predictions can make a failing model look
better. Decide how missing predictions count and report them. Use validation
comparisons for selection, then assess the selected configuration on a
preserved final test. If the final test drives another choice, it has become
part of selection and cannot remain an untouched final assessment.""",
        """For a suspicious improvement, verify the ID sets and subtraction
direction first. For an implausibly narrow interval, inspect the independent
unit and whether paired errors were separated. Reproducing a seeded vector
checks computation, not sampling validity. Record missing predictions rather
than dropping them through an inner join.""",
    ),
    "tf-036": (
        """## Make a release decision reconstructible

The capstone's weight vector [2, -1] and ordered input [3, 4] produce 2.
Swapping those inputs produces 5. Both arrays have the same shape and dtype,
so the fixed probe connects feature order to behavior in a way that a file
existence check cannot. A release bundle needs the schema and preprocessing
contract as well as model bytes.

Canonical serialization gives a stable byte representation for the split
manifest. A SHA256 digest then changes when a recorded ID changes. This
detects an identity change relative to an expected digest; it does not prove
that the split was independent or that its author is trusted. Keep the
actual disjointness check, grouping rule and provenance beside the digest.

Required gates have three meaningful states: passed, failed and unexecuted.
The fixture accepts only literal True for each required gate, so an unknown
restart proof does not become an implicit pass. A recorded boolean should
point to the observation that supports it. Prediction parity, a fresh-process
restart and a schema check are separate pieces of evidence, not interchangeable
labels for one successful run.

Retain the previous artifact and the input contract needed to use it when
recording a rollback path. An artifact name without recoverable bytes and
compatible preprocessing is not a demonstrated rollback. The final record
also preserves the two-row holdout count and synthetic-fixture limitation.
A no-go decision is a successful application of the lesson when required
evidence is absent or a gate fails. The next step is to obtain the missing
evidence or repair the failed contract, then reassess the complete bundle.""",
        """If all gates appear green, check that each has an actual receipt
for the candidate bytes. If a schema-valid request predicts incorrectly,
inspect feature order and units. If rollback is claimed, identify the retained
artifact and compatible transformation. Keep unknown evidence distinct from
failure, while letting either block a required release gate.""",
    ),
}

DEPTH_NOTES = {identity: review[0].strip() for identity, review in REVIEWS.items()}
DIAGNOSIS_NOTES = {identity: review[1].strip() for identity, review in REVIEWS.items()}
