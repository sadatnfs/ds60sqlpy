"""Topic-specific depth review, kept separate from executable exercise specifications."""
from __future__ import annotations

from typing import Any

from depth_reviews_advanced import add_advanced_reviews

REVIEWS: dict[str, dict[str, Any]] = {}


def review(number: int, findings: list[str], decisions: str, deep_dive: str, diagnosis: str) -> None:
    REVIEWS[f"torch-{number:03d}"] = {
        "findings": findings,
        "decisions": decisions.strip(),
        "deep_dive": deep_dive.strip(),
        "diagnosis": diagnosis.strip(),
        "paired_guide_reviewed": f"tf-{number:03d}",
        "executable_change": False,
        "worked_code_change": False,
    }


review(1,
    ["The published holdout needed a clearer distinction from a blind assessment.", "Experiment selection and extrapolation needed a concrete decision trace.", "Malformed words obscured the evidence boundary."],
    """Use an experiment card whenever a dataset, objective or framework changes. Decide first whether the intended prediction concerns new rows from familiar sources, new source families, or a later time period. Those claims require different splits. A more complex model cannot repair a split that gives training access to the answer's source identity.

For the visible seven-point fixture, the useful decision is whether the implementation obeys its declared learning and evaluation procedure. The reader has already seen the relationship y=2x, so this fixture cannot serve as a blind test of scientific discovery. Treat a production decision as pending until a representative independent assessment and operational evidence exist.""",
    """## Build an auditable experiment card

An experiment needs a timeline as well as a table. First define the target and which inputs exist when a prediction is made. Next choose training and selection populations. Then fit parameters or preprocessing using only their allowed data. Freeze those decisions before examining the final assessment. If a later result changes the learning rate, feature set, threshold or stopping point, that result has become selection information even if the file is still named test.

The training-only constant in this chapter is four. Its value comes from targets 2, 4 and 6. Keep it fixed when calculating the later errors:

| Assessment input | Target | Fixed prediction | Prediction minus target | Squared error |
| --- | --- | --- | --- | --- |
| 4 | 8 | 4 | -4 | 16 |
| 5 | 10 | 4 | -6 | 36 |
| 6 | 12 | 4 | -8 | 64 |
| 7 | 14 | 4 | -10 | 100 |

The squared-error numerator is 216 and the denominator is four, giving MSE54 in squared target units. Choosing the assessment mean11 as the constant would lower the error, but it would be a different experiment because the prediction rule used assessment labels. A number cannot identify that information leak by itself; the decision history does.

Notice a second assumption: all assessment inputs lie outside the training input range1..3. The fixture therefore includes extrapolation. A larger error than on training does not uniquely diagnose overfitting; a different input range is also relevant. In a real application, report both the population relationship and the fitted rule. A random row split, a source-family split and a forward-time split answer different questions.

The hand-written rule y=2x has zero error here. That establishes its arithmetic on the visible points. It does not establish that an optimizer learned the rule, that an unknown population follows it, or that another feature pipeline preserves the same units. A training claim additionally needs an initial parameter state, an actual update sequence and an observed resulting state. Later chapters provide those receipts one operation at a time.

A framework comparison is another controlled experiment. Match record identities, feature order, dtype, parameter initialization, objective denominator, optimizer rule and model mode. Compare forward predictions before loss, loss before gradients, and gradients before updated parameters. If one implementation returns a matching scalar but a different gradient, the comparison has already failed even though the headline loss agrees.

A defensible card ends with a bounded conclusion and the next evidence needed. For this fixture: arithmetic and procedure can be checked; population reliability remains unestablished. For a later deployment: define the independent unit, intended operating range, error costs and operational acceptance before treating a model score as permission to use it.""",
    """If a result seems unexpectedly strong, reconstruct which labels influenced every decision. A changed preprocessing statistic or threshold can use assessment data without appearing in the optimizer loop. Check row identities and source-family identities separately; distinct row names do not prevent a shared account or duplicated document from leaking across a split.

If the constant baseline differs from four, inspect which target population was averaged. If the MSE differs from54, inspect the four residuals and denominator before changing a model. If a report calls y=2x trained, locate the actual initial state and updates. If no updates ran, label it an analytic oracle. Finally, distinguish the visible teaching holdout from an undisclosed assessment: preserving its programmatic split is valuable procedure evidence, but the learner already knows its answers.""")

review(2,
    ["The decision section was empty.", "Storage offsets, contiguity and ownership needed separate reasoning.", "Broadcast pairing needed a complete numerical counterexample."],
    """Use a view when shared storage is intentional and the consumer's mutation behavior is controlled. Use clone when the interface promises independent storage. Use contiguous to satisfy a layout requirement only after establishing that requirement; it can return the existing tensor when the layout is already suitable, so it is not an ownership guarantee.

Choose dtype and device at the input boundary rather than hoping an operation converts them as intended. Floating model inputs, integer class indices and Boolean masks have different roles. Before a paired loss or subtraction, require the semantic axes and record identities to match, not merely equal lengths or a broadcast-compatible shape.""",
    """## Trace axes, storage and pairing separately

For a contiguous2-by-3 tensor containing0 through5, the stride tuple(3,1) means one step along the first axis moves three stored elements and one step along the second moves one. Ignoring a nonzero base storage offset, element(i,j) is located at element offset3i+j. In float64 each element uses eight bytes, so offset5 corresponds to40 bytes from that base. Strides describe storage movement in elements, not a count of rows or bytes.

Transposing gives shape(3,2) and strides(1,3). The value at transposed[2,1] is the original[1,2], still five. No rearrangement of the underlying values is required for that interpretation. A contiguous materialization may allocate a new ordering for a later operation, but the fact that a tensor is contiguous does not establish that nobody else shares its storage. The official view documentation makes that aliasing boundary explicit. [PyTorch2.9 tensor views](https://docs.pytorch.org/docs/2.9/tensor_view.html).

The worked sequence deliberately mutates state. ExampleA creates x, ExampleB takes its first-row view and changes x[0,0] to99, and ExampleC clones the now-mutated tensor. Its correct comparison is therefore clone=-1 versus original=99. Re-running ExampleC alone with an unrelated x would be a different fixture. Keep the stated sequential scratch-file contract visible when reproducing the examples.

Copying storage and changing the gradient graph are different operations. clone provides independent storage but can remain connected to the source through autograd. Detach changes the differentiation boundary but can still share storage. A later inference snapshot that needs both properties may require both operations. Do not infer either property from a convenient display or from reshape, which can choose a view or a copy according to layout.

Broadcasting provides a second independent counterexample. With v=[1,2,3] and column=v[:,None], the right-aligned shapes are(1,3) and(3,1). Their difference is:

| Column value | Difference against vector1,2,3 |
| --- | --- |
| 1 | [0,1,2] |
| 2 | [-1,0,1] |
| 3 | [-2,-1,0] |

The intended paired differences are only the diagonal zeros. The broadcast operation instead creates nine comparisons whose squared mean is12/9=4/3. Reducing that grid to one scalar cannot restore the lost pairing. A model can therefore optimize a nonzero objective even though every intended prediction equals its target.

A practical tensor boundary should name every axis, required dtype, device and ownership rule. A shape check catches a column/vector mismatch, but it cannot detect that two equally shaped batches have different record orders or units. Keep those semantic checks beside the tensor metadata. The framework enforces legal arithmetic; the application defines which arithmetic corresponds to the task.""",
    """When a loss unexpectedly becomes a matrix, print full shape tuples before flattening or squeezing. A vector and a one-column matrix can have the same length while producing a pairwise grid. Check the actual row identities before any reshape repair.

When caller data changes, identify views and in-place writes. Replacing view with reshape does not establish independent ownership; test the promised mutation boundary with a deliberately changed output. When view rejects a layout, inspect strides and the required logical order instead of transposing until dimensions happen to fit. A contiguous copy can solve a layout requirement while leaving a semantic axis mistake untouched. When arithmetic raises a device or dtype error, repair the declared boundary explicitly rather than broadly converting class indices, masks and model features to the same representation.""")

review(3,
    ["The decision section was empty.", "Forward layout and parameter count needed a shape ledger.", "Registration, differentiation and optimizer membership needed clearer separation."],
    """Use an affine layer as a directly inspectable baseline when an additive combination of declared features is meaningful. Add nonlinear layers only when the task and evidence justify their extra behavior. The same shape can encode different feature orders or units, so an accepted matrix multiplication is not a complete model-schema check.

Keep parameter registration separate from trainability and optimizer membership. A registered Parameter can be frozen, and an optimizer can still hold an obsolete parameter object after a module is replaced. This early chapter establishes the state inventory; later transfer and checkpoint chapters examine how that inventory changes over time.""",
    """## Derive the forward map and parameter contracts

Let a batch haveB observations,I input features andO outputs. The mathematical row-vector expression uses X shaped(B,I), W shaped(I,O) and b shaped(O), producing Y shaped(B,O). PyTorch stores the corresponding Linear weight as(O,I), so its forward expression is X@weight.T+b. The transpose translates the storage convention; it is not a proposal to exchange the observation and feature axes. [PyTorch2.9 Linear](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Linear.html).

| Object | This fixture | General contract |
| --- | --- | --- |
| Input X | (2,3) | (B,I) |
| Stored weight | (1,3) | (O,I) |
| Mathematical W | (3,1) | (I,O) |
| Bias | (1,) | (O,) |
| Output | (2,1) | (B,O) |

For the first row[1,2,3], the products are1,0,-3. Adding bias2 gives zero. The second row[0,1,0] contributes zero before the same shared bias, giving two. The bias is not a separate fitted offset for each observation. WithO outputs there areI×O weight scalars andO bias scalars, orO(I+1) total. ChangingB changes the number of evaluated rows, not the parameter count.

Suppose an upstream loss supplies derivatives g1 and g2 for these two scalar outputs. The stored weight gradient is[g1,2g1+g2,3g1], and the bias gradient isg1+g2. The bias gradient sums over the batch because one bias participates in both outputs. Each input-row gradient is its upstream scalar multiplied by[1,0,-1]. These shapes can be predicted before using autograd:weight.grad must match(1,3),bias.grad must match(1,),and input derivatives match(2,3).

A feature-order mistake can remain invisible to every dimension check. If the first input is accidentally exported as[3,2,1], its output becomes3-1+2=4 instead of zero while all shapes remain valid. Likewise,a centimeter-to-meter conversion requires a corresponding weight interpretation if the represented function is to stay the same. The data schema must therefore preserve names,order and units beside the width.

Autograd and module registration answer different questions. A plain tensor with requires_grad=True can participate in a differentiable computation, but model.parameters() will not discover it merely because it is an attribute. Assigning nn.Parameter registers it. Registration does not require that gradients currently be enabled:freezing can turn requires_grad off while retaining the parameter in the module's state. Buffers form another category of registered state introduced later.

The known-value initialization runs under no_grad so assignment is not recorded as part of the differentiation graph. It does not make the layer permanently nontrainable. Calling the layer computes outputs but does not update parameters;an optimizer update is a separate later operation. These distinctions let the reader locate whether a failure concerns the forward function,the differentiation graph,the state inventory or the update mechanism.""",
    """If a matrix product fails, nameB,I andO and check the shared feature dimension before adding a transpose. If output width unexpectedly grows, inspect the bias axis. If dimensions pass but a prediction differs, calculate the first row's dot product and then inspect feature order and units.

If a tensor receives a gradient but does not move, compare its identity with the objects returned by model.parameters() and held by the optimizer. Conversely,a frozen Parameter can remain in state_dict without receiving a gradient. Count scalar entries with numel;counting Parameter objects would report two objects instead of four scalars in this fixture. During framework comparison, transpose the Dense kernel into the Linear storage layout explicitly and compare the first forward result before interpreting any training difference.""")

