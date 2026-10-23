"""Explicit advanced PyTorch depth additions; executable specifications stay unchanged."""

# Long lines preserve authored Markdown paragraphs and tables.
# ruff: noqa: E501
from __future__ import annotations

from collections.abc import Callable

ReviewWriter = Callable[[int, list[str], str, str, str], None]


def add_advanced_reviews(add_review: ReviewWriter) -> None:
    add_review(
        19,
        [
            "Output-size, dilation and parameter-sharing rules lacked a symbolic shape derivation.",
            "The forward patch example did not explain how shared kernel and input gradients accumulate.",
            "Semantic layout conversion, memory format and translation equivariance needed separate contracts.",
        ],
        """Choose convolution when local structure and reuse of the same learned rule across positions are useful assumptions for the task. Decide the channel convention, boundary padding, stride and receptive-field growth before choosing a filter count. Weight sharing reduces parameters; it does not prove that a particular learned filter is useful or that the whole network is translation-invariant.

For a framework comparison, match the mathematical kernel and input axes before comparing values. Keep the literal ramp fixture as an arithmetic oracle, then use a nonuniform changed pixel to test locality. The CPU example establishes those small computations. It does not measure accelerator throughput or train an image classifier.""",
        """## Derive the spatial map and its backward accumulation

Write a PyTorch image as X with shape(N,C_in,H,W) and a grouped Conv2d kernel as K with shape(C_out,C_in/g,k_H,k_W), where g is groups. For the ordinary g=1 case, each output channel sums over every input channel and one spatial patch. With stride s, symmetric numeric padding p and dilation d on one axis, the effective kernel width is k_eff=d(k-1)+1 and the output width is floor((W+2p-k_eff)/s)+1. Apply the same calculation independently to height. This is a count of valid kernel-start positions, not a statement that the image has been resized. [PyTorch2.9 Conv2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Conv2d.html).

For W=H=3,k=2,d=1,p=0,s=1, there are two starts on each axis. The tensor shape is therefore(1,1,2,2). At the top-left start, the dot product is1×1+2×0+4×0+5×(-1)=-4. At the top-right start it is2-6=-4. Equal outputs follow from this ramp and this kernel, not from a rule that every convolution outputs a constant. Stride2 keeps only the start at zero and produces(1,1,1,1).

Parameter count and evaluated output count are different. With two output channels, one input channel, a2×2 kernel and no bias, there are2×1×2×2=8 learned scalars regardless of spatial image size. Enabling bias adds one scalar per output channel, not one per output pixel. The same coefficient participates in multiple local dot products, so its gradient must accumulate contributions from all positions where it was used.

A separate analytic backward trace makes that sharing explicit. Suppose L is the sum of the four output values, so every upstream output derivative is one. Each kernel derivative is the sum of the corresponding input positions across the four patches:

| Kernel entry | Input values contributing | dL/dK |
| --- | --- | --- |
| top-left | 1,2,4,5 | 12 |
| top-right | 2,3,5,6 | 16 |
| bottom-left | 4,5,7,8 | 24 |
| bottom-right | 5,6,8,9 | 28 |

The input gradient, using the original kernel, is[[1,1,0],[1,0,-1],[0,-1,-1]]. The center pixel participates in four patches, but its+1 and-1 contributions cancel while the other two coefficients are zero. A zero derivative at that pixel is therefore not a disconnected graph. Adding a trainable bias would give bias gradient four for this summed loss. These derivatives are an analytic extension of the fixture; the unchanged worked blocks test forward values and do not enable input/kernel autograd themselves.

Receptive fields grow through compositions. Start with jump j=1 and field size r=1. A layer updates r to r+(k_eff-1)j and j to js. Two stride-one2×2 layers have a3×3 receptive field, not4×4. If the first2×2 layer has stride2, the second stride-one2×2 layer sees a4×4 input field because its adjacent inputs are already two original pixels apart. Padding affects which positions refer to actual data at the boundary.

Layout conversion must preserve these meanings. NCHW to NHWC uses permutation(0,2,3,1); the inverse is(0,3,1,2). A TensorFlow HWIO kernel becomes PyTorch OIHW with permutation(3,2,0,1) for this ordinary convolution. A reshape with the same element count can produce legal dimensions while pairing the wrong channels or pixels. PyTorch channels_last memory format is yet another concept: it can change strides while the public tensor shape still uses NCHW semantics.

Both frameworks perform cross-correlation here. Rotating the asymmetric kernel changes the output to+4. A symmetric kernel could hide an accidental rotation; the asymmetric fixture exposes it. Weight sharing gives an equivariance relationship under suitable shifts and boundary assumptions, not unconditional invariance. Stride, padding and later reductions can break a simple shift correspondence. Likewise, the zero-sum kernel ignores a constant image offset on these VALID patches, but zero padding at edges or a different learned kernel changes that statement.""",
        """If output dimensions differ, write the effective kernel and start-position count for each axis before changing tensor layout. If the shape agrees but values differ, calculate one patch with channel indices visible and check whether the kernel was rotated. If a TensorFlow comparison fails, verify both image and kernel permutations and the dtype before adjusting tolerances.

If a gradient differs by the number of positions, inspect whether shared contributions were summed or averaged by the loss. If only a center-pixel gradient is zero, check cancellation before diagnosing disconnection. A single changed corner pixel should influence only the outputs whose receptive fields include it. Keep stride, boundary and layout mistakes distinct: all can produce an accepted tensor operation with the wrong semantic result.""",
    )
    add_review(
        20,
        [
            "Pooling information loss needed a backward-sensitivity trace and boundary counterexamples.",
            "A flip round trip was not distinguished fully from a valid target transformation.",
            "Pooling defaults and ownership of deterministic evaluation outputs needed explicit decisions.",
        ],
        """Choose a pooling rule according to which information the next stage should retain. Maximum and average pooling can have the same output shape while preserving different evidence and sending gradients through different input positions. Decide window, stride and padding explicitly when comparing frameworks.

Choose an augmentation only after specifying how every target changes. Classification may justify an invariant label, while direction, coordinates, segmentation masks or bounding boxes often require a corresponding target transform. Keep evaluation deterministic under its declared policy and preserve the exercise's owned-output contract separately from value equality.""",
        """## Trace discarded information, gradients and target semantics

For the patch[[1,3],[2,4]], max pooling returns4 and average pooling returns(1+3+2+4)/4=2.5. Now change only the first entry from1 to0. The maximum stays4, while the average becomes9/4=2.25. The two maps are therefore not interchangeable summaries even though both return one number. Many different patches share the same maximum, so no later layer can reconstruct all discarded values from that output alone.

Consider an upstream derivative g=1 for this one pooled output. With a unique maximum, the max-pool backward route sends one to the selected4 and zero to the other positions. Average pooling sends1/4 to every entry. This explains the perturbation result locally: a small change to the nonmaximum1 has zero first-order effect on the max but a quarter-sized effect on the average. Raising3 past4 changes the selected maximum, so the derivative route changes at that boundary. At a tie there is no unique ordinary derivative of the max function; do not assume gradients are split equally or use a tied point as a smooth finite-difference oracle.

The worked call uses kernel_size2 and the default stride equal to the kernel size. With overlapping windows, one input can receive contributions from several pooled outputs, so its final gradient sums those routes. Pooling itself has no learned kernel coefficients in these examples. Its effect on training is through the information and derivatives it passes to learned layers.

Padding conventions matter on negative inputs. PyTorch max pooling uses implicit negative infinity for its padding, so a padded location cannot defeat a valid negative maximum. Replacing that with ordinary zero padding would make a patch of negative responses appear to contain a larger zero. For average pooling, count_include_pad and any divisor override affect the denominator near boundaries. The paired TensorFlow worked example uses VALID padding, so none of those boundary differences is exercised there. Match explicit conventions before claiming a padded cross-framework equivalence. [PyTorch2.9 MaxPool2d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MaxPool2d.html).

A local pool can be invariant to permutations inside one fixed window, but shifting an image can move values between windows. Max pooling is not a general guarantee that the complete model ignores translations. Stride and window boundaries can discard small features or alias a pattern. Whether that tradeoff helps depends on the task and the downstream representation, not only the smaller tensor shape.

The horizontal flip reverses the width axis, which is the final axis in this NCHW fixture. Applying it twice restores the original pixel arrangement. That proves an involution of indices. It does not prove that the intermediate image retains its label. If the target is a direction, the full transform is(image,label)→(flipped_image,opposite_direction), and applying that full transform twice restores both components. Keeping left while reversing the arrow would manufacture an inconsistent training example.

The same reasoning extends to structured targets. A segmentation mask must use the same geometric transform as its image. A box or keypoint needs its coordinates transformed under the declared origin and pixel convention. A crop can remove the evidence needed for a classification label. A library offering the operation says nothing about whether these task assumptions hold. When augmented siblings come from one original source, keep their family inside the intended training/evaluation split; otherwise a visually altered duplicate can leak source information across the split.

The evaluation exercise adds an ownership promise: return equal values in an independent tensor, so a caller's later mutation cannot alter the source. An identity-valued alias would pass a value comparison and fail that ownership contract. In PyTorch, clone is the relevant explicit storage operation here. TensorFlow's ordinary immutable tensor API has different mutation semantics, so do not infer the same storage promise merely from the paired chapter's identity-valued transformation.

Random training augmentation, when introduced, belongs to the experiment's RNG state. A seeded CPU demonstration is useful reproducibility evidence within its declared environment, not a universal promise of identical random transforms across platforms. Test semantic and geometric invariants and keep the actual sample/seed configuration with the run. Evaluation variation should be intentional and separately described, not accidental training-mode behavior.""",
        """When a pooling result is unexpected, inspect the window coordinates, stride and denominator before changing a model. On negative border values, check whether padding introduced zero where max pooling expected negative infinity. When a gradient differs only at a tied maximum, move to a unique-maximum fixture or explain the nonsmooth convention.

When augmentation improves a score suspiciously, inspect source-family leakage and whether labels were transformed consistently. A flip round trip only verifies indexing. For an evaluation-output ownership test, mutate the returned tensor and verify the source remains unchanged; equality before mutation cannot establish that. Keep geometry, target semantics, randomness and storage ownership as four separate checks.""",
    )
    add_review(
        21,
        [
            "Embedding lookup gradients and padding semantics needed an exact row-by-row trace.",
            "Packed recurrent output, final-state axes and the detached worked-example boundary needed explanation.",
            "Zero padding, mask propagation and valid-token versus per-sequence objectives were conflated by insufficient detail.",
        ],
        """Use explicit lengths or masks whenever storage contains artificial positions. Choose whether the objective weights valid tokens equally or weights sequences equally, because unequal sequence lengths make those different learning problems. A reserved padding ID is a vocabulary policy, not a value inferred from an embedding's magnitude.

Use packing for the supported recurrent valid-prefix contract, or an explicit masked recurrent design when lengths do not describe the data. Keep integer token IDs, floating features, Boolean masks and CPU length tensors in their distinct roles. The fixed GRU fixture compares state semantics; it is not an end-to-end trained language model.""",
        """## Follow lookup, recurrent state and loss participation separately

The embedding table has shape(V,D)=(4,2). IDs shaped(B,T)=(1,3) select rows and produce values shaped(B,T,D)=(1,3,2). The mask has shape(1,3), and the length vector has one entry per sequence, shape(1). IDs[2,3,0] select[2,2],[3,-1],[0,0], while the vocabulary rule marks only the first two positions valid. A genuine token could have a zero vector, so vector magnitude cannot replace that rule.

ExampleB differentiates the sum of all lookup outputs. Each used nonpadding row receives the sum of upstream vectors for its occurrences. Here rows2 and3 each receive[1,1], unused row1 receives zero, and padding row0 receives zero from the lookup backward rule. If ID2 appeared twice, its dense gradient contribution would be[2,2]. Token indices themselves are discrete selectors, not floating parameters to differentiate through. [PyTorch2.9 Embedding](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Embedding.html).

padding_idx controls the embedding operation's gradient contribution. It does not automatically propagate a mask through a GRU, initialize every supplied pretrained padding row to zero, or protect a row from explicit mutation. Optimizer-wide operations such as decay on a nonzero row are a separate state/update question. The worked table deliberately supplies a zero padding row and performs no optimizer step, so its actual evidence is the stated gradient pattern. Keras mask_zero=True instead creates mask metadata for compatible consumers; that is not a mechanical synonym for PyTorch's padding-gradient rule.

With batch_first=True, the un-packed GRU input uses(B,T,D). Its final hidden state still uses(num_layers×directions,B,H), so the one-layer unidirectional fixture returns(1,1,2). batch_first does not reorder the hidden-state axes. A bidirectional final-state tensor has two directional entries per layer and cannot be replaced casually by the last padded output row. PackedSequence also carries ordering/length bookkeeping; enforce_sorted=False avoids requiring the caller to sort this tiny batch manually. Lengths describe positive valid prefixes and are supplied on CPU for this interface.

Why does a zero padding vector still change a recurrent state? A recurrent step includes the previous hidden state and biases. For a GRU, write r and z for reset/update gates, n for the candidate, and h_new=(1-z)n+z h_old. Even when x=0, the recurrent affine terms and biases can make r,z,n nontrivial. The padded third step is therefore another computation, not an identity operation.

The fixed parameters make a compact analytic trace possible because both hidden coordinates remain equal. Let h denote either coordinate and let u be the sum of the two input features. With all weights and both bias vectors equal to0.1, the gates are r=z=sigmoid(0.1u+0.2h+0.2), the candidate is tanh(0.1u+0.1+r(0.2h+0.1)), and the next coordinate is(1-z)n+zh. Starting at h=0, the inputs have u=4,2,0. The first two steps give the valid-prefix state; the third changes it even though u=0. Packing with length2 omits that third transition, which is why the packed and prefix states match while the full padded run differs.

ExampleC uses values.detach(). That explicitly disconnects the GRU comparison from the embedding graph whose backward was already exercised in ExampleB. It still permits gradients with respect to GRU parameters in an ordinary differentiable forward, but this fixture does not call a GRU backward or update them. Do not interpret matching packed/prefix forward states as evidence that an entire embedding-plus-GRU training graph was tested. In a fresh end-to-end training step, use a fresh lookup graph and preserve the intended gradient path instead of detaching it accidentally.

The masked token objective is L=(sum over b,t of m_bt×loss_bt)/(sum over b,t of m_bt). The two valid log2 terms give numerator2log2 and denominator2, so the mean is log2. Dividing by padded width3 gives2log2/3 and changes the scale whenever padding is appended. For this mean, the derivative with respect to each valid loss is1/2 and the padding loss derivative is zero. An all-padding batch has no valid denominator and needs an explicit refusal or skip policy.

A per-sequence mean followed by averaging sequences is a different objective when lengths differ. A sequence with one token and one with nine tokens each receive half the weight under that policy, whereas a global token mean assigns one-tenth versus nine-tenths. Decide the statistical unit before implementing accumulation or batching. Keras mask propagation can help layers ignore padding, but it does not remove the need to inspect the objective's actual numerator and denominator.""",
        """If a final state changes when padding is appended, inspect packing/lengths and whether a recurrent layer processed the artificial tail. A zero embedding is insufficient when biases and hidden recurrence remain active. If hidden-state dimensions seem transposed, remember that batch_first changes input/output layout but not the final-state axis convention.

If the padding row has a lookup gradient, verify padding_idx and the actual ID convention. If a row changes despite zero lookup contribution, inspect optimizer decay, retained optimizer state and explicit writes separately. If embedding gradients disappear during recurrent training, locate detach/no_grad boundaries and compare with the deliberately detached worked comparison. If a masked loss shrinks as padded width grows, inspect the denominator; if results differ with batch composition, distinguish token-weighted and sequence-weighted objectives.""",
    )
    add_review(
        22,
        [
            "Query/key/value axes and the softmax Jacobian needed a concrete forward/backward trace.",
            "Mask polarity differences needed a parameter-level table and a float-mask counterexample.",
            "Prefix agreement was overinterpreted as a complete arithmetic or model-causality check.",
        ],
        """Use attention when an output needs a content-dependent mixture of source representations. Decide first which information exists at each query position. Encoder self-attention, causal decoder attention and cross-attention have different allowed source sets even when they use the same matrix formula.

Choose masks from absolute query/key positions and padding policy, then translate them to the exact API parameter convention. Keep the small CPU SDPA helper as a deliberately restricted square self-attention contract. A cache with unequal query/key lengths or a multihead module needs a new shape/alignment review rather than an unexamined copy of this triangle.""",
        """## Derive attention values and information boundaries

Let Q have shape(L,d_k), K shape(S,d_k) and V shape(S,d_v). Scores S_score=QK^T/sqrt(d_k) have shape(L,S): each row belongs to one query and each column to one key. Softmax runs across the key axis, and P@V produces(L,d_v). The lesson restricts L=S and matching query/key widths to make this map inspectable. Batched multihead code adds batch/head axes; those do not replace the query and key meanings.

When every score is zero, a legal row containing m keys assigns each probability1/m. The causal rows here permit one,two and three keys, giving[2,0],[1,1] and[8/3,8/3]. Multiplying an unrestricted uniform1/3 distribution by the triangle afterward would instead leave row sums1/3,2/3,1. Forbidden keys already participated in normalization, so masking must define the legal score set before softmax or be followed by a correctly specified renormalization.

The zero-score example cannot verify the scale factor:zero divided by any finite positive width factor remains zero. For the nonuniform second query[0,1], the two legal keys[1,0] and[0,1] produce scores0 and a=1/sqrt(2). Let p=exp(a)/(1+exp(a)), approximately0.669762. The correct mixture is[2(1-p),2p], approximately[0.660477,1.339523]. Omitting the scale changes p to exp(1)/(1+exp(1)),approximately0.731059, while a causal prefix test can still pass. Thus nonuniform prefix agreement checks an information boundary but is not an independent numerical oracle for every score operation.

A backward trace separates the roles of Q,K and V. If upstream derivatives are G=dL/dY, then dL/dV=P^T G and dL/dP=G V^T. For one softmax row p with incoming derivative u, the score derivative is p elementwise-multiplied by(u-sum(p*u)). This subtracts the probability-weighted mean because changing one score changes every normalized weight in that row. Then dL/dQ=(dL/dS_score)K/sqrt(d_k), and dL/dK=(dL/dS_score)^T Q/sqrt(d_k). Shapes must match the corresponding inputs. At Q=K=0, both query/key derivative paths can evaluate to zero even though the output still depends on V; that is another reason to use a nonuniform diagnostic.

Boolean mask meaning belongs to the parameter,not the word PyTorch:

| API parameter | Boolean True means | Typical role |
| --- | --- | --- |
| functional SDPA attn_mask | position participates | allowed query-key relation |
| nn.MultiheadAttention attn_mask | position is forbidden | blocked query-key relation |
| nn.MultiheadAttention key_padding_mask | key is ignored | padding keys per batch |
| paired manual TensorFlow where-mask | score is retained | allowed query-key relation |

The functional and module contracts are documented separately. [PyTorch2.9 SDPA](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.scaled_dot_product_attention.html), [PyTorch2.9 MultiheadAttention](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MultiheadAttention.html). Inverting polarity does not by itself translate shape: a square query-key mask and a batch-by-key padding mask are different objects. Ignoring padded keys also does not automatically remove padded query outputs from a later loss.

A float mask is an additive score bias,not a Boolean mask expressed as0.0/1.0. Adding one to an allowed score and zero to a forbidden score leaves the latter eligible for softmax. For a hard exclusion convention, the additive representation uses zero for allowed entries and negative infinity for excluded entries. The helper rejects rows with no legal key before calling the kernel so the lesson does not depend on backend-specific all-masked output behavior.

Causality also depends on position alignment. In the square shifted-target fixture, query i may attend to input positions j<=i because its target is the next token. If the target token itself was fed at the same input position without shifting,the diagonal would leak the answer even though the mask looks causal. With a cached prefix and one new query,query position is an offset into the full key history; a freshly constructed1-by-S upper-left triangle is not automatically the desired cached-decoding mask. State the absolute position relation first.

Prefix invariance should recompute the shorter input,not slice a full attention matrix that already used future data. It is still only a test of the components exercised. Upstream bidirectional features,position-mixing normalization,target construction or contaminated retrieval can leak future information before a correct attention mask sees it. A full decoder needs a corresponding end-to-end boundary test.

Functional SDPA applies dropout according to dropout_p,including when an enclosing module is in evaluation mode. The unchanged helper passes0 explicitly. A training wrapper must derive the argument from its mode deliberately. This CPU arithmetic fixture does not qualify a fused accelerator backend,memory scaling or generation quality;it establishes the stated finite values and mask behavior.""",
        """If values are wrong but prefixes still agree,calculate the nonuniform second-row probabilities and inspect scaling,transpose and softmax axis. If a future perturbation changes earlier rows,check mask polarity,position offsets and any upstream features that already mixed positions. A triangular display cannot establish those contracts.

If padded query outputs affect the objective,inspect the loss participation mask separately from the key mask. If evaluation changes between calls,inspect the functional dropout argument as well as module mode and RNG. If gradients are zero on the uniform fixture,replace zero Q/K with the declared nonuniform case before diagnosing a disconnected graph. Keep the helper's all-masked rejection and finite-input checks instead of widening tolerances around undefined or unreviewed cases.""",
    )
    add_review(
        23,
        [
            "The scalar update sequence needed exact before/loss/gradient/after states.",
            "Accumulation weighting and clipping order were named without an unequal-microbatch counterexample.",
            "Missing gradients,nonfinite gradients and optimizer displacement needed different diagnostic meanings.",
        ],
        """Debug one update with a fixed fixture before adding epochs,accumulation or performance tooling. Name which parameter state produced each loss and gradient,and observe the actual optimizer-held parameter objects. A numerically correct detached loss is not a differentiable training objective.

Use accumulation to implement a declared additive objective under a memory budget,not to assume every set of microbatches is equivalent to one large batch. Choose the global denominator first. Clip the accumulated gradient at the intended update boundary,after unscaling if mixed precision is used,and keep a nonfinite result as a failed update rather than a valid clipped number.""",
        """## Trace the optimizer state transition and objective denominator

ExampleA computes a numeric loss from w=0 and detaches it. Its value is still four,but its dependency on w is no longer in the recorded graph. Setting requires_grad on that detached scalar would create a new leaf;it would not reconstruct the missing operation. The failed backward leaves the original parameter unchanged,so the sequential ExampleB still begins at w=0.

For x=[1,2,3],y=2x and mean squared error,the objective is L(w)=(14/3)(w-2)^2. Its derivative is(28/3)(w-2). With learning rate1/10,the update is w_next=w/15+28/15. The exact trace is:

| Step | Weight before | Loss before | Gradient | Weight after |
| --- | --- | --- | --- | --- |
| first | 0 | 56/3 | -56/3 | 28/15 |
| second | 28/15 | 56/675 | -56/45 | 448/225 |

The loss at the final weight is56/151875. A logged loss tensor calculated before step still represents the earlier state after the parameter changes. Recompute the forward objective to report post-update loss;printing the new weight beside the old loss without labeling them mixes two different states.

backward adds to stored gradient buffers. If the second step does not clear the first gradient,the stored value becomes -56/3-56/45=-896/45,and the next weight becomes868/225 rather than448/225. That precise wrong trace distinguishes accidental accumulation from a wrong derivative formula. set_to_none=True also makes absence visible:None means no stored gradient was produced for that parameter in the relevant pass,whereas a connected derivative can be an actual zero. An optimizer may treat those cases differently,especially with state or decay.

Intentional microbatch accumulation needs a global denominator. Split the same three rows into one row and two rows at w=0. The local mean gradients are -4 and -26. Averaging those means equally gives -15,but the full-data gradient is(1×(-4)+2×(-26))/3=-56/3. One correct implementation weights each local mean by its valid-example count divided by the total,or accumulates local summed losses and divides by the total valid count. For padded tokens or sample weights,the denominator is the valid weight mass,not necessarily the number of stored rows.

This algebra assumes an additive loss evaluated at the same parameter state with equivalent forward behavior. Updating parameters between microbatches is a different trajectory. BatchNorm statistics,dropout draws,contrastive in-batch negatives and other batch-dependent computations can make a large batch differ even when gradient normalization is correct. State the scope of an equivalence claim rather than using accumulation as a universal replacement.

Norm clipping is another nonlinear boundary. Concatenate the participating parameter gradients into g. L2 clipping uses approximately g'=g×min(1,c/||g||),with a small numerical stabilizer in the implementation. For[3,4],the norm is five and c=1 gives approximately[0.6,0.8]. The function returns the original five while mutating gradients in place. Starting from zero,plain SGD at0.1 then moves to approximately[-0.06,-0.08]. [PyTorch2.9 clip_grad_norm_](https://docs.pytorch.org/docs/2.9/generated/torch.nn.utils.clip_grad_norm_.html).

Clipping each contribution before accumulation can change the result. Scalar contributions100 and-99 sum to one;clipping their sum to magnitude one leaves one. Clipping each separately to±1 and then adding gives zero. Therefore clip at the declared update boundary after the intended weighting and accumulation. With scaled gradients,unscale before applying a threshold expressed in ordinary gradient units.

Clipping limits the supplied gradient norm. It does not universally bound optimizer displacement when momentum,adaptive preconditioning,weight decay or retained state also affect the update. It also cannot repair invalid labels,nonfinite forward values or leakage. error_if_nonfinite=True makes an infinite/NaN norm a refusal rather than a meaningful update. The unchanged CPU fixture checks these local distinctions;it does not qualify mixed-precision or distributed execution.""",
        """For an incorrect weight,compare the four columns of the exact trace and stop at the first mismatch. If the second gradient contains the first one,inspect zero_grad placement. If gradients are None,inspect the graph and optimizer parameter membership instead of replacing every missing value with zero. If loss is correct but untracked,look for detach,item,NumPy conversion or no_grad in the forward path.

If accumulation differs from a full-batch reference,compare valid counts and loss reductions before changing the learning rate. Then check batch-dependent forward behavior. If clipping returns five but the new gradient has norm near one,that is expected;the return is pre-clipping norm. If updates still look too large,inspect optimizer state and decay. A nonfinite gradient should stop the update and preserve diagnostic context,not be hidden by a permissive clipping call.""",
    )
    add_review(
        24,
        [
            "The classifier capstone needed an independently derived first update and preprocessing denominator comparison.",
            "Visible synthetic labels and two test rows were insufficiently separated from population reliability.",
            "Confusion accounting,threshold ties and subgroup denominators needed a complete decision trace.",
        ],
        """Use the one-weight logistic model because the declared target is the sign of one scalar coordinate. Additional hidden layers would add parameters without resolving uncertainty in this visible task. Freeze preprocessing,step budget and decision threshold before examining the two test decisions. If those choices are tuned from later results,record that population as selection data rather than claiming it stayed an untouched test.

Treat the capstone as an inspectable training-and-evaluation procedure. The labels and geometric rule are public,and the test points extend beyond the training coordinate range. A successful fixture proves the declared local behavior;it does not establish a blind scientific discovery,calibration or reliability for a real application.""",
        """## Derive the classifier and audit every assessment row

The training values[-2,-1,1,2] have mean zero and squared deviations summing to ten. Population variance divides by four,giving2.5 and scale sqrt(2.5). PyTorch's correction=0 matches NumPy's default used in the paired TensorFlow guide. Using the default sample correction would divide by three and produce sqrt(10/3). Both scales are mathematically meaningful statistics,but they define different model inputs and update trajectories. Equal final class labels would not prove framework parity.

The stored model weight has shape(1,1),inputs and targets have shape(4,1),and logits have shape(4,1). The bias is deliberately absent. Binary cross-entropy with logits is applied directly to those logits. Applying sigmoid first and then passing its output to the logits loss would change the objective. A target shaped(4,) is also a different interface from(4,1),even when it contains the same four numbers;preserve the declared axes rather than relying on broadcasting or reshaping after a failure.

For one normalized feature t and label y,the logit is z=wt and the loss derivative with respect to w is(sigmoid(z)-y)t. At w=0,all probabilities are one-half. Writing s=sqrt(2.5),the four derivative contributions are -1/s,-1/(2s),-1/(2s),-1/s. Their mean is -3/(4s),approximately-0.474342. The first SGD step at0.1 therefore makes w approximately0.0474342. This analytic sign and scale explain why the later fixed40-step run should have a positive finite weight.

The data are separable under this one-feature rule. In an unregularized logistic model,continued loss reduction can push the weight larger without a finite optimum that must be reached. Forty steps are a declared computational budget,not evidence of convergence or a reason to repeat training until a preferred test score appears. If early stopping or hyperparameters are to be selected,they need a separate selection procedure and data boundary.

The decision rule is logit>=0,which corresponds to probability>=0.5. At the zero initial weight,both test logits are exactly zero and this tie convention predicts the positive class for both rows. After a positive weight,the transformed-3 point has a negative logit and the+3 point a positive one. The final confusion table is:

| Test input | Truth | Decision | Count category |
| --- | --- | --- | --- |
| -3 | negative | negative | TN=1 |
| +3 | positive | positive | TP=1 |

FP and FN are zero,and the four counts sum to two. The fixed class-zero baseline instead has TN=1,FN=1. Its one error and the model's zero errors are evaluated on the same two units. This is a useful paired comparison,but one changed decision would move accuracy by50 percentage points,so the apparent difference is not a stable population estimate.

The subgroup counterexample changes only the positive row's decision. The negative group then has0 errors out of1 and the positive group1 out of1. Reporting only an aggregate error rate of1/2 hides which group failed. At the same time,one observation per group is not sufficient for a reliable subgroup performance claim. These sign-based teaching groups are not a demonstrated fairness analysis of a real population.

Distinct train/test IDs are necessary but not sufficient for independence. Real data can contain copied examples,shared source families,temporal leakage or features only available after the decision. The literal fixture has none of those hidden sources by construction,but its rule is already visible to the learner. Preserve this difference between a procedure test and an undisclosed final assessment.

Finally,normalization parameters belong to the fitted artifact. The test coordinates must reuse the training mean and scale. Recomputing statistics on each inference batch changes predictions according to which other rows arrived together. A release should save feature order,units,mean,scale,dtype and threshold with the model state,and compare a known input through the complete preprocessing-and-model path. Model weights alone are not the whole predictor.""",
        """If a paired-framework weight differs,check correction=0,initialization,loss reduction,target shape and update count before assuming a backend defect. Compute the first derivative -3/(4sqrt(2.5)) and inspect its sign. If the model predicts both classes incorrectly,verify that thresholding uses logits rather than a second sigmoid interpretation and that truth rows retain their identity order.

If confusion counts do not sum to two,inspect Boolean complements,shape broadcasting and missing rows. If a subgroup report lacks its denominator,it is incomplete. If a result looks exceptionally strong,revisit the public geometric rule,tiny visible holdout and extrapolation range before calling it population evidence. A failed data or evaluation boundary is a no-go result even when the arithmetic accuracy is perfect.""",
    )
    add_review(
        25,
        [
            "Contrastive temperature needed an exact loss/gradient derivation rather than a sharpness label.",
            "The projection-gradient check needed its actual trainable branch and expected matrix explained.",
            "False negatives,zero norms and changing candidate populations needed distinct failure contracts.",
        ],
        """Choose a representation objective from the relationship the application needs to preserve. Define positives,negatives and source-family exclusions before optimizing similarity. Decide whether vector magnitude carries useful signal or whether a directional comparison is intended;normalization changes the model contract rather than merely cleaning up a score.

Use the fixed two-candidate example to inspect relative scores and one query-projection derivative. Broader retrieval evaluation needs representative queries,relevance judgments,candidate identities and a fixed index/model version. A finite contrastive loss or nonzero gradient cannot establish that the labels are sensible or the representation captures natural-language meaning.""",
        """## Derive the contrastive competition and its gradient

For nonzero vectors a and b,the dot product is sum_i a_i b_i and cosine is their dot divided by||a||||b||. With a=[1,0],positive=[1,1] and negative=[0,1],the scores are1 and0,while cosines are1/sqrt(2) and0. Scaling the positive by ten increases its dot to ten without changing direction. That particular example keeps the ranking,but in general a large poorly aligned vector can outrank a small well-aligned vector under dot product and lose under cosine.

A zero vector has no direction. PyTorch's normalization/similarity APIs use an epsilon convention for numerical stability;receiving a finite number from that convention does not make a zero vector semantically informative. If the application requires directional similarity,validate finite nonzero norms and define a refusal or fallback policy. The paired TensorFlow chapter's explicit zero-norm rejection is a data contract,not a claim that every framework cosine API raises automatically. [PyTorch2.9 normalize](https://docs.pytorch.org/docs/2.9/generated/torch.nn.functional.normalize.html).

Let candidates have scores s_j and let candidate0 be the positive. For temperature tau>0,define p_j=exp(s_j/tau)/sum_k exp(s_k/tau). The loss is -log(p_0)=logsumexp(s/tau)-s_0/tau. Stable cross entropy computes this without manually exponentiating large logits. With scores[1,0] and tau1,p_0≈0.731059 and loss≈0.313262,which equals log(1+exp(-1)). With tau0.5,the effective logits are[2,0],p_0≈0.880797 and loss≈0.126928.

Positive temperature scaling preserves the ranking of fixed scores. It changes probabilities and the derivative dL/ds_j=(p_j-y_j)/tau. Lower temperature does not guarantee a larger gradient on every example,because the probabilities also change. For this already-correct pair,the positive-score derivative is approximately-0.268941 at tau1 and-0.238406 at tau0.5. Hard or incorrectly ranked examples can behave differently. Treat temperature as an objective and calibration choice,not a universal gradient amplifier.

The reference trains neither candidate vector in its projection check. It defines q=aP with an identity2×2 trainable P,then uses the fixed positive and negative vectors as candidates. At tau1,let c=1/(1+exp(1))≈0.268941. The query derivative is -c[1,1]+c[0,1]=[-c,0]. Since a=[1,0],the projection derivative is the outer product a^T[-c,0],or[[-c,0],[0,0]]. Only the first projection row receives this contribution. This exact analytic matrix is stronger explanatory evidence than the reference's broad finite/nonzero assertion.

A shared encoder applied to the anchor and both candidates would have additional gradient paths. A symmetric contrastive objective would also evaluate reverse-direction comparisons. Those are different experiments from this one-branch projection check. The unchanged reference calls backward but does not take a projection optimizer step,so its evidence is differentiability and a local gradient,not a completed representation-learning run.

Negative sampling defines the competition. With M equal candidate scores,the loss is log(M),so changing the number of negatives changes the numerical baseline even when the representation is unchanged. Losses from two candidate-pool designs are not automatically comparable. In-batch negatives also couple examples:changing batch membership can change an anchor's objective even if its positive pair stays fixed. This is one reason microbatch gradient accumulation need not reproduce a larger in-batch contrastive batch.

If a positive and negative are literally the same vector under the same scoring path,their scores must agree. For a two-candidate loss,the positive probability is one-half and the opposing query-gradient terms cancel. The model cannot satisfy contradictory role labels through that shared representation. If the vectors are different views of the same relevant document,the model may instead learn a nuisance distinction. Identity checks catch exact collisions;family/version and relevance audits are needed for less obvious false negatives.

Several relevant candidates may require a multi-positive objective or a relevance-aware sampling policy rather than marking all but one as negative. Evaluation should keep the intended corpus,candidate count and exclusions visible. A high score is not an external truth label,and embeddings from different model/tokenizer/normalization versions should not be mixed merely because their dimensions match. Record the representation-space identity with any saved retrieval index.""",
        """If dot scores grow while directional quality does not,inspect norms and the intended normalization policy. If cosine returns a finite value for a zero vector,apply the application's semantic boundary instead of interpreting epsilon behavior as a meaningful direction. If the projection gradient differs,derive the two score derivatives and check which branches are trainable.

If loss changes after increasing batch size or candidate count,reconstruct the denominator and negative set before attributing improvement to the encoder. If positives are pulled apart,check exact IDs,source families and alternate relevant answers among negatives. If temperature changes ranking for fixed finite scores and positive tau,inspect a separate sorting or preprocessing change. A finite loss with contradictory supervision remains an invalid experiment.""",
    )
    add_review(
        26,
        [
            "Residual forward identity needed a nonzero branch-gradient derivation.",
            "Parameter objects,buffers,constructor metadata and optimizer identity needed distinct state roles.",
            "Custom backward needed a vector-Jacobian-product explanation and clearer gradcheck limits.",
        ],
        """Use a custom module to express a reusable computation with a stable state inventory. Create persistent learned state once and validate the feature contract on later calls. Choose a residual connection when its identity path is part of the intended architecture,not simply because addition makes a shape mismatch disappear.

Prefer ordinary differentiable PyTorch operations when they express the computation correctly. Write autograd.Function only when a concrete operation requires a custom rule,and then specify its input domain,upstream-gradient behavior and supported derivative orders. Numerical checks complement analytic and composition tests;they do not certify every branch automatically.""",
        """## Derive residual gradients and stable module identity

For X shaped(B,D),a square kernel K shaped(D,D) and scalar scale s,the module computes Y=X+sXK. Both terms have shape(B,D). A different branch width requires an explicit projection or a different architecture. Broadcasting an unrelated tensor into the residual sum may be legal arithmetic but would not satisfy this feature contract.

At K=0 and s=1,the forward map is exactly Y=X. That does not make the branch untrainable. For upstream G=dL/dY,the matrix derivatives are dL/dX=G+sGK^T and dL/dK=sX^T G. With the fixture X=[[1,2],[3,4]] and L equal to the sum of output entries,G is all ones,so dL/dK=[[4,4],[6,6]] even at K=0. The input derivative is G because the zero branch adds no additional input sensitivity. The skip path preserves a direct derivative route while the branch can begin learning.

ExampleC changes K to identity and s to0.5. Its forward result is1.5X. Under the same hypothetical summed loss,dL/dX=1.5G and dL/dK=[[2,2],[3,3]]. The paired TensorFlow residual has no scale buffer and therefore gives2X when its kernel is identity. That difference is an intentional mathematical configuration difference,not a framework disagreement. Match the scale before comparing corresponding derivatives.

The module owns one Parameter object with four scalar entries and one scalar buffer. Counting objects and counting scalars answer different questions. Parameters participate in named_parameters and are candidates for optimizer membership. The registered scale buffer participates in module state and device/dtype movement but is not automatically passed to an optimizer. Its current construction does not request gradients. An ordinary tensor attribute would not automatically receive all of those registration behaviors.

state_dict is not the complete program. It contains the registered kernel and persistent buffer,but reconstruction still needs the module class and width argument. Python configuration such as width is not made into serialized tensor state merely because it is an attribute. A release must preserve that construction contract alongside the tensors. Also,a state_dict mapping is not by itself an independent snapshot of every underlying tensor;clone the values when comparing against later in-place mutations.

Stable object identity matters as much as a stable parameter count. Replacing a four-element Parameter with a fresh four-element Parameter inside forward keeps the scalar count unchanged while leaving an existing optimizer holding the old object. Gradients can then appear on the new parameter without an update from that optimizer. The unchanged exercise checks both identity and count to expose this failure. Keras build/add_weight and PyTorch __init__/Parameter use different construction idioms,but both need a persistent tracked object across calls.

## Treat a custom backward as a local vector-Jacobian product

For f(x)=x^3,the local derivative is3x^2. backward receives the derivative from later computation,so it must return grad_output×3x^2. At x=2,the derivative of2f(x) is2×12=24. Returning only3x^2 would pass a unit-upstream test but fail this composition. For a vector of independently cubed elements,the returned gradient has the same shape and multiplies each incoming component by its own local derivative.

save_for_backward preserves the tensor values required by the rule and lets autograd enforce relevant lifetime/version checks. Do not mutate saved input storage between forward and backward or detach a value that must support a higher-order derivative. A function with several inputs returns a corresponding derivative entry for each differentiable input,and None where that input has no requested derivative under the declared contract. [Extending PyTorch2.9 autograd](https://docs.pytorch.org/docs/2.9/notes/extending.html).

gradcheck perturbs real-valued inputs and compares numerical sensitivities with the backward rule. The supplied float64 points0.2 and-0.7 avoid a nondifferentiable branch,and the analytic derivatives are0.12 and1.47. Finite precision,probe size and conditioning still matter. A forward implementation that changes branches at the probe point may not have the derivative the numerical test assumes. Overlapping storage can also invalidate an interpretation that perturbations affect one independent coordinate.

A first-derivative check does not establish double backward,forward-mode support,arbitrary broadcasting or performance. Add the relevant contract tests when those features are actually required. The fixture's cube is small enough to inspect symbolically,and the upstream-factor test catches a distinct error from the basic numerical comparison. None of these checks requires a compiled extension or an external package.""",
        """If an identity residual receives no kernel gradient,inspect the branch input and graph before concluding that a zero forward branch cannot learn. If the parameter count stays fixed but training stops,compare object identities in the module and optimizer. If loading tensors produces a different function,check constructor width and buffer values as well as weights.

If a custom backward passes only when the outer coefficient is one,multiply the output by a different upstream factor and inspect the vector-Jacobian product. If gradcheck fails near a kink or at float32 precision,choose a justified smooth float64 probe before loosening tolerances. If higher derivatives are required,test them explicitly rather than inferring them from a first-order pass. Preserve saved-tensor ownership instead of bypassing autograd checks with untracked mutation.""",
    )
    add_review(
        27,
        [
            "Freeze semantics needed a four-part state/mode/gradient/optimizer contract.",
            "The head update and newly available base-gradient path lacked an exact local derivation.",
            "Unfreezing needed explicit optimizer-state choices rather than implying recreation is mandatory.",
        ],
        """Freeze a base when reusing its current representation is a deliberate adaptation strategy,and define whether its running buffers and stochastic behavior must remain fixed too. Separate requires_grad,optimizer membership,stored gradients and train/eval mode. None of those controls alone proves the complete freeze contract.

Treat unfreezing as a new training phase with a stated learning rate,parameter set and optimizer-state policy. Creating a fresh optimizer is the simple policy used here. Adding a reviewed parameter group to an existing optimizer is another supported choice when preserving prior head state is intended;it should not happen implicitly.""",
        """## Trace what freezing preserves and what it does not

The base is a bias-free2-to-2 Linear layer initialized to identity. Its stored weight has shape(2,2),and base(x)=x for the three fixture rows. The head has shape(1,2) and begins at zero. Disabling base parameter gradients and supplying only head.parameters() to SGD establishes two distinct boundaries:the base does not receive new parameter derivatives,and the optimizer is not asked to update it.

The head update has an independent analytic value. With targets[1,2,3],zero predictions and mean squared error,the residuals are[-1,-2,-3]. The head gradient is(2/3) times the feature-weighted residual sum,namely[-8/3,-10/3]. SGD at0.1 produces head weights[4/15,1/3] and predictions[4/15,1/3,3/5]. This explains both the observed nonzero head update and why the base need not change for the head to learn.

When the base is later unfrozen,the derivative path through it becomes relevant. If its stored weight is B and the head row is h,features are XB^T and logits are XB^T h^T. The base gradient combines the output residuals with h and X. After the head has nonzero weights,that gradient can be nonzero. Enabling requires_grad does not add B to an optimizer that was constructed from head parameters only. The update set must be changed deliberately.

A parameter can remain in an optimizer after requires_grad becomes false. That flag prevents new gradient construction for the leaf,but it does not erase an old .grad tensor. An optimizer step using that stale tensor can still change the parameter. Clear stored gradients at the phase boundary and inspect the exact optimizer-held objects. For the supplied built-in update policy,grad=None skips the corresponding update;an allocated zero gradient and a missing gradient are not interchangeable in every state/decay situation.

Freezing parameters is also different from wrapping computation in no_grad. If a trainable upstream adapter needs gradients through a fixed base,its input derivative must remain connected even though base parameters are frozen. no_grad around the whole base would sever that upstream path. Conversely,when features are truly fixed and no earlier component is trained,avoiding unnecessary graph construction can be an intentional efficiency choice. State the intended gradient destination first.

Mode-dependent buffers form another axis. BatchNorm affine weights can be frozen while training-mode forward still updates running mean,running variance and batch counters. Dropout can remain stochastic without any trainable parameter of its own. base.eval() changes those module behaviors;it does not disable autograd or alter optimizer membership. A later parent_model.train() can recursively put the base back into training mode,so the intended fixed-mode policy must be restored or encoded deliberately in the training procedure.

A freeze receipt should compare the complete intended tensor state,not just the Linear weight. Clone the relevant state_dict tensors before the phase so the snapshot does not alias later mutations. Record mode flags separately because they are not ordinary learned tensors in state_dict. The tiny Linear base has no running statistics,while the separate BatchNorm exercise makes this hidden-state issue observable.

At unfreeze,there are two different optimizer-state policies. A new optimizer resets momentum/adaptive state for the head as well as introducing the base,which changes the trajectory. add_param_group can preserve existing head state while adding previously excluded parameters with explicit group options. It requires avoiding duplicate membership and deciding rates,decay and scheduler behavior for the new group. The API supports this use,but the resulting experiment still needs its own state receipt. [PyTorch2.9 add_param_group](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.add_param_group.html).

The paired Keras guide uses trainable flags and a deliberate training argument for the base. Those mechanisms are not a one-to-one spelling substitution for PyTorch requires_grad,optimizer lists and train/eval. In either framework,verify before/after tensors,buffer behavior and actual updated identities. The local identity base is a controlled ownership fixture,not a downloaded pretrained model or evidence that transfer will improve an unseen task.""",
        """If a supposedly frozen weight changes,inspect stale .grad values,optimizer membership,decay and explicit in-place writes. If weights stay fixed but predictions drift,inspect running buffers and stochastic training mode. If an unfrozen parameter gets a gradient but does not move,check whether the current optimizer contains that exact object.

If upstream adaptation stops learning after freezing the base,look for a broad no_grad/detach boundary that removed the needed input derivative. If an unfreeze run differs from continuation,compare the chosen optimizer reset versus retained-state policy before blaming the learning rate. A snapshot that shares storage with the current model cannot prove preservation;clone it and test a controlled changed tensor.""",
    )
    add_review(
        28,
        [
            "Restart parity needed a state-dependency ledger and a precise RNG draw timeline.",
            "The fixed data-position marker was not clearly separated from restoring a real loader or sampler.",
            "Snapshot aliasing,optimizer reconstruction and checkpoint publication limits needed explanation.",
        ],
        """Choose a checkpoint boundary by asking what determines the next update. An inference artifact may need only the predictor's parameters,buffers and construction/preprocessing contract. A training continuation also needs optimizer history and every active source of randomness,scheduling and data position. Save only the components actually used,while stating which are fixed or absent.

Use a fresh-process next-step comparison to test reconstruction. Match the next batch and stochastic draws before comparing updated weights. The lesson deliberately uses one CPU generator and a literal batch;restoring workers,distributed sampling or partially consumed external streams remains a separate contract.""",
        """## Reconstruct the next state transition,not just the current prediction

Training state is the input to a transition. A useful inventory separates components by how they influence the next step:

| Component | Role in this fixture | What weights alone omit |
| --- | --- | --- |
| model tensors | current scalar predictor | current value if absent |
| Adam moments and step | update direction/normalization | history-dependent next update |
| optimizer group options | rate and optimizer configuration | the intended update policy |
| CPU RNG state | next probe and target-noise draws | position in the random stream |
| data_position=2 | declared completed-update marker | progress metadata |
| literal x and target rule | fixed next-batch construction | a reproducible input contract |

Adam maintains m_t=beta1*m_(t-1)+(1-beta1)*g_t and v_t=beta2*v_(t-1)+(1-beta2)*g_t^2,then uses step-dependent bias correction and an epsilon-stabilized normalized update. Two models with identical weights but different m,v,t need not take the same next step. Saving after two real updates makes those histories nontrivial;checkpointing before any update would leave a much weaker test.

The weights-only negative control is deliberately given the same next noise tensor as the uninterrupted run. Its different result therefore isolates missing optimizer history rather than simultaneously changing the batch and the optimizer. It is a stronger experiment than comparing two restarted jobs whose data order and RNG streams are also unknown. The paired TensorFlow chapter tests the same reconstruction principle,although its scalar objective and optimizer rate differ from this PyTorch fixture;their literal weights are not a cross-framework equality oracle.

The RNG timeline has an easily missed construction step. torch.manual_seed(7) sets an initial stream. Creating nn.Linear consumes initialization randomness even though the code subsequently overwrites its weight with zero. The two initial updates use zero noise and no further random draws. The saved RNG state therefore represents a particular position after construction,not simply the number7. The uninterrupted path next draws a three-value probe,then a2×1 noise tensor,and then updates.

The child reconstructs the model and optimizer,loads their saved state,and only then restores torch RNG state. Restoring before constructing Linear would let initialization consume a draw from the restored stream. Setting the seed again would return to the stream's beginning instead of its saved position. Matching the three-value probe checks this ordering directly before the weight comparison tests the next noisy update. [PyTorch2.9 reproducibility guidance](https://docs.pytorch.org/docs/2.9/notes/randomness.html).

Other randomness is absent from this particular continuation. Python random,NumPy Generator objects,DataLoader generators,worker processes and accelerator generators would need their own explicit treatment if used. A global torch seed does not automatically serialize every library's current generator state. Likewise,a data_position integer does not restore a real iterator here:the next batch is always constructed from literal x=[1,2]. Incrementing the marker to three proves the stated bookkeeping,not worker-prefetch or distributed-sampler recovery.

State dictionaries also have ownership semantics. model.state_dict() provides references to model state tensors;holding that mapping in memory is not an immutable copy while later updates mutate the model. The example immediately serializes the mapping before continuation,so the file preserves that point. For an in-memory before/after comparison,clone the values;for a restore comparison,reload the completed saved file rather than assuming a still-live dictionary remained unchanged.

Reconstruct the same architecture and optimizer parameter-group structure before loading. Optimizer state is associated with the supplied parameter groups and their ordering;similar tensor shapes do not prove the state was attached to the intended semantic parameter after an architecture edit. A scheduler,gradient scaler,EMA model or accumulated-but-not-yet-stepped gradients would add more continuation state when present. None is silently claimed restored by this small Adam example.

weights_only=True restricts the object forms used by the local tensor-and-primitive checkpoint loader. It is not a publisher-authentication mechanism or a complete resource/shape validation policy for arbitrary outside files. map_location='cpu' establishes the intended device boundary. The child process uses the existing interpreter,has a timeout and exposes stderr on failure,so a failed reconstruction is not replaced by expected output text.

Finally,the tested boundary is a completed torch.save followed by a fresh-process load. It does not inject a crash halfway through writing or prove power-loss durability. A persistent production checkpoint needs its own staged-publication,integrity and retention procedure. The local directory is owned and disposable,and the successful test removes it. Next-step parity is valuable evidence for this exact transition and environment,not a promise of bitwise agreement across versions,hardware or nondeterministic pipelines.""",
        """If immediate predictions match but the next weight diverges,compare Adam step/moments,group options and the exact next input before changing tolerances. If the random probe differs,inspect restore order and every intervening draw,including model construction. If the probe matches but the update does not,inspect optimizer reconstruction and loss configuration.

If a supposed saved snapshot changes in memory,check state_dict aliasing. If the data-position marker is correct but a real pipeline repeats or skips records,the marker did not restore its loader/sampler contract. Treat child timeout,nonzero exit or incompatible tensor shapes as a failed continuation with retained diagnostics. Do not describe a completed-file test as crash-safe publication or a one-CPU-generator test as distributed reproducibility.""",
    )
    add_review(
        29,
        [
            "Stable softmax/cross-entropy needed an exact shifted-logit and gradient derivation.",
            "Range,precision and cancellation were not distinguished by concrete dtype comparisons.",
            "Autocast,gradient scaling and clipping order needed separate hardware-qualified boundaries.",
        ],
        """Use logits-aware objectives and numerically appropriate reductions before considering a lower-precision execution policy. Validate finite inputs and the intended class/reduction contract separately. More precision can reduce some arithmetic error,but it cannot repair an incorrect target,information leak or denominator.

Choose autocast and scaling only for an explicitly qualified device/operator workflow. The current CPU fixture checks arithmetic stability and dtype properties. It does not run or benchmark a mixed-precision training path,so GPU speed,overflow-recovery and convergence claims need additional evidence.""",
        """## Separate the mathematical distribution from its representation

For logits z=[1000,999],the first-class probability is exp(1000)/(exp(1000)+exp(999)). Dividing numerator and denominator by exp(1000) gives1/(1+exp(-1)),approximately0.731059. The other probability is approximately0.268941. The mathematical ratio is well defined even though directly materializing exp(1000) overflows the types used in the counterexample.

More generally,subtracting the same finite m from every logit preserves softmax in exact arithmetic. Choosing m=max(z) makes every shifted exponent at most one and at least one exactly one. For the target0 loss,the shifted form is log(1+exp(-1)),approximately0.313262. The gradient is p-one_hot(target),or approximately[-0.268941,0.268941]. Its entries sum to zero because a common logit shift does not change the objective. This gives an independent forward and backward contract.

Stability is more specific than a function name. logsumexp avoids raw exponential overflow,but computing a large logsumexp value and then subtracting a nearly equal large target logit can still lose precision. A fused logits loss or log_softmax formulation can preserve the small relative difference more directly. Similarly,computing a tiny probability and then taking its log can underflow where a direct log-probability calculation remains finite. Inspect intermediate representation rather than assuming algebraic equivalence implies equal floating-point error.

Range and precision are different properties:

| Type | Approximate maximum finite magnitude | Relative spacing near one |
| --- | --- | --- |
| float16 | 65,504 | 2^-10 |
| bfloat16 | 3.39×10^38 | 2^-7 |
| float32 | 3.40×10^38 | 2^-23 |
| float64 | 1.80×10^308 | 2^-52 |

bfloat16 has a much wider exponent range than float16 but fewer fraction bits. A value can avoid overflow while still be represented coarsely. Epsilon near one is not a universal absolute tolerance for all magnitudes or all algorithms. Summation length,conditioning,cancellation and the operations actually performed matter. [PyTorch2.9 numerical accuracy](https://docs.pytorch.org/docs/2.9/notes/numerical_accuracy.html).

Shift invariance also has a finite-representation limit. If a huge common offset has already rounded two distinct logits to the same stored value,subtracting their maximum cannot recover the lost difference. The lesson's1000 and999 remain distinct and are therefore an appropriate stability fixture. A NaN input is a different case:maximum subtraction does not repair it,and the explicit validator rejects it before evaluating the objective.

Autocast selects operation dtypes according to a backend policy. It is not equivalent to converting every model tensor and intermediate to float16. Some operations may run or accumulate in higher precision,while others use a lower-precision path. Eligibility and kernel behavior are device/version specific. A CPU bfloat16 path and a CUDA float16 path therefore need separate acceptance rather than one generic mixed-precision label. [PyTorch2.9 AMP](https://docs.pytorch.org/docs/2.9/amp.html).

Gradient scaling addresses another boundary. Multiplying a scalar loss by s multiplies its derivatives by s. An update workflow can compute those scaled derivatives,unscale them back to ordinary units,and detect nonfinite values before an optimizer step. This can protect some small backward values from underflow. It cannot recover information already lost in the forward pass or make an invalid loss meaningful.

Clipping thresholds must be applied to unscaled gradients if they are defined in ordinary gradient units. Otherwise changing the scale factor silently changes the effective clipping policy. A scaler may skip an optimizer update after detecting overflow;step counters,scheduler progression and logs should distinguish an attempted iteration from an actual parameter update. The scaler's own state belongs in a training checkpoint when it affects subsequent behavior.

A stable finite loss can still optimize the wrong example pairing,class index or reduction. Conversely,a finite forward value can have a problematic derivative at a singular or extreme point. Check forward inputs,loss,gradients and resulting parameter state as separate stages. The default examples retain small deterministic CPU work and make no throughput or accelerator-memory claim.""",
        """If exponentials overflow,inspect whether the implementation unnecessarily materialized them instead of using shifted logits or a fused objective. If the fused loss is finite but a manual logsumexp subtraction differs slightly,inspect cancellation and dtype before declaring the backend wrong. If a common shift destroys a score difference,check whether that difference was representable before softmax.

If a gradient becomes nonfinite,locate the first invalid stage rather than replacing every NaN with zero. If clipping behaves differently under scaling,verify that unscale precedes the threshold. If an AMP run appears faster,confirm equivalent outputs,actual update counts,warmup and the qualified device path. finfo metadata and a CPU arithmetic pass are not measurements of mixed-precision training performance.""",
    )
    add_review(
        30,
        [
            "Unequal-shard weighting needed a direct connection to backend averaging conventions.",
            "The full-batch and sequential-microbatch trajectories needed exact distinct endpoints.",
            "Empty shards,regularization and batch-dependent forward behavior needed explicit assumptions.",
        ],
        """Define the global statistical objective before choosing communication or accumulation mechanics. Decide whether examples,tokens,weights or groups receive equal influence,and carry the corresponding denominator alongside every local numerator. Equal rank weight is correct only when that is the intended objective or local denominators agree.

Use the one-CPU fixture to validate the algebra and one-update boundary. A real distributed run additionally needs compatible process participation,collective ordering,parameter state and failure handling. Do not infer those operational properties from a correct scalar weighted mean.""",
        """## Derive the global gradient and the reduction factor

Let rank or shard r contain n_r participating examples,local gradient sum S_r and local mean g_r=S_r/n_r when n_r>0. The global example-mean gradient is(sum_r S_r)/(sum_r n_r),equivalently(sum_r n_r g_r)/N. For means2 and6 with counts1 and3,the numerator is2+18=20 and N=4,giving five. Averaging the two means gives four and defines a different objective with equal shard weight.

The vector[2,4,6,8] is an independent four-example oracle. Splitting it1:3 gives sums2 and18,which recombine to20/4=5. An empty shard contributes sum zero and count zero;its local mean need not be evaluated at all. A globally empty collection has N=0 and must not be divided by zero or described as a valid zero-gradient batch without an explicit skip policy.

For the actual squared-loss fixture,x=[1,2,3,4],y=2x and w=0. The per-example derivatives are -4x^2,or[-4,-16,-36,-64]. Their sum is-120 and global mean-30. The two backward calls in ExampleC accumulate the summed objectives at the same unchanged w,then divide once by four. One SGD update at0.01 gives w=0.3.

Stepping after each microbatch changes both normalization and evaluation state. The first one-row mean has gradient-4,so w becomes0.04. The second three-row mean is then evaluated at that new value and has derivative(58/3)(0.04-2),approximately-37.893333. Its second update ends at approximately0.418933,not0.3. This discrepancy is expected because it is a different optimization trajectory,not an accumulation bug to hide with a tolerance.

A distributed reducer introduces another factor. Under a fixed R-rank configuration that averages gradients across ranks,backpropagating a local summed loss divided by global N would produce only1/R of the intended global gradient after averaging. One appropriate local scaling for this stated convention is L_r=(R/N)×sum_i loss_ri. The reducer then returns(1/R)sum_r(R S_r/N)=sum_r S_r/N. Equivalently,weight each nonempty local mean by R n_r/N. When all n_r are equal,the ordinary mean of local means already has the intended weighting.

That derivation assumes the documented reducer behavior and a fixed participation set. Custom communication hooks,uneven-input mechanisms and changed divisors require a fresh derivation. PyTorch DDP documents that its gradient synchronization semantics depend on the loss reduction and participating processes. [PyTorch2.9 DistributedDataParallel](https://docs.pytorch.org/docs/2.9/generated/torch.nn.parallel.DistributedDataParallel.html). The current lesson launches no process group and therefore verifies none of that communication behavior experimentally.

Padding and sample weights replace the simple n_r with the relevant valid weight mass. Counting tensor storage positions instead of supervised tokens can scale the gradient according to padding. A rank with no valid targets may still need to participate in the distributed protocol;simply skipping its backward while other ranks enter collectives can be an operational error. The CPU arithmetic handles an empty contribution,but a real implementation needs a separately tested participation policy.

Regularization also needs one global meaning. If the objective is mean data loss plus lambda R(theta),adding the full regularizer independently for every accumulated microbatch and then summing multiplies its contribution by the microbatch count. Add it once per intended update or distribute its coefficient deliberately. Optimizer weight decay has its own update semantics and likewise should not be assumed equivalent when the number of optimizer steps changes.

The equivalence requires more than denominators. Parameters and relevant model state must stay fixed while local contributions are formed. BatchNorm statistics,dropout draws,contrastive negative sets and cross-example losses can differ when a large batch is split. Even a mathematically correct reduction cannot make those different forward computations identical. For stateful optimizers,the one-step boundary preserves the intended momentum/adaptive update count;multiple steps change that history.

A future distributed acceptance packet should join the global objective,rank counts,actual reducer convention,parameter synchronization,cancellation and next-step parity. It should also report communication and throughput only after those quantities are measured. The paired TensorFlow chapter derives the same global arithmetic but does not qualify a TensorFlow strategy or a PyTorch backend merely by simulating shards on one CPU.""",
        """If gradients differ by a constant factor,inspect local loss reduction,global valid count and the backend's sum-versus-average rule. If only unequal batches fail,compare n_r explicitly instead of assuming rank means have equal denominators. If the endpoint differs after microbatching,check whether parameters were stepped between contributions.

If an empty shard hangs a distributed experiment,the arithmetic zero contribution is not the whole participation contract;inspect collective ordering and the chosen uneven-input mechanism. If accumulation changes results despite correct weighting,inspect BatchNorm,dropout and cross-example objectives. Keep regularization and optimizer-step frequency visible. A successful CPU mean calculation is not evidence of multi-process setup,device behavior or scaling.""",
    )
    add_review(
        31,
        [
            "Graph capture,backend execution and optimizing compilation needed a phase-by-phase distinction.",
            "The graph counter and timing interval needed precise observable meanings.",
            "Profiler totals,signature diversity and setup amortization needed concrete interpretation.",
        ],
        """Use compilation to evaluate a specific execution strategy for a repeated,well-defined workload. First establish an independent eager result and the supported input contracts. Select and name the backend deliberately;the counting backend in this lesson is a capture diagnostic,not an optimizing native compiler.

Use profiling to answer a bottleneck question and timing to measure a declared interval. Keep cold setup,steady calls,data preparation and instrumentation overhead separate. Optimize only after the output and state contract is unchanged,and report the workload and variability rather than a universal framework ranking.""",
        """## Separate capture,guards,execution and measurement

The eager function computes x*x+1. For[1,2],the result is[2,5];for[3,4],it is[10,17]. These literal values establish correctness without relying on the compiled wrapper as its own oracle. The selected backend receives a captured FX graph and example inputs,appends that graph to a diagnostic list,and returns graph.forward. Tensor operations then execute through that eager graph function. No optimized native kernel generation is requested by this backend.

torch.compile is the entry to a larger capture/guard/backend system. fullgraph=True asks this function to be captured as one graph and reports unsupported graph breaks rather than quietly presenting a partly captured program as the intended full graph. dynamic=False specializes the relevant shapes in this example. Those options do not remove Python dispatch and guard work around every later call. [PyTorch2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html).

The graph-list length counts backend capture invocations,not tensor executions. The same float32 shape can be called again with different values and reuse its graph. The float64 call changes the operation contract and adds a capture in this fixture. Other relevant guards can involve shape,strides,device,requires_grad,module mode or Python values. A cache hit is useful only when those assumptions still describe the input correctly.

Data-dependent Python control is a different issue from merely changing tensor values. A branch based on a tensor converted to a Python scalar can force a graph break or require a separately supported representation. Do not infer that this pure arithmetic example qualifies arbitrary Python side effects or control flow. Counting captures can help locate recompilation,but it cannot by itself show that all application work was represented in one optimized graph.

The measured interval starts after a warm float32 call and contains twenty repeated calls at the same input. The current reference checks the final observed output after that interval;it does not retain a separate per-call output ledger. CPU tensor operations in this path complete before the observed result is used. The elapsed time includes wrapper dispatch and guard/execution costs,but excludes initial capture,model construction and a realistic input pipeline. It is a small diagnostic sample,not a latency distribution.

Setup amortization can be expressed without inventing a benchmark. If setup cost is C,an eager call costs E,and a prepared alternative costs G,then N calls cost approximately NE versus C+NG under a simple stationary model. A break-even N>C/(E-G) exists only if E>G. Hypothetical C=200ms,E=1ms,G=0.5ms would require more than400 calls. Those are illustrative units,not measurements from this lesson,and the eager graph backend may have no positive speedup to amortize at all.

Real measurements need a fixed mode,dtype,shape distribution,thread setting and input/output boundary. Dynamic request shapes can trigger additional setup that a one-signature loop omits. Memory allocation,caches,JIT warmup and concurrent host load also matter. If a future accelerator path launches asynchronously,a host timer without an appropriate completion boundary can measure enqueue time rather than finished work. This CPU lesson does not qualify that device timing path.

The profiler answers which operations ran and where instrumented time was attributed. aten::mul and aten::add are expected for the eager expression,while conversions or wrapper operations can also appear. Their presence is not evidence that an optimizer fused them. Inclusive operator times can contain child work,so summing every inclusive entry can double-count. Self time and total time answer different questions,and aggregate CPU work can differ from elapsed wall time when threads overlap. [PyTorch2.9 profiler](https://docs.pytorch.org/docs/2.9/profiler.html).

Profiling itself adds work. Keep an instrumented diagnosis run separate from the ordinary timing comparison unless the overhead is explicitly part of the measured system. The paired TensorFlow guide similarly distinguishes tf.function tracing from XLA compilation and names its NumPy-materialization boundary. Those are analogous questions,not identical runtimes or a fair performance contest by default.

The useful result is a packet containing correct outputs,capture/reuse observations,actual operation names,the exact timing boundary and a limited conclusion. A nonnegative elapsed interval proves the timer ran;it does not establish that this backend is faster,that throughput scales,or that a deployment meets a latency target.""",
        """If graph count grows unexpectedly,inspect the wrapper lifetime and changed guards before assuming compilation failed. If fullgraph rejects a function,locate the unsupported Python/tensor boundary instead of disabling the option and retaining the old claim. If outputs agree only at one input,add a changed-value oracle before timing more repetitions.

If a speed result looks implausible,check whether setup,synchronization,materialization or input preparation were included consistently. If profiler time exceeds wall time,inspect nesting and parallel attribution before adding columns together. If the backend only returns graph.forward,report graph capture honestly and leave native optimization or accelerator speed unclaimed.""",
    )
    add_review(
        32,
        [
            "State reconstruction and exported-program constraints needed a direct interface comparison.",
            "Static batch specialization and declared dynamic bounds needed precise tested-versus-declared scope.",
            "Feature semantics,artifact ownership and inference versus training continuation needed distinct acceptance gates.",
        ],
        """Choose an artifact according to what the consumer must reconstruct. Use architecture plus state_dict when the consumer owns the compatible module definition. Use torch.export when a constrained tensor-program interface is the intended handoff. Neither format automatically carries the entire preprocessing,feature meaning or training-continuation contract.

Declare which dimensions may vary and verify representative and boundary inputs in the intended runtime. Keep artifact existence,deserialization,execution and numerical parity as separate observations. The current reference exercises a static two-row export and one three-row dynamic call;other declared bounds and deployment backends remain additional acceptance work.""",
        """## Compare tensor state with a constrained program

The fixed Linear layer has two input features,one output and no bias. Its stored weight is[2,-1],so row[1,2] maps to zero and row[3,4] maps to two. The output shape is(B,1). This explicit affine rule is the independent persistence oracle:the restored result should match the known function,not merely another object that happens to share the original weights.

state_dict records named parameters and persistent buffers. Loading it into a new nn.Linear(2,1,bias=False) checks compatibility with that reconstructed architecture. It does not serialize the Python class definition,feature names,normalization policy or arbitrary nonregistered state. Strict loading can detect missing/unexpected keys and incompatible tensor shapes,but equal shapes do not establish semantic equivalence. Reversing the two feature meanings changes[1,2]'s prediction from zero to three while preserving every dimension.

torch.export captures a tensor program with assumptions derived from the example and declared dynamic shapes. In the static example,the batch dimension is specialized to two. The ordinary reconstructed Linear can evaluate a three-row batch,because its parameters constrain feature width rather than batch size. The static exported module rejects that same batch under its captured guard. That rejection is expected interface enforcement,not evidence that the affine calculation itself requires exactly two observations. [PyTorch2.9 export](https://docs.pytorch.org/docs/2.9/export.html).

The dynamic export names a batch dimension with declared range1..4 while keeping feature width two. A three-row call is compared with the ordinary module in the reference. That establishes one in-range dynamic case. The current executable does not separately test batch sizes one,four or an out-of-range five against the dynamic artifact,so those should not be claimed as observed results merely because the range appears in source. Export constraints are useful,but acceptance still needs the actual intended boundary cases when that interface is relied on.

A dynamic dimension does not mean arbitrary rank,dtype,feature width or arbitrary Python control. Shape constraints describe a family of tensor programs that the export process could justify. If later code needs a new branch or input structure,it may require a new export and qualification. A successful strict export is also not a promise that every target runtime or lowering backend can execute the resulting operators.

The fresh interpreter is an important independence boundary. It creates a new Linear,loads the saved tensors,and separately loads the exported program from the file path. It cannot accidentally satisfy the test by reusing the parent's in-memory model. Keeping loaded artifact owners and their derived modules in named variables makes the lifecycle inspectable. The child has a bounded timeout and exposes stderr on failure,so a failed load or guard is not converted into a success transcript.

The two saved forms have different reconstruction semantics from Keras .keras and SavedModel inference export. The paired TensorFlow example also uses a different one-feature affine fixture. Compare the artifact responsibilities and each independent local oracle rather than expecting identical filenames,load APIs or literal predictions across frameworks.

Prediction parity and training continuation remain separate. Matching[0,2] says nothing about Adam moments,RNG position,data iteration or scheduler state. Conversely,a training checkpoint may contain state irrelevant to a minimal inference consumer. The previous checkpoint chapter tests the next update;this chapter tests a fixed prediction interface. Preserve that distinction in filenames,metadata and review claims.

Only the locally created trusted artifacts are loaded. weights_only=True constrains the state-dictionary load path but does not authenticate a publisher or prove that an arbitrary file has acceptable resource demands. The exported program has its own versioned loader/runtime contract. An archive suffix or a successful save call is not proof of compatibility with another framework,architecture or deployment format.

The handoff should retain artifact identity,constructor/program version,feature order and units,dtype/device,mode,shape constraints,preprocessing and output interpretation. Test the full predictor with known inputs in the consumer environment. A graph that reproduces one matrix multiplication can still sit behind a mismatched normalizer or class-label mapping,and those application errors will not be repaired by re-exporting the same weights.""",
        """If state loading fails,compare the intended constructor,keys and tensor shapes before using permissive loading. If loading succeeds but values differ,check feature order,normalization,dtype and evaluation mode. If only a new batch length fails,inspect static versus declared dynamic export constraints rather than changing the model's feature width.

If a fresh-process check fails,read the child's actual stderr and confirm it loaded the created artifact rather than another path. Do not infer boundary behavior at1,4 or5 from the single three-row dynamic example. If inference matches but resumed training diverges,return to optimizer/RNG/data-state restoration;prediction parity is not the corresponding test.""",
    )
    add_review(
        33,
        [
            "Inference mode,eval and an owned normal output tensor needed a precise lifetime/gradient explanation.",
            "Per-record batching parity needed its stateless-model assumptions and singleton-axis trace.",
            "Input finiteness,batch bounds and output-value guarantees needed clearer scope.",
        ],
        """Choose a pure inference boundary when callers need predictions rather than derivatives. Validate the declared dtype,device,rank,feature meaning and request budget before forward computation. Keep a separate path for gradient-based explanation or adaptation rather than silently disabling its graph.

Use a dedicated evaluation model with an explicit output ownership contract. Decide whether batch independence is required for the application and test it under that model's actual mode. Finite inputs alone do not guarantee finite outputs for arbitrary magnitudes,so a production contract also needs a justified range or output-finiteness policy beyond this tiny fixture.""",
        """## Trace validation,mode,storage and batching as separate boundaries

The function accepts a CPU float32 tensor shaped(B,2),with1<=B<=4 and finite entries. Those checks occur before the model call. They are not interchangeable:an integer matrix has the wrong representation policy,a one-dimensional vector lacks the required batch axis,a three-feature matrix has the wrong schema,and a five-row matrix exceeds the declared work bound. A predictable validation order helps callers diagnose the first rejected condition.

The model computes2x_0-x_1. For[1,2] and[3,4],the results are zero and two. Linear returns(B,1),and squeeze(-1) removes only the known singleton output-feature axis to produce(B). A blanket squeeze() would also remove the batch axis when B=1,creating a scalar result and breaking a stable one-result-per-record interface. This is why axis-specific shape operations belong in the API contract.

model.eval() changes mode-dependent behavior such as ordinary Dropout and BatchNorm. It does not disable autograd. no_grad disables ordinary reverse-mode recording for operations in its scope. inference_mode removes additional bookkeeping,including some view/version tracking,and also has restrictions relevant to later differentiation. The choice should follow the consumer's intended use,not a rule that one context is always faster or universally better. [PyTorch2.9 inference_mode](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad_mode.inference_mode.html).

The worked function leaves inference_mode before cloning the result. That clone gives the caller independent normal tensor storage with requires_grad false under this path. It does not reconnect a gradient to the original model computation. The output can be inspected and mutated without changing caller input or model state. Cloning inside the inference context would still create an inference tensor,so the location of the operation matters if later ordinary tensor behavior is part of the interface.

For this stateless affine model,each row's output depends only on that row and fixed weights. Predicting one row alone or alongside the other must therefore agree. A training-mode BatchNorm layer could depend on neighboring records,and some models intentionally contain cross-record operations. A model configured without running BatchNorm statistics can also retain batch-dependent behavior in evaluation. Batch independence is a tested property of this predictor,not a universal theorem about eval().

Record identity remains necessary even when numeric parity holds. Concatenating singleton predictions in a different order can create a correctly shaped but misaligned result. A future batching service must preserve request-to-row mapping,not merely return the correct multiset of values. The local helper starts no server and proves no authentication,queueing,cancellation or concurrent-serving behavior.

The model object is dedicated to this teaching inference path. Calling eval on a model simultaneously shared with a training loop would mutate shared mode state. An output clone cannot repair that ownership problem. A real integration should define separate model instances or a deliberate synchronization/immutability policy,then test state preservation. The fixture does not claim thread-safe serving from a global mutable model.

Finite-value validation is also narrower than an output guarantee. A very large finite float32 input multiplied by two can overflow even though isfinite(input) passed. The literal rows here are small and produce exact finite outputs. If a service promises finite predictions for all accepted requests,it must bound feature magnitudes appropriately or validate output finiteness and define a failure policy. Silently clipping inputs would change the represented model unless that preprocessing rule was declared and tested.

Likewise,shape validation cannot identify swapped features or changed units. The[2,-1] coefficient vector assumes one fixed ordering. A valid two-column float32 array carrying different semantics can pass every tensor check and still be the wrong request. Save names,units and preprocessing metadata with the predictor,and use known input/output cases through that complete path.

The paired TensorFlow helper accepts a float32 NumPy array and returns a copied NumPy output. Its immutable tensor operations and explicit copy have different mechanics from PyTorch inference tensors,but the application-level goals are comparable:strict input policy,one output per record,batch parity and no caller-data mutation. Compare those observed contracts rather than treating training=False and inference_mode as identical APIs.""",
        """If a singleton call returns a scalar,inspect squeeze dimensions before changing caller code. If batch and singleton predictions differ,check mode,normalization and any cross-record computation. If outputs mutate source data,inspect aliases and where the owned copy is created. If a later gradient operation fails on an inference tensor,decide whether the original context was appropriate instead of forcing requires_grad onto a disconnected result.

If a finite request produces a nonfinite prediction,inspect arithmetic range and the declared output policy;input finiteness alone was insufficient. If all tensor checks pass but predictions are semantically wrong,check feature order and units. Keep these local contract failures separate from untested service-level concerns such as concurrent model mutation or request scheduling.""",
    )
    add_review(
        34,
        [
            "Duplicate weighting and subgroup uncertainty needed exact denominator counterexamples.",
            "Perturbation outcomes needed a stated target policy rather than an unchanged-prediction slogan.",
            "Privacy mechanisms,severity gates and finite empirical evidence needed separate meanings.",
        ],
        """Define the evaluation unit,conditions and failure severity before aggregating a score. Preserve numerator and denominator for each declared group,and distinguish an untested group from a tested group with zero observed errors. Choose any deduplication or weighting rule from the intended unit of analysis rather than deleting repeated-looking rows automatically.

Use perturbations only under an explicit target interpretation. Record privacy claims only when an actual mechanism and its analysis support them. The synthetic arrays are suitable for learning evidence accounting;they establish no privacy mechanism or universal robustness guarantee.""",
        """## Keep population,perturbation and mechanism claims separate

The original three records contain one error:groupA has1/2 and groupB has0/1. Overall error is1/3. Repeating the correct record c five additional times creates eight rows but only three unique IDs. A naive row-weighted error becomes1/8 even though no new case was tested. The apparent improvement comes entirely from changing the weight of one existing success.

This counterexample does not imply that every repeated identity should be removed. A longitudinal task may legitimately contain several observations from one person or device. The question is which unit the reported quantity is intended to average over,and whether dependence is modeled. Exact duplicate detection,source-family grouping and a weighting policy are related but different controls. A set of three IDs alone also does not prove those units are statistically independent.

Zero errors among one observation is weak evidence about an unknown error probability. Under a deliberately stated independent Bernoulli sampling model,the chance of observing zero errors in n cases is(1-p)^n. Solving(1-p)^n=0.05 gives a one-sided95% upper bound1-0.05^(1/n):0.95 at n=1 and approximately0.0295 at n=100. This arithmetic illustrates why denominators matter. The hand-selected synthetic cases do not automatically satisfy the random-sampling assumptions needed to interpret that bound as a population claim.

An empty group has no measured rate. Returning None preserves that absence;returning zero invents a successful observation. A report or chart should not replace missing rates with zero merely to fill a display. Likewise,a confidence calculation cannot create coverage for a group or condition that never appeared in the data. Keep coverage counts and the intended target population beside every aggregate.

The perturbation rule here is f(x)=1 when x>=0. Starting at one,the shifts-0.1,-0.9,-1.1 produce0.9,0.1,-0.1 and therefore labels1,1,0. If the target itself is defined by the observed sign,the final change is correct behavior after crossing the decision boundary. Calling it a robustness failure would assume an invariant label that the task definition does not support.

A different application might model these shifts as measurement noise while the latent class remains fixed. That is a different target policy and needs its own oracle. For this simple sign rule,perturbations with magnitude strictly below one cannot cross from the starting point to the negative side. That analytic statement is local to this scalar rule and declared perturbation set;it is not evidence that an arbitrary neural classifier is robust to all small changes.

Severity is another independent axis. Nine minor passes and one severe failure yield a90% overall pass rate. If the predeclared release rule blocks on any severe failure,the correct decision remains no-go. Choosing a favorable aggregate after observing the severe failure changes the decision policy. Preserve case-level identity,severity and the actual failed condition so a summary cannot erase it.

Privacy is not established by removing names from an example or by obtaining a good accuracy score. Differential privacy describes a randomized mechanism's output behavior under a defined change to a dataset. Its guarantee depends on the neighboring-dataset unit,privacy parameters and the mechanism/accounting assumptions. Record-level adjacency and person-level adjacency are different promises when a person contributes multiple rows. Clipping,noise,sampling and repeated releases require a coherent analysis;this chapter implements none of them. [NIST SP800-226](https://csrc.nist.gov/pubs/sp/800/226/final) discusses evaluation of such guarantees and implementation hazards.

An empirical privacy attack test and a mathematical privacy guarantee answer different questions. Failing to observe leakage in a few attempts does not prove a bound over all neighboring datasets and outputs. Conversely,a claimed formal bound does not remove the need to inspect the actual implementation,access controls and intended release. The lesson's model card therefore records synthetic teaching use and no privacy guarantee rather than promoting absence of personal data into a property of the training algorithm.

A useful card joins intended use,data/version identity,evaluation units,group counts,perturbation policy,severity results and untested conditions. It can summarize existing evidence but does not create it. The paired TensorFlow route uses the same reasoning fixtures,so framework choice does not change the denominator,independence or privacy interpretation.""",
        """If a rate improves after adding duplicate rows,recompute it at the declared independent-unit or weighting level. If a zero-error group looks conclusive,inspect its count and sampling assumptions. If a missing group displays zero,repair the missing-value representation rather than accepting an invented measurement.

If a perturbation changes a prediction,first decide whether the correct label should change too. If one severe failure disappears inside a high pass percentage,restore the predeclared severity gate. If a card claims privacy,locate the actual mechanism,unit and accounting evidence. Synthetic data,redaction and a finite attack set should not be substituted for a guarantee they did not establish.""",
    )
    add_review(
        35,
        [
            "The paired loss comparison needed its full per-ID table and covariance explanation.",
            "The three-point bootstrap needed an exact empirical distribution and a distinction from new evidence.",
            "Resampling units,training variability and selection history needed separate uncertainty contracts.",
        ],
        """Compare models on the same identified assessment units using a predeclared loss and subtraction order. Preserve the pairing before any resampling. Choose row,family or temporal-block resampling according to the unit whose variability the inference is meant to represent.

Treat a bootstrap over saved predictions as conditional on those fitted models and observed data. More resampling draws can reduce Monte Carlo approximation error,but cannot increase the number of independent assessment units or undo model selection on the final test. Combine uncertainty with practical effect size and other release gates rather than treating one interval as automatic approval.""",
        """## Derive the paired contrast and the finite bootstrap law

Align by stable ID before calculating losses. The fixture's dictionary insertion orders differ,so zipping values would compare unrelated targets and predictions. The correct table is:

| ID | Truth | A prediction | B prediction | A squared loss | B squared loss | A minus B |
| --- | --- | --- | --- | --- | --- | --- |
| a | 0 | 0 | 1 | 0 | 1 | -1 |
| b | 1 | 2 | 2 | 1 | 1 | 0 |
| c | 2 | 2 | 3 | 0 | 1 | -1 |

The mean contrast is-2/3 in squared-target units. Its sign favors A for this loss and these three cases. It does not mean A wins on every possible metric,group or deployment condition. Equal key sets are required before indexing;silently dropping missing predictions can select an easier assessment subset.

Pairing preserves shared case difficulty. In general,Var(lossA-lossB)=Var(lossA)+Var(lossB)-2Cov(lossA,lossB). Independently resampling the two models discards that covariance and answers a different question. The particular fixture has B losses all equal to one,so its covariance term is zero;it is not by itself a strong counterexample for every unpaired bootstrap mistake.

A separate analytic example makes the dependence visible. Suppose two cases have losses A=[1,11] and B=[0,10]. Every paired difference is one,so every paired resampled mean is one. Independent resampling can pair the easy A loss with the hard B loss or vice versa and create variation that was absent from the paired contrast. This explains the method without claiming that the original three-case code exercised that different fixture.

For the actual differences[-1,0,-1],an empirical draw has probability2/3 of-1 and1/3 of zero. Each bootstrap estimate averages three independent draws from that empirical distribution. Let K count the selected-1 values;then K has a Binomial(3,2/3) law and the estimate is-K/3:

| Resampled mean | Exact empirical probability |
| --- | --- |
| -1 | 8/27 |
| -2/3 | 12/27 |
| -1/3 | 6/27 |
| 0 | 1/27 |

The expected bootstrap mean is-2/3 and its variance is2/27 under this empirical resampling model. These are properties of resampling the three observed values,not a proof that the unknown population has this four-point distribution. The thousand generated estimates approximate these probabilities with random frequency variation. The reference checks shape,finiteness and the exact allowed range,not a guaranteed count for each value.

More draws refine the numerical approximation to that empirical distribution. They do not turn three cases into a thousand independent assessment observations. Even the ideal empirical percentile interval can be uninformative here:the lower tail includes-1 and the upper tail reaches zero. The code does not calculate or certify a particular confidence interval,and any interval method would still need its sampling assumptions and quantile convention stated.

If several rows come from one source family,resample families together when the intended independence is at that level. Define the estimand as well:equal family means and row-weighted population means differ when families have different sizes. Time dependence may require blocks or another design rather than an ordinary independent-row bootstrap. Stable row IDs alone do not resolve those dependencies.

The local torch.Generator makes this calculation reproducible without depending on unrelated global draws. A fresh generator seeded identically reproduces the index matrix in the tested environment. NumPy's generator in the paired TensorFlow route is a different random implementation;identical seed numbers do not require identical index matrices across the two libraries. Compare the statistical contract,allowed values and within-implementation replay rather than treating cross-library random bits as a shared oracle.

This resampling holds the fitted prediction vectors fixed. It does not include variation from retraining with a different initialization,batch order or training sample. If the decision concerns the whole fitting procedure,that uncertainty needs a broader experimental design. If test results are used to select another architecture,threshold or stopping rule,the test has become selection information. An unchanged filename cannot restore an untouched assessment boundary.

Finally,a negative point estimate is not a complete release decision. Record effect size,uncertainty,assessment coverage,severe failures and operating costs under their own evidence. The tiny fixture teaches pairing and resampling mechanics while making its limited independent sample size explicit.""",
        """If the contrast changes when dictionary order changes,repair the identity join. If a model lacks an assessment ID,stop instead of comparing a convenient intersection. If bootstrap draws exceed[-1,0] here,inspect index bounds,axis reduction and whether the paired difference vector was actually sampled.

If an unpaired method gives different uncertainty,inspect the covariance and resampling unit rather than choosing the narrower result. If repeated seeds disagree,check generator ownership and preceding draws. If a thousand draws are presented as a thousand new test cases,restore the distinction between Monte Carlo approximation and independent evidence. If final-test feedback changed a configuration,record the selection history before interpreting the reported interval.""",
    )
    add_review(
        36,
        [
            "The release capstone needed an analytic training/holdout oracle and explicit artifact boundaries.",
            "Hash integrity,metadata validation and publisher trust needed separate meanings.",
            "Local acceptance,negative-gate success,rollback identity and production readiness needed precise scope.",
        ],
        """Treat release as a conjunction of independently reviewable contracts rather than a filename or a score. Decide the predictor's schema,artifact identity,evaluation population and failure behavior before packaging. A required check that is missing is not equivalent to a pass,and an expected negative test passes only when the system rejects the invalid case as intended.

Keep the local teaching acceptance separate from production readiness. The current bundle proves a small trained function can be reconstructed and rejects a mismatched weight digest. A two-row visible holdout,an unexercised rollback name and no operational deployment test support a production no-go,which is a valid capstone conclusion.""",
        """## Connect the trained function to the released bytes

The training objective is L(w)=(14/3)(w-2)^2 on x=[1,2,3]. With learning rate0.01,the error e_t=w_t-2 follows e_(t+1)=(68/75)e_t. Starting at zero gives w_t=2-2(68/75)^t. After the fixed thirty updates,the analytic weight is approximately1.89420638. This derivation supplies an independent check on the training mechanism rather than relying only on the loop's finite-value assertion.

The held-out inputs are4 and5,with targets8 and10. The training-mean target baseline predicts four,so its squared errors are16 and36 and MSE is26. For the trained scalar model,the holdout MSE is((16+25)/2)(w_30-2)^2=82(68/75)^60,approximately0.229442. The threshold below26 is therefore interpretable for this visible fixture. It does not establish population quality:the rule y=2x is public,and both assessment inputs extrapolate beyond the training range.

The predictor is more than its state tensor. Its architecture is bias-free Linear(1,1),its dtype is float64,its feature list is['x'],and its output represents the same scalar target units. The manifest carries that schema,split IDs,step count and a digest of the serialized weight file. A future normalized or categorical model would also need its fitted preprocessing and label mapping. Reconstructing a tensor of the right shape cannot recover omitted semantic metadata.

The digest binds the manifest's expected weight identity to the actual saved bytes. The child recomputes SHA256 before loading and rejects a mismatch. The deliberate all-zero expected digest exercises that rejection path. It is a successful negative test because the invalid bundle fails with the expected diagnostic;it does not mean the corrupted bundle is an accepted release.

Integrity is narrower than authenticity or correctness. A digest does not identify a trusted publisher by itself,and a party able to replace both weights and the expected digest can create a different self-consistent pair. Correctly hashed bytes can also encode a poor model or dishonest split. The lesson's local artifacts are trusted teaching inputs,so it tests byte mismatch detection rather than a signed distribution or supply-chain system.

The child separately checks the exact schema before constructing the model. That catches a changed feature/dtype/width contract even if the weight bytes are unchanged. The current child does not independently revalidate every possible lineage field or reproduce training. The parent established disjoint split IDs earlier,and the manifest records them;those facts should not be inflated into authenticated data lineage or a recomputed training receipt.

Fresh-process prediction parity removes the possibility of satisfying the test by reusing the original model object. The child loads the saved state with weights_only=True on CPU,sets evaluation mode,and predicts the two fixed rows under inference_mode. The parent compares with its recorded outputs at1e-12 for this float64 fixture. That is a local inference-reconstruction proof,not an optimizer/RNG continuation proof. The earlier checkpoint and export lessons are separate evidence items rather than booleans to assume here.

A useful gate table keeps these distinctions explicit:

| Gate | Evidence in this capstone | Limit |
| --- | --- | --- |
| training procedure | thirty actual updates and analytic fixture | no unseen-population claim |
| weight integrity | recomputed digest and deliberate mismatch rejection | no publisher authentication |
| schema | exact child-side dictionary comparison | no general semantic-schema validator |
| reconstruction | fresh child predictions agree | not training continuation |
| assessment | two visible held-out rows and baseline | very limited coverage |
| rollback | previous identity v1 recorded | no previous artifact restored here |
| operations | not exercised | production remains no-go |

The previous-artifact string is a decision reference,not proof that a recoverable file exists or that it is compatible with current preprocessing. A real rollback rehearsal would load the identified previous artifact,verify its schema and predictions,and define the effect on any surrounding state. This exercise retains the reference without claiming that rehearsal occurred.

Publication and cleanup also have boundaries. The files are created in one owned TemporaryDirectory and removed after the checks. No server,registry or deployment is started. A completed save/load test does not establish crash-safe publication,concurrent-reader behavior or long-term retention. Those require their own artifact lifecycle and operational tests.

The final record can therefore say local_contracts_pass=True and production_go=False without contradiction. It acknowledges successful mechanics while preserving missing assessment and operational evidence. The paired TensorFlow release uses different formats and some different gates,but follows the same principle:each claim should be supported by the corresponding actual check,and a required unknown or failure must remain visible.""",
        """If the trained weight differs,compare the recurrence,step count,learning rate and reduction before investigating serialization. If the child loads but predictions differ,check architecture,dtype,feature semantics and the exact artifact path. If the corrupted digest is accepted,the integrity gate is disconnected from loading and the local acceptance must fail.

If a release record marks an unexecuted checkpoint or rollback test true,replace that assumption with the actual unavailable state and required next evidence. If a hash matches but evaluation is leaky,do not treat integrity as a quality override. If cleanup would target an existing learner directory,stop and restore the owned-artifact boundary. Preserve the production no-go until the named missing gates have independent evidence.""",
    )
