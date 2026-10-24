from pathlib import Path


def deepen(spec):
    spec['mental'] = '''Low-rank adaptation, or LoRA, freezes a base linear weight and learns an additive update represented by two smaller matrices. It changes the model's function through weight adaptation, while retrieval changes which evidence is supplied at inference time. LoRA is therefore a method for learning task behavior from examples, not a substitute for keeping a changing domain corpus current or enforcing access control on retrieved documents.

Use the row-vector convention Y = X(W + sAB), where X is [N,Din], W is [Din,Dout], A is [Din,r], B is [r,Dout], and s=alpha/r. Every product must preserve those contracts: XA is [N,r], (XA)B is [N,Dout], and AB is [Din,Dout]. The update rank is at most r, because its columns lie in the column space of A. At most is a bound, not a guarantee that training uses all r directions. The effective rank can be smaller because factors are rank deficient or because the data and gradient updates preserve a symmetry.

The chapter deliberately chooses W=I8, A filled with 1/8, B=0, rank 2 and alpha 4. This preserves the base function initially, allows every first-step derivative to be calculated by hand, and produces a real PyTorch SGD update. The symmetric A columns lead to equal B rows after the first step, so this particular update has rank one even though its parameterization allows rank two. That is a useful limitation to inspect rather than a claim that every rank-two adapter behaves this way.

Only A and B are optimized. The frozen base remains part of the forward computation and can still carry derivatives to earlier trainable operations. Freezing its parameters is not the same as disabling gradient recording for the whole forward pass. The lesson separates parameter ownership, function preservation, gradient flow, rank and inference merging so a successful adapter update is not confused with demonstrated domain-assistant quality.'''
    spec['anatomy'] = r'''### Orientation and parameter accounting

A base [Din,Dout] matrix contains Din*Dout entries. The factors contain r*(Din+Dout). For this 8-by-8 example and r=2, the base has 64 entries and the adapter has 32. For a square width d the ratio is 2r/d, so a width-4096, rank-8 adapter has 65,536 entries versus 16,777,216 base entries, a ratio of 1/256. That counts these matrices only; it is not a measured total-memory reduction.

PyTorch Linear stores a weight with shape [Dout,Din] and applies its transpose to row inputs. In that storage convention a typical update is B_pt A_pt, where A_pt is [r,Din] and B_pt is [Dout,r]. The course factors are A=A_pt^T and B=B_pt^T, making (B_pt A_pt)^T = AB. Copying factor names from another implementation without translating the orientation can produce a shape error or, for square matrices, a silently different function.

### Deriving both factor gradients

Let G=dL/dY have shape [N,Dout]. The adapter branch is s(XA)B. Matrix differentiation gives dL/dB = s(XA)^T G, with shape [r,Dout]. The gradient for A is dL/dA = s X^T G B^T, with shape [Din,r]. The input derivative is G(W+sAB)^T, so the frozen W still contributes to gradient propagation toward earlier layers even though W itself is not updated.

At initialization B=0. Therefore the A gradient is a connected tensor of zeros because its formula contains B^T. The B gradient can be nonzero because A is nonzero. If both factors start at zero, both gradients are zero and this ordinary gradient-based update cannot escape that point. A zero gradient and a missing gradient are different diagnoses: PyTorch can return an all-zero tensor for a connected parameter, while None can indicate that no derivative was accumulated for that parameter.

### Calculate the exact first step

The input X is a row of eight ones, so XA=[1,1]. With B=0 and W=I8, Y is a row of eight ones. The loss is the mean of eight squared outputs against zero: L=1. The output derivative is G=2Y/8, so every entry is 1/4. With s=2, every B-gradient entry is 2*1*(1/4)=1/2, and every A-gradient entry is zero.

SGD with learning rate 0.1 changes every B entry to -0.05 and leaves A at 0.125. Each entry of AB is 2*(0.125)*(-0.05)=-0.0125. Multiplication by s gives an effective update of -0.025 in every base-matrix entry. Multiplying by the eight-one input sums eight such contributions, producing Y_new=0.8 in every output coordinate. The new mean squared loss is therefore 0.8^2=0.64. The reference checks these values, not merely that something changed or that a loss happened to decrease.

The gradient denominator is essential. Using summed squared error instead of a mean multiplies G and both factor gradients by eight under this fixture. With the same learning rate, that is a different optimization step. Likewise, changing alpha without compensating elsewhere changes the forward update scale and the gradients; alpha is not just metadata attached to an adapter file.'''
    spec['decisions'] = '''Use LoRA when the task requires learning a repeatable behavior or representation change and a constrained update is a useful tradeoff. Examples include a stable output format, domain-specific extraction conventions or a measured task requiring adaptation beyond available prompts. For frequently changing factual content, start by improving retrieval and evidence handling. For sensitive subject matter, evaluate supported answers, refusal and abstention behavior, not only training loss.

Choose target modules deliberately. Adapting query and value projections, all attention projections, feed-forward matrices or embeddings gives different parameter counts and different places to change the computation. The same rank value does not imply the same capacity across these choices. Compare rank and target-module choices under a fixed data split and scoring rule. A single toy objective cannot establish a universally best rank or learning rate.

Parameter savings affect optimizer state and trainable gradients, but the frozen base must still be stored and used. Forward activations, intermediate adapter activations, attention buffers and checkpointing strategy also contribute to memory. For the width-4096 arithmetic example, float32 base weights alone occupy 64 MiB and the two adapter factors occupy 0.25 MiB. Those are storage calculations for one pair of matrices, not GPU peak-memory measurements. Adam-like optimization can add moments for trainable parameters, and mixed-precision or quantized implementations add their own state and kernels.

Merging computes a new effective weight W+sAB for inference. Do it into a separate artifact when the original base is shared by other adapters. Test the merged and unmerged computations in the intended dtype and model mode. In finite precision, changing multiplication order or quantizing the merged result can change outputs within or beyond an allowed tolerance. Adapter dropout, if used during training, should follow the model's evaluation contract before comparing inference parity. Store base revision, tokenizer identity, rank, scale, target modules, training-data identity and relevant software versions with the adapter.'''
    spec['diagnosis'] = '''If the initial adapter changes the base output unexpectedly, inspect whether one factor is actually zero and whether an extra bias or dropout is active. If A has a zero first gradient but B has a nonzero gradient, that matches the derived initialization. If both gradients are zero, inspect the factor initialization, the objective and whether the output derivative is zero. If a gradient is None, inspect requires_grad, detach and the recorded graph before blaming the low-rank parameterization.

If the base changes, check optimizer membership and any in-place merge. If earlier adapters stop receiving gradients through a frozen layer, check whether an over-broad no_grad context removed the required input derivative path. Frozen weights can remain constants in a differentiable computation; disabling every operation is a stronger change.

If the rank is lower than configured, inspect factor singular values and initialization symmetry. This fixture intentionally produces rank one after its first update. If merged predictions differ, verify factor orientation, alpha/r, base revision, dtype and evaluation mode before increasing tolerances. Finally, if training metrics improve but supported-answer quality does not, inspect the data, masking and held-out task design. The repository's optional pretrained generation probe demonstrates that mechanically successful adaptation can still produce an incorrect formula despite supplied evidence.'''
    spec['terms'] = [('Adapter rank', 'The inner dimension bounding, but not guaranteeing, the rank of the learned update.'), ('LoRA scale', 'The multiplier alpha/r used in this forward function and its gradients.'), ('Frozen base', 'Weights excluded from updates while still participating in the differentiable forward computation.'), ('Merged inference', 'Using a separately constructed effective weight W+sAB under a checked inference contract.')]
    codes = [
'''w = torch.eye(8)
a = nn.Parameter(torch.ones((8, 2)) / 8)
b = nn.Parameter(torch.zeros((2, 8)))
rank = 2
alpha = 4
scale = alpha / rank
x = torch.ones((1, 8))
assert w.numel() == 64
assert a.numel() + b.numel() == 32
assert scale == 2''',
'''initial = x @ (w + scale * (a @ b))
saved = w.clone()
assert torch.equal(initial, x @ w)
assert torch.equal(a @ b, torch.zeros((8, 8)))''',
'''loss = initial.square().mean()
loss.backward()
assert a.grad is not None and b.grad is not None
assert torch.count_nonzero(a.grad).item() == 0
torch.testing.assert_close(b.grad, torch.full((2, 8), 0.5), atol=1e-6, rtol=0)
assert w.grad is None''',
'''before_b = b.detach().clone()
optimizer = torch.optim.SGD([a, b], lr=0.1)
optimizer.step()
after = x @ (w + scale * (a @ b))
assert not torch.equal(before_b, b)
torch.testing.assert_close(b, torch.full((2, 8), -0.05), atol=1e-6, rtol=0)
torch.testing.assert_close(after, torch.full((1, 8), 0.8), atol=1e-6, rtol=0)
torch.testing.assert_close(after.square().mean(), torch.tensor(0.64), atol=1e-6, rtol=0)
assert torch.equal(w, saved)''',
'''merged = w.detach().clone() + scale * (a @ b).detach()
torch.testing.assert_close(x @ merged, after.detach(), atol=1e-6, rtol=0)
assert torch.equal(w, saved)''',
'''delta = (a @ b).detach()
assert int(torch.linalg.matrix_rank(delta)) == 1
assert int(torch.linalg.matrix_rank(delta)) <= rank
torch.testing.assert_close((4 / rank) * delta, 2 * ((2 / rank) * delta), atol=1e-6, rtol=0)''',
]
    for exercise, code in zip(spec['exercises'], codes, strict=True):
        exercise['code'] = code
    spec['exercises'][0]['prompt'] = 'Construct W=I8, A=ones(8,2)/8, B=zeros(2,8), rank 2 and alpha 4, then count stored entries.'
    spec['exercises'][0]['expected'] = '64 base entries, 32 trainable adapter entries and scale 2.'
    spec['exercises'][1]['prompt'] = 'Compare the effective output with the frozen base before any update.'
    spec['exercises'][1]['expected'] = 'Both outputs equal a row of eight ones; the initial update matrix is zero.'
    spec['exercises'][2]['prompt'] = 'Differentiate the mean squared output against a zero target and inspect both factor gradients.'
    spec['exercises'][2]['expected'] = 'A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.'
    spec['exercises'][3]['prompt'] = 'Take one SGD step of size 0.1 on A and B and derive the updated output and objective.'
    spec['exercises'][3]['expected'] = 'B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.'
    spec['exercises'][4]['prompt'] = 'Create a detached merged matrix without mutating W and compare its predictions.'
    spec['exercises'][4]['expected'] = 'Merged/unmerged parity within 1e-6; original W remains exactly unchanged.'
    spec['exercises'][5]['prompt'] = 'Measure the update rank after this symmetric first step and compare alpha 4 with alpha 2 using the same factors.'
    spec['exercises'][5]['expected'] = 'The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.'
    spec['exercises'][2]['why'] = 'The derivative for A contains B transpose, so it is zero at B=0 while remaining connected to the graph. The derivative for B is s(XA) transpose times G. Here XA=[1,1], G is eight copies of 1/4 and s=2, giving 0.5 in every entry. This independent arithmetic is more diagnostic than only checking whether a gradient is nonzero.'
    spec['exercises'][3]['why'] = 'The first update changes B from zero to -0.05 and leaves A unchanged. The scaled update matrix has -0.025 in every entry, so an eight-one input loses 0.2 from each output coordinate. The new output is 0.8 and its mean squared loss is 0.64. A summed loss would change this gradient scale and would require a different numerical prediction.'
    spec['exercises'][5]['why'] = 'Rank r is an upper bound. Equal A columns and equal B rows make this particular nonzero matrix rank one. The result does not contradict the rank-two parameterization, but it warns against assuming every adapter uses all configured directions. The scale comparison holds factors fixed; independently retraining with another alpha would generally change those factors too.'
    spec['appendix'] = Path(__file__).with_name('lora-oracle.md').read_text()