review(4,
    ["The decision section was empty.", "Mean reduction needed a batch-by-output derivation and masked-gradient trace.", "Objective weighting and metric preference needed concrete comparisons."],
    """Choose the reduction and participation unit before comparing model scores or learning rates. Elementwise means are appropriate only when every included element should receive equal weight. An equal-example objective,equal-group objective andequal-token objective can differ when lengths or group sizes differ. Preserve the numerator and denominator as inspectable quantities.

Use squared error when its penalty matches the problem and its units are understood. Report another metric when it answers a useful evaluation question,but do not choose that metric after seeing which model it favors. A changed reduction changes the objective andgradient scale;it is not automatically evidence that the optimizer became more orless stable.""",
    "## The denominator determines the gradient\n\nFor predictions and targets with identical shape(B,D), let r_bd=prediction_bd-target_bd. The squared-error sum is S=Σ_bΣ_d r_bd². PyTorch's mean MSE divides byB×D,so L=S/(BD). Its derivative with respect to each prediction is2r_bd/(BD). The sum objective instead gives2r_bd. This is why changing a reduction changes every gradient even when the forward residuals are identical. [PyTorch2.9 MSELoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.MSELoss.html).\n\nFor the residual vector[1,-1,2], S=6 andN=3. The sum gradient is[2,-2,4],while the mean gradient is[2/3,-2/3,4/3]. Duplicating every record doubles the sum andduplicates its derivative contributions. The mean objective remains two because both numerator and denominator double. This argument assumes equal replication of all participating entries;selectively repeating hard examples changes their weighting.\n\nA two-output example makes the semantic unit visible. WithB=2,D=2 andall residuals equal to one,the element mean is one,the total sum is four,and the mean of per-example feature sums is two. The first objective gives each scalar derivative0.5;the last gives each scalar derivative1. Both can be mathematically legitimate,but they encode different scaling. A framework cannot infer which one the application intended from the word mean.\n\nMasking must use the same participation rule in the numerator and denominator. Keeping only the first two residuals gives numerator2,count2 andloss1. Zeroing the third contribution andthen averaging the original three positions gives2/3. The valid mean gradient for the retained residuals is[1,-1];dividing by the padded length shrinks it to[2/3,-2/3]. Padding can therefore change both reported quality and training updates without adding any new observation.\n\nAn all-false mask is not the same as two accepted residuals equal to zero. The former has no defined mean denominator;the latter has a valid zero loss. Decide whether the surrounding pipeline should reject an empty objective or skip an update under an explicit policy. Silently calling it a perfect batch hides a missing-data condition.\n\nGroup weighting provides another counterexample. If one group contains residual[2] andanother contains[0,0,0],the all-record MSE is4/4=1. The unweighted mean of group MSEs is(4+0)/2=2. The correct choice depends on whether equal influence belongs to observations or groups. Accumulation anddistributed-gradient chapters return to this denominator problem when batch sizes differ.\n\nFinally,loss and evaluation metric need not rank candidates the same way. Residuals[0,0,4] have MAE4/3 andMSE16/3;residuals[2,2,2] have MAE2 andMSE4. Squared error prefers the second candidate because it penalizes the large miss more strongly,while absolute error prefers the first. State the objective anderror costs before seeing the ranking.",
    "If duplicating a batch changes a reported mean,inspect the actual reduction and any mask or weight denominator. If adding padding makes the objective smaller,compare the included count with the tensor's total element count. If gradients differ by a constant factor across implementations,check batch andfeature reductions before adjusting the learning rate.\n\nIf the forward scalar agrees but gradients do not,inspect per-entry losses andshapes. Broadcasting can create a different pairing that accidentally shares one scalar value. If a masked batch has no participants,handle that absence explicitly instead of widening a tolerance aroundNaN. During TensorFlow comparison,inspect both feature reduction andbatch/sample weighting;matching a function's name does not establish that the same axes entered the denominator.")


review(5,
    ["The decision section was empty.", "Finite differences needed a truncation/cancellation derivation and a distinction from learning-rate steps.", "The numerical helper did not reject a nonfinite point when a constant function hid it."],
    """Use finite differences as a small independent diagnostic for a smooth scalar function or a selected coordinate of a larger computation. Recompute the complete forward function at each probe and keep parameters, data, model mode and randomness fixed. A stochastic dropout sample or changed minibatch can overwhelm the small difference being measured.

Prefer an analytic derivative when a tiny expression permits one, and compare several sensible probe sizes instead of declaring the smallest h best. Avoid interpreting a symmetric probe at a known kink as proof of an ordinary derivative. The helper is a bounded numerical check, not a certificate for every floating-point scale or a replacement for understanding the function's domain.""",
    "## Derive the slope before using it as an update\n\nFor f(w)=(w-2)², expand the derivative or apply the square rule to obtain f'(w)=2(w-2). At w=0 the loss is four and the derivative is -4. These are different quantities with different units: the derivative measures loss change per unit of w. A learning rate converts that sensitivity into a chosen parameter displacement. With rate0.1, the update is0-0.1(-4)=0.4 and the recomputed loss is(0.4-2)²=2.56.\n\nThe central finite difference uses two probes separated by2h:\n\n`D_h = [f(w+h)-f(w-h)]/(2h)`.\n\nExpanding this particular quadratic gives f(w+h)-f(w-h)=4h(w-2), so D_h=2(w-2) exactly in real arithmetic. This special cancellation explains why the three supplied h values agree unusually well. It does not establish that central differences are exact for arbitrary nonlinear functions. For a sufficiently smooth general function, the leading truncation error is proportional to h² and a third derivative near the probe point.\n\nA forward difference has a different error even on this quadratic. At zero, [f(h)-f(0)]/h=-4+h. Thus h=0.1 gives -3.9, h=0.01 gives -3.99, and h=0.001 gives -3.999. The visible offset is a property of the numerical approximation, not an autograd error. Deriving the approximation's expected bias prevents a correct implementation from being rejected for the wrong reason.\n\nFloating-point cancellation pushes in the opposite direction from truncation error. As h shrinks, the two function values can become nearly equal compared with their magnitude. Their subtraction can lose meaningful digits, and a sufficiently small perturbation may not change the represented point at all. Scaling, dtype and the function's local behavior all matter. Sweep several probe scales and inspect the error curve rather than applying a universal h or tolerance.\n\nThe probe distance h is not the optimizer learning rate. A probe estimates local sensitivity without choosing a training trajectory; an update deliberately changes model state. A negative derivative identifies a locally descending direction, but a large finite update can still overshoot. For the supplied quadratic, a rate1.1 update from zero moves to4.4 and increases loss to5.76, despite using the correct derivative.\n\nAt abs(w) around zero, the left slope is -1 and the right slope is+1. A symmetric probe returns zero because the sides cancel, even though no unique ordinary derivative exists. ReLU gives a related counterexample: its symmetric slope at zero is 0.5 while PyTorch's selected backward convention is zero. Use a smooth point when checking equality with a classical derivative; at a kink, explain the convention separately.\n\nFinally, `autograd.grad` returns the requested derivatives. It does not mean that the leaf's `.grad` buffer was populated. The return tuple and the accumulation behavior of `backward` are separate interfaces. [PyTorch2.9 autograd.grad](https://docs.pytorch.org/docs/2.9/generated/torch.autograd.grad.html). A returned -4 with w.grad stillNone is therefore expected here, while a genuinely disconnected path requires a different diagnosis.",
    """If the numerical slope changes erratically as h shrinks, inspect whether w+h and w-h remain distinct represented numbers and whether the function values are finite. If the result is a stable factor-of-two error, check the2h denominator. If the probe reports zero unexpectedly, verify that the callable recomputes the complete function rather than closing over a previously calculated activation.

Reject a nonfinite probe point explicitly, even when a constant callable would return finite outputs and hide that invalid point. Keep a missing gradient path separate from a connected derivative of zero. If a correct negative derivative produces a higher updated loss, recompute the new objective and inspect the learning rate before altering the derivative. At a kink, record one-sided behavior and the framework convention instead of widening a tolerance until incompatible mathematical objects appear equal.""")

review(6,
    ["The decision section was empty.", "The chain factors needed an exact forward/backward table.", "In-place version checking and saved-graph lifetime needed a concrete failure sequence."],
    """Use an explicit intermediate trace when introducing a new differentiable operation, debugging a custom backward rule or comparing two implementations with matching forward values. A small scalar chain lets every local factor be checked independently before the same reasoning is applied to vectors and matrices.

Prefer a fresh forward graph for each ordinary training iteration. Retain a graph only when a deliberate algorithm needs repeated derivative queries from the same unchanged forward computation. Treat in-place mutation as a state-ownership decision, not an automatic memory optimization. Use documented update and copying boundaries rather than bypassing autograd safeguards with `.data`.""",
    """## Trace the graph and its saved values

The chain is w→z→a→L, with z=2w, a=z² and L=(a-1)². At w=1, the full trace is:

| Operation | Forward value | Immediate derivative |
| --- | --- | --- |
| z=2w | z=2 | dz/dw=2 |
| a=z² | a=4 | da/dz=2z=4 |
| L=(a-1)² | L=9 | dL/da=2(a-1)=6 |

Backward composes sensitivities in reverse dependency order: dL/dw=6×4×2=48. Omitting the inner scale gives24, even though every forward value remains correct. Changing the inner scale to three gives z=3,a=9,L=64 and derivative16×6×3=288. A learning-rate adjustment that hides the missing factor for scale2 would not repair the algorithm for scale3.

The scalar expression can also be expanded to L=16w⁴-8w²+1. Its derivative64w³-16w equals48 at one, providing a symbolic check independent of the local-factor table. The finite-difference check recomputes the complete expression at1+h and1-h. Holding a=4 fixed while perturbing w would instead probe a constant function with slope zero. Equal forward values at one point do not establish equal dependencies.

For larger tensors, reverse-mode differentiation propagates vector-Jacobian products rather than materializing every possible derivative matrix. A scalar loss supplies the initial sensitivity one; each operation transforms the incoming sensitivity using its saved forward values. This explains why the graph must retain information from the actual forward pass and why asking for derivatives of a nonscalar result requires an explicit upstream-gradient convention.

Consider `objective = value.square()` when value is two. Backward needs the original value to produce derivative four. If code then changes that storage to three before calling backward, the old objective still represents the forward value four, but the saved input has changed. Computing derivative six from the new storage would mix two different states. PyTorch's saved-tensor version checks reject such an invalid sequence rather than silently returning that mixed-state result. [PyTorch2.9 autograd mechanics](https://docs.pytorch.org/docs/2.9/notes/autograd.html).

Using no_grad around the mutation prevents recording that new operation. It does not restore the saved value or make the earlier graph consistent. A safe ordinary update sequence completes the current derivative computation, updates parameter state at a deliberate boundary, then recomputes the next forward graph. Clone can provide separate mutable storage, but a clone is not a substitute for knowing which value each graph depends on.

After a normal derivative computation, saved intermediates can be released. Keeping a reference to loss does not promise another backward pass can reconstruct those released values. Repeated training usually needs a new forward pass, whereas an algorithm intentionally querying multiple derivatives can request graph retention and accept its memory cost. Do not confuse retaining a graph with accumulating gradients across distinct fresh graphs.

ReLU adds a separate mathematical boundary. At a negative input the derivative is zero; at a positive input it is one. At zero there is no unique classical derivative, and PyTorch chooses zero for backward. The numerical convention is not a graph-disconnection error. It should be recorded explicitly when designing derivative tests rather than judged against a symmetric probe's0.5 as if both were the same object.""",
    """For a factor mismatch, inspect the local derivative table before changing a learning rate. For a zero finite difference, ensure the complete function is recomputed at each perturbed input. For a tensor-version error, locate the first in-place write to a value saved by the forward graph, including writes through an alias or a no_grad block.

A leaf-mutation guard and a later saved-value version error describe different failure points. Do not silence either with `.data`; that can replace an informative failure with an incorrect derivative. If a second backward reports released intermediates, decide whether the algorithm needs a fresh forward computation or deliberate graph retention. If an activation derivative disagrees only at a kink, compare one-sided slopes and the documented convention before investigating numerical precision.""")


REVIEWS["torch-005"]["executable_change"] = True
REVIEWS["torch-005"]["worked_code_change"] = True


review(7,
    ["The decision section was empty.", "Graph history, gradient buffers, storage ownership and module mode needed a separate-state comparison.", "None-versus-zero gradients needed an optimizer-aware interpretation."],
    """Choose each control for its specific purpose. Use backward when the training algorithm accumulates contributions into parameter gradients. Clear those buffers between independent optimizer steps, while retaining them deliberately across correctly scaled microbatches. Use retain_grad only when an intermediate derivative is useful for a bounded diagnostic.

Use detach to stop differentiation through a value, clone to establish independent storage, and their combination when an observation must have both properties. Use eval to select evaluation behavior of stateful or stochastic layers. Use no_grad or inference_mode separately when recording derivatives is unnecessary. These choices should remain explicit because gradient-based explanation can legitimately run a model in evaluation mode.""",
    "## Separate four kinds of state\n\nA tensor's value, storage aliases, graph role and stored gradient are related but different facts. Module mode adds another independent control:\n\n| Control or observation | What it changes or reports | What it does not establish |\n| --- | --- | --- |\n| requires_grad | Whether relevant operations can be tracked for derivatives | Independent storage or optimizer membership |\n| is_leaf and grad_fn | Role in the recorded graph | Whether the Python variable name sounds like a parameter |\n| backward | Adds derivative contributions to eligible stored gradients | A parameter update |\n| detach | Removes the current differentiation connection | A copy of storage |\n| clone | Copies storage | A detached gradient history |\n| no_grad | Suppresses recording for ordinary operations in its scope | Evaluation behavior of Dropout or BatchNorm |\n| eval | Selects evaluation behavior of affected modules | Disabled autograd or cleared gradients |\n\nFor tensors requiring gradients, a leaf is not the result of a tracked differentiable operation. An intermediate such as2w has an operation history even when assigned to a named variable. Tensors not requiring gradients are treated as leaves by convention. A conversion or copy operation can therefore change the graph role of a tracked tensor;inspect the actual metadata instead of assuming every user-named tensor is a leaf. [PyTorch2.9 is_leaf](https://docs.pytorch.org/docs/2.9/generated/torch.Tensor.is_leaf.html).\n\nThe first fixture has w=0 and intermediate=2w. Backpropagating that scalar gives incoming sensitivity one at the intermediate and sensitivity two at w. The intermediate's gradient is visible only because retain_grad was requested. Its absence by default would be a storage-policy observation,not evidence that the chain rule failed.\n\nNow reset w.grad to None and compute(w-2)². The new contribution is -4. Building the same expression again creates a fresh graph,but backward adds another -4 into the existing gradient buffer,leaving -8. A fresh graph does not clear a previous buffer. Resetting to None before the third computation gives -4 again without changing w itself.\n\nNone and numeric zero have different meanings. None may indicate that no gradient has been stored,that a reset occurred,that the tensor was unused,or that an intermediate was not retained. A numeric zero can be the correct derivative of a connected path. Optimizers can also treat them differently:parameters with None gradients are commonly skipped,whereas zero gradients may still interact with momentum or weight decay. This distinction is documented for zero_grad rather than being merely a display detail. [PyTorch2.9 zero_grad](https://docs.pytorch.org/docs/2.9/generated/torch.optim.Optimizer.zero_grad.html).\n\nThe detach example changes shared storage. After detached=source.detach(),writing detached[0]=9 changes source[0] as well. The earlier source.detach().clone() snapshot remains one because it owns a copy. The snapshot is suitable for comparing later mutation,but detaching a value that the objective actually needs can break learning. Ownership and differentiation must both match the intended interface.\n\nFinally,model.eval() does not stop derivatives through a Linear layer. It changes a module's training flag and the behavior of layers that consult it. no_grad affects ordinary operation recording while leaving the original tensor's requires_grad flag unchanged;factory operations with an explicit requires_grad argument are a documented exception to treating the scope as a blanket flag rewrite. Keep mode,recording and gradient-buffer decisions separate in the surrounding training or inference function.",
    """If a gradient doubles across supposedly independent steps,check where zero_grad occurs and whether backward was called twice. If an intermediate's grad is None,inspect is_leaf and whether retain_grad was requested before declaring the path disconnected. If a frozen or unused parameter moves,inspect optimizer state and the difference between a zero gradient and no gradient.

If a saved observation changes later,look for shared storage through detach or a view. If a model in eval mode still creates a graph,that is expected unless gradient recording was separately disabled. If a logging detach unexpectedly stops training,trace whether the detached value was fed back into the loss. These diagnoses require inspecting values,graph connections,buffers and module mode independently rather than replacing every None with zero or adding no_grad around the whole loop.""")

review(8,
    ["The decision section was empty.", "The one-step oracle needed a full objective and stability derivation.", "The broadcast counterexample needed to show a changed optimum,not only a different first gradient."],
    """Use this one-step audit before trusting a longer training loop,porting an optimizer path or comparing frameworks. Fix every input,initial value and reduction so a disagreement can be localized to forward computation,backward accumulation or parameter mutation. Start with plain SGD,zero momentum and zero weight decay before adding stateful optimizer behavior.

A successful update is evidence about this numerical mechanism. It is not a model-quality result,and the exact learning-rate interval derived here belongs only to this one-parameter quadratic. Later nonlinear,stochastic and distributed models require their own scale and stability analysis rather than borrowing this bound as a default.""",
    """## Derive the complete scalar training transition

The hypothesis is prediction_i=w x_i for x=[1,2,3] and y=2x. With a mean over three paired observations,the objective simplifies to:

`L(w) = (1²+2²+3²)(w-2)²/3 = (14/3)(w-2)²`.

Its derivative is`g(w)=(28/3)(w-2)`. At w=0,the predictions are zeros,residuals[-2,-4,-6],squared errors[4,16,36],loss56/3 and gradient-56/3. The input features can remain ordinary constant tensors because the requested derivative is with respect to w. Targets also remain fixed labels rather than state the optimizer is allowed to change.

For learning rateη=1/10,plain SGD gives w_new=w-ηg=28/15. The new residual is(w_new-2)x=(-2/15)x,so its entries are[-2/15,-4/15,-6/15]. Squaring and averaging gives56/675. The before-loss,gradient,new parameter and after-loss are four separately inspected observations:

| Stage | Weight | Quantity observed |
| --- | --- | --- |
| Forward | 0 | L=56/3 |
| Backward | 0 | stored gradient=-56/3 |
| Step | 28/15 | parameter changed by28/15 |
| New forward | 28/15 | L=56/675 |

Backward does not perform the update,and step does not recompute the loss. The old loss tensor still records the earlier forward result after the parameter changes. The fresh Parameter starts with no stored gradient,which makes the first backward unambiguous;repeated independent steps need an explicit clearing policy. The SGD API specifies how momentum,weight decay and other options would change this simpler transition. [PyTorch2.9 SGD](https://docs.pytorch.org/docs/2.9/generated/torch.optim.SGD.html).

The exact quadratic also permits a stability calculation. Let e=w-2 be the error from the optimum. One update gives e_new=(1-28η/3)e. Repeated full-batch updates contract this error only when|1-28η/3|<1,or0<η<3/14. Atη=0.1,the contraction factor is1/15. Atη=0.25,it is-4/3:the parameter crosses the optimum and its error grows. The first weight becomes14/3 and the new loss896/27,larger than the initial56/3 despite a correct derivative.

Changing to a summed objective changes that bound because the gradient is three times larger. This is why learning-rate claims require a declared denominator. The result is exact for this fixed convex scalar objective;it is not a universal neural-network learning-rate rule.

The mistaken column target produces a different objective over every input-target pair. Its mean can be expanded as`L_bad(w)=(14/3)w²-16w+56/3`. At zero,it shares the correct initial loss56/3,but its derivative is-16. Its optimum is12/7 rather than two,and its minimum is104/21 rather than zero. This is a changed statistical pairing,not merely an objective-scale factor. Adjusting the learning rate to disguise the first gradient difference cannot restore the intended optimum.

An audit should therefore check the residual shape and per-record identity before reducing to a scalar. It should then compare the derivative with the independent NumPy probe and verify that the optimizer owns the exact Parameter object whose gradient was computed. Only after those boundaries pass does a longer loop add useful evidence.""",
    """If backward produces the right derivative but w remains zero,check whether step ran and whether the optimizer contains that exact Parameter object. If w changes but the reported loss stays56/3,inspect whether code reused the old loss tensor instead of recomputing the forward expression. Clearing gradients should leave the updated parameter unchanged.

If the initial loss agrees but the gradient is-16,inspect for the(3,3) broadcast grid before changing SGD. If a correct gradient increases the loss,check update sign and learning rate;the exact quadratic bound distinguishes overshoot from a differentiation defect. If a second update is identical to the first,check for a stale stored gradient. Preserve the four-stage trace so a failure can be attributed to the correct boundary rather than hidden inside one final scalar.""")


review(9,
    ["The decision section was empty.", "Batch/update counts needed an exact parameter-state trace.", "Metric weighting needed separation from evaluation at the final model state."],
    """Choose batch size together with the intended update budget, memory budget and statistical unit. Equal epochs do not imply equal optimizer-step counts, and equal step counts do not imply equal numbers of observed records. Record both when comparing runs. Keep a short final batch unless a documented shape or algorithm requirement justifies dropping it.

Use zero_grad between independent minibatch updates. If memory constraints require accumulation, define a separate policy that holds parameters fixed while accumulating correctly weighted contributions and steps once at the intended boundary. Do not treat a loop that steps repeatedly on an uncleared gradient as an equivalent large-batch implementation.""",
    """## Trace every update at the state where its gradient was computed

Six records with batch size two produce three batches per epoch:IDs[1,2],[3,4],[5,6]. With one optimizer step per batch,one epoch means three updates. At batch size one,the same epoch means six updates. Neither count identifies the resulting parameter trajectory without the data order,loss reduction andlearning rate.

For this scalar fixture,y=2x and each batch mean loss has derivative2 mean(x²)(w-2). With rate0.01,the exact correct trajectory is:

| Batch inputs | mean(x²) | Weight before | Fresh gradient | Weight after |
| --- | --- | --- | --- | --- |
| [1,2] | 2.5 | 0 | -10 | 0.1 |
| [3,4] | 12.5 | 0.1 | -47.5 | 0.575 |
| [5,6] | 30.5 | 0.575 | -86.925 | 1.44425 |

Each gradient uses the latest weight. Clearing the buffer before each backward ensures that the applied gradient is precisely the one shown in its row. The same records in a different order can yield another trajectory because their local curvature and current parameter state differ.

Without clearing,the first step is still0.1. The next backward adds -47.5 to the stored -10,giving -57.5,and the second weight becomes0.675. The final fresh derivative is -80.825,but the accumulated buffer becomes -138.325 and the final weight2.05825. These are derivatives evaluated at different historical weights. A single constant learning-rate adjustment does not turn this procedure into the intended minibatch algorithm.

Interestingly,the incorrect endpoint happens to lie closer to the known optimum two on this tiny sequence. That does not make the implementation correct. It violated the declared update rule,and another sequence can behave very differently. An acceptance test must inspect the mechanism and state trace rather than reward whichever accidental final training loss is smaller.

Intentional accumulation is different. Hold w fixed,compute each microbatch's contribution to one declared objective,accumulate the scaled gradients,and call step once. For the full six-record mean at w=0,the gradient is2 mean(x²)(-2)=-182/3. One rate0.01 step gives91/150,about0.606667. This differs from the three-step minibatch result because it is one update from one fixed state. When microbatch sizes differ,weight each microbatch mean by its participating count divided by the total count.

Metric reporting needs the same denominator discipline. A mean loss two from two records contributes numerator four;mean loss eight from one record contributes numerator eight. The record-weighted mean is(4+8)/3=4,not the unweighted batch-mean average five. But there is another interpretation boundary:losses measured before successive updates belong to different model states. Their weighted average is an online training statistic,not necessarily the loss of the final model. A final-model metric requires a separate fixed-state evaluation pass.

Record identities protect the training population. A shared permutation of x andy preserves y=2x after shuffling. Independently permuting either side changes the prediction task while leaving each marginal array plausible. For five records at batch size two,the tail has one record;dropping it changes which observations participated in the epoch. The loop should retain that decision in its budget and denominator report.""",
    """If the number of steps is wrong,inspect the batch slices and tail policy before looking at the optimizer. If a second step is too large,inspect whether the gradient buffer still contains a prior contribution. Compare the exact0.1,0.575,1.44425 trace with the incorrect uncleared trajectory rather than accepting only a finite endpoint.

If batch-size changes appear to improve a model,compare examples seen,update count and ordering before attributing the result to batch size alone. If an epoch metric depends on how records are partitioned into batches,reconstruct loss sums and counts. If it is reported as a final-model score,check whether all records were evaluated at one fixed final state. Finally,keep record IDs through shuffling so a correct-looking tensor shape cannot hide broken target pairing.""")

review(10,
    ["The decision section was empty.", "Subset delegation and split identity needed a concrete index/shape trace.", "The held-out perturbation needed exact fitted-statistic arithmetic and claim limits."],
    'Choose the split unit from the intended deployment claim. For new-account prediction,keep all records from each account on one side of the split. For a future-time claim,also respect when inputs andlabels become available. A random row split is appropriate only when its independence andinformation assumptions match the task.\n\nUse Dataset andSubset to implement access after that design has been chosen. Fit normalization or other learned preprocessing from the training population andfreeze it for the declared inductive assessment. A deliberately transductive method using target-population covariates is a different protocol andmust be evaluated andreported as such,rather than quietly changing this training-only contract.',
    "## Trace selection, fitted state and delegated access\n\nThe eight literal records form four account groups. Training selects original indices0,1,2,3 fromA and B;assessment selects4,5,6,7 fromC andD. The two Subset objects do not copy or redefine those records. They map their local index into the original dataset. Thus assessment[0] returns original identity4,accountC,value20. A local batch position zero is not a replacement for the source identity.\n\n| Population | Original identities | Values | Mean |\n| --- | --- | --- | --- |\n| Training accountsA,B | 0,1,2,3 | 1,3,5,7 | 4 |\n| Assessment accountsC,D | 4,5,6,7 | 20,22,30,32 | 26 |\n| All records | 0..7 | All eight values | 15 |\n\nEach item returns a scalar tensor plus identity andgroup metadata. Stacking the four selected training scalars creates a tensor shaped(4,),whose mean is the fitted normalization state. Applying that scalar to four assessment values yields[16,18,26,28]. Those transformed assessment values do not have mean zero,and they should not be forced to. Their nonzero mean is information about the assessment population relative to the training baseline.\n\nThe held-out perturbation is a direct test of the information boundary. Replacing only the final assessment value32 with3200 leaves the training values and mean four unchanged. The global mean changes from15 to411 because the total becomes3288 over eight records. A preprocessing path whose fitted training mean changes under this perturbation has consumed assessment information,even if no target label was read.\n\nAlternating row indices produces superficially balanced four-row sets but puts one row from every account on each side. Row-ID intersections are empty while the account-group intersection isA,B,C,D. If the claim concerns new accounts,this is a failure before any neural layer is built. A stronger optimizer ormore epochs cannot undo that information crossing.\n\nDataset is an access interface,not an isolation or immutability guarantee. Subset delegates to the underlying dataset,so later mutation of that object's values can change what a subset returns. A retrieved scalar tensor may also share storage with its source. Use out-of-place transformations oran explicit ownership boundary when mutation is intended,andfreeze the fitted preprocessing state independently of mutable dataset access. [PyTorch2.9 Dataset,Subset anddata loading](https://docs.pytorch.org/docs/2.9/data.html).\n\nKeeping identity andgroup fields does not require feeding them into the model as features. They support split checks,duplicate detection,pairing anderror analysis. An account identifier used as an embedding feature would require a separate justification about availability and the meaning of unseen account IDs;it should not enter the model accidentally merely because it travels through the loader.\n\nFinally,four assessment rows here represent only two held-out account families. The fixture is too small andtoo structured to establish reliable population performance. Its useful evidence is that the access interface,group isolation andpreprocessing boundary behave as declared. Later evaluation should preserve the relevant independent units when estimating uncertainty rather than treating correlated rows as additional independent accounts.",
    'If a training statistic changes after an assessment-only perturbation,trace which index set was used during fitting andwhether a shared preprocessing object was refit. If row IDs are disjoint but quality is suspiciously high,inspect source-family IDs andnear-duplicate records rather than renaming rows. If assessment values unexpectedly become centered at zero,check for assessment-specific refitting.\n\nIf a Subset returns an unexpected identity,distinguish its local index from the delegated source index. If an augmentation changes later reads,inspect tensor aliases andunderlying dataset mutation. If a report calls four correlated assessment rows four independent accounts,repair the unit of inference before calculating uncertainty. Dataset correctness and evaluation validity must both pass;neither implies the other.')


review(11,
    ["The decision section was empty.", "Module state categories needed a concrete ownership and persistence table.", "Optimizer object membership and dtype conversion needed an operational ordering explanation."],
    """Put persistent learned state and child layers in the module construction path, then use forward to compute from that state. Register fixed tensor state as a buffer when it should follow module conversions and persistence. Keep ordinary metadata as ordinary attributes only when its lifecycle does not require those tensor-state mechanisms.

Finish deliberate model construction and device/dtype placement before creating an optimizer. If a later algorithm replaces or adds parameters, update optimizer membership and any retained optimizer state explicitly. A module's current parameter iterator is not a live subscription that automatically rewrites an already constructed optimizer.""",
    """## Trace module-owned state and optimizer-owned references

The scalar model owns a Parameter named weight and a buffer named offset. Both are scalar float64 tensors, but only weight is selected by model.parameters(). Its forward expression is weight*x+offset. The offset influences predictions while remaining fixed under the demonstrated SGD step because it is not in that optimizer's parameter list.

| Item | Registered category | In parameters() | In default state_dict() | Changed by this SGD step |
| --- | --- | --- | --- | --- |
| weight | Parameter | Yes | Yes | Yes |
| offset | Persistent buffer | No | Yes | No |
| An arbitrary plain tensor attribute | Ordinary attribute | No | No | Only if separately managed |

These are registration defaults, not a law that buffers can never participate in autograd or that every registered Parameter must be trainable. requires_grad and optimizer membership remain separate choices. A buffer registered with persistent=False still follows module conversion but is omitted from state_dict. The supplied offset uses the default persistent behavior. [PyTorch2.9 Module state APIs](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Module.html).

A call to model(x) routes through Module machinery and its forward method. At weight=offset=0, the three inputs1,2,3 produce three zeros. No loss, backward call or optimizer step is implied by that invocation. The explicit loop then clears gradients, computes the paired mean squared objective, backpropagates and applies SGD. The one-step weight28/15 is the same scalar oracle as the earlier chapter, while offset remains zero.

Converting the module to float32 moves both registered tensors through the module conversion mechanism. A plain auxiliary tensor could remain at its old dtype or device and later cause an operation mismatch. This example checks CPU dtype movement; it does not qualify a GPU placement path. In a larger model, also inspect optimizer state after a late conversion because momentum or other optimizer tensors have their own lifecycle.

Object identity makes the stale-optimizer failure concrete. At construction, the optimizer stores a reference to the original weight object. Replacing fresh.weight with a new Parameter changes what forward reads, but the old optimizer list still refers to the former object. A new backward can populate the replacement's grad while step examines the old object's gradient instead. Rebuilding or deliberately editing parameter groups is therefore part of the model-change operation, not an optional cleanup detail.

Creating Parameters inside forward causes a related failure. Repeated calls can create new objects after the optimizer captured its membership, so the current computation and the objects being updated diverge. A stable model should preserve its intended parameter identities across batch sizes unless it implements a deliberate, tested dynamic-state policy. The final exercise compares calls of length one and four for that reason.

State serialization also has a boundary. state_dict supplies a mapping of registered parameter and persistent-buffer state, but it is not automatically an immutable historical snapshot of independent storage. If a diagnostic must survive later in-place model mutation, clone the relevant values or serialize them at a defined point. Later checkpoint lessons distinguish a saved model state from optimizer, RNG and data-order state needed for a training restart.

For the paired Keras model, compare the represented function before comparing the training interface. A no-bias Dense kernel and the zero-offset scalar PyTorch model can represent the same map, but their storage layouts and construction APIs differ. Explicitly match dtype, denominator and update budget; a high-level training call can report a pre-update loss just as a retained PyTorch loss tensor can.""",
    """If a tensor is missing from state_dict or model.parameters(),inspect how it was assigned and registered. If a fixed statistic stays on another dtype or device,check whether it is an unregistered attribute rather than a buffer. If a new parameter has a gradient but never moves,compare object identities against every optimizer parameter group.

If parameter count changes after a forward call,look for construction inside forward or an untracked container of child modules. If a state snapshot changes later,inspect shared storage instead of assuming a dictionary copy made tensor copies. If a framework comparison disagrees after one update,reconstruct the scalar28/15 oracle and verify whether an extra trainable bias or different reduction was introduced.""")

review(12,
    ["The capstone decision section was empty.", "The special basis-vector fixture allowed an independent closed-form100-step oracle that was missing.", "The final-model metric needed distinction from the last pre-update loss in the curve."],
    """Use a capstone to combine independently checked boundaries: data identity, fitted baseline, parameter construction, update sequence and held-out evaluation. Prefer a model whose hypothesis class matches the stated synthetic mechanism so implementation errors remain diagnosable. More layers would add ambiguity without making this known linear fixture a stronger population study.

Freeze the split, initial state, rate and100-step budget before assessment. If the two holdout results trigger another design choice, treat them as selection evidence and use another independent assessment for a fresh claim. Keep an analytic mechanism oracle beside the fitted experiment so a low final error cannot conceal compensating mistakes.""",
    "## Derive a capstone oracle from the training design\n\nThe six input rows are zero, the three coordinate basis vectors, then[1,1,1] and[2,1,1]. The target is2a-b+c, so the targets are[0,2,-1,1,2,4]. The first four rows are training and the last two are assessment. Input shape is(6,3), target shape(6,1), and the bias-free Linear stores one row of three weights. This shape contract must remain unchanged throughout fitting and evaluation.\n\nThe training-only baseline is(0+2-1+1)/4=0.5. On assessment targets2 and 4, its squared errors are2.25 and12.25, giving MSE7.25. This baseline ignores features but uses the same assessment records and metric as the learned model. Fitting its constant to the assessment mean would invalidate that comparison.\n\nThe basis-vector training design makes the optimizer trajectory independently solvable. Let the stored weight row be w=[w_a,w_b,w_c] and the intended row be w*=[2,-1,1]. The zero input contributes a zero residual because the model has no bias. The other three rows isolate one coefficient each, so the training objective is:\n\n`L_train(w) = [(w_a-2)²+(w_b+1)²+(w_c-1)²]/4`.\n\nIts gradient is(w-w*)/2. With SGD rate0.1, one update changes the error to0.95(w-w*). Starting at zero, after t updates the weight is`w_t=(1-0.95^t)w*`. This oracle does not read PyTorch's gradient buffer or reuse the training-loop implementation. It follows from the declared design matrix and denominator.\n\nAfter100 updates, the missing fraction is r=0.95^100,about0.00592. The weights are approximately[1.98816,-0.99408,0.99408]. The final training MSE is1.5r² and the assessment MSE is10r²,about0.000351. The assessment formula follows because its predictions are(1-r) times targets2 and 4,so the two squared residuals are4r² and16r². These exact symbolic quantities strengthen the capstone beyond merely observing that loss decreased or beat7.25.\n\nThe curve records each loss before that iteration's update. Its first value is1.5 and its last value corresponds to99 completed updates,namely1.5×0.95^198. The separately recomputed final training error follows100 updates and is1.5×0.95^200. Calling curve[-1] the final model's loss would create a one-step interpretation error even though every loop operation ran successfully.\n\nThe fixture is identifiable within this hypothesis class because the three nonzero training rows span all three feature directions. That mathematical fact helps explain successful recovery on linear combinations of those directions. It does not show that an arbitrary real dataset is linear,noise-free,representative orwell-conditioned. Adding a trainable bias,changing feature scaling or altering the loss denominator changes the derivation andrequires a new oracle.\n\nThe final report should retain training and assessment IDs, their counts, parameter dtype and layout,initial state,actual update count,baseline score,final fixed-state errors and the visible synthetic limitation. model.eval() and no_grad make evaluation behavior and derivative recording explicit; no optimizer step occurs during assessment. The two assessment rows demonstrate the intended procedure,but are far too few andtoo deliberately constructed to support a broad reliability claim.\n\nThe paired TensorFlow implementation uses the same mathematical fixture in float32,whereas this PyTorch reference uses float64. Compare the function,transposed kernel layout,denominator and update count before tolerances. A small rounding difference is different from a missing update,an unintended bias or a changed split.",
    """If fitting fails to approach the coefficient row[2,-1,1],inspect feature order,stored weight orientation,zero initialization and the no-bias setting. If the learned weight differs from(1-0.95^100) times that row,inspect the denominator and actual number of steps before changing a learning rate. A decrease alone cannot distinguish99 from100 updates or an accidental extra intercept.

If a reported final loss matches the last training-curve value rather than the recomputed final model,check the before/after update timing. If the baseline is not7.25,verify that its mean came only from training targets. If holdout error informed another decision,record that change of role. Preserve the independent scalar pilot and the closed-form capstone trace so a large collection of passing prints cannot replace mechanism-level evidence.""")

REVIEWS["torch-012"]["executable_change"] = True
REVIEWS["torch-012"]["worked_code_change"] = True


review(13,
    ["The decision section was empty.", "Stable binary loss needed its algebra and gradient,not only API naming.", "Threshold cost assumptions,double-sigmoid gradients andcalibration limits needed concrete reasoning."],
    'Use one logit per binary event when the target represents a yes/no outcome. Keep the training objective in logit space and apply sigmoid for a probability-oriented report or decision policy. Choose threshold,calibration anderror costs using an appropriate validation protocol rather than tuning them on a final assessment.\n\nBefore using class orpositive-label weights,write the weighted objective andits denominator. Weighting changes the fitting target and can change the meaning of the raw sigmoid output. It is not equivalent to changing a decision threshold after fitting,and it does not independently establish calibrated probabilities on a new population.',
    "## Separate score,probability,loss anddecision\n\nThe binary logit z is unrestricted. Its sigmoid is p=1/(1+exp(-z)),and the unweighted binary cross entropy is -y log p-(1-y)log(1-p). For the declared binary targets y∈{0,1},the stable logit-space form is:\n\n`loss = max(z,0) - z*y + log1p(exp(-abs(z)))`.\n\nThe exponent is never applied to a large positive magnitude in the final term. This avoids first rounding a probability to zero orone andthen taking its logarithm. The derivative with respect to z is p-y before any mean-reduction factor. At z=0,y=1,the loss islog2 and the derivative is-0.5. A mean across N equally weighted binary entries divides that derivative contribution byN. [PyTorch2.9 BCEWithLogitsLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BCEWithLogitsLoss.html).\n\nFor logits[-2,0,2],the reported probabilities are approximately[0.1192,0.5,0.8808]. They preserve ranking. A threshold0.5 with a greater-than-or-equal tie rule classifies the zero logit as positive. Threshold0.8 corresponds to a logit boundary log(0.8/0.2)=log4,about1.3863. Moving that boundary changes decisions without changing any fitted parameter orscore.\n\nThe double-sigmoid error changes more than a label convention. At original z=0,the first sigmoid gives0.5. Passing that value as a logit asks the loss to interpret probability sigmoid(0.5),about0.6225. The positive-label loss becomes log(1+exp(-0.5)),about0.4741,instead oflog2. If the first sigmoid remains in the graph,the derivative with respect to the original z gains another factor p(1-p):at zero it is about-0.0944 rather than-0.5. Finite outputs therefore do not prove the intended objective or gradient.\n\nStable arithmetic also does not imply a good prediction. A logit1000 with label1 has a loss near zero;the same logit with label0 has loss near1000. Both are valid finite outputs of the stable formulation. The extreme-score fixture checks numerical behavior,not whether the labels are correct orthe model generalizes.\n\nDecision costs require an additional probability assumption. If p is a calibrated probability for the relevant population,correct decisions have zero cost,false positives costC_FP andfalse negatives costC_FN,then choosing positive has expected costC_FP(1-p),while choosing negative costsC_FN p. The positive decision is favored when p≥C_FP/(C_FP+C_FN). This derivation does not apply unchanged when costs vary byrecord,abstention is allowed,capacity is constrained orthe probabilities are miscalibrated.\n\nPositive-label weighting changes the loss itself. With positive-term multiplierα,the derivative for a positive target becomesα(p-1),while a negative target contributes p. The reduction convention still matters;do not silently replace the library's element-mean reduction with a sum-of-weights denominator. Such weighting can be useful for a declared fitting goal,but the resulting sigmoid should not be assumed to retain an unweighted population-probability interpretation without further calibration evidence.\n\nThe data boundary should validate target range,shape,dtype andfiniteness. A floating target tensor is required by this binary objective,but floating representation alone does not prove that its values lie in the intended range. Likewise,a sigmoid output lies between zero and one by construction;that mathematical range does not establish empirical reliability. Report ranking,probability loss,decision errors andcalibration as related but distinct observations.",
    'If loss isfinite buttraining isunexpectedly weak,inspect whether sigmoid was applied before a logits-aware objective. Compare both the midpoint loss and the derivative,not only the predicted labels. If extreme scores produceNaN in a hand-written log(sigmoid()) path,use the combined objective rather than clipping until an assertion passes.\n\nIf error counts change while logits stay fixed,inspect threshold andtie policy before blaming optimization. If a confidence score is presented as an empirical success frequency,look for calibration evidence on the relevant population. If positive-label weights were introduced,record the changed objective and denominator. Validate target range andmatching shape explicitly instead of treating a successful API call as a complete data contract.')

review(14,
    ["The decision section was empty.", 'Class-axis and target contracts needed a spatial/batched shape table.', "Cross-entropy gradients,soft targets andweighted denominators needed clearer boundaries."],
    'Choose the loss from the event being predicted. Use a categorical objective when exactly one ofC outcomes is the target for each unit. Use separate binary objectives when several labels can hold simultaneously. The final layer width alone cannot make that decision,andcasting orreshaping labels cannot repair a wrong event definition.\n\nKeep class vocabulary,axis location,target representation andignored-label policy explicit. For framework comparison,translate the class axis before comparing reductions. Treat probability targets,label smoothing andclass weights as separate objective variants whose validity and denominator must be checked,rather than assuming they behave identically to integer class-index targets.',
    "## Derive the class competition andits tensor contract\n\nFor a single multiclass record with logits z_0..z_(C-1),softmax assigns p_c=exp(z_c)/Σ_j exp(z_j). The indexed-target loss is`logsumexp(z)-z_y`. It compares the observed class with all alternatives through one shared normalization. Adding the same constant to every logit leaves the probabilities and loss unchanged,which is why a numerically stable implementation can subtract a row maximum.\n\nAt three zero logits and target class1,p=[1/3,1/3,1/3] and loss=log3. The gradient with respect to the three logits is[1/3,-2/3,1/3] before a batch reduction. The components sum to zero because raising every score equally cannot change class competition. This provides a derivative interpretation beyond the forward scalar.\n\nPyTorch's indexed-target shapes are:\n\n| Task | Logits | Integer target | Class axis |\n| --- | --- | --- | --- |\n| One record | (C,) | scalar | The only logit axis |\n| Ordinary batch | (N,C) | (N,) | Dimension1 |\n| Spatial labels | (N,C,H,W) | (N,H,W) | Dimension1 |\n| Independent multilabel batch | (N,C) | Floating(N,C) | Each label is a binary event |\n\nA sparse target index is a category identity,not a numeric value to regress. It must be a valid class index under the declared vocabulary. Probability-target forms instead match the logit shape andrequire a meaningful distribution across the class axis. The application should validate nonnegativity andnormalization rather than assuming a floating tensor automatically supplies valid soft labels. The official API distinguishes these forms and their reductions. [PyTorch2.9 CrossEntropyLoss](https://docs.pytorch.org/docs/2.9/generated/torch.nn.CrossEntropyLoss.html).\n\nApplying softmax before CrossEntropyLoss feeds probabilities into an API that interprets them as logits and normalizes again. Uniform scores are a poor detector of this bug because any equal-valued score vector still produces a uniform distribution andlosslog3. A nonuniform fixture such as[2,0,-2] exposes the changed confidence andobjective. This is another reason to retain asymmetric,nonuniform examples alongside exact symmetric reference points.\n\nMultilabel prediction has a different denominator andprobability meaning. For two records and three binary labels,there are six binary events. Zero logits give each marginal probability0.5,so the three probabilities in a row sum to1.5 rather than one. That sum can represent an expected count of positive labels;it is not itself a probability of one mutually exclusive outcome. Shared features can still relate the labels,andindependent binary losses do not automatically describe their full joint distribution.\n\nEach zero-logit binary entry contributeslog2. Summing all six gives6log2;the element mean giveslog2;the mean across records of a sum across three labels gives3log2. All three are possible reductions,but they imply different objective andgradient scales. State whether the denominator counts records,labels,valid pixels oranother participation unit.\n\nWeights andignored entries require another check. For class-index targets with class weights,PyTorch's weighted mean uses the participating target-class weights in its denominator,andignore_index excludes designated targets from that participation. Do not transfer that exact formula automatically to soft-target cross entropy orpositive-weighted binary loss. A padded spatial or sequence target can otherwise change training scale while the displayed output tensor shape remains plausible.\n\nFor Keras comparisons,the default class-axis convention is often the last axis,whereas the PyTorch spatial categorical interface expects classes at dimension1. Reorder axes andalign target indexing explicitly;merely matching total element count can normalize across the wrong population or couple unrelated observations.",
    "If probabilities sum along the batch axis instead of the class axis,inspect the softmax dimension andgive each axis a semantic name. If a class-index target was converted to a floating matrix just to avoid an error,verify whether the task actually changed to a soft-target or multilabel objective. A class index3 is invalid for three classes0..2,regardless of how confidently a model predicts.\n\nIf a double-softmax mistake passes the uniform-logit case,test a nonuniform row and compare the target probability andgradient. If padding or class weighting changes the scalar unexpectedly,reconstruct the library's exact participation denominator for that target form. Never compare a per-label mean with a per-record summed objective as though their matching function names implied the same training problem.")


review(15,
    ["The decision section was empty.", 'Sampler state,collation masks and tail populations needed distinct contracts.', "The collator silently truncated floating token IDs into a Long tensor."],
    """Choose Dataset for access, a sampler for the intended draw policy, and collation for the batch representation. Keep these decisions separate from model fitting. Use num_workers=0 for the default classroom so worker-process startup and external random-state behavior do not obscure the data contract.

Scale loading only after measuring where time is spent and qualifying the relevant process/platform behavior. Decide whether sampling is a permutation, sampling with replacement or a grouped policy, because their valid identity-count expectations differ. Validate token types and padding metadata at collation instead of allowing an implicit integer cast to change observations silently.""",
    '## Trace one observation through sampling and collation\n\nA map-style Dataset maps an index to one item. A sampler chooses indices, and a DataLoader retrieves those items and groups them through a collator. The model sees the resulting batch, not an abstract guarantee that every source record appeared exactly once. TensorDataset keeps components aligned by their common leading dimension, which is why one sampled index selects its ID and value together.\n\nFor five records and batch size two without dropping, the traversal has three batch elements with sizes2,2,1. Concatenated IDs are 0..4 exactly once. Dataset length five and loader batch count three describe different stages. With drop_last=True and no shuffle, the final ID4 is omitted. With shuffling, a different identity may land in the tail; the omission still changes the epoch population even if all produced tensor shapes are uniform.\n\nA local torch.Generator makes the source of sampler randomness explicit. Constructing two fresh generators with seed7 starts two equivalent sequences in the pinned runtime. Reusing one consumed generator does not reset it:the next traversal begins from later RNG state. A global manual_seed call also does not describe which later operations consume draws. Reproducibility needs the generator ownership, draw order, dataset state and runtime, not only one integer seed. [PyTorch2.9 reproducibility notes](https://docs.pytorch.org/docs/2.9/notes/randomness.html).\n\nDefault collation can stack compatible tensor shapes, but variable-length sequences require a declared representation. For[2,3] and[4], this helper produces Long tokens shaped(2,2), lengths shaped(2,), and values[[2,3],[4,0]] with lengths[2,1]. The corresponding validity mask from position<length is[[True,True],[True,False]]. There are three participating tokens, not four.\n\nPadding fills storage; it does not create an observed token. Lengths remain authoritative even if zero can occur as an actual token ID in another contract. A later embedding padding_idx, attention mask or loss mask must agree on the sentinel and validity policy. A token loss averaged over all four stored positions would give the padded slot denominator weight it did not earn. Mask polarity also belongs to the consuming API, so a valid-position mask may need inversion for an API whose True means blocked.\n\nThe repaired collator accepts nonempty sequences of nonnegative integer token IDs representable in signed int64. It rejects Boolean, floating, negative and out-of-range IDs before assigning into a Long buffer. Without that boundary, a value2.7 could silently become2 during assignment. A downstream embedding lookup would then process a different symbol while every tensor shape looked correct. The collator does not know the eventual vocabulary size; that additional range check belongs with the vocabulary/model contract.\n\nMultiple workers add more state. Worker processes may have replicated dataset instances and their own Python/NumPy random generators. Iterable datasets need deliberate sharding to avoid repeated records. Platform start methods, picklable functions, resource cleanup and bounded prefetch also matter. These are reasons to qualify a multiprocessing design separately, not reasons to assume that more workers always improve throughput. The default examples create no worker processes and make no cross-platform performance claim. [PyTorch2.9 data-loading contracts](https://docs.pytorch.org/docs/2.9/data.html).\n\nFinally, identity checks must fit the sampling policy. A no-replacement permutation should preserve the complete ID bag. A weighted sampler with replacement may deliberately repeat IDs, so its acceptance contract concerns draw counts and weights instead. Keep the chosen policy and actual records visible before interpreting a training loss.',
    """If batch shapes are inconsistent,inspect item shapes and the collator output before changing the model. If token values change during collation,check for implicit dtype conversion and reject invalid IDs before constructing the integer batch. If a padded loss looks too small,compare stored positions with valid lengths.

If a fresh-seed replay differs,inspect whether the same generator was actually reset or merely reused, whether another operation consumed it, and whether dataset transforms have separate RNG state. If records disappear,check drop_last and the sampled tail. If records repeat under multiple workers,check iterable-dataset sharding and distinguish intended replacement sampling from accidental duplication. Keep the default single-process evidence separate from an unqualified multiprocess loading claim.""")

review(16,
    ["The decision section was empty.", "XOR needed an affine impossibility proof and a full hidden-feature trace.", "The symmetric XOR matrix could not detect the claimed transpose mistake.", "Initialization symmetry needed conditions on downstream gradients and activation regions."],
    """Separate representational capacity from optimization. First show that the architecture can express a small required function using explicit parameters. Then investigate whether a chosen initialization and training procedure can find a useful solution. More epochs cannot make an affine-only map separate XOR in the original two input coordinates.

Choose an initialization in relation to the activation, feature scale and intended forward/backward variance behavior. Use controlled weights for a diagnostic, but do not mistake that manual construction for a successful training run. When testing layout translation, include a nonsymmetric fixture so an accidental transpose has an observable effect.""",
    """## Prove the capacity boundary and then inspect optimization

Suppose a classifier uses an affine score s=a x1+b x2+c and predicts class1 when s>0. XOR requires(1,0) and(0,1) positive, so a+c>0 and b+c>0. It requires(0,0) and(1,1) nonpositive, so c≤0 and a+b+c≤0. Summing the positive requirements gives a+b+2c>0; summing the negative requirements gives the same quantity≤0. The contradiction proves that no such affine separator exists, independent of a random seed or training budget.

Stacking affine layers does not remove that boundary. `(XW1+b1)W2+b2 = X(W1W2)+(b1W2+b2)` is still affine in the input. A bottleneck can even restrict the possible rank. Nonlinear parameterization of the weights may change optimization behavior, but it does not create a nonlinear input function. Adding an engineered interaction feature would change the input representation and therefore the problem being considered.

The manual construction uses d=x1-x2, h1=max(d,0), h2=max(-d,0), and output=h1+h2:

| Input | Raw difference pair | ReLU features | Output |
| --- | --- | --- | --- |
| (0,0) | (0,0) | (0,0) | 0 |
| (0,1) | (-1,1) | (0,1) | 1 |
| (1,0) | (1,-1) | (1,0) | 1 |
| (1,1) | (0,0) | (0,0) | 0 |

Without ReLU,the two raw differences cancel everywhere. With ReLU,the sum is|x1-x2|. On binary corners that equals XOR, but on continuous inputs(.2,.8) and(.8,.2) it equals0.6. That value is a function output, not automatically a calibrated probability or a new definition of a binary logical operator.

The XOR projection matrix[[1,-1],[-1,1]] is symmetric. Consequently,W.T equalsW,so the original fixture alone cannot detect a forgotten transpose when copying a mathematical matrix into nn.Linear's stored(out,in) layout. The strengthened example adds a separate nonsymmetric matrix[[1,2],[3,4]]. For input[0,1],XW gives[3,4],while XW.T gives[2,4]. That probe makes the storage translation observable while retaining the original XOR construction unchanged.

Activation gradients distinguish a dead region from a broken graph. ReLU at a negative preactivation has a connected derivative zero; at a positive one its derivative is one. At the kink,the framework uses its chosen convention. Repeatedly negative preactivations can therefore block useful gradient flow even though every operation is differentiable on the active path. Inspect activation signs and intermediate gradients before declaring the architecture incapable.

Identical hidden rows produce identical features on the same input. Equal gradients additionally require symmetric downstream influence and other state; unequal output weights can break that symmetry. If a whole ReLU network is initialized in a zero/symmetric configuration, both hidden activations and upstream signals can vanish, leaving ordinary gradient descent unable to create useful differences. Separate Parameter objects are not by themselves evidence of diverse features.

Variance-aware initialization gives a useful approximation. For independent zero-mean inputs and weights, a preactivation's variance scales roughly with fan_in×Var(weight)×Var(input). ReLU discards about half the second moment under a symmetric distribution, motivating an initialization scale near2/fan_in for that simplified setting. Those assumptions need not hold exactly for correlated finite data. Choose the documented initializer and gain for the intended activation rather than assuming every layer's default initialization implements that exact rule. [PyTorch2.9 initialization APIs](https://docs.pytorch.org/docs/2.9/nn.init.html).""",
    """If an affine-only model never solves XOR,derive the incompatible inequalities before increasing the training budget. If the manual nonlinear construction works but fitting fails,inspect initialization, active ReLU regions, gradient magnitudes and update policy. A connected zero gradient does not become nonzero by retain_grad or by detaching the value.

If a layout test passes with a square symmetric matrix,add a nonsymmetric probe before claiming transpose correctness. If identical units remain redundant,check both their initial rows and their downstream gradient signals rather than assuming all equal initial features must receive equal updates. If the construction returns0.6 outside the binary corners,state the actual absolute-difference function instead of treating the value as an empirically validated XOR probability.""")

for _changed in ("torch-015", "torch-016"):
    REVIEWS[_changed]["executable_change"] = True
    REVIEWS[_changed]["worked_code_change"] = True


review(17,
    ["The decision section was empty.", "Dropout expectation was stated without its variance or backward trace.", "Penalty coefficients, loss reduction and adaptive weight decay needed an explicit comparison."],
    """Select a regularizer against a held-out criterion that reflects the intended task, and keep the data-loss term visible. A smaller parameter norm or a stochastic training curve is mechanism evidence, not evidence that prediction improved. Compare a declared baseline, coefficient, seed policy and stopping rule before attributing a change to regularization.

Use model mode to control stochastic modules and gradient mode to control differentiation. These controls serve different purposes. Evaluation with gradients is appropriate for sensitivity analysis, while no_grad on a model left in training mode can still sample Dropout and update BatchNorm buffers. When choosing optimizer weight decay, inspect the actual update rule and the parameter groups to which it applies.""",
    """## Derive the objective, random transformation and gradient

The fixture has w=[1,-2]. The absolute-value sum is three, the squared-value sum is five, and the Euclidean norm is sqrt(5). These are different quantities. This chapter's squared L2 penalty is lambda times the sum of squared weights, without a one-half factor. At lambda=0.1 it contributes0.5 to the objective and gradient[0.2,-0.4]. Doubling both weights doubles the L1 sum to six but quadruples the squared sum to twenty. That scale dependence matters when preprocessing changes the meaning of a unit weight.

Suppose one coordinate has data gradient g=0.3, parameter w=1 and learning rate eta=0.1. Ordinary SGD on data loss plus0.1*w² uses total gradient0.3+0.2=0.5 and gives w'=0.95. The update can also be written (1-2*eta*lambda)w-eta*g. An SGD weight-decay coefficient0.2 corresponds to this particular explicit penalty convention. A coefficient0.1 would correspond to a half-scaled objective and would instead give0.96 for this example. A shared name or numeric coefficient does not fix the objective's convention.

For an adaptive optimizer, adding2*lambda*w to g also changes the moment estimates and coordinatewise scaling. Decoupled AdamW applies its decay separately from those moment calculations. Consequently the SGD algebra above does not establish an Adam/AdamW equivalence. Compare the optimizer formula, update count, learning-rate schedule and decayed parameter groups. [PyTorch2.9 AdamW](https://docs.pytorch.org/docs/2.9/generated/torch.optim.AdamW.html).

Loss reduction adds another scale choice. Replacing a mean over B observations with a sum multiplies the data gradient by B but leaves a separately added fixed penalty unchanged. That reduces the relative penalty strength unless its coefficient is adjusted. Repeating the full penalty at each microbatch also changes its total contribution if the intent was one large-batch objective. Specify whether the penalty is applied once per optimizer step and how accumulated data gradients are normalized.

For Dropout probability p<1, let m be a Bernoulli keep indicator with probability q=1-p. Inverted Dropout computes y=m*x/q during training. Thus E[y]=x and Var(y)=x²*p/q. This statement conditions on the input value; it does not assert that a finite collection of outputs has exactly the same mean. At p=0.5 and x=1, each output is zero or two, each with probability one-half. The derivative with respect to x is the same multiplier m/q, so the sampled backward path is either zero or two. During evaluation the transformation is identity. [PyTorch2.9 Dropout](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Dropout.html).

The fixture contains32 unit activations. Under independent elementwise masking, the count K of retained values has mean16 and variance8. The observed tensor mean is2K/32, so its expectation is one and its variance is1/32. Its standard deviation is about0.177. A particular call can retain15 or18 values without violating the contract. Even all-zero and all-two tensors are possible, though rare. That is why the executable assertion checks shape and allowed values rather than requiring exactly16 survivors or a particular cross-platform random mask.

Expected activation preservation also does not imply preservation after nonlinear downstream operations. If a scalar activation is always one without Dropout, its square is one. With p=0.5, its squared dropped value is zero or four and has expectation two. Therefore a model's expected squared loss need not equal its loss at the expected activation. Dropout changes the stochastic training objective, not just the way an unchanged loss is sampled.

The state table helps prevent accidental coupling of unrelated controls:

| Configuration | Dropout mask | Autograd recording for eligible inputs |
| --- | --- | --- |
| train mode, ordinary grad mode | Sampled | Enabled |
| eval mode, ordinary grad mode | Identity | Enabled |
| train mode inside no_grad | Sampled | Disabled |
| eval mode inside no_grad | Identity | Disabled |

Exercise six deliberately uses the second row: an evaluation-mode Dropout still carries derivatives, and summing its identity output gives an all-ones input gradient. An inference service commonly uses the fourth row, but gradient-based explanation or adversarial sensitivity analysis may intentionally use the second. Monte Carlo Dropout requires its own deliberate mode policy; simply switching an entire model to train can also change unrelated BatchNorm state.

For an interview, explain why a training loss can rise after regularization while validation loss improves: the optimized objective includes a penalty or stochastic computation, so it is not the same measured quantity as deterministic predictive loss. Then ask whether the validation comparison was selected repeatedly and whether independent evidence remains. Conversely, lower weight norm by itself does not establish better calibrated probabilities, useful rankings or smaller out-of-population error.""",
    """If evaluation predictions vary, inspect every stochastic input transformation and module's mode before blaming numerical precision. If no_grad did not stop the variation, remember that it does not switch Dropout into evaluation. If a frozen feature extractor changes behavior, inspect both its mode and its buffers rather than only requires_grad flags.

If a regularization coefficient behaves differently after changing batch size or accumulation steps, write the complete numerator, denominator and penalty frequency. If two optimizers disagree, compare their state updates and whether decay enters the moments. If Dropout tests fail only because a different mask appears, replace the random-pattern expectation with the declared shape/value invariants. If the objective improves but prediction quality does not, inspect the separately logged data loss and the independent validation population.""")

review(18,
    ["The decision section was empty.", "Axis retention versus reduction needed a complete shape ledger.", "Momentum parity needed a non-half coefficient and distinct variance estimators.", "Freezing affine gradients was not distinguished from freezing running statistics."],
    """Choose normalization by the intended dependency structure. BatchNorm couples the values sharing a channel statistic during training, which can be appropriate for a batch-based feature model but requires representative batches and a deliberate inference-state policy. Tokenwise LayerNorm is useful when each token's features should be normalized without using other token positions. It does not by itself prevent information leakage elsewhere in a sequence model.

When transferring a model or comparing frameworks, specify layout, reduced axes, epsilon, affine parameters, training mode, variance estimators and stored state. Match a forward output and a state transition separately. A matching running mean or equal momentum argument is insufficient. Decide explicitly whether a frozen backbone should keep adapting its normalization buffers.""",
    """## Trace normalization axes, state and derivatives

For each normalization group, define mean mu, population variance v and centered values c=x-mu. The internal normalized values are z=c/sqrt(v+epsilon); a learned scale gamma and offset beta then give y=gamma*z+beta. The grouping determines which other values can affect an output. The final tensor shape alone does not reveal that dependency.

| Layer and input | Statistics reduce over | Retained group identity | Affine parameter shape |
| --- | --- | --- | --- |
| BatchNorm1d on [N,C] | N | Channel C | [C] |
| BatchNorm1d on [N,C,L] | N and L | Channel C | [C] |
| BatchNorm2d on [N,C,H,W] | N,H,W | Channel C | [C] |
| LayerNorm(D) on [N,T,D] | D | Each [N,T] token | [D] |
| LayerNorm((T,D)) on [N,T,D] | T,D | Each N record | [T,D] |

The last two rows are different models. The first LayerNorm preserves token independence in its normalization statistics; the second lets future tokens affect earlier ones. On a channels-first image, LayerNorm(C) would act on the final axis only if that axis happens to have size C; it does not automatically interpret the second axis as channels. Reorder axes or choose the intended normalized_shape explicitly.

In the supplied BatchNorm fixture, columns[1,3] and[3,5] have means[2,4]. Each centered column is[-1,1]. Dividing the squared-deviation sum two by sample count two gives population variance one. Dividing by count minus one gives the unbiased estimate two. PyTorch uses the first estimate for training normalization and the second for updating running variance. Its momentum weights the new statistic. With default tracked statistics, eval uses stored state; setting track_running_stats=False changes that contract. [PyTorch2.9 BatchNorm1d](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BatchNorm1d.html).

With momentum0.5, initial running mean zero and initial running variance one, the first update gives mean[1,2] and variance[1.5,1.5]. During that training call, however, the outputs use the current batch mean[2,4] and population variance[1,1], not those newly stored values. With initial gamma=1,beta=0, they are[[-1,-1],[1,1]] divided by sqrt(1+epsilon). Calling eval afterward on the original batch instead gives[[0,1],[2,3]] divided by sqrt(1.5+epsilon). A changed output therefore does not require a changed trainable weight.

For a scalar fixed batch mean b, PyTorch momentum a gives r_t=(1-a)r_(t-1)+a*b. Starting from zero, the solution is r_t=(1-(1-a)^t)*b. With a=0.2 and b=[2,4], the first two means are[0.4,0.8] and[0.72,1.44]. Keras expresses the same mean recurrence using retention momentum m=0.8. If both APIs instead receive0.2, their first means differ: PyTorch gives[0.4,0.8] while Keras gives[1.6,3.2]. The original0.5 fixture hides this difference because a and1-a coincide.

Mean-recursion matching still leaves variance state unmatched. The paired TensorFlow chapter's explicit two-row probe[0,4] has population variance four and checks Keras moving variance0.5*1+0.5*4=2.5. Its unbiased sample variance is eight, so the corresponding PyTorch running update would be0.5*1+0.5*8=4.5. These are predictions from the named rules, not evidence that one should transplant a variance buffer between frameworks. The paired chapter contains the Keras execution contract, and this chapter's executable checks independently establish PyTorch's1.5 update on its own fixture. Epsilon and affine defaults must also be aligned before comparing outputs.

A useful geometric view is that centering removes the constant direction inside each group. For one LayerNorm group with d features, write g_i=dL/dz_i after incorporating any affine scale into the upstream gradient. Let s=sqrt(v+epsilon). Differentiating both the mean and variance gives

`dL/dx_i = (g_i - mean(g) - z_i*mean(g*z)) / s`.

This expression explains the dependency: an upstream derivative at one feature contributes to the means that influence other features in the same group. Summing the input derivatives gives zero, up to arithmetic error, because shifting all features by a common constant leaves the normalized values unchanged. The familiar exact removal of the radial direction is softened when epsilon is nonzero. Do not drop epsilon from a derivative calculation while retaining it in the forward pass.

For row[1,3], mu=2,v=1 and z=[-1,1]/sqrt(1+epsilon). Appending a separate row[100,200] does not change this row under LayerNorm(2), since it belongs to a different group. Changing one of the first row's own features does affect both normalized outputs. LayerNorm computes its current input statistics in both train and eval modes and uses a biased variance estimate; its learned affine values can change the final output mean and variance. [PyTorch2.9 LayerNorm](https://docs.pytorch.org/docs/2.9/generated/torch.nn.LayerNorm.html).

State freezing requires three independent questions. Are affine parameters receiving gradients? Can an optimizer update them? Can the layer mutate running buffers? Setting PyTorch BatchNorm weight and bias requires_grad=False addresses the first question, not the third. A train-mode call can still change running_mean, running_var and num_batches_tracked. Conversely eval can use fixed buffers while gradients still flow through affine parameters or inputs. These controls matter during transfer learning and sensitivity analysis.

Keras BatchNorm has a specific documented behavior: trainable=False selects inference behavior even for a direct call with training=True. The paired TensorFlow guide tests that rule. It is not a general equivalence between Keras trainable and PyTorch requires_grad, and it is not a claim about every Keras layer. Compiled Keras workflows also have their own recompilation rule after trainability changes. [Keras BatchNormalization](https://keras.io/api/layers/normalization_layers/batch_normalization/).

Small-batch and sequential applications need an additional assumption check. A single [1,C] training batch has no second observation per channel for the ordinary BatchNorm training contract; the lesson's singleton call deliberately occurs in eval after state exists. For [N,C,L], statistics include L, so using a whole sequence can couple future and past positions. A causal attention mask cannot undo that normalization dependency. State initialization, batch composition, last-batch policy and sequence layout therefore belong in the model contract, not only in a loader implementation detail.""",
    """If normalization outputs disagree, first calculate one group's members and axes. Check whether the API's axis names a retained channel or a reduced feature dimension. Then compare current-batch statistics, stored statistics, epsilon and affine values separately. A matching output shape cannot catch a wrong reduction group.

If validation changes running state, inspect train/eval at the exact call and whether running statistics are tracked. Freezing affine gradients is not a running-buffer policy. If framework means disagree, translate the coefficient algebra before changing tolerances; if means match but variances disagree, inspect the estimators and initialization. If a sequence leaks future information despite a correct attention mask, test normalization with a future-token perturbation. If a constant row is not zero after LayerNorm, inspect its learned beta before declaring the epsilon guard broken.""")

TYPO_REPAIRS = {
    'who ll y': 'wholly',
    'org an i z in g': 'organizing',
    'ExampleA': 'Example A',
    'ExampleB': 'Example B',
    'ExampleC': 'Example C',
    'haveB': 'have B',
    'byN': 'by N',
    'orone': 'or one',
    'byrecord': 'by record',
    'islog': 'is log',
    'oflog': 'of log',
    'costC_FP': 'cost C_FP',
    'costC_FN': 'cost C_FN',
    'costsC_FN': 'costs C_FN',
    'toNone': 'to None',
    'Pass h0': 'Pass h=0',
    'its+1': 'its +1',
    'and-1': 'and -1',
    'a3×3': 'a 3×3',
    'a4×4': 'a 4×4',

    'full graph=True': 'fullgraph=True',
    'capture dF X': 'captured FX',
    'CPU act iv i ties': 'CPU activities',
    'a ten::add': 'aten::add',
    'ann.Linear': 'an nn.Linear',
    'Saved Model': 'SavedModel',
    'oran oversized': 'or an oversized',
    "record'sp re dict i on": "record's prediction",
    'Are source bound': 'A resource bound',
    'represent able': 'representable',
    'torch.log sum exp': 'torch.logsumexp',
    'over r id den': 'overridden',
    'd is connection': 'disconnection',
    'out rank': 'outrank',
    'label led': 'labeled',
    'care lessly': 'carelessly',
    'sha rd': 'shard',
    'eachs hard': 'each shard',
    'emptys hard': 'empty shard',
    'Col late': 'Collate',
    'col late': 'collate',
    'rebuild s': 'rebuilds',
    'num_workers0is': 'num_workers=0 is',
    'dropout_p0': 'dropout_p=0',
    'C on v2d': 'Conv2d',
    'F.conv2d': 'F.conv2d',
    'P ac k e d': 'Packed',
    'r o t at in git': 'rotating it',
    'register s': 'registers',
    'slide s': 'slides',
    'UseQ=K': 'Use Q=K',
    '3x2queries': '3-by-2 queries',
    'in1..4': 'in 1..4',

    "co incident all y": "coincidentally", "expect in g": "expecting", "de coupled": "decoupled", "a recomputed": "are computed", "Epsilon avoid": "Epsilon avoids", "re visited": "revisited", "research e r": "researcher", "u n established": "unestablished",
    "Detach in g": "Detaching", "subtract iv e": "subtractive", "fee l s": "feels",
    "Asymmetric kernel could hide an unintended rotation": "A symmetric kernel could hide an unintended rotation", "C on v2 d": "Conv2d", "F.conv2 d": "F.conv2d", "padding_id x": "padding_idx", "P ac k e d sequence": "PackedSequence", "torch vision": "torchvision", "sigmoid e d": "sigmoid-transformed", "favor in g": "favoring", "Binary Cross entropy": "BinaryCrossentropy", "B C E": "BCE", "Multi label": "Multilabel", "multi label": "multilabel", "UseF.": "Use F.", "isa direct": "is a direct", "pre fetching": "prefetching", "equalize s": "equalizes", "diagonal l y": "diagonally", "representation al": "representational", "in capable": "incapable", "opposite s": "opposites", "Innn.Linear": "In nn.Linear", "Seta2": "Set a 2", "clear e d": "cleared", "__get item__": "__getitem__", "alter nat in g": "alternating", "implement__len__": "implement __len__", "mistaken l y": "mistakenly", "undo in g": "undoing", "innn.Parameter": "in nn.Parameter", "Atw0": "At w=0", "graph internal s": "graph internals", "work around": "workaround", "Forf(w)": "For f(w)", "Useh.": "Use h=0.", "atw0": "at w=0", "neww.": "new w=0.", "Annn.Parameter": "An nn.Parameter", "annn.Module": "an nn.Module",
}


def apply_reviews(specs: dict[str, dict[str, Any]]) -> None:
    for identifier, details in REVIEWS.items():
        spec = specs[identifier]
        for field in ["mental", "anatomy", "comparison"]:
            for old, new in TYPO_REPAIRS.items():
                spec[field] = spec[field].replace(old, new)
            spec[field] = _readable(spec[field])
        spec["terms"] = [(_readable(_repair(term)), _readable(_repair(definition))) for term, definition in spec["terms"]]
        for exercise in spec["exercises"]:
            for field in ["title", "prompt", "expected", "why"]:
                for old, new in TYPO_REPAIRS.items():
                    exercise[field] = exercise[field].replace(old, new)
                exercise[field] = _readable(exercise[field])
        if identifier == "torch-004":
            spec["anatomy"] = spec["anatomy"].replace("this course validates exact shape equality before calling it", "a paired-record application should validate exact shape equality before calling it; these literal fixtures construct matching shapes")
        spec["interview"] = [
            (_readable(_repair(question)), _readable(_repair(answer))) for question, answer in spec["interview"]
        ]
        for field in ["decisions", "deep_dive", "diagnosis"]:
            spec[field] = _readable(_repair(details[field]))


def _repair(text: str) -> str:
    for old, new in TYPO_REPAIRS.items():
        text = text.replace(old, new)
    return text


def _readable(text: str) -> str:
    import re

    def clean(part: str) -> str:
        def numeric(match: Any) -> str:
            word, number, suffix = match.groups()
            if word.lower() in {"float", "int", "uint", "complex", "sha"}:
                return word + number + (" " + suffix if suffix else "")
            if word in {"Conv", "ConvTranspose", "MaxPool", "AvgPool", "AdaptiveAvgPool", "BatchNorm"}:
                return match.group(0)
            return word + " " + number + (" " + suffix if suffix else "")

        part = re.sub(r"\b([A-Za-z]{2,})(\d+)([A-Za-z]*)", numeric, part)
        part = re.sub(r"\band(?=[A-Za-z0-9])", "and ", part)
        part = re.sub(r"\bor(?=(?:less|more|the|a|an|zero|another|output|input)\b)", "or ", part)
        part = re.sub(r"([;:])(?=[A-Za-z])", r"\1 ", part)
        part = re.sub(r",(?=\S)", ", ", part)
        part = re.sub(r"(?<=\d) e(?=[+-]\d)", "e", part)
        return part

    pieces = re.split(r"(```[\s\S]*?```|`[^`\n]*`|\]\([^\n]*?\))", text)
    return "".join(part if part.startswith(("```", "`", "](")) else clean(part) for part in pieces)


def write_review_matrix(root: Any) -> None:
    import json
    plan = json.loads((root / "courses/deep-learning-pytorch/track.json").read_text())
    evidence = json.loads((root / "courses/deep-learning-pytorch/authoring/review_runtime_evidence.json").read_text())["records"]
    matrix = []
    for topic in plan["lessons"]:
        details = REVIEWS.get(topic["id"])
        matrix.append({
            "id": topic["id"],
            "title": topic["title"],
            "status": "reviewed_and_deepened" if details else "pending_substantive_review",
            "findings": details["findings"] if details else [],
            "paired_guide_reviewed": details["paired_guide_reviewed"] if details else None,
            "executable_change": details["executable_change"] if details else False,
            "worked_code_change": details["worked_code_change"] if details else False,
            "review_runtime_evidence": [record for record in evidence if record["lesson_id"] == topic["id"]],
        })
    (root / "courses/deep-learning-pytorch/authoring/review_matrix.json").write_text(
        json.dumps({"review_date": "2026-10-23", "chapters": matrix}, indent=2) + "\n"
    )


add_advanced_reviews(review)
